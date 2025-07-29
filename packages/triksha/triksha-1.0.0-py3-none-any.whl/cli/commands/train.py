from rich.console import Console
import inquirer
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import os
from pathlib import Path
from db_handler import DravikDB

class TrainingCommands:
    """Commands for model training"""
    
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.console = Console()
        self.dravik_db = DravikDB()  # Initialize database handler
        
    def train_model(self):
        """Train a model using selected parameters"""
        try:
            self.console.print("[blue]Starting model fine-tuning process[/]")
            
            # First, select dataset
            dataset_choices = self._prepare_dataset_choices()
            dataset_question = [
                inquirer.List(
                    'dataset_type',
                    message="Select dataset type for fine-tuning",
                    choices=dataset_choices,
                    default='poc'  # Default to POC dataset
                )
            ]
            
            dataset_answer = inquirer.prompt(dataset_question)
            if not dataset_answer:
                return
            
            dataset_type = dataset_answer['dataset_type']
            
            # Next, select model from Hugging Face
            model_questions = [
                inquirer.List(
                    'model_name',
                    message="Select base model for fine-tuning",
                    choices=[
                        ('Mistral 7B v0.1', 'mistralai/Mistral-7B-v0.1'),
                        ('Llama 2 7B', 'meta-llama/Llama-2-7b-hf'),
                        ('Llama 2 13B', 'meta-llama/Llama-2-13b-hf'),
                        ('Falcon 7B', 'tiiuae/falcon-7b'),
                        ('Gemma 7B', 'google/gemma-7b'),
                        ('Custom model (enter path)', 'custom')
                    ],
                    default='mistralai/Mistral-7B-v0.1'
                )
            ]
            
            model_answer = inquirer.prompt(model_questions)
            if not model_answer:
                return
                
            model_name = model_answer['model_name']
            
            # If custom model, ask for the path
            if model_name == 'custom':
                custom_model_question = [
                    inquirer.Text(
                        'custom_model_path',
                        message="Enter HuggingFace model path",
                        validate=lambda _, x: len(x) > 0
                    )
                ]
                custom_answer = inquirer.prompt(custom_model_question)
                if not custom_answer:
                    return
                model_name = custom_answer['custom_model_path']
            
            # Now, select finetuning method
            finetuning_questions = [
                inquirer.List(
                    'finetuning_method',
                    message="Select fine-tuning method",
                    choices=[
                        ('Supervised Fine-Tuning (SFT)', 'sft'),
                        ('Low-Rank Adaptation (LoRA)', 'lora'),
                        ('Quantized Low-Rank Adaptation (QLoRA)', 'qlora'),
                        ('Custom fine-tuning script', 'custom_script')
                    ],
                    default='qlora'
                )
            ]
            
            finetuning_answer = inquirer.prompt(finetuning_questions)
            if not finetuning_answer:
                return
                
            finetuning_method = finetuning_answer['finetuning_method']
            
            # If custom script, ask for the path
            script_path = None
            if finetuning_method == 'custom_script':
                script_questions = [
                    inquirer.Path(
                        'script_path',
                        message="Enter path to your Python script (.py or .ipynb)",
                        exists=True,
                        path_type=inquirer.Path.FILE
                    )
                ]
                
                script_answer = inquirer.prompt(script_questions)
                if not script_answer:
                    return
                script_path = script_answer['script_path']
                
                # Validate file extension
                if not script_path.endswith(('.py', '.ipynb')):
                    self.console.print("[red]Error: File must be a .py or .ipynb file[/]")
                    return
            
            # Show advanced settings if requested
            advanced_question = [
                inquirer.Confirm(
                    'use_advanced_settings',
                    message="Configure advanced training settings?",
                    default=False
                )
            ]
            
            advanced_answer = inquirer.prompt(advanced_question)
            if not advanced_answer:
                return
            
            advanced_settings = {}
            if advanced_answer.get('use_advanced_settings', False):
                adv_questions = [
                    inquirer.Text(
                        'learning_rate',
                        message="Learning rate",
                        default="2e-4"
                    ),
                    inquirer.Text(
                        'batch_size',
                        message="Batch size",
                        default="1"
                    ),
                    inquirer.Text(
                        'epochs',
                        message="Number of epochs",
                        default="3"
                    ),
                    inquirer.Text(
                        'lora_r',
                        message="LoRA rank (if applicable)",
                        default="16"
                    ),
                    inquirer.List(
                        'quantization',
                        message="Quantization method",
                        choices=[
                            ('None', 'none'),
                            ('8-bit (faster, more memory efficient)', '8bit'),
                            ('4-bit (very memory efficient, slower)', '4bit')
                        ],
                        default='8bit'
                    )
                ]
                
                adv_answers = inquirer.prompt(adv_questions)
                if adv_answers:
                    advanced_settings = adv_answers
            
            # Display training configuration
            self.console.print("\n[bold blue]Training Configuration:[/]")
            self.console.print(f"Base model: [cyan]{model_name}[/]")
            self.console.print(f"Fine-tuning method: [cyan]{finetuning_method}[/]")
            self.console.print(f"Dataset: [cyan]{dataset_type}[/]")
            
            if finetuning_method == 'custom_script':
                self.console.print(f"Custom script: [cyan]{script_path}[/]")
                
            if advanced_settings:
                self.console.print("\n[bold blue]Advanced Settings:[/]")
                for key, value in advanced_settings.items():
                    self.console.print(f"{key}: [cyan]{value}[/]")
            
            # Confirmation
            confirm = inquirer.confirm(
                message="Start fine-tuning with these settings?",
                default=True
            )
            
            if confirm:
                self._start_finetuning(
                    model_name=model_name,
                    dataset_type=dataset_type,
                    finetuning_method=finetuning_method,
                    script_path=script_path,
                    advanced_settings=advanced_settings
                )
            else:
                self.console.print("[yellow]Fine-tuning cancelled.[/]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error in fine-tuning setup: {str(e)}[/]")
            import traceback
            traceback.print_exc()
    
    def _start_finetuning(self, model_name: str, dataset_type: str, 
                         finetuning_method: str, script_path: Optional[str] = None,
                         advanced_settings: Optional[Dict[str, Any]] = None):
        """Start the actual fine-tuning process"""
        try:
            self.console.print("[bold green]Starting fine-tuning process...[/]")
            
            # Prepare output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name_short = model_name.split('/')[-1]
            output_dir = f"models/{model_name_short}_{finetuning_method}_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save configuration for reference
            config = {
                "model_name": model_name,
                "dataset_type": dataset_type,
                "finetuning_method": finetuning_method,
                "timestamp": timestamp,
                "advanced_settings": advanced_settings or {}
            }
            
            # Save to database
            self.dravik_db.save_training_config(config)
            
            if finetuning_method == 'custom_script':
                # Execute custom script
                self.console.print(f"[blue]Executing custom script: {script_path}[/]")
                if script_path.endswith('.py'):
                    import subprocess
                    cmd = [
                        'python',
                        script_path,
                        '--model', model_name,
                        '--dataset', dataset_type,
                        '--output_dir', output_dir
                    ]
                    subprocess.run(cmd)
                elif script_path.endswith('.ipynb'):
                    self.console.print("[blue]Converting notebook to script and executing...[/]")
                    import nbformat
                    from nbconvert.preprocessors import ExecutePreprocessor
                    
                    with open(script_path) as f:
                        nb = nbformat.read(f, as_version=4)
                    
                    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
                    ep.preprocess(nb, {'metadata': {'path': '.'}})
                    
                    self.console.print("[green]Notebook execution completed[/]")
            else:
                # Use selected fine-tuning method
                self.console.print(f"[blue]Using {finetuning_method.upper()} method for fine-tuning[/]")
                
                # This is where you would call the appropriate fine-tuning function
                # For now, just report that it's not yet implemented
                self.console.print("[yellow]Fine-tuning execution not yet implemented[/]")
                self.console.print(f"[green]Training configuration saved to database[/]")
            
        except Exception as e:
            self.console.print(f"[bold red]Error during fine-tuning: {str(e)}[/]")
            import traceback
            traceback.print_exc()

    
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
                if dataset_name not in [choice[1] for choice in dataset_choices]:
                    dataset_choices.append((f"Structured: {dataset_name}", f"structured_{dataset_name}"))
            
            for dataset_name in poc_datasets:
                if dataset_name not in [choice[1] for choice in dataset_choices]:
                    dataset_choices.append((f"POC: {dataset_name}", f"poc_{dataset_name}"))
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load custom datasets: {e}[/]")
            
        return dataset_choices