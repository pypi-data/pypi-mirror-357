"""Training commands for the Dravik CLI"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import inquirer

# Training-related imports with error handling
try:
    from ...training.train_adversarial_model import main as train_adversarial_model
    from ...training.kubernetes_runner import KubernetesTrainingManager
    from ...training.finetuner import TrufflehogFinetuner
except ImportError:
    # Provide fallback implementations
    def train_adversarial_model():
        return {"status": "error", "message": "Training module not available"}
    
    class KubernetesTrainingManager:
        def __init__(self, config=None):
            self.config = config or {}
        
        def start_training(self, params):
            return False
    
    class TrufflehogFinetuner:
        def __init__(self):
            pass
        
        def fine_tune(self, params):
            return False

try:
    from ...utils.config_loader import load_training_config
except ImportError:
    def load_training_config():
        return {}

try:
    from ...db_handler import DravikDB
except ImportError:
    class DravikDB:
        def list_datasets(self, dataset_type):
            return []
        
        def get_formatted_dataset(self, name):
            return None

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import traceback
import glob
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
import uuid
import subprocess
from concurrent.futures import ThreadPoolExecutor

try:
    from ...training.finetuner import Finetuner, FinetuningConfig
except ImportError:
    # Provide fallback implementations
    class Finetuner:
        def __init__(self, config):
            self.config = config
        
        def run_finetuning(self):
            return {"status": "error", "output_dir": "not_available"}
    
    class FinetuningConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

class TrainingCommands:
    """Command class for training operations"""
    
    def __init__(self, db, config):
        """
        Initialize training commands
        
        Args:
            db: Database connection
            config: Application configuration
        """
        self.db = db
        self.config = config
        self.console = Console()
        self.dravik_db = DravikDB()  # Direct instance for database operations
        
        # Setup directories
        self.training_dir = Path(config.get('training_dir', 'training_outputs'))
        self.training_dir.mkdir(exist_ok=True, parents=True)
        self.configs_dir = Path(config.get('configs_dir', 'training_configs'))
        self.configs_dir.mkdir(exist_ok=True, parents=True)
        
    def train_model(self, dataset=None):
        """Guide users through setting up and running model fine-tuning
        
        Args:
            dataset: Optional dataset object from select_dataset_for_training
        """
        self.console.print(Panel.fit(
            "[bold]Model Fine-tuning[/]\n\n"
            "This wizard will guide you through the process of fine-tuning a language model.\n"
            "You'll select a model, dataset, and training configuration.",
            title="[green]MODEL FINE-TUNING WIZARD[/]",
            border_style="green"
        ))
        
        try:
            # Check HuggingFace authentication before proceeding
            hf_authenticated = self._check_huggingface_auth()
            if not hf_authenticated and not self._prompt_for_huggingface_token():
                self.console.print("[yellow]Training cancelled due to missing authentication.[/]")
                return
                
            # Use provided dataset or select one if not provided
            if dataset:
                self.console.print(f"[green]Using selected dataset: {dataset.get('name', 'Unknown')}[/]")
                dataset_name = dataset.get('name', 'Unknown')
                dataset_id = dataset.get('id')
                dataset_type = dataset.get('type', 'structured')
            else:
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
                
                # Let user select a specific dataset
                dataset_options = []
                
                try:
                    if dataset_type == "raw":
                        available_datasets = self.dravik_db.list_raw_datasets()
                    elif dataset_type == "structured":
                        available_datasets = self.dravik_db.list_structured_datasets()
                    elif dataset_type == "formatted":
                        available_datasets = self.dravik_db.list_formatted_datasets()
                    elif dataset_type == "poc":
                        available_datasets = self.dravik_db.list_poc_datasets()
                    else:
                        available_datasets = []
                    
                    dataset_options = [(name, name) for name in available_datasets]
                except Exception as e:
                    self.console.print(f"[red]Error listing datasets: {str(e)}[/]")
                    dataset_options = []
                
                if not dataset_options:
                    self.console.print("[yellow]No datasets found for the selected type.[/]")
                    return
                
                # Let user select a specific dataset
                dataset_question = [
                    inquirer.List(
                        'dataset_name',
                        message=f"Select a {dataset_type} dataset",
                        choices=dataset_options + [("Cancel", None)]
                    )
                ]
                
                dataset_answer = inquirer.prompt(dataset_question)
                if not dataset_answer or not dataset_answer['dataset_name']:
                    self.console.print("[yellow]Dataset selection cancelled.[/]")
                    return
                
                dataset_name = dataset_answer['dataset_name']
                dataset_id = dataset_name  # Use name as ID
            
            # Now select model
            model_choices = [
                ("Gemma", "google/gemma-7b"),
                ("Phi", "microsoft/phi-2"),
                ("Llama 2", "meta-llama/Llama-2-7b-hf"),
                ("Mistral", "mistralai/Mistral-7B-v0.1"),
                ("Mixtral", "mistralai/Mixtral-8x7B-v0.1"),
                ("T5-base", "t5-base"),
                ("T5-large", "t5-large"),
                ("FLAN-T5", "google/flan-t5-xl"),
                ("GPT-2", "gpt2"),
                ("Other...", "custom")
            ]
            
            model_question = [
                inquirer.List(
                    'model_name',
                    message="Select a base model for fine-tuning",
                    choices=model_choices
                )
            ]
            
            model_answer = inquirer.prompt(model_question)
            if not model_answer:
                return
                
            model_name = model_answer['model_name']
            
            # If custom model, ask for name
            if model_name == "custom":
                custom_model_question = [
                    inquirer.Text(
                        'custom_model',
                        message="Enter Hugging Face model name (e.g. 'EleutherAI/pythia-6.9b')",
                        validate=lambda _, x: len(x.strip()) > 0
                    )
                ]
                
                custom_model_answer = inquirer.prompt(custom_model_question)
                if not custom_model_answer:
                    return
                    
                model_name = custom_model_answer['custom_model']
            
            # Select fine-tuning approach
            approach_choices = [
                ("LoRA (Low-Rank Adaptation - efficient fine-tuning)", "lora"),
                ("QLoRA (Quantized LoRA - more memory efficient)", "qlora"),
                ("Full fine-tuning (entire model, resource intensive)", "full"),
                ("Parameter-Efficient Fine-Tuning (PEFT)", "peft")
            ]
            
            approach_question = [
                inquirer.List(
                    'approach',
                    message="Select a fine-tuning approach",
                    choices=approach_choices
                )
            ]
            
            approach_answer = inquirer.prompt(approach_question)
            if not approach_answer:
                return
                
            approach = approach_answer['approach']
            
            # Display selected options and confirm
            self.console.print(f"[green]Selected dataset: {dataset_name}[/]")
            self.console.print(f"[green]Selected model: {model_name}[/]")
            self.console.print(f"[green]Selected approach: {approach}[/]")
            
            # Ask for confirmation
            confirm = inquirer.confirm("Proceed with fine-tuning?", default=True)
            if not confirm:
                self.console.print("[yellow]Fine-tuning cancelled.[/]")
                return
                
            # Start fine-tuning
            output_dir = self.training_dir / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create config
            fine_tuning_config = FinetuningConfig(
                model_name=model_name,
                output_dir=str(output_dir),
                training_type=approach,
                dataset_type=dataset_type
            )
            
            # Execute training
            self.console.print("[bold green]Starting fine-tuning process...[/]")
            
            try:
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
                if "gated repo" in str(e).lower() or "401 client error" in str(e).lower():
                    self.console.print("[bold red]Error: You're trying to access a gated model repository.[/]")
                    self.console.print("[yellow]This model requires authentication with Hugging Face.[/]")
                    
                    # Offer to retry with auth
                    if self._prompt_for_huggingface_token(force=True):
                        self.console.print("[green]Authentication successful! Please try training again.[/]")
                    else:
                        self.console.print("[yellow]Without proper authentication, you cannot access this model.[/]")
                else:
                    # Re-raise other exceptions
                    raise
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Training setup cancelled by user.[/]")
        except Exception as e:
            self.console.print(f"[bold red]Error during training setup: {str(e)}[/]")
            if self.config.get('verbose', False):
                self.console.print(traceback.format_exc())
    
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
                "metrics": metrics,
                "status": "completed",
                "config": {
                    "learning_rate": metrics.get('learning_rate', 2e-5),
                    "batch_size": metrics.get('batch_size', 8),
                    "epochs": metrics.get('epochs', 3),
                    "model_name": model_name,
                }
            }
            
            # Use DravikDB to save the result if it has the method
            if hasattr(self.dravik_db, 'save_training_result'):
                self.dravik_db.save_training_result(training_info)
            
            # Also save to a JSON file
            info_file = os.path.join(output_dir, "training_info.json")
            with open(info_file, "w") as f:
                json.dump(training_info, f, indent=2)

            # Remove any active or error files
            active_file = os.path.join(output_dir, "training_active.json")
            if os.path.exists(active_file):
                os.remove(active_file)
                
            error_file = os.path.join(output_dir, "training_error.json")
            if os.path.exists(error_file):
                os.remove(error_file)
                
            self.console.print("[green]Training result saved.[/]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save training result: {e}[/]")
    
    def _check_huggingface_auth(self) -> bool:
        """Check if HuggingFace authentication is set up"""
        try:
            # Try to import huggingface_hub
            from huggingface_hub import HfFolder
            
            # Check if token exists
            token = HfFolder.get_token()
            if token is not None:
                self.console.print("[green]✓ HuggingFace Hub authentication is set up[/]")
                return True
            
            # Check environment variables
            for env_var in ["HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_TOKEN"]:
                if env_var in os.environ and os.environ[env_var]:
                    self.console.print(f"[green]✓ HuggingFace token found in {env_var}[/]")
                    
                    # Login with the token
                    try:
                        from huggingface_hub import login
                        login(token=os.environ[env_var])
                        self.console.print("[green]✓ Successfully authenticated with Hugging Face Hub[/]")
                        return True
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Authentication failed with token from {env_var}: {e}[/]")
            
            self.console.print("[yellow]⚠ No HuggingFace authentication found[/]")
            return False
        except ImportError:
            self.console.print("[yellow]Warning: huggingface_hub package not installed[/]")
            return False
        except Exception as e:
            self.console.print(f"[yellow]Warning: Error checking HuggingFace authentication: {e}[/]")
            return False
    
    def _prompt_for_huggingface_token(self, force: bool = False) -> bool:
        """Prompt user for HuggingFace token and set environment variable"""
        if not force and not inquirer.confirm("Would you like to set up HuggingFace authentication now?", default=True):
            return False
            
        self.console.print("\n[bold cyan]HuggingFace Authentication[/]")
        self.console.print("[cyan]Some models require authentication to access.[/]")
        self.console.print("[cyan]You can create a token at: https://huggingface.co/settings/tokens[/]")
        
        token = get_pasted_input(
            message="Enter your HuggingFace token",
            default=""
        )
        
        if not token:
            self.console.print("[yellow]No token provided. Some models may not be accessible.[/]")
            return False
            
        try:
            # Set environment variable
            os.environ["HF_TOKEN"] = token
            
            # Try logging in
            from huggingface_hub import login
            login(token=token)
            
            self.console.print("[green]✓ Successfully authenticated with Hugging Face Hub[/]")
            
            # Ask if user wants to save token to .env file
            if inquirer.confirm("Save token to environment for future use?", default=True):
                env_file = Path.home() / "dravik" / ".env"
                
                # Create or update .env file
                env_content = ""
                if env_file.exists():
                    with open(env_file, 'r') as f:
                        env_content = f.read()
                
                # Check if HF_TOKEN already exists in file
                if "HF_TOKEN=" in env_content:
                    # Replace existing token
                    env_lines = env_content.splitlines()
                    for i, line in enumerate(env_lines):
                        if line.startswith("HF_TOKEN="):
                            env_lines[i] = f"HF_TOKEN={token}"
                            break
                    env_content = "\n".join(env_lines)
                else:
                    # Add new token
                    if env_content and not env_content.endswith("\n"):
                        env_content += "\n"
                    env_content += f"HF_TOKEN={token}\n"
                
                # Save to .env file
                os.makedirs(env_file.parent, exist_ok=True)
                with open(env_file, 'w') as f:
                    f.write(env_content)
                
                self.console.print(f"[green]✓ Token saved to {env_file}[/]")
            
            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up authentication: {e}[/]")
            return False
            
    def view_training_history(self):
        """View training history with detailed information"""
        self.console.print(Panel.fit(
            "[bold]Training History[/]\n\n"
            "Review past training jobs, their configurations, and results.",
            title="[green]TRAINING HISTORY[/]",
            border_style="green"
        ))
        
        # Load training history
        training_jobs = self._load_training_history()
        
        if not training_jobs:
            self.console.print("[yellow]No training history found. Run a training job first.[/]")
            return
        
        # Find active/ongoing training jobs
        active_jobs = [job for job in training_jobs if job.get('status') == 'in_progress']
        completed_jobs = [job for job in training_jobs if job.get('status') == 'completed']
        failed_jobs = [job for job in training_jobs if job.get('status') == 'failed']
        
        # Display a summary table
        table = Table(title="Training Jobs")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Date", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Dataset", style="magenta")
        table.add_column("Approach", style="blue")
        table.add_column("Status", style="bright_white")
        
        # Display active jobs at the top with a special indicator
        job_id = 1
        
        if active_jobs:
            self.console.print("[bold yellow]⚡ Active Training Jobs[/]")
            for job in active_jobs:
                # Get job details
                date = self._format_date(job.get("created_at", ""))
                model = self._format_model_name(job.get("model_name", "Unknown"))
                dataset = job.get("dataset_type", "Unknown")
                approach = job.get("approach", "Unknown").upper()
                status = "[yellow]In Progress[/]"
                progress = job.get("progress", {})
                
                # Add progress info if available
                if progress:
                    current_epoch = progress.get("current_epoch", 0)
                    total_epochs = progress.get("total_epochs", 0)
                    if total_epochs > 0:
                        status = f"[yellow]Running - Epoch {current_epoch}/{total_epochs}[/]"
                
                table.add_row(str(job_id), date, model, dataset, approach, status)
                job_id += 1
        
        # Display completed jobs
        if completed_jobs:
            if active_jobs:
                self.console.print("\n[green]Completed Training Jobs[/]")
            
            for job in completed_jobs:
                date = self._format_date(job.get("created_at", ""))
                model = self._format_model_name(job.get("model_name", "Unknown"))
                dataset = job.get("dataset_type", "Unknown")
                approach = job.get("approach", "Unknown").upper()
                status = "[green]Completed[/]"
                
                table.add_row(str(job_id), date, model, dataset, approach, status)
                job_id += 1
        
        # Display failed jobs
        if failed_jobs:
            for job in failed_jobs:
                date = self._format_date(job.get("created_at", ""))
                model = self._format_model_name(job.get("model_name", "Unknown"))
                dataset = job.get("dataset_type", "Unknown")
                approach = job.get("approach", "Unknown").upper()
                status = "[red]Failed[/]"
                
                table.add_row(str(job_id), date, model, dataset, approach, status)
                job_id += 1
        
        # Display the table
        self.console.print(table)
        
        # Ask if user wants to view details of a specific job
        if inquirer.confirm("View details of a specific training job?", default=False):
            job_id = inquirer.text(
                message="Enter job ID to view",
                validate=lambda x: x.isdigit() and 1 <= int(x) <= len(training_jobs)
            )
            
            try:
                job_index = int(job_id) - 1
                self._display_job_details(training_jobs[job_index])
            except (ValueError, IndexError):
                self.console.print("[red]Invalid job ID.[/]")
    
    def _format_date(self, date_string: str) -> str:
        """Format a date string for display"""
        if not date_string:
            return "Unknown"
        
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_string
    
    def _format_model_name(self, model_name: str) -> str:
        """Format model name for display, shortening very long names"""
        if '/' in model_name:
            # For HuggingFace style names, just show the model part
            parts = model_name.split('/')
            return f"{parts[0].split('-')[0]}/{parts[1].split('-')[0]}"
        
        # Truncate very long names
        if len(model_name) > 20:
            return model_name[:18] + "..."
            
        return model_name
    
    def _display_job_details(self, job: Dict[str, Any]):
        """Display detailed information about a training job"""
        self.console.print(Panel.fit(
            f"[bold]Training Job Details[/]",
            title="[green]JOB DETAILS[/]",
            border_style="green"
        ))
        
        # Basic information
        self.console.print(f"[bold]Model:[/] {job.get('model_name', 'Unknown')}")
        self.console.print(f"[bold]Dataset:[/] {job.get('dataset_type', 'Unknown')}")
        self.console.print(f"[bold]Approach:[/] {job.get('approach', 'Unknown').upper()}")
        self.console.print(f"[bold]Date:[/] {self._format_date(job.get('created_at', ''))}")
        self.console.print(f"[bold]Status:[/] {job.get('status', 'Unknown').replace('_', ' ').title()}")
        
        # Show output directory if available
        if job.get('output_dir'):
            output_dir = job.get('output_dir')
            self.console.print(f"[bold]Output Directory:[/] {output_dir}")
            
            # Check if directory exists
            if os.path.exists(output_dir):
                # Check if model files exist
                model_files = list(Path(output_dir).glob("*.bin"))
                if model_files:
                    self.console.print(f"[green]✓ Model files found: {len(model_files)} checkpoint files[/]")
            else:
                self.console.print(f"[yellow]⚠ Output directory not found[/]")
        
        # Show progress for in-progress jobs
        if job.get('status') == 'in_progress' and job.get('progress'):
            progress = job.get('progress', {})
            self.console.print("\n[bold cyan]Current Progress:[/]")
            self.console.print(f"Epoch: {progress.get('current_epoch', 0)}/{progress.get('total_epochs', 0)}")
            self.console.print(f"Steps: {progress.get('current_step', 0)}/{progress.get('total_steps', 0)}")
            self.console.print(f"Current Loss: {progress.get('current_loss', 'N/A')}")
            self.console.print(f"Learning Rate: {progress.get('learning_rate', 'N/A')}")
            self.console.print(f"Elapsed Time: {progress.get('elapsed_time', 'N/A')}")
            
            # Show a visual progress bar if we have step information
            if progress.get('current_step') and progress.get('total_steps'):
                current = progress.get('current_step', 0)
                total = progress.get('total_steps', 100)
                percent = min(100, max(0, int(current / total * 100))) if total > 0 else 0
                
                # Create a progress bar
                bar = "█" * (percent // 5) + "░" * ((100 - percent) // 5)
                self.console.print(f"\n{bar} {percent}%")
                
        # Display metrics if available
        if job.get('metrics'):
            self.console.print("\n[bold]Training Metrics:[/]")
            metrics = job.get('metrics', {})
            
            # Create a metrics table
            metrics_table = Table(show_header=True, header_style="bold")
            metrics_table.add_column("Metric")
            metrics_table.add_column("Value")
            
            # Training metrics
            train_metrics = metrics.get('train_metrics', {})
            for key, value in train_metrics.items():
                if isinstance(value, (int, float)):
                    metrics_table.add_row(f"Train {key}", f"{value:.5f}")
            
            # Evaluation metrics
            eval_metrics = metrics.get('eval_metrics', {})
            for key, value in eval_metrics.items():
                if isinstance(value, (int, float)):
                    metrics_table.add_row(f"Eval {key}", f"{value:.5f}")
            
            self.console.print(metrics_table)
        
        # Display configuration if available
        if job.get('config'):
            self.console.print("\n[bold]Training Configuration:[/]")
            config = job.get('config', {})
            
            # Format as JSON for display
            config_json = json.dumps(config, indent=2)
            self.console.print(Syntax(config_json, "json", theme="monokai", word_wrap=True))
        
        # If job failed, show error information
        if job.get('status') == 'failed' and job.get('error'):
            self.console.print("\n[bold red]Error Information:[/]")
            self.console.print(f"[red]{job.get('error')}[/]")
            if job.get('traceback'):
                self.console.print(job.get('traceback'))
        
        # Offer options to continue with this model
        if job.get('status') == 'completed':
            self.console.print("\n[bold green]Options:[/]")
            
            options = [
                ('Back to training history', 'back'),
                ('Export model info', 'export'),
            ]
            
            # Add option to load model for inference if output directory exists
            if job.get('output_dir') and os.path.exists(job.get('output_dir')):
                options.insert(0, ('Load model for inference', 'inference'))
            
            # Add option to continue training if output directory exists
            if job.get('output_dir') and os.path.exists(job.get('output_dir')):
                options.insert(0, ('Continue training this model', 'continue'))
            
            option_question = [
                inquirer.List(
                    'option',
                    message="What would you like to do?",
                    choices=options
                )
            ]
            
            option_answer = inquirer.prompt(option_question)
            if not option_answer:
                return
                
            option = option_answer['option']
            
            if option == 'inference':
                self.console.print("[yellow]Model inference functionality will be available in a future update.[/]")
            elif option == 'continue':
                self.console.print("[yellow]Continue training functionality will be available in a future update.[/]")
            elif option == 'export':
                self._export_model_info(job)
    
    def _export_model_info(self, job: Dict[str, Any]):
        """Export model info to a file"""
        try:
            # Create export directory if it doesn't exist
            export_dir = Path.home() / "dravik" / "exports" / "models"
            export_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate filename
            model_name = job.get('model_name', 'unknown').split('/')[-1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_name}_{timestamp}.json"
            filepath = export_dir / filename
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(job, f, indent=2)
                
            self.console.print(f"[green]Model info exported to {filepath}[/]")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting model info: {e}[/]")
    
    def _load_training_history(self) -> List[Dict[str, Any]]:
        """Load training history from database or files"""
        training_jobs = []
        
        # Try to load from database if available
        try:
            if hasattr(self.dravik_db, 'get_training_history'):
                db_jobs = self.dravik_db.get_training_history()
                if db_jobs:
                    training_jobs.extend(db_jobs)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load training history from database: {e}[/]")
        
        # Try to load from training info files
        try:
            # Look for all training directories
            pattern = str(self.training_dir / "training_*")
            training_dirs = glob.glob(pattern)
            
            for training_dir in training_dirs:
                info_file = os.path.join(training_dir, "training_info.json")
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r') as f:
                            job_info = json.load(f)
                            
                            # Set default status if not present
                            if 'status' not in job_info:
                                job_info['status'] = 'completed'
                                
                            # Add to list if not already in database results
                            if not any(db_job.get('output_dir') == training_dir for db_job in training_jobs):
                                job_info['output_dir'] = training_dir
                                training_jobs.append(job_info)
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not load training info from {info_file}: {e}[/]")
                
                # Look for active job files
                active_file = os.path.join(training_dir, "training_active.json")
                if os.path.exists(active_file):
                    try:
                        with open(active_file, 'r') as f:
                            active_job = json.load(f)
                            active_job['status'] = 'in_progress'
                            active_job['output_dir'] = training_dir
                            
                            # Add to list if not already present
                            existing = [job for job in training_jobs if job.get('output_dir') == training_dir]
                            if existing:
                                # Update existing entry
                                existing[0].update(active_job)
                            else:
                                training_jobs.append(active_job)
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not load active job from {active_file}: {e}[/]")
                
                # Look for error files
                error_file = os.path.join(training_dir, "training_error.json")
                if os.path.exists(error_file):
                    try:
                        with open(error_file, 'r') as f:
                            error_job = json.load(f)
                            error_job['status'] = 'failed'
                            error_job['output_dir'] = training_dir
                            
                            # Add to list if not already present
                            existing = [job for job in training_jobs if job.get('output_dir') == training_dir]
                            if existing:
                                # Update existing entry
                                existing[0].update(error_job)
                            else:
                                training_jobs.append(error_job)
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not load error job from {error_file}: {e}[/]")
        
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not search for training directories: {e}[/]")
        
        # Sort by creation date, newest first
        training_jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return training_jobs
    
    def _save_training_progress(self, output_dir: str, progress: Dict[str, Any]):
        """Save training progress for active jobs"""
        try:
            # Create active file with progress information
            active_file = os.path.join(output_dir, "training_active.json")
            
            # Read existing data if available
            training_info = {}
            if os.path.exists(active_file):
                with open(active_file, 'r') as f:
                    training_info = json.load(f)
            
            # Update with new progress
            training_info.update({
                "progress": progress,
                "updated_at": datetime.now().isoformat()
            })
            
            # Save to file
            with open(active_file, 'w') as f:
                json.dump(training_info, f, indent=2)
                
        except Exception as e:
            print(f"Error saving training progress: {e}")
    
    def _save_training_error(self, output_dir: str, error: str, traceback_str: str = None):
        """Save error information for failed jobs"""
        try:
            # Create error file
            error_file = os.path.join(output_dir, "training_error.json")
            
            # Read existing data if available
            training_info = {}
            if os.path.exists(error_file):
                with open(error_file, 'r') as f:
                    training_info = json.load(f)
            
            # Update with error information
            training_info.update({
                "error": error,
                "traceback": traceback_str,
                "status": "failed",
                "failed_at": datetime.now().isoformat()
            })
            
            # Save to file
            with open(error_file, 'w') as f:
                json.dump(training_info, f, indent=2)
                
            # Remove active file if it exists
            active_file = os.path.join(output_dir, "training_active.json")
            if os.path.exists(active_file):
                os.remove(active_file)
                
        except Exception as e:
            print(f"Error saving training error: {e}")

    def manage_training_configs(self):
        """Manage training configurations with create/edit/delete options"""
        self.console.print(Panel.fit(
            "[bold]Training Configurations[/]\n\n"
            "Create, edit, and manage training configurations for fine-tuning models.",
            title="[green]TRAINING CONFIGURATIONS[/]",
            border_style="green"
        ))
        
        # Main configuration management menu
        while True:
            options = [
                ("View existing configurations", "view"),
                ("Create new configuration", "create"),
                ("Edit existing configuration", "edit"),
                ("Delete configuration", "delete"),
                ("Back to training menu", "back")
            ]
            
            action = inquirer.prompt([
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=options
                )
            ])
            
            if not action or action['action'] == 'back':
                break
                
            if action['action'] == 'view':
                self._view_training_configs()
            elif action['action'] == 'create':
                self.console.print("[yellow]Configuration creation is coming soon![/]")
            elif action['action'] == 'edit':
                self.console.print("[yellow]Configuration editing is coming soon![/]")
            elif action['action'] == 'delete':
                self.console.print("[yellow]Configuration deletion is coming soon![/]")
    
    def _view_training_configs(self):
        """View existing training configurations"""
        self.console.print("[bold]Training Configurations[/]")
        self.console.print("[yellow]This feature is coming soon![/]")
