"""Training commands for Dravik CLI"""
from typing import List, Tuple, Dict, Any, Optional
from rich.console import Console
from pathlib import Path
import inquirer
import json
from datetime import datetime

from training.finetuner import Finetuner, FinetuningConfig
from db_handler import DravikDB

class TrainingCommands:
    """Commands for model training"""
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.console = Console()
        self.dravik_db = DravikDB()
    
    def _prepare_dataset_choices(self) -> List[Tuple[str, str]]:
        """Prepare dataset choices for fine-tuning"""
        # Default dataset options
        dataset_choices = [
            ("Full Dataset (Complete structured dataset)", "full"),
            ("POC Dataset (Smaller proof-of-concept dataset)", "poc")
        ]
        
        # Try to find additional datasets in the database
        try:
            # Get structured and POC datasets from the database
            structured_datasets = self.dravik_db.list_datasets("structured")
            poc_datasets = self.dravik_db.list_datasets("poc")
            
            # Add custom datasets if available
            for dataset_name in structured_datasets:
                dataset_choices.append((f"Structured: {dataset_name}", f"structured_{dataset_name}"))
            
            for dataset_name in poc_datasets:
                dataset_choices.append((f"POC: {dataset_name}", f"poc_{dataset_name}"))
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load custom datasets: {e}[/]")
            
        return dataset_choices
            
    def train_model(self):
        """Train a model using selected parameters"""
        try:
            # First, select dataset
            dataset_choices = self._prepare_dataset_choices()
            dataset_question = [
                inquirer.List(
                    'dataset_type',
                    message="Select dataset type for fine-tuning",
                    choices=dataset_choices,
                    default='poc'
                )
            ]
            
            dataset_answer = inquirer.prompt(dataset_question)
            if not dataset_answer:
                return
            
            dataset_type = dataset_answer['dataset_type']
            
            # Now select model
            model_choices = [
                ("Mistral 7B", "mistralai/Mistral-7B-v0.1"),
                ("Llama 2 7B", "meta-llama/Llama-2-7b-hf"),
                ("Zephyr 7B", "HuggingFaceH4/zephyr-7b-beta")
            ]
            
            model_question = [
                inquirer.List(
                    'model_name',
                    message="Select model to fine-tune",
                    choices=model_choices
                )
            ]
            
            model_answer = inquirer.prompt(model_question)
            if not model_answer:
                return
                
            model_name = model_answer['model_name']
            
            # Select approach
            approach_choices = [
                ("LoRA (Low-Rank Adaptation)", "lora"),
                ("QLoRA (Quantized Low-Rank Adaptation)", "qlora"),
                ("Full Fine-tuning", "full")
            ]
            
            approach_question = [
                inquirer.List(
                    'approach',
                    message="Select fine-tuning approach",
                    choices=approach_choices
                )
            ]
            
            approach_answer = inquirer.prompt(approach_question)
            if not approach_answer:
                return
                
            approach = approach_answer['approach']
            
            # Display selected options and confirm
            self.console.print(f"[green]Selected dataset: {dataset_type}[/]")
            self.console.print(f"[green]Selected model: {model_name}[/]")
            self.console.print(f"[green]Selected approach: {approach}[/]")
            
            # Ask for confirmation
            confirm = inquirer.confirm("Proceed with fine-tuning?", default=True)
            if not confirm:
                self.console.print("[yellow]Fine-tuning cancelled.[/]")
                return
                
            # Start fine-tuning
            output_dir = Path("training_outputs") / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create config
            fine_tuning_config = FinetuningConfig(
                model_name=model_name,
                output_dir=str(output_dir),
                training_type=approach,
                dataset_type=dataset_type.split('_')[0] if '_' in dataset_type else dataset_type
            )
            
            # Execute training
            self.console.print("[bold green]Starting fine-tuning process...[/]")
            
            finetuner = Finetuner(fine_tuning_config)
            results = finetuner.run_finetuning()
            
            self.console.print("[bold green]Fine-tuning complete![/]")
            self.console.print(f"[green]Output directory: {results['output_dir']}[/]")
            
            # Save training info to database
            try:
                self._save_training_result(
                    dataset_type=dataset_type,
                    model_name=model_name,
                    approach=approach,
                    output_dir=results['output_dir'],
                    metrics=results
                )
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not save training result to database: {e}[/]")

        except Exception as e:
            self.console.print(f"[bold red]Error in fine-tuning: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            
    def _save_training_result(self, dataset_type: str, model_name: str, approach: str, 
                             output_dir: str, metrics: Dict[str, Any]):
        """Save training result to database"""
        try:
            training_info = {
                "dataset_type": dataset_type,
                "model_name": model_name,
                "approach": approach,
                "output_dir": output_dir,
                "created_at": datetime.now().isoformat(),
                "metrics": metrics
            }
            
            # Use DravikDB to save the result if it has the method
            if hasattr(self.dravik_db, 'save_training_result'):
                self.dravik_db.save_training_result(training_info)
            else:
                # Otherwise save to a JSON file
                with open(Path(output_dir) / "training_info.json", "w") as f:
                    json.dump(training_info, f, indent=2)
                    
            self.console.print("[green]Training result saved.[/]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save training result: {e}[/]")

    def view_training_history(self):
        """View training history"""
        self.console.print("[yellow]Training history view not yet implemented[/]")
    
    def manage_training_configs(self):
        """Manage training configurations"""
        self.console.print("[yellow]Training config management not yet implemented[/]")
