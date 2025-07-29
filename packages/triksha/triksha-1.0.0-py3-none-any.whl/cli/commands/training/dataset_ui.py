"""UI components for dataset management"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import inquirer
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class DatasetUI:
    """UI class for dataset management operations"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize dataset UI"""
        self.console = console or Console()
    
    def get_huggingface_dataset_info(self) -> Optional[Dict[str, str]]:
        """Get HuggingFace dataset information from user"""
        try:
            questions = [
                inquirer.Text(
                    'dataset_id',
                    message="Enter the HuggingFace dataset ID (e.g. 'databricks/databricks-dolly-15k')"
                ),
                inquirer.Text(
                    'subset',
                    message="Enter dataset subset (optional, press Enter to skip)"
                ),
                inquirer.Confirm(
                    'confirm',
                    message="Proceed with download?",
                    default=True
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or not answers['confirm']:
                return None
                
            return {
                'dataset_id': answers['dataset_id'],
                'subset': answers['subset'] if answers['subset'] else None
            }
            
        except Exception as e:
            self.console.print(f"[red]Error getting dataset info: {str(e)}[/]")
            return None
    
    def get_adversarial_format_options(self) -> Optional[Dict[str, Any]]:
        """Get adversarial formatting options from user"""
        try:
            # Show format types
            format_types = [
                ("Jailbreak Detection", "jailbreak"),
                ("Safety Assessment", "safety"),
                ("Back", "back")
            ]
            
            questions = [
                inquirer.List(
                    'format_type',
                    message="Select the adversarial format type",
                    choices=[choice[0] for choice in format_types]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['format_type'] == "Back":
                return None
                
            format_type = next(ft[1] for ft in format_types if ft[0] == answers['format_type'])
            
            # Get additional options based on format type
            if format_type == "jailbreak":
                additional_questions = [
                    inquirer.Text(
                        'prompt_prefix',
                        message="Enter custom prompt prefix (optional)",
                        default="You are a secure AI assistant. Respond appropriately to: "
                    ),
                    inquirer.Text(
                        'response_prefix',
                        message="Enter custom response prefix (optional)",
                        default="I must decline to help with: "
                    )
                ]
                
                additional_answers = inquirer.prompt(additional_questions)
                if additional_answers:
                    return {
                        'format_type': format_type,
                        'prompt_prefix': additional_answers['prompt_prefix'],
                        'response_prefix': additional_answers['response_prefix']
                    }
            
            return {'format_type': format_type}
            
        except Exception as e:
            self.console.print(f"[red]Error getting format options: {str(e)}[/]")
            return None
    
    def select_dataset(self, datasets: List[Dict[str, Any]], purpose: str = "view") -> Optional[str]:
        """Select a dataset from a list"""
        if not datasets:
            self.console.print("[yellow]No datasets available[/]")
            return None
            
        try:
            # Create choices list
            choices = [(f"{d['name']} ({d['samples']} samples, {d['source']})", d['id']) for d in datasets]
            choices.append(("Back", "back"))
            
            questions = [
                inquirer.List(
                    'dataset_id',
                    message=f"Select a dataset to {purpose}",
                    choices=[choice[0] for choice in choices]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['dataset_id'] == "Back":
                return None
                
            return next(choice[1] for choice in choices if choice[0] == answers['dataset_id'])
            
        except Exception as e:
            self.console.print(f"[red]Error selecting dataset: {str(e)}[/]")
            return None
    
    def get_export_options(self) -> Optional[Dict[str, Any]]:
        """Get export options from user"""
        try:
            questions = [
                inquirer.List(
                    'format',
                    message="Select export format",
                    choices=[
                        ("JSON (recommended for preserving data structure)", "json"),
                        ("CSV (flat structure, good for spreadsheets)", "csv"),
                        ("Back", "back")
                    ]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['format'] == "back":
                return None
            
            # Get output path
            path_question = [
                inquirer.Text(
                    'output_path',
                    message="Enter output path (optional, press Enter for default location)"
                )
            ]
            
            path_answer = inquirer.prompt(path_question)
            
            return {
                'format': answers['format'],
                'output_path': path_answer['output_path'] if path_answer and path_answer['output_path'] else None
            }
            
        except Exception as e:
            self.console.print(f"[red]Error getting export options: {str(e)}[/]")
            return None
    
    def confirm_deletion(self, dataset_name: str) -> Tuple[bool, bool]:
        """Confirm dataset deletion and whether to delete files"""
        try:
            questions = [
                inquirer.Confirm(
                    'confirm',
                    message=f"Are you sure you want to delete dataset '{dataset_name}'?",
                    default=False
                ),
                inquirer.Confirm(
                    'delete_files',
                    message="Also delete associated files?",
                    default=True
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return False, False
                
            return answers['confirm'], answers['delete_files']
            
        except Exception as e:
            self.console.print(f"[red]Error confirming deletion: {str(e)}[/]")
            return False, False
    
    def display_dataset_preview(self, dataset: Dict[str, Any], samples: List[Dict[str, Any]]):
        """Display a preview of dataset samples"""
        try:
            # Display dataset info
            info_table = Table(title="Dataset Information", box=box.ROUNDED)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="green")
            
            for key, value in dataset.items():
                if key not in ['data', 'samples'] and value is not None:
                    info_table.add_row(key.capitalize(), str(value))
            
            self.console.print(info_table)
            
            # Display samples
            self.console.print("\n[bold]Sample Data:[/]")
            for i, sample in enumerate(samples, 1):
                self.console.print(f"\n[cyan]Sample {i}:[/]")
                
                if isinstance(sample, dict):
                    for key, value in sample.items():
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 100:
                            value = f"{value[:97]}..."
                        self.console.print(f"[blue]{key}:[/] {value}")
                else:
                    self.console.print(str(sample))
                    
        except Exception as e:
            self.console.print(f"[red]Error displaying preview: {str(e)}[/]")
    
    def show_operation_result(self, success: bool, operation: str, details: Optional[str] = None):
        """Show the result of an operation"""
        if success:
            self.console.print(f"[green]✓ {operation} successful[/]")
            if details:
                self.console.print(f"[dim]{details}[/]")
        else:
            self.console.print(f"[red]✗ {operation} failed[/]")
            if details:
                self.console.print(f"[red]{details}[/]") 