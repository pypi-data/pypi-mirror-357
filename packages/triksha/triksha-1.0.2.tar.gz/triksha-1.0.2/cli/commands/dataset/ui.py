"""UI components for dataset commands"""
import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import the new UI helpers
from utils.ui_helpers import get_pasted_input, get_dataset_name

class DatasetUI:
    """UI elements for dataset operations"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize dataset UI"""
        self.console = console or Console()
        # Use a simple theme for inquirer
        self.theme = inquirer.themes.Default()
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get dataset information from the user"""
        
        # Initial welcome panel
        self.console.print("\n[bold green]Dataset Download[/]\n")
        self.console.print("Download datasets from HuggingFace to use for training and benchmarking.\n")
        
        # Ask for the dataset name
        dataset_name_question = [
            inquirer.Text(
                'dataset_name',
                message="Enter HuggingFace dataset name (e.g. 'datasets/alpaca')",
                validate=lambda _, x: len(x.strip()) > 0
            )
        ]
        
        dataset_name_answer = inquirer.prompt(dataset_name_question, theme=self.theme)
        if not dataset_name_answer:
            return {}
        
        # Ask if the user wants to use cached dataset
        cache_question = [
            inquirer.Confirm(
                'use_cache',
                message="Use cached dataset if available?",
                default=True
            )
        ]
        
        cache_answer = inquirer.prompt(cache_question, theme=self.theme)
        if not cache_answer:
            return {}
            
        # Additional configuration options
        config_question = [
            inquirer.Confirm(
                'configure_advanced',
                message="Configure advanced options?",
                default=False
            )
        ]
        
        config_answer = inquirer.prompt(config_question, theme=self.theme)
        if not config_answer:
            return {}
            
        # Advanced configuration if requested
        advanced_options = {}
        if config_answer.get('configure_advanced', False):
            # Ask for custom destination path
            path_question = [
                inquirer.Confirm(
                    'custom_path',
                    message="Use custom destination path?",
                    default=False
                )
            ]
            
            path_answer = inquirer.prompt(path_question, theme=self.theme)
            if not path_answer:
                return {}
                
            if path_answer.get('custom_path', False):
                custom_path_question = [
                    inquirer.Text(
                        'destination_path',
                        message="Enter destination path",
                        default=str(Path.home() / "dravik" / "data" / "raw")
                    )
                ]
                
                custom_path_answer = inquirer.prompt(custom_path_question, theme=self.theme)
                if not custom_path_answer:
                    return {}
                    
                advanced_options['destination_path'] = custom_path_answer['destination_path']
        
        # Return the dataset information
        result = {
            "dataset_name": dataset_name_answer['dataset_name'],
            "use_cache": cache_answer['use_cache']
        }
        
        # Add any advanced options
        result.update(advanced_options)
        
        return result
    
    def get_export_info(self, available_datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get export preferences from the user
        
        Args:
            available_datasets: List of available datasets with their types
            
        Returns:
            Dictionary with export preferences or None if canceled
        """
        if not available_datasets:
            self.console.print("[yellow]No datasets available for export.[/]")
            return None
            
        self.console.print("[bold]Export Dataset[/]")
        self.console.print("[dim]Select a dataset to export and choose the export format.[/]")
        
        # Create choices list with dataset name and type
        choices = [(f"{ds['name']} ({ds['type']})", ds) for ds in available_datasets]
        
        # Let user select which dataset to export
        dataset_question = inquirer.List(
            'dataset',
            message="Select dataset to export",
            choices=choices
        )
        
        # Let user choose the export format
        format_question = inquirer.List(
            'format',
            message="Select export format",
            choices=[
                ('JSON (recommended for complex data)', 'json'),
                ('CSV (best for tabular data)', 'csv')
            ]
        )
        
        # Let user choose the export location
        location_options = [
            (f"Default location ({Path.home() / 'dravik' / 'exports'})", None),
            ("Custom location", "custom")
        ]
        
        location_question = inquirer.List(
            'location',
            message="Select export location",
            choices=location_options
        )
        
        # Get user answers
        answers = inquirer.prompt([dataset_question, format_question, location_question])
        if not answers:
            return None
            
        # If user selected custom location, ask for the path
        output_path = None
        if answers['location'] == "custom":
            path_input = get_pasted_input(
                message="Enter export directory path",
                default=str(Path.home() / "dravik" / "exports")
            )
            output_path = path_input if path_input else str(Path.home() / "dravik" / "exports")
        
        # Selected dataset
        selected_dataset = answers['dataset']
        
        return {
            'dataset_name': selected_dataset['name'],
            'dataset_type': selected_dataset['type'],
            'format': answers['format'],
            'output_path': output_path
        }
    
    def get_delete_info(self, available_datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get deletion preferences from the user
        
        Args:
            available_datasets: List of available datasets with their types
            
        Returns:
            Dictionary with deletion preferences or None if canceled
        """
        if not available_datasets:
            self.console.print("[yellow]No datasets available for deletion.[/]")
            return None
        
        self.console.print("[bold]Delete Dataset[/]")
        self.console.print("[dim]Select a dataset to delete.[/]")
        
        # Create choices list with dataset name and type
        choices = [(f"{ds['name']} ({ds['type']})", ds) for ds in available_datasets]
        
        # Let user select which dataset to delete
        dataset_question = inquirer.List(
            'dataset',
            message="Select dataset to delete",
            choices=choices
        )
        
        # Get user answers
        answers = inquirer.prompt([dataset_question])
        if not answers:
            return None
        
        # Selected dataset
        selected_dataset = answers['dataset']
        
        return {
            'dataset_name': selected_dataset['name'],
            'dataset_type': selected_dataset['type']
        }
    
    def confirm_deletion(self, dataset_name: str, dataset_type: str) -> bool:
        """
        Confirm dataset deletion with the user
        
        Args:
            dataset_name: Name of the dataset to delete
            dataset_type: Type of dataset ('raw', 'structured', 'poc')
            
        Returns:
            True if user confirms deletion, False otherwise
        """
        # Show a warning message with dataset name and type
        self.console.print(f"[bold red]You are about to delete: {dataset_name} ({dataset_type})[/]")
        self.console.print("[red]This action cannot be undone![/]")
        
        # Ask if the user wants a simpler confirmation method
        questions = [
            inquirer.List(
                'confirm_method',
                message="How would you like to confirm deletion?",
                choices=[
                    ('Type the dataset name (safest)', 'type'),
                    ('Simple yes/no confirmation', 'yes_no')
                ]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return False
            
        confirm_method = answers['confirm_method']
        
        if confirm_method == 'type':
            # Make it clear what specifically needs to be typed
            self.console.print(f"\n[bold]Type just the dataset name (without the type) to confirm:[/]")
            self.console.print(f"[dim]Dataset name: [/][cyan]{dataset_name}[/]")
            
            typed_name = get_pasted_input(
                message=f"Type '{dataset_name}' to confirm deletion",
                default=""
            )
            
            # Check if the typed name matches
            if typed_name != dataset_name:
                self.console.print("[yellow]Names don't match. Deletion cancelled.[/]")
                return False
        else:
            # Simple yes/no confirmation
            confirmation = inquirer.confirm(
                message=f"Are you absolutely sure you want to delete {dataset_name} ({dataset_type})?",
                default=False
            )
            
            if not confirmation:
                self.console.print("[yellow]Deletion cancelled.[/]")
                return False
        
        return True
    
    def get_formatting_options(self, model_templates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get dataset formatting preferences from the user
        
        Args:
            model_templates: Available model formatting templates
            
        Returns:
            Dictionary with formatting preferences or None if canceled
        """
        self.console.print("[bold]Dataset Formatting for Adversarial Training[/]")
        self.console.print("[dim]Format your dataset of adversarial prompts for specific model architecture.[/]")
        
        # Create choices from available templates
        format_choices = [(template["name"], template) for _, template in model_templates.items()]
        
        # Let user select a formatting template
        format_question = inquirer.List(
            'format',
            message="Select a model format for your dataset",
            choices=format_choices
        )
        
        # Get user answer
        format_answer = inquirer.prompt([format_question])
        if not format_answer:
            return None
            
        selected_format = format_answer['format']
        
        # If custom format is selected, get the format details
        if selected_format["name"] == "Custom Format":
            custom_format = self._get_custom_format(selected_format)
            if not custom_format:
                return None
            selected_format = custom_format
        
        # Get information about prompt field location
        self.console.print("\n[bold cyan]Prompt Field Information[/]")
        self.console.print("[dim]Specify which field in your dataset contains the adversarial prompts.[/]")
        
        field_question = inquirer.Text(
            'prompt_field',
            message="Field containing adversarial prompts (e.g., 'input', 'instruction', 'prompt')",
            validate=lambda _, x: len(x) > 0
        )
        
        field_answer = inquirer.prompt([field_question])
        if not field_answer:
            return None
        
        # Get response generation options
        response_options = self._get_response_options()
        if not response_options:
            return None
        
        return {
            'model_format': selected_format,
            'prompt_field': field_answer['prompt_field'],
            'response_options': response_options
        }

    def _get_custom_format(self, base_format: Dict[str, Any]) -> Dict[str, Any]:
        """Get custom format details from the user"""
        self.console.print("\n[bold cyan]Custom Format Configuration[/]")
        self.console.print("[dim]Define how your dataset should be formatted.[/]")
        
        # Ask for custom format details
        format_questions = [
            inquirer.Text(
                'instruction_format',
                message="Instruction format template (with {instruction} placeholder)",
                default="{instruction}"
            ),
            inquirer.Text(
                'completion_format',
                message="Completion format template (with {completion} placeholder)",
                default="{completion}"
            ),
            inquirer.Text(
                'input_format',
                message="Input format template (with {instruction} and {input} placeholders)",
                default="{instruction}\n\n{input}"
            ),
            inquirer.Text(
                'safeguard_format',
                message="Safeguard response format for adversarial examples",
                default="I cannot assist with {problem_type} as it could {harm_description}."
            )
        ]
        
        format_answers = inquirer.prompt(format_questions)
        if not format_answers:
            return None
            
        # Update the base format with custom values
        base_format.update(format_answers)
        return base_format
    
    def _configure_adversarial_options(self) -> Optional[Dict[str, Any]]:
        """Configure adversarial training options"""
        self.console.print("\n[bold cyan]Adversarial Training Configuration[/]")
        self.console.print("[dim]Configure how the dataset should be processed for adversarial training.[/]")
        
        # Ask if adversarial training should be enabled
        enable_question = [
            inquirer.Confirm(
                'enable_adversarial',
                message="Enable adversarial training safeguards?",
                default=True
            )
        ]
        
        enable_answer = inquirer.prompt(enable_question)
        if not enable_answer:
            return None
            
        if not enable_answer['enable_adversarial']:
            return {"enable_adversarial": False}
        
        # Configure adversarial options if enabled
        options_questions = [
            inquirer.Text(
                'adversarial_ratio',
                message="Percentage of adversarial examples to include (0-100%)",
                default="30",
                validate=lambda val: val.isdigit() and 0 <= int(val) <= 100
            ),
            inquirer.Confirm(
                'detect_existing',
                message="Automatically detect existing adversarial examples?",
                default=True
            ),
            inquirer.Confirm(
                'add_safeguards',
                message="Add safeguard responses to examples?",
                default=True
            )
        ]
        
        options_answers = inquirer.prompt(options_questions)
        if not options_answers:
            return None
            
        # Add adversarial options to configuration
        return {
            "enable_adversarial": True,
            "adversarial_ratio": int(options_answers['adversarial_ratio']) / 100,
            "detect_existing": options_answers['detect_existing'],
            "add_safeguards": options_answers['add_safeguards']
        }

    def _get_response_options(self) -> Optional[Dict[str, Any]]:
        """Get options for generating safeguard responses"""
        self.console.print("\n[bold cyan]Safeguard Response Options[/]")
        self.console.print("[dim]Configure how safeguard responses will be generated for prompts.[/]")
        
        options_questions = [
            inquirer.List(
                'response_style',
                message="Select the style of safeguard responses",
                choices=[
                    ('Varied (different responses for different prompts)', 'varied'),
                    ('Consistent (same basic response pattern)', 'consistent'),
                    ('Strict (very clear refusal responses)', 'strict')
                ],
                default='varied'
            ),
            inquirer.Text(
                'custom_response',
                message="Add custom response template (optional, leave empty to use defaults)",
                default=""
            ),
            inquirer.Confirm(
                'include_prompt_context',
                message="Include prompt context in responses (makes responses more specific)?",
                default=True
            )
        ]
        
        options_answers = inquirer.prompt(options_questions)
        if not options_answers:
            return None
        
        # Build response configuration
        return {
            "style": options_answers['response_style'],
            "custom_template": options_answers['custom_response'] if options_answers['custom_response'] else None,
            "include_prompt_context": options_answers['include_prompt_context'],
        }

    def display_dataset_selection(self, datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Display a list of datasets and let the user select one
        
        Args:
            datasets: List of dataset metadata
            
        Returns:
            Selected dataset or None if canceled
        """
        if not datasets:
            self.console.print("[yellow]No datasets found.[/]")
            return None
        
        # Create a table for better visualization of datasets
        from rich.table import Table
        from rich.text import Text
        
        table = Table(title="Available Datasets", show_header=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Format", style="green")
        table.add_column("Examples", style="blue", justify="right")
        table.add_column("Created", style="magenta")
        
        # Count datasets by format
        format_count = {}
        for dataset in datasets:
            fmt = dataset.get("format", "unknown")
            format_count[fmt] = format_count.get(fmt, 0) + 1
        
        if len(format_count) > 1:
            self.console.print(f"[bold cyan]Found datasets in {len(format_count)} different formats:[/]")
            for fmt, count in format_count.items():
                self.console.print(f"  • [green]{fmt}[/]: {count} datasets")
            self.console.print()
            
        # Add datasets to the table with index
        for i, dataset in enumerate(datasets, 1):
            # Format creation date
            created_at = dataset.get("created_at", "Unknown")
            if isinstance(created_at, str) and len(created_at) > 10:
                created_at = created_at[:10]  # Just show the date
                
            # Get size info or example count
            example_count = dataset.get("example_count", "Unknown")
            if isinstance(example_count, int) and example_count > 1000:
                example_count = f"{example_count//1000}K"
            
            # Get dataset type and format
            dataset_type = dataset.get("type", "Unknown")
            format_value = dataset.get("format", "Unknown")
            
            # Format type with color
            type_text = Text()
            if dataset_type == "raw":
                type_text.append("RAW", style="bold yellow")
            elif dataset_type == "structured":
                type_text.append("STRUCTURED", style="bold green")
            elif dataset_type == "poc":
                type_text.append("POC", style="bold blue") 
            elif dataset_type == "adversarial":
                type_text.append("ADVERSARIAL", style="bold red")
            elif dataset_type == "evaluation":
                type_text.append("EVAL", style="bold magenta")
            else:
                type_text.append(dataset_type.upper(), style="white")
                
            # Format value with color
            format_text = Text()
            format_color = "white"
            if format_value == "standard":
                format_color = "green"
            elif format_value == "adversarial":
                format_color = "red"
            elif format_value == "evaluation":
                format_color = "magenta"
            elif format_value == "raw":
                format_color = "yellow"
            elif format_value == "poc":
                format_color = "blue"
                
            format_text.append(format_value, style=format_color)
            
            # Add row to the table
            table.add_row(
                str(i),
                dataset.get("name", "Unknown"),
                type_text,
                format_text,
                str(example_count),
                created_at
            )
        
        # Display the table
        self.console.print(table)
        self.console.print()
        
        # Group datasets by format for better organization in the selection list
        datasets_by_format = {}
        for dataset in datasets:
            fmt = dataset.get("format", "unknown")
            if fmt not in datasets_by_format:
                datasets_by_format[fmt] = []
            datasets_by_format[fmt].append(dataset)
        
        # Format dataset choices for selection
        dataset_choices = []
        
        # If there are multiple formats, use sections
        if len(datasets_by_format) > 1:
            for fmt, fmt_datasets in datasets_by_format.items():
                # Add a separator/header if we have multiple formats
                if dataset_choices:  # Don't add separator before the first section
                    dataset_choices.append((f"--- {fmt.upper()} DATASETS ---", None))
                else:
                    dataset_choices.append((f"--- {fmt.upper()} DATASETS ---", None))
                
                # Add datasets for this format
                for i, dataset in enumerate(fmt_datasets):
                    # Create label with useful info including type
                    index = datasets.index(dataset) + 1  # Get the original index
                    label = f"{index}. {dataset['name']} [{dataset.get('type', '').upper()}]"
                    
                    # Add example count if available
                    example_count = dataset.get("example_count", "Unknown")
                    if example_count != "Unknown":
                        if isinstance(example_count, int) and example_count > 1000:
                            label += f" ({example_count//1000}K examples)"
                        else:
                            label += f" ({example_count} examples)"
                    
                    dataset_choices.append((label, dataset))
        else:
            # Simple list if only one format
            for i, dataset in enumerate(datasets, 1):
                # Create label with useful info including type
                label = f"{i}. {dataset['name']} [{dataset.get('type', '').upper()}]"
                
                # Add example count if available
                example_count = dataset.get("example_count", "Unknown")
                if example_count != "Unknown":
                    if isinstance(example_count, int) and example_count > 1000:
                        label += f" ({example_count//1000}K examples)"
                    else:
                        label += f" ({example_count} examples)"
                
                dataset_choices.append((label, dataset))
        
        # Add cancel option
        dataset_choices.append(("", None))
        dataset_choices.append(("Cancel", None))
        
        # Ask user to select
        selection = inquirer.prompt([
            inquirer.List(
                'dataset',
                message="Select a dataset",
                choices=dataset_choices
            )
        ])
        
        return selection['dataset'] if selection else None

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
                    choices=format_types
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['format_type'] == "back":
                return None
                
            format_type = answers['format_type']
            
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