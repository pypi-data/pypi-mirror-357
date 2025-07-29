"""Commands for dataset management in the Dravik CLI"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import inquirer

# Import dataset-related utilities with error handling
try:
    from ...utils.data_loader import load_jailbreak_dataset, load_benchmark_dataset
except ImportError:
    def load_jailbreak_dataset():
        return {"prompts": [], "metadata": {}}
    
    def load_benchmark_dataset():
        return {"data": [], "metadata": {}}

try:
    from ...utils.formatter import format_dataset
except ImportError:
    def format_dataset(data, format_type="json"):
        return json.dumps(data, indent=2) if format_type == "json" else str(data)

from rich import box  # Add this import for box styles
import uuid
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sqlite3
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from ...db_handler import DravikDB

# Import the fundamental components
try:
    from ...raw_dataset import save_raw_dataset
    from ...formatters import get_available_format_choices
except ImportError:
    # Provide fallback implementations
    def save_raw_dataset(name):
        return False
    
    def get_available_format_choices():
        return ["simple_text", "llama2", "alpaca", "custom"]
    
    class DravikDB:
        def list_datasets(self, dataset_type):
            return []
        
        def get_raw_dataset(self, name):
            return None

class DatasetCommands:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.console = Console()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.dravik_db = DravikDB()

    def download_dataset(self):
        """Handle dataset download workflow using raw_dataset.py"""
        try:
            # Prompt for dataset name
            dataset_name = self._prompt_dataset_name()
            if not dataset_name:
                return

            # Use raw_dataset.py's save_raw_dataset function
            self.console.print(f"[blue]Downloading dataset: {dataset_name}...[/]")
            result = save_raw_dataset(dataset_name)
            
            if result:
                self.console.print(f"[green]Dataset {dataset_name} successfully downloaded and saved[/]")
            else:
                self.console.print(f"[red]Failed to download dataset {dataset_name}[/]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error downloading dataset: {str(e)}")

    def format_dataset(self):
        """Handle dataset formatting workflow using formatter.py"""
        try:
            # Get list of raw datasets from db_handler
            raw_datasets = self.dravik_db.list_datasets("raw")
            
            if not raw_datasets:
                self.console.print("[yellow]No raw datasets found. Please download a dataset first.[/]")
                return
                
            # Let user select dataset to format
            dataset_name = self._select_from_list(raw_datasets, "Select dataset to format")
            if not dataset_name:
                return
                
            # Get the raw dataset content to inspect its structure if needed
            raw_data = self.dravik_db.get_raw_dataset(dataset_name)
            if not raw_data:
                self.console.print(f"[red]Error: Could not retrieve dataset: {dataset_name}[/]")
                return
            
            # Let user select which model format to use
            self.console.print("\n[cyan]Select the model format for this dataset:[/]")
            self.console.print("[dim]Different models require specific dataset formats for fine-tuning.[/]")
            
            format_choices = get_available_format_choices()
            
            format_questions = [
                inquirer.List(
                    'model_format',
                    message="Select target model format",
                    choices=format_choices
                )
            ]
            
            format_answers = inquirer.prompt(format_questions)
            if not format_answers:
                return
                
            model_format = format_answers['model_format']
            
            # For custom format, ask for field structure
            custom_template = None
            if model_format == "custom":
                self.console.print("\n[cyan]Custom Format Configuration[/]")
                self.console.print("Define the fields in your custom dataset format.")
                self.console.print("[dim]Use {prompt} and {completion} as placeholders for the actual text.[/]")
                
                fields = []
                while True:
                    field_question = [
                        inquirer.Text(
                            'field_name',
                            message="Enter field name (leave empty when done)",
                            validate=lambda _, x: True
                        )
                    ]
                    
                    field_answer = inquirer.prompt(field_question)
                    if not field_answer or not field_answer['field_name']:
                        break
                        
                    field_name = field_answer['field_name']
                    
                    template_question = [
                        inquirer.List(
                            'template',
                            message=f"What should '{field_name}' contain?",
                            choices=[
                                ('Prompt text', '{prompt}'),
                                ('Completion text', '{completion}'),
                                ('Custom static text', 'static')
                            ]
                        )
                    ]
                    
                    template_answer = inquirer.prompt(template_question)
                    if not template_answer:
                        continue
                    
                    template = template_answer['template']
                    if template == 'static':
                        static_text_question = [
                            inquirer.Text(
                                'static_text',
                                message=f"Enter static text for '{field_name}'",
                                validate=lambda _, x: len(x) > 0
                            )
                        ]
                        
                        static_text_answer = inquirer.prompt(static_text_question)
                        if static_text_answer:
                            template = static_text_answer['static_text']
                    
                    fields.append((field_name, template))
                
                if fields:
                    custom_template = {name: template for name, template in fields}
                else:
                    self.console.print("[yellow]No fields defined. Using default format.[/]")
                    model_format = "simple_text"
            
            # Now try to find the prompts and completions
            try:
                self.console.print("[blue]Analyzing dataset structure...[/]")
                
                # Show dataset structure to help user identify prompt location
                self._show_dataset_structure(raw_data)
                
                # Ask the user to specify the prompt key
                prompt_key = self._prompt_for_dataset_key(raw_data, "prompt")
                if not prompt_key:
                    self.console.print("[red]Format cancelled.[/]")
                    return
                
                # Ask the user to specify the completion/response key if needed
                completion_key = self._prompt_for_dataset_key(raw_data, "completion/response (optional)")
                
                # Try formatting with the selected model format
                self.console.print(f"[blue]Formatting dataset for {model_format} format...[/]")
                
                from formatter import format_with_model_template
                result = format_with_model_template(
                    dataset_name, 
                    model_format,
                    prompt_key, 
                    completion_key,
                    custom_template
                )
                
                if result:
                    self.console.print(f"[green]Dataset {dataset_name} successfully formatted for {model_format}[/]")
                else:
                    self.console.print(f"[red]Failed to format dataset {dataset_name}[/]")
                
            except Exception as e:
                self.console.print(f"[red]Error during formatting: {str(e)}[/]")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            self.console.print(f"[bold red]Error formatting dataset: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _show_dataset_structure(self, raw_data: Dict[str, Any]):
        """Display the structure of the dataset to help identify keys"""
        self.console.print("[cyan]Dataset Structure:[/]")
        
        # Identify the main splits
        splits = [k for k in raw_data.keys() if not k.startswith('_')]
        
        table = Table(title="Dataset Overview")
        table.add_column("Split", style="cyan")
        table.add_column("Keys", style="green")
        table.add_column("Sample Count", style="yellow")
        
        for split in splits:
            if isinstance(raw_data[split], dict):
                keys = list(raw_data[split].keys())
                # Estimate sample count from first available key with list value
                sample_count = "Unknown"
                for key in keys:
                    if isinstance(raw_data[split][key], list):
                        sample_count = str(len(raw_data[split][key]))
                        break
                table.add_row(split, ", ".join(keys), sample_count)
        
        self.console.print(table)
        
        # Show example values for potential prompt keys
        self.console.print("\n[cyan]Sample Values:[/]")
        for split in splits:
            if isinstance(raw_data[split], dict):
                for key, values in raw_data[split].items():
                    if isinstance(values, list) and len(values) > 0:
                        self.console.print(f"[green]{split}.{key}[/] (first item):")
                        
                        # Display a preview of the first item
                        sample_value = str(values[0])
                        if len(sample_value) > 100:
                            sample_value = sample_value[:100] + "..."
                        self.console.print(f"  {sample_value}\n")
    
    def _prompt_for_dataset_key(self, raw_data: Dict[str, Any], key_type: str) -> str:
        """Ask user to specify which key contains prompts or completions"""
        # Collect potential keys from the dataset
        potential_keys = []
        splits = [k for k in raw_data.keys() if not k.startswith('_')]
        
        for split in splits:
            if isinstance(raw_data[split], dict):
                for key in raw_data[split].keys():
                    if key not in potential_keys and isinstance(raw_data[split][key], list):
                        potential_keys.append(f"{split}.{key}")
        
        # Add option to specify a custom path
        potential_keys.append("Specify custom path")
        
        # Create the question
        questions = [
            inquirer.List(
                'key_path',
                message=f"Select which key contains the {key_type} data",
                choices=potential_keys
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return ""
            
        key_path = answers['key_path']
        
        # Handle custom path
        if key_path == "Specify custom path":
            custom_questions = [
                inquirer.Text(
                    'custom_path',
                    message=f"Enter the path to {key_type} data (e.g., 'train.instruction')"
                )
            ]
            custom_answers = inquirer.prompt(custom_questions)
            if not custom_answers:
                return ""
            key_path = custom_answers['custom_path']
        
        # Validate the key exists
        parts = key_path.split('.')
        current = raw_data
        valid_path = True
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                valid_path = False
                break
                
        if not valid_path:
            self.console.print(f"[red]Warning: Key '{key_path}' not found in dataset.[/]")
            if not inquirer.confirm("Continue anyway?", default=False):
                return ""
        
        return key_path

    def list_and_view_datasets(self):
        """Handle dataset listing and viewing using db_handler.py"""
        try:
            # Get datasets from each category using db_handler
            raw_datasets = self.dravik_db.list_datasets("raw")
            structured_datasets = self.dravik_db.list_datasets("structured") 
            poc_datasets = self.dravik_db.list_datasets("poc")
            
            if not raw_datasets and not structured_datasets and not poc_datasets:
                self.console.print("[yellow]No datasets found[/]")
                return
            
            # Display in enhanced table format
            table = Table(title="Available Datasets", box=box.ROUNDED)
            table.add_column("ID", style="bright_blue")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Format", style="magenta")
            table.add_column("Formatted At", style="yellow")
            
            # Get the dataset information including metadata
            all_datasets_details = []
            
            # Process raw datasets
            for idx, name in enumerate(raw_datasets):
                # Raw datasets don't have format information
                all_datasets_details.append({
                    "id": f"R{idx+1}",
                    "name": name,
                    "type": "Raw",
                    "format": "N/A",
                    "formatted_at": "N/A"
                })
            
            # Process structured and POC datasets
            for dataset_type in ["structured", "poc"]:
                dataset_names = structured_datasets if dataset_type == "structured" else poc_datasets
                type_prefix = "S" if dataset_type == "structured" else "P"
                
                for idx, name in enumerate(dataset_names):
                    # Get dataset content to extract format and timestamp
                    content = self.dravik_db.get_dataset_content(dataset_type, name)
                    
                    # Extract format and timestamp from metadata
                    dataset_format = "Unknown"
                    formatted_at = "Unknown"
                    
                    if content:
                        # Try different metadata fields based on format structure
                        if "format" in content:
                            dataset_format = content["format"]
                        
                        if "formatted_at" in content:
                            formatted_at = self._format_timestamp(content["formatted_at"])
                        elif "timestamp" in content:
                            formatted_at = self._format_timestamp(content["timestamp"])
                    
                    all_datasets_details.append({
                        "id": f"{type_prefix}{idx+1}",
                        "name": name,
                        "type": "Structured" if dataset_type == "structured" else "POC",
                        "format": dataset_format,
                        "formatted_at": formatted_at
                    })
            
            # Sort datasets by name for better organization
            all_datasets_details.sort(key=lambda x: x["name"])
            
            # Add all datasets to table
            for dataset in all_datasets_details:
                table.add_row(
                    dataset["id"],
                    dataset["name"], 
                    dataset["type"],
                    dataset["format"],
                    dataset["formatted_at"]
                )
                
            self.console.print(table)
            
            # Ask if user wants to view details of a specific dataset
            if inquirer.confirm("View dataset details?", default=False):
                self._view_dataset_details_enhanced(all_datasets_details)
                
        except Exception as e:
            self.console.print(f"[bold red]Error listing datasets: {str(e)}")
            import traceback
            traceback.print_exc()

    def _view_dataset_details_enhanced(self, all_datasets_details):
        """View details of a selected dataset with enhanced ID-based selection"""
        try:
            # Create dataset choices with IDs
            dataset_choices = [(f"{d['id']} - {d['name']} ({d['type']})", d) for d in all_datasets_details]
            
            # Let user select a dataset by ID
            questions = [
                inquirer.List(
                    'dataset',
                    message="Select dataset to view",
                    choices=dataset_choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return
                
            selected = answers['dataset']
            
            # Get dataset content based on type
            content = None
            if selected['type'] == "Raw":
                content = self.dravik_db.get_raw_dataset(selected['name'])
            else:
                dataset_type = "structured" if selected['type'] == "Structured" else "poc"
                content = self.dravik_db.get_dataset_content(dataset_type, selected['name'])
            
            if not content:
                self.console.print("[yellow]Dataset content not found.[/]")
                return
                
            # Display dataset details in enhanced format
            self.console.print(Panel(f"[bold blue]{selected['name']}[/] ({selected['type']} dataset)"))
            
            # Create metadata panel with all available information
            metadata_rows = []
            
            # Add standard metadata
            metadata_rows.append(f"[cyan]ID:[/] {selected['id']}")
            metadata_rows.append(f"[cyan]Name:[/] {selected['name']}")
            metadata_rows.append(f"[cyan]Type:[/] {selected['type']}")
            metadata_rows.append(f"[cyan]Format:[/] {selected['format']}")
            metadata_rows.append(f"[cyan]Formatted At:[/] {selected['formatted_at']}")
            
            # Add additional metadata if available
            if isinstance(content, dict):
                # Check different possible metadata locations
                metadata_sources = [
                    content.get("meta", {}),
                    content.get("_metadata", {}),
                    content.get("metadata", {}),
                    {k: v for k, v in content.items() if k not in ["data"] and not k.startswith("_")}
                ]
                
                # Collect all metadata
                all_metadata = {}
                for source in metadata_sources:
                    all_metadata.update(source)
                
                # Add all metadata to rows
                for key, value in all_metadata.items():
                    if key not in ["id", "name", "type", "format", "formatted_at"]:
                        metadata_rows.append(f"[cyan]{key}:[/] {value}")
            
            self.console.print(Panel(
                "\n".join(metadata_rows),
                title="Dataset Information",
                border_style="blue"
            ))
            
            # Display structure or sample data
            self._display_dataset_samples(content, selected['type'])
            
        except Exception as e:
            self.console.print(f"[bold red]Error viewing dataset: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _display_dataset_samples(self, content, dataset_type):
        """Display sample data from the dataset"""
        self.console.print("\n[bold cyan]Sample Data:[/]")
        
        if dataset_type == "Raw":
            if "train" in content:
                # Show the keys 
                keys = list(content["train"].keys())
                if keys:
                    self.console.print(f"[green]Dataset keys:[/] {', '.join(keys)}")
                
                # Show sample entries
                self.console.print("\n[bold cyan]Sample entries from raw dataset:[/]")
                
                # Select one key to show examples from
                main_key = keys[0]  # Usually the first key will be something like "text" or "prompt"
                if "text" in keys:
                    main_key = "text"
                elif "prompt" in keys:
                    main_key = "prompt"
                
                # Get samples
                try:
                    entries = content["train"][main_key]
                    if isinstance(entries, list):
                        # Show up to 3 samples
                        sample_count = min(3, len(entries))
                        for i in range(sample_count):
                            sample = entries[i]
                            self.console.print(f"\n[cyan]Example {i+1}:[/]")
                            if isinstance(sample, str):
                                # Truncate very long strings
                                if len(sample) > 200:
                                    self.console.print(f"{sample[:200]}...")
                                else:
                                    self.console.print(sample)
                            else:
                                self.console.print(str(sample)[:200] + "..." if len(str(sample)) > 200 else str(sample))
                except Exception as e:
                    self.console.print(f"[yellow]Could not display samples: {e}[/]")
        else:
            if "data" in content and isinstance(content["data"], list):
                # Create a nice table for structured data samples
                sample_count = min(3, len(content["data"]))
                self.console.print(f"[green]Sample entries ({sample_count} of {len(content['data'])}):[/]")
                
                # Determine fields to display
                all_fields = set()
                for i in range(sample_count):
                    if isinstance(content["data"][i], dict):
                        all_fields.update(content["data"][i].keys())
                
                if all_fields:
                    # Create a table for sample data
                    sample_table = Table(title="Sample Data", box=box.SIMPLE)
                    sample_table.add_column("Entry", style="bright_blue", width=5)
                    
                    # Add columns for common fields
                    important_fields = ["prompt", "completion", "instruction", "input", "output", "text"]
                    for field in important_fields:
                        if field in all_fields:
                            sample_table.add_column(field.capitalize(), style="green")
                            all_fields.remove(field)
                    
                    # Add columns for remaining fields
                    for field in sorted(all_fields):
                        sample_table.add_column(field.capitalize(), style="yellow")
                    
                    # Add rows for each sample
                    for i in range(sample_count):
                        sample = content["data"][i]
                        if isinstance(sample, dict):
                            row = [str(i+1)]
                            
                            # Add values for important fields
                            for field in important_fields:
                                if field in sample:
                                    value = sample[field]
                                    if isinstance(value, str):
                                        # Truncate long strings
                                        if len(value) > 80:
                                            value = value[:77] + "..."
                                    row.append(str(value))
                                elif field in all_fields:
                                    row.append("")
                            
                            # Add values for remaining fields
                            for field in sorted(all_fields):
                                if field in sample:
                                    value = sample[field]
                                    if isinstance(value, str):
                                        # Truncate long strings
                                        if len(value) > 80:
                                            value = value[:77] + "..."
                                    row.append(str(value))
                                else:
                                    row.append("")
                            
                            sample_table.add_row(*row)
                    
                    self.console.print(sample_table)
    
    def _format_timestamp(self, timestamp_str):
        """Format timestamp string to a more readable format"""
        try:
            if not timestamp_str or timestamp_str in ["N/A", "Unknown"]:
                return "Unknown"
                
            # Try to parse ISO format timestamp
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            # Return original if parsing fails
            return timestamp_str

    def _prompt_dataset_name(self) -> Optional[str]:
        """Prompt user for dataset name"""
        questions = [
            inquirer.Text(
                'dataset_name',
                message="Enter HuggingFace dataset name (e.g. 'datasets/alpaca')",
                validate=lambda _, x: len(x) > 0
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['dataset_name'] if answers else None
        
    def _select_from_list(self, items: List[str], message: str) -> Optional[str]:
        """Let user select an item from a list"""
        if not items:
            return None
            
        choices = [(item, item) for item in items]
        
        questions = [
            inquirer.List(
                'item',
                message=message,
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['item'] if answers else None
        
    def _view_dataset_details(self, raw_datasets, structured_datasets, poc_datasets):
        """View details of a selected dataset"""
        # Create combined list of all datasets with their types
        all_datasets = []
        
        for name in raw_datasets:
            all_datasets.append({"name": name, "type": "raw"})
            
        for name in structured_datasets:
            all_datasets.append({"name": name, "type": "structured"})
            
        for name in poc_datasets:
            all_datasets.append({"name": name, "type": "poc"})
            
        # Create dataset choices
        dataset_choices = [(f"{d['name']} ({d['type']})", d) for d in all_datasets]
        
        # Let user select a dataset
        questions = [
            inquirer.List(
                'dataset',
                message="Select dataset to view",
                choices=dataset_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
            
        selected = answers['dataset']
        
        # Get dataset content based on type
        content = None
        if selected['type'] == "raw":
            content = self.dravik_db.get_raw_dataset(selected['name'])
        else:
            content = self.dravik_db.get_dataset_content(selected['type'], selected['name'])
        
        if not content:
            self.console.print("[yellow]Dataset content not found.[/]")
            return
            
        # Display dataset details
        self.console.print(Panel(f"[bold blue]{selected['name']}[/] ({selected['type']} dataset)"))
        
        # Display metadata if available
        if isinstance(content, dict) and "_metadata" in content:
            metadata = content["_metadata"]
            self.console.print(Panel(
                "\n".join([f"[cyan]{k}:[/] {v}" for k, v in metadata.items()]),
                title="Metadata"
            ))
        
        # Display structure or sample
        if selected['type'] == "raw":
            if "train" in content:
                # Show the keys 
                keys = list(content["train"].keys())
                if keys:
                    self.console.print(f"[green]Dataset keys:[/] {', '.join(keys)}")
                
                # Now show sample entries (new functionality)
                self.console.print("\n[bold cyan]Sample entries from raw dataset:[/]")
                
                # Select one key to show examples from
                main_key = keys[0]  # Usually the first key will be something like "text" or "prompt"
                if "text" in keys:
                    main_key = "text"
                elif "prompt" in keys:
                    main_key = "prompt"
                
                # Get samples
                try:
                    entries = content["train"][main_key]
                    if isinstance(entries, list):
                        # Show up to 3 samples
                        sample_count = min(3, len(entries))
                        for i in range(sample_count):
                            sample = entries[i]
                            self.console.print(f"\n[cyan]Example {i+1}:[/]")
                            if isinstance(sample, str):
                                # Truncate very long strings
                                if len(sample) > 200:
                                    self.console.print(f"{sample[:200]}...")
                                else:
                                    self.console.print(sample)
                            else:
                                self.console.print(str(sample)[:200] + "..." if len(str(sample)) > 200 else str(sample))
                except Exception as e:
                    self.console.print(f"[yellow]Could not display samples: {e}[/]")
        else:
            if "data" in content and isinstance(content["data"], list):
                sample_count = min(3, len(content["data"]))
                self.console.print(f"[green]Sample entries ({sample_count} of {len(content['data'])}):[/]")
                
                for i in range(sample_count):
                    sample = content["data"][i]
                    if isinstance(sample, dict):
                        self.console.print(f"\n[cyan]Entry {i+1}:[/]")
                        for key, value in sample.items():
                            if isinstance(value, str) and len(value) > 100:
                                value = value[:100] + "..."
                            self.console.print(f"  [yellow]{key}:[/] {value}")
