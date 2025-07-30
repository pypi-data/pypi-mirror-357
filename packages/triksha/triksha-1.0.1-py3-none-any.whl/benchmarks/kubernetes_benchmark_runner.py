#!/usr/bin/env python3
"""
Kubernetes Benchmark Runner

This module runs inside a Kubernetes pod to perform benchmarks.
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
from typing import Dict, List, Any, Optional
import sqlite3
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("kubernetes_benchmark.log")
    ]
)
logger = logging.getLogger(__name__)

# Import benchmark modules - try both absolute and relative imports
try:
    from benchmarks import BenchmarkRunner
    from benchmarks.api.bypass_tester import BypassTester
    from benchmarks.flexible_benchmark import FlexibleBenchmarkRunner
    from benchmarks.utils.backup_manager import BackupManager
except ImportError:
    # Try relative import if package not installed
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from benchmark_runner import BenchmarkRunner
    from api.bypass_tester import BypassTester
    from flexible_benchmark import FlexibleBenchmarkRunner
    from utils.backup_manager import BackupManager

class KubernetesBenchmarkRunner:
    """Handle benchmarking inside a Kubernetes pod with pause/resume capability"""
    
    def __init__(self):
        """Initialize the runner"""
        self.run_id = os.environ.get("BENCHMARK_RUN_ID")
        self.output_dir = os.environ.get("BENCHMARK_OUTPUT_DIR")
        self.config_json = os.environ.get("BENCHMARK_CONFIG")
        
        if not self.run_id or not self.output_dir or not self.config_json:
            raise ValueError("Required environment variables not set: BENCHMARK_RUN_ID, BENCHMARK_OUTPUT_DIR, BENCHMARK_CONFIG")
            
        logger.info(f"Initializing benchmark run {self.run_id} in {self.output_dir}")
        
        # Parse the benchmark config
        self.config = json.loads(self.config_json)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        
        # Benchmark state
        self.paused = False
        self.metrics_db_path = os.path.join(self.output_dir, "metrics.db")
        self.backup_manager = BackupManager()
        
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
        CREATE TABLE IF NOT EXISTS benchmark_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_idx INTEGER,
            model_name TEXT,
            success BOOLEAN,
            response_time REAL,
            response_length INTEGER,
            timestamp REAL,
            additional_metrics TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS benchmark_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            timestamp REAL,
            message TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def _save_metrics(self, prompt_idx: int, model_name: str, success: bool, 
                    response_time: float, response_length: int, additional: Dict = None):
        """Save metrics to the database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        additional_json = json.dumps(additional) if additional else "{}"
        
        cursor.execute('''
        INSERT INTO benchmark_metrics (
            prompt_idx, model_name, success, response_time, response_length, timestamp, additional_metrics
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            prompt_idx, 
            model_name, 
            1 if success else 0, 
            response_time, 
            response_length,
            time.time(), 
            additional_json
        ))
        
        conn.commit()
        conn.close()
        
    def _save_status(self, status: str, message: str = ""):
        """Save status to the database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO benchmark_status (status, timestamp, message)
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
    
    def _check_pause(self):
        """Check if we're paused and wait if necessary"""
        while self.paused:
            logger.debug("Benchmark is paused, waiting...")
            time.sleep(1)
            
    def _setup_callbacks(self):
        """Set up callbacks for benchmarking progress"""
        def on_prompt_start(prompt_idx, prompt, model_name):
            self._check_pause()
            logger.info(f"Starting prompt {prompt_idx+1} with model {model_name}")
            
        def on_prompt_complete(prompt_idx, prompt, model_name, result):
            success = result.get("success", False)
            response_time = result.get("response_time", 0)
            response_length = len(result.get("response", ""))
            
            logger.info(f"Completed prompt {prompt_idx+1} with model {model_name}: " + 
                      f"success={success}, time={response_time:.2f}s, length={response_length}")
            
            self._save_metrics(
                prompt_idx,
                model_name,
                success,
                response_time,
                response_length,
                result
            )
            
        def on_benchmark_complete(results):
            logger.info(f"Benchmark completed with results: {json.dumps(results, indent=2)}")
            self._save_status("completed", "Benchmark completed successfully")
            
        return {
            "on_prompt_start": on_prompt_start,
            "on_prompt_complete": on_prompt_complete,
            "on_benchmark_complete": on_benchmark_complete
        }
        
    def run_api_benchmark(self):
        """Run an API benchmark based on the config"""
        logger.info("Starting API benchmark")
        self._save_status("started", "API benchmark started")
        
        try:
            # Extract configuration
            model_path = self.config.get("model_path", "karanxa/Dravik")
            target_models = self.config.get("target_models", ["gpt-4", "gemini-pro"])
            num_prompts = self.config.get("num_prompts", 5)
            
            # Initialize the benchmark runner
            runner = BenchmarkRunner(model_path=model_path, verbose=True)
            
            # Generate prompts
            prompts = runner.generate_test_prompts(num_prompts)
            
            # Log the prompts
            for i, prompt in enumerate(prompts):
                logger.info(f"Prompt {i+1}: {prompt[:100]}...")
            
            # Set up callbacks
            callbacks = self._setup_callbacks()
            
            # Run the benchmark with pause checks
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_with_pause_checks():
                return await runner.run_benchmark(prompts)
            
            results = loop.run_until_complete(run_with_pause_checks())
            loop.close()
            
            # Save the final results
            with open(os.path.join(self.output_dir, "results.json"), "w") as f:
                json.dump(results, f, indent=2)
                
            # Execute callback
            callbacks["on_benchmark_complete"](results)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during API benchmark: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self._save_status("failed", f"API benchmark failed with error: {str(e)}")
            return False
    
    def run_flexible_benchmark(self):
        """Run a flexible benchmark based on the config"""
        logger.info("Starting flexible benchmark")
        self._save_status("started", "Flexible benchmark started")
        
        try:
            # Extract configuration
            target_model = self.config.get("target_model", "karanxa/Dravik")
            domain = self.config.get("domain", "general")
            benchmark_name = self.config.get("benchmark_name")
            eval_models = self.config.get("eval_models", [])
            max_examples = self.config.get("max_examples", 10)
            
            # Initialize the flexible benchmark runner
            runner = FlexibleBenchmarkRunner(
                target_model=target_model,
                domain=domain,
                benchmark_name=benchmark_name,
                eval_models=eval_models,
                output_dir=self.output_dir,
                max_examples=max_examples,
                verbose=True
            )
            
            # Set up progress callback
            def progress_callback(example_idx, total, metrics):
                self._check_pause()  # Check if paused
                
                logger.info(f"Progress: {example_idx+1}/{total}")
                logger.info(f"Metrics: {metrics}")
                
                self._save_metrics(
                    example_idx,
                    metrics.get("model", "unknown"),
                    metrics.get("success", False),
                    metrics.get("time", 0),
                    metrics.get("length", 0),
                    metrics
                )
            
            # Run the benchmark
            runner.set_progress_callback(progress_callback)
            results = runner.run()
            
            # Save the final results
            with open(os.path.join(self.output_dir, "results.json"), "w") as f:
                json.dump(results, f, indent=2)
                
            self._save_status("completed", "Flexible benchmark completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during flexible benchmark: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self._save_status("failed", f"Flexible benchmark failed with error: {str(e)}")
            return False
            
    def run(self):
        """Run the appropriate benchmark based on the config"""
        logger.info(f"Starting benchmark run with config: {json.dumps(self.config, indent=2)}")
        
        # Determine which benchmark to run
        benchmark_type = self.config.get("benchmark_type", "api")
        
        if benchmark_type == "api":
            return self.run_api_benchmark()
        elif benchmark_type == "flexible":
            return self.run_flexible_benchmark()
        else:
            logger.error(f"Unknown benchmark type: {benchmark_type}")
            self._save_status("failed", f"Unknown benchmark type: {benchmark_type}")
            return False

def main():
    """Main entry point"""
    try:
        runner = KubernetesBenchmarkRunner()
        success = runner.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Unrecoverable error: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 