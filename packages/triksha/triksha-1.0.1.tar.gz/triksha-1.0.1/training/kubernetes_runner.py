#!/usr/bin/env python3
"""
Kubernetes Training Runner

This module runs inside a Kubernetes pod to perform model training.
It loads configuration from environment variables and periodically
checks for pause/resume signals from the control plane.
"""
import os
import sys
import json
import time
import signal
import logging
from pathlib import Path
import threading
from typing import Dict, Any, Optional
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("kubernetes_training.log")
    ]
)
logger = logging.getLogger(__name__)

# Import training modules
try:
    from training.finetuner import Finetuner, FinetuningConfig
except ImportError:
    # Try relative import if package not installed
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from finetuner import Finetuner, FinetuningConfig

class KubernetesTrainingRunner:
    """Handle training inside a Kubernetes pod with pause/resume capability"""
    
    def __init__(self):
        """Initialize the runner"""
        self.run_id = os.environ.get("TRAINING_RUN_ID")
        self.output_dir = os.environ.get("TRAINING_OUTPUT_DIR")
        self.config_json = os.environ.get("TRAINING_CONFIG")
        
        if not self.run_id or not self.output_dir or not self.config_json:
            raise ValueError("Required environment variables not set: TRAINING_RUN_ID, TRAINING_OUTPUT_DIR, TRAINING_CONFIG")
            
        logger.info(f"Initializing training run {self.run_id} in {self.output_dir}")
        
        # Parse the training config
        self.config = json.loads(self.config_json)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        
        # Training state
        self.paused = False
        self.finetuner = None
        self.metrics_db_path = os.path.join(self.output_dir, "metrics.db")
        
        # Initialize metrics database
        self._setup_metrics_db()
        
        # Start the pause monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_pause_status, daemon=True)
        self.monitor_thread.start()
        
    def _setup_metrics_db(self):
        """Set up SQLite database for metrics"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            epoch INTEGER,
            step INTEGER,
            loss REAL,
            learning_rate REAL,
            timestamp REAL,
            additional_metrics TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            timestamp REAL,
            message TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def _save_metrics(self, epoch: int, step: int, loss: float, lr: float, additional: Dict = None):
        """Save metrics to the database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        additional_json = json.dumps(additional) if additional else "{}"
        
        cursor.execute('''
        INSERT INTO training_metrics (epoch, step, loss, learning_rate, timestamp, additional_metrics)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (epoch, step, loss, lr, time.time(), additional_json))
        
        conn.commit()
        conn.close()
        
    def _save_status(self, status: str, message: str = ""):
        """Save status to the database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO training_status (status, timestamp, message)
        VALUES (?, ?, ?)
        ''', (status, time.time(), message))
        
        conn.commit()
        conn.close()
        
    def _monitor_pause_status(self):
        """Monitor for pause/resume signals via pod labels"""
        import kubernetes.client
        from kubernetes.client.rest import ApiException
        
        # Get the pod name from downward API
        pod_name = os.environ.get("HOSTNAME")
        if not pod_name:
            logger.warning("Could not get pod name, pause/resume functionality disabled")
            return
            
        logger.info(f"Starting pause monitor for pod {pod_name}")
        
        try:
            # Create the Kubernetes API client
            kubernetes.config.load_incluster_config()
            api = kubernetes.client.CoreV1Api()
            
            # Monitor for pause label
            while True:
                try:
                    pod = api.read_namespaced_pod(name=pod_name, namespace="default")
                    labels = pod.metadata.labels or {}
                    
                    # Check for pause label
                    paused = labels.get("dravik.ai/paused") == "true"
                    
                    # If pause state changed, handle it
                    if paused != self.paused:
                        if paused:
                            logger.info("Received pause signal")
                            self._save_status("paused", "Received pause signal from control plane")
                        else:
                            logger.info("Received resume signal")
                            self._save_status("resumed", "Received resume signal from control plane")
                            
                        self.paused = paused
                        
                except ApiException as e:
                    logger.warning(f"Error checking pod status: {str(e)}")
                    
                # Check every 5 seconds
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error in pause monitor: {str(e)}")
            
    def _handle_sigterm(self, signum, frame):
        """Handle SIGTERM gracefully"""
        logger.info("Received SIGTERM, shutting down gracefully")
        self._save_status("terminating", "Received termination signal")
        sys.exit(0)
        
    def _create_finetuning_config(self) -> FinetuningConfig:
        """Create a FinetuningConfig from the JSON config"""
        # Extract training parameters
        training_params = self.config.get("training_params", {})
        
        # Create the config object
        finetuning_config = FinetuningConfig(
            model_name=self.config["model_id"],
            output_dir=self.output_dir,
            training_type=self.config["approach"],
            # Dataset handling
            dataset_path=self._get_dataset_path(),
            dataset_type=self.config["dataset"].get("type", "custom"),
            # Training parameters
            learning_rate=training_params.get("learning_rate", 2e-5),
            batch_size=training_params.get("batch_size", 8),
            epochs=training_params.get("epochs", 3),
            # Optionally add LoRA params if present
            lora_r=training_params.get("lora_rank", 16),
            lora_alpha=training_params.get("lora_alpha", 32),
            # Advanced params if available
            gradient_accumulation_steps=training_params.get("gradient_accumulation_steps", 4),
            warmup_ratio=training_params.get("warmup_ratio", 0.03)
        )
        
        return finetuning_config
    
    def _get_dataset_path(self) -> str:
        """Get the dataset path from the config"""
        dataset_config = self.config.get("dataset", {})
        
        if isinstance(dataset_config, dict) and "path" in dataset_config:
            # If the dataset is a custom path
            return dataset_config["path"]
        elif isinstance(dataset_config, dict) and "id" in dataset_config:
            # If the dataset is from a database, look for it in the expected data directory
            return f"/app/data/{dataset_config['id']}"
        else:
            # Default fallback
            return "/app/data/training_data.json"
    
    def run(self):
        """Run the training process"""
        logger.info("Starting training process")
        self._save_status("started", "Training process started")
        
        try:
            # Create the finetuning config
            finetuning_config = self._create_finetuning_config()
            
            # Initialize the finetuner
            self.finetuner = Finetuner(finetuning_config)
            
            # Set up custom callbacks to handle pause/resume
            class PauseAwareCallbacks:
                def __init__(self, runner):
                    self.runner = runner
                    self.current_epoch = 0
                    self.total_epochs = finetuning_config.epochs
                    self.current_step = 0
                    self.total_steps = 0
                
                def on_train_begin(self):
                    logger.info("Training started")
                    runner._save_status("training", "Training process began")
                
                def on_epoch_begin(self, epoch, total_epochs, steps):
                    logger.info(f"Starting epoch {epoch}/{total_epochs} with {steps} steps")
                    self.current_epoch = epoch
                    self.total_epochs = total_epochs
                    self.total_steps = steps
                
                def on_step(self, step, total_steps, loss, lr):
                    # Check if we're paused
                    while runner.paused:
                        time.sleep(1)  # Wait while paused
                        
                    self.current_step = step
                    
                    # Save metrics every 10 steps 
                    if step % 10 == 0:
                        runner._save_metrics(
                            self.current_epoch, 
                            step, 
                            loss, 
                            lr
                        )
                
                def on_epoch_end(self, epoch, metrics):
                    logger.info(f"Completed epoch {epoch} with metrics: {metrics}")
                    runner._save_metrics(
                        epoch, 
                        self.total_steps, 
                        metrics.get("loss", 0.0),
                        metrics.get("learning_rate", 0.0),
                        metrics
                    )
                
                def on_train_end(self, model_path):
                    logger.info(f"Training completed, model saved to {model_path}")
                    runner._save_status("completed", f"Training completed, model saved to {model_path}")
            
            # Create callback handler and attach to finetuner
            callbacks = PauseAwareCallbacks(self)
            self.finetuner.set_callbacks(callbacks)
            
            # Run the training
            logger.info("Starting fine-tuning process")
            result = self.finetuner.run_finetuning()
            
            # Save the result information
            result_path = os.path.join(self.output_dir, "result.json")
            with open(result_path, "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Training complete! Model saved to: {self.output_dir}")
            self._save_status("completed", f"Training completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self._save_status("failed", f"Training failed with error: {str(e)}")
            return False


def main():
    """Main entry point"""
    try:
        runner = KubernetesTrainingRunner()
        success = runner.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Unrecoverable error: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 