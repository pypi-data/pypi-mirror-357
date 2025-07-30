#!/usr/bin/env python3
"""
Utility script for running model training with automatic dependency handling.

Usage:
  python train_model.py --model <model_name> --dataset <dataset> --output <output_dir>

Example:
  python train_model.py --model mistralai/Mistral-7B-v0.1 --dataset data/poc/formatted_dataset.json --output training_output
"""

import argparse
import os
import sys
from pathlib import Path
import traceback
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from training.finetuner import Finetuner, FinetuningConfig
from utils.dependency_manager import DependencyManager

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Train a model with automatic dependency handling"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        required=True, 
        help="Model name or path from Hugging Face"
    )
    
    parser.add_argument(
        "--dataset", 
        type=str, 
        required=True, 
        help="Path to dataset file or dataset type (poc, structured, etc.)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default="training_output", 
        help="Output directory for model and checkpoints"
    )
    
    parser.add_argument(
        "--approach", 
        type=str, 
        choices=["qlora", "lora", "full"], 
        default="qlora", 
        help="Training approach to use"
    )
    
    parser.add_argument(
        "--epochs", 
        type=int, 
        default=3, 
        help="Number of epochs to train for"
    )
    
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=1, 
        help="Batch size for training"
    )
    
    parser.add_argument(
        "--learning-rate", 
        type=float, 
        default=2e-4, 
        help="Learning rate for training"
    )
    
    parser.add_argument(
        "--install-deps",
        action='store_true',
        help="Automatically install missing dependencies"
    )
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"[INFO] Starting training script with model: {args.model}")
    
    # Check if model requires specific dependencies
    print(f"[INFO] Checking dependencies for model: {args.model}")
    
    model_name = args.model.lower()
    required_dependencies = []
    
    # Find all dependencies required for this model
    for arch, dependencies in DependencyManager.MODEL_DEPENDENCIES.items():
        if arch.lower() in model_name:
            required_dependencies.extend(dependencies)
    
    # Check if each dependency is installed
    missing_dependencies = []
    for dependency in required_dependencies:
        package_name = dependency.split(">=")[0].split("==")[0].strip()
        try:
            __import__(package_name)
            print(f"[INFO] ✓ Required dependency {package_name} is installed")
        except ImportError:
            missing_dependencies.append(dependency)
            print(f"[WARNING] ✗ Required dependency {package_name} is missing")
    
    # Handle missing dependencies
    if missing_dependencies:
        print(f"[WARNING] Missing dependencies: {', '.join(missing_dependencies)}")
        
        if args.install_deps:
            print("[INFO] Installing missing dependencies...")
            for dependency in missing_dependencies:
                print(f"[INFO] Installing {dependency}...")
                if not DependencyManager.install_package(dependency):
                    print(f"[ERROR] Failed to install {dependency}")
                    print("Please install the dependencies manually and try again:")
                    for dep in missing_dependencies:
                        print(f"  pip install {dep}")
                    sys.exit(1)
            
            print("[INFO] All dependencies installed successfully")
        else:
            print("[ERROR] Missing required dependencies. Run with --install-deps to install them automatically or install manually:")
            for dependency in missing_dependencies:
                print(f"  pip install {dependency}")
            sys.exit(1)
    
    # Setup fine-tuning configuration
    config = FinetuningConfig(
        model_name=args.model,
        output_dir=str(output_dir),
        training_type=args.approach,
        dataset_path=args.dataset,
        dataset_type="custom" if os.path.isfile(args.dataset) else args.dataset,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        epochs=args.epochs
    )
    
    print(f"[INFO] Configuration setup complete. Ready to start fine-tuning.")
    
    try:
        # Create and run finetuner
        finetuner = Finetuner(config)
        
        # Define simple progress callback
        class ProgressCallback:
            def on_train_begin(self):
                print("[INFO] Training started")
                
            def on_epoch_begin(self, epoch, total_epochs, steps):
                print(f"[INFO] Starting epoch {epoch}/{total_epochs} with {steps} steps")
                
            def on_step(self, step, total_steps, loss, learning_rate):
                if step % 50 == 0:
                    print(f"[INFO] Step {step}/{total_steps}, Loss: {loss:.4f}, LR: {learning_rate:.6f}")
                    
            def on_epoch_end(self, epoch, metrics):
                print(f"[INFO] Epoch {epoch} completed. Loss: {metrics.get('loss', 'N/A')}")
                
            def on_train_end(self, output_dir):
                print(f"[INFO] Training completed. Model saved to: {output_dir}")
        
        # Set callbacks
        finetuner.set_callbacks(ProgressCallback())
        
        # Run fine-tuning
        results = finetuner.run_finetuning()
        
        # Print results summary
        print("\n[INFO] Training Results Summary:")
        print(f"  Model: {args.model}")
        print(f"  Output directory: {results['output_dir']}")
        print(f"  Training approach: {args.approach}")
        
        # Print evaluation metrics if available
        if 'eval_metrics' in results:
            print("\n[INFO] Evaluation Metrics:")
            for metric, value in results['eval_metrics'].items():
                if isinstance(value, (int, float)):
                    print(f"  {metric}: {value:.6f}")
                else:
                    print(f"  {metric}: {value}")
        
        # Save training results
        results_file = output_dir / "training_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "model": args.model,
                "dataset": args.dataset,
                "approach": args.approach,
                "results": results
            }, f, indent=2)
        
        print(f"[INFO] Results saved to {results_file}")
        print("\n[INFO] Training completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Training failed: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
