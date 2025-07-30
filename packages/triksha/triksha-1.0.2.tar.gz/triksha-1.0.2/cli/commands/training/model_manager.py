"""Model management for training operations"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.progress import Progress
import time

class ModelManager:
    """Handles model operations including loading, training and inference"""
    
    def __init__(self, db, config):
        """Initialize model manager"""
        self.db = db
        self.config = config
        self.console = Console()
        self.models_dir = Path(config.get('models_dir', 'models'))
        self.models_dir.mkdir(exist_ok=True, parents=True)
        
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available base models for fine-tuning"""
        # This would typically query available models from a config or API
        # For now, returning a hard-coded list of commonly used models
        return [
            {
                "id": "mistralai/Mistral-7B-v0.1",
                "display_name": "Mistral 7B",
                "description": "High-quality 7B parameter model",
                "size_gb": 14,
                "compatible_approaches": ["lora", "qlora"]
            },
            {
                "id": "meta-llama/Llama-2-7b-hf",
                "display_name": "Llama 2 7B",
                "description": "Meta's Llama 2 7B base model",
                "size_gb": 14,
                "compatible_approaches": ["lora", "qlora", "full"]
            },
            {
                "id": "meta-llama/Llama-2-13b-hf",
                "display_name": "Llama 2 13B",
                "description": "Meta's Llama 2 13B base model (requires more resources)",
                "size_gb": 26,
                "compatible_approaches": ["lora", "qlora"]
            },
            {
                "id": "stabilityai/stablelm-base-alpha-7b",
                "display_name": "StableLM 7B",
                "description": "Stability AI's 7B parameter base model",
                "size_gb": 14,
                "compatible_approaches": ["lora", "qlora", "full"]
            },
            {
                "id": "HuggingFaceH4/zephyr-7b-beta",
                "display_name": "Zephyr 7B",
                "description": "High-quality instruction-tuned model",
                "size_gb": 14,
                "compatible_approaches": ["lora", "qlora"]
            }
        ]
    
    def train_model(self, config: Dict[str, Any], output_dir: str, callbacks: Dict = None):
        """Train a model using the specified configuration"""
        self.console.print(f"[bold green]Starting training of model: {config['model_id']}[/]")
        self.console.print(f"[green]Output directory: {output_dir}[/]")
        
        # Import the actual training implementation
        try:
            from training.finetuner import Finetuner, FinetuningConfig
            
            # Create output dir if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the config
            with open(os.path.join(output_dir, "config.json"), "w") as f:
                json.dump(config, f, indent=2)
            
            # Convert our UI config to the FinetuningConfig expected by Finetuner
            training_params = config["training_params"]
            finetuning_config = FinetuningConfig(
                model_name=config["model_id"],
                output_dir=output_dir,
                training_type=config["approach"],
                # Dataset handling
                dataset_path=self._get_dataset_path(config["dataset"]),
                dataset_type=config["dataset"].get("type", "custom"),
                # Training parameters
                learning_rate=training_params.get("learning_rate", 2e-5),
                batch_size=training_params.get("batch_size", 8),
                epochs=training_params.get("epochs", 3),
                # Optionally add LoRA params if present
                lora_r=training_params.get("lora_rank", 16) if "lora_rank" in training_params else 16,
                lora_alpha=training_params.get("lora_alpha", 32) if "lora_alpha" in training_params else 32,
                # Advanced params if available
                gradient_accumulation_steps=training_params.get("gradient_accumulation_steps", 4),
                warmup_ratio=training_params.get("warmup_ratio", 0.03),
                use_8bit="quantization" in training_params and training_params["quantization"] == "8bit"
            )
            
            # Initialize the finetuner
            finetuner = Finetuner(finetuning_config)
            
            # Set up callback hooks if we have callbacks
            if callbacks:
                class TrainingCallbacks:
                    def __init__(self, callbacks_dict):
                        self.callbacks = callbacks_dict
                    
                    def on_train_begin(self):
                        if 'on_start' in self.callbacks:
                            self.callbacks['on_start']()
                    
                    def on_epoch_begin(self, epoch, total_epochs, steps):
                        if 'on_epoch_begin' in self.callbacks:
                            self.callbacks['on_epoch_begin'](epoch, total_epochs, steps)
                    
                    def on_step(self, step, total_steps, loss, lr):
                        if 'on_step' in self.callbacks:
                            self.callbacks['on_step'](step, total_steps, loss, lr)
                    
                    def on_epoch_end(self, epoch, metrics):
                        if 'on_epoch_end' in self.callbacks:
                            self.callbacks['on_epoch_end'](epoch, metrics)
                    
                    def on_train_end(self, model_path):
                        if 'on_complete' in self.callbacks:
                            self.callbacks['on_complete'](model_path)
                
                # Create callback handler and attach to finetuner
                callback_handler = TrainingCallbacks(callbacks)
                finetuner.set_callbacks(callback_handler)
            
            # Run the training
            self.console.print(f"[cyan]Running fine-tuning process...[/]")
            result = finetuner.run_finetuning()
            
            # Save the result information
            result_path = os.path.join(output_dir, "result.json")
            with open(result_path, "w") as f:
                json.dump(result, f, indent=2)
            
            self.console.print(f"[bold green]Training complete! Model saved to: {output_dir}[/]")
            return output_dir
            
        except ImportError:
            self.console.print("[bold red]Error: Could not import Finetuner. Make sure the training module is installed.[/]")
            self.console.print("[yellow]Running in simulation mode for UI testing.[/]")
            
            # Simulation mode - this code stays the same
            self._simulate_training(config, output_dir, callbacks)
            return output_dir
    
    def _simulate_training(self, config: Dict[str, Any], output_dir: str, callbacks: Dict = None):
        """Simulate a training process for testing the UI"""
        import time
        import random
        
        self.console.print("[yellow]Simulating training process...[/]")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the configuration
        with open(os.path.join(output_dir, "config.json"), "w") as f:
            json.dump(config, f, indent=2)
        
        # Get total epochs and steps per epoch
        epochs = config["training_params"]["epochs"]
        steps_per_epoch = 50  # Simulate 50 steps per epoch
        
        # Simulate initialization
        time.sleep(2)
        
        # Call on_start callback if provided
        if callbacks and "on_start" in callbacks:
            callbacks["on_start"]()
        
        # Simulate epochs
        for epoch in range(1, epochs + 1):
            # Call on_epoch_begin callback if provided
            if callbacks and "on_epoch_begin" in callbacks:
                callbacks["on_epoch_begin"](epoch, epochs, steps_per_epoch)
            
            # Simulate steps
            for step in range(1, steps_per_epoch + 1):
                # Simulate a training step
                time.sleep(0.1)
                
                # Calculate a decreasing loss
                base_loss = 2.0 * (1 - (epoch - 1) / epochs)
                loss = base_loss * (1 - (step / steps_per_epoch) * 0.3) + random.uniform(-0.1, 0.1)
                loss = max(0.1, loss)  # Ensure loss doesn't go below 0.1
                
                # Calculate learning rate with decay
                lr = config["training_params"]["learning_rate"] * (1 - (epoch - 1 + step/steps_per_epoch) / epochs)
                
                # Call on_step callback if provided
                if callbacks and "on_step" in callbacks:
                    callbacks["on_step"](step, steps_per_epoch, loss, lr)
            
            # Simulate epoch metrics
            metrics = {
                "loss": loss,
                "perplexity": 2 ** loss,
                "accuracy": 0.5 + (0.4 * (epoch / epochs))
            }
            
            # Call on_epoch_end callback if provided
            if callbacks and "on_epoch_end" in callbacks:
                callbacks["on_epoch_end"](epoch, metrics)
        
        # Create a dummy model file
        with open(os.path.join(output_dir, "model.bin"), "wb") as f:
            f.write(b"\x00" * 1024)  # Write 1KB of zeros
        
        model_path = os.path.join(output_dir, "model.bin")
        
        # Call on_complete callback if provided
        if callbacks and "on_complete" in callbacks:
            callbacks["on_complete"](model_path)
        
        # Save dummy result information
        result = {
            "status": "success",
            "epochs_completed": epochs,
            "final_loss": loss,
            "model_path": model_path
        }
        
        with open(os.path.join(output_dir, "result.json"), "w") as f:
            json.dump(result, f, indent=2)
        
        self.console.print("[bold green]Simulation complete![/]")
        return output_dir
    
    def _get_dataset_path(self, dataset_config: Dict[str, Any]) -> Optional[str]:
        """Get the file path for a dataset from its configuration"""
        if not dataset_config:
            return None
        
        # Direct path provided
        if "path" in dataset_config and os.path.exists(dataset_config["path"]):
            return dataset_config["path"]
        
        # Try to get from database
        if "id" in dataset_config:
            try:
                query = "SELECT path FROM datasets WHERE id = ?"
                cursor = self.db.cursor()
                cursor.execute(query, (dataset_config["id"],))
                result = cursor.fetchone()
                if result and os.path.exists(result[0]):
                    return result[0]
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not fetch dataset from DB: {str(e)}[/]")
        
        return None
    
    def load_model(self, model_path: str) -> bool:
        """Load a model for inference"""
        try:
            if not os.path.exists(model_path):
                self.console.print(f"[bold red]Error: Model path not found: {model_path}[/]")
                return False
            
            self.console.print(f"[green]Loading model from: {model_path}[/]")
            
            # This would typically load the model into memory
            # For now, just simulate the loading process
            with Progress() as progress:
                task = progress.add_task("[cyan]Loading model...", total=100)
                
                for i in range(0, 101, 10):
                    progress.update(task, completed=i)
                    time.sleep(0.2)
            
            self.console.print("[bold green]Model loaded successfully![/]")
            return True
        
        except Exception as e:
            self.console.print(f"[bold red]Error loading model: {str(e)}[/]")
            return False
