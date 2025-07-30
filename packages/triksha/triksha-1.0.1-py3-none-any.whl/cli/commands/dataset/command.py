"""Dataset command implementation"""
from rich.console import Console
from typing import Dict, Any, List, Optional
import inquirer
from pathlib import Path
import os
import time
import json
import csv
from datetime import datetime  # Add this import for datetime functionality
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
import traceback
import random
import lancedb
from datasets import load_dataset
import pandas as pd
import questionary
import uuid
import requests

from .ui import DatasetUI
from utils.rich_helpers import escape_rich_markup, safe_rich_print


class DatasetCommands:
    """Handle dataset-related commands"""

    # Templates for adversarial training formatting
    ADVERSARIAL_TEMPLATES = {
        "jailbreak": {
            "prompt_prefix": "You are a secure AI assistant. Respond appropriately to: ",
            "response_prefix": "I must decline to help with: ",
            "categories": ["manipulation", "harmful_content", "security_bypass"]
        },
        "safety": {
            "prompt_prefix": "Ensure safe response to: ",
            "response_prefix": "Safety assessment: ",
            "categories": ["toxicity", "bias", "harmful_instructions"]
        }
    }

    # Model architecture templates for dataset formatting
    MODEL_TEMPLATES = {
        # ...existing code...
    }

    # Adversarial safeguard responses templates
    ADVERSARIAL_SAFEGUARDS = [
        # ...existing code...
    ]

    # Problem categories for adversarial safeguards
    PROBLEM_TYPES = [
        # ...existing code...
    ]

    # Harm descriptions for adversarial safeguards
    HARM_DESCRIPTIONS = [
        # ...existing code...
    ]

    # Alternative suggestions for adversarial safeguards
    ALTERNATIVES = [
        # ...existing code...
    ]

    def __init__(self, db, config=None):
        self.db = db
        self.config = config
        self.console = Console()
        self.ui = DatasetUI(console=self.console)

        # Setup directories
        self.base_dir = Path.home() / "dravik"
        self.datasets_dir = self.base_dir / "data" / "datasets"
        self.raw_dir = self.datasets_dir / "raw"
        self.processed_dir = self.datasets_dir / "processed"

        # Create directories
        for dir_path in [self.datasets_dir, self.raw_dir, self.processed_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)

        # Initialize LanceDB connection
        try:
            self.lance_uri = str(self.base_dir / "data" / "lancedb")
            self.lance_db = lancedb.connect(self.lance_uri)
            self.console.print("[green]✓ Connected to LanceDB[/]")
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not connect to LanceDB: {str(e)}[/]")
            self.lance_db = None

    def download_dataset(self, dataset_info: Optional[Dict[str, Any]] = None):
        """Download a dataset from HuggingFace with interactive menu support"""
        try:
            # If dataset_info not provided, get it from user input
            if not dataset_info:
                questions = [
                    inquirer.Text(
                        'dataset_id',
                        message="Enter HuggingFace dataset ID (e.g. 'databricks/databricks-dolly-15k')"
                    ),
                    inquirer.Confirm(
                        'use_auth',
                        message="Use HuggingFace authentication?",
                        default=False
                    ),
                    inquirer.Confirm(
                        'disable_ssl_verify',
                        message="Disable SSL verification? (use if experiencing SSL certificate errors)",
                        default=False
                    )
                ]
                dataset_info = inquirer.prompt(questions)
                if not dataset_info:
                    return

            dataset_id = dataset_info.get('dataset_id')
            use_auth = dataset_info.get('use_auth', False)
            disable_ssl_verify = dataset_info.get('disable_ssl_verify', False)

            # Validate dataset ID
            if not dataset_id:
                self.console.print("[red]Dataset ID is required[/]")
                return

            # If SSL verification is disabled, set environment variable
            if disable_ssl_verify:
                self.console.print("[yellow]Warning: SSL verification disabled[/]")
                os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
                import requests
                requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

            # Setup paths and cache directory
            cache_dir = Path.home() / "dravik" / "data" / "cache"
            cache_dir.mkdir(exist_ok=True, parents=True)

            # Check if dataset is already cached
            dataset_name = dataset_id.split('/')[-1]
            
            # Special handling for jailbreak-classification
            is_jailbreak_classification = "jailbreak-classification" in dataset_id
            if is_jailbreak_classification:
                self.console.print("[cyan]Detected jailbreak-classification dataset, using special handling[/]")
                
            # Add dataset name to info
            dataset_info['name'] = dataset_name
            
            cache_file = cache_dir / f"{dataset_name}.json"

            if cache_file.exists() and not dataset_info.get('force_reload', False):
                if inquirer.confirm(f"Dataset '{dataset_name}' found in cache. Use cached version?", default=True):
                    self.console.print(
                        f"[cyan]Using cached dataset: {dataset_name}[/]")
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)

                        # Process the cached dataset
                        unique_id = self._process_and_save_dataset(
                            cached_data, dataset_id, dataset_info)
                        self.console.print(
                            f"[bold green]✓ Dataset loaded from cache successfully! ID: {unique_id}[/]")

                        # Show dataset preview
                        self._show_dataset_preview(cached_data)
                        return unique_id
                    except Exception as e:
                        self.console.print(
                            f"[yellow]Error loading from cache: {str(e)}. Will download fresh copy.[/]")

            # Check for HuggingFace token if auth requested
            token = None
            if use_auth:
                # Use ApiKeyManager to get/prompt for the API key
                from utils.api_prompt_helpers import ensure_api_key
                token = ensure_api_key(
                    "huggingface", 
                    "This API key is needed to access private or gated datasets on HuggingFace."
                )
                
                if not token:
                    self.console.print(
                        "[red]Authentication required but no token provided. Aborting.[/]")
                    return

            # Advanced configuration options
            subset = None
            split = "train"
            streaming = True

            if dataset_info.get('advanced_options', False) or inquirer.confirm("Configure advanced download options?", default=False):
                advanced = inquirer.prompt([
                    inquirer.Text(
                        'subset',
                        message="Enter dataset subset (leave empty if none)"
                    ),
                    inquirer.Text(
                        'split',
                        message="Enter dataset split",
                        default="train"
                    ),
                    inquirer.Confirm(
                        'streaming',
                        message="Stream large dataset?",
                        default=True
                    )
                ])

                if advanced:
                    subset = advanced.get('subset') if advanced.get(
                        'subset') else None
                    split = advanced.get('split', 'train')
                    streaming = advanced.get('streaming', True)

            # Display download information
            self.console.print("\n[bold cyan]Dataset Download Information:[/]")
            self.console.print(f"[cyan]Dataset ID:[/] {dataset_id}")
            if subset:
                self.console.print(f"[cyan]Subset:[/] {subset}")
            self.console.print(f"[cyan]Split:[/] {split}")
            self.console.print(
                f"[cyan]Authentication:[/] {'Enabled' if token else 'Disabled'}")
            self.console.print(
                f"[cyan]Streaming:[/] {'Enabled' if streaming else 'Disabled'}")
            self.console.print(f"[cyan]Cache Directory:[/] {cache_dir}")

            # Configure progress display
            from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn

            # Implement a retry mechanism for robustness
            max_attempts = 3
            attempt = 0

            while attempt < max_attempts:
                attempt += 1

                try:
                    # Show progress with more information
                    with Progress(
                        TextColumn("[bold blue]{task.description}"),
                        BarColumn(),
                        TextColumn(
                            "[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeRemainingColumn()
                    ) as progress:
                        download_task = progress.add_task(
                            f"[cyan]Downloading {dataset_id}...", total=100)
                        processing_task = progress.add_task(
                            "[cyan]Processing...", visible=False, total=100)

                        # Update progress incrementally during download
                        # Datasets library doesn't provide download progress, so we'll simulate it
                        for i in range(1, 60):
                            progress.update(download_task, completed=i)
                            time.sleep(0.05)  # Small delay for visual feedback

                        # First, try to get dataset info to check for required configurations
                        from datasets import load_dataset_builder

                        try:
                            # Try to load the dataset builder to check for required configurations
                            builder = load_dataset_builder(dataset_id)

                            # Check if the dataset requires a configuration
                            if builder.config_id is None and len(builder.builder_configs) > 0:
                                # Dataset requires a configuration but none was specified
                                config_names = [
                                    config.name for config in builder.builder_configs]
                                self.console.print(
                                    f"[yellow]Dataset requires a configuration. Available configs: {', '.join(config_names)}[/]")

                                # Automatically select the first configuration
                                selected_config = config_names[0]
                                self.console.print(
                                    f"[cyan]Automatically selecting configuration: {selected_config}[/]")
                            else:
                                selected_config = None
                        except Exception as e:
                            # If we can't get the builder info, we'll try without a configuration
                            self.console.print(
                                f"[yellow]Could not determine dataset configuration requirements: {str(e)}[/]")
                            selected_config = None

                        # Prepare download arguments
                        download_args = {
                            "path": dataset_id,
                            "split": split,
                            "streaming": streaming,
                            "cache_dir": str(cache_dir)
                        }

                        # Add token if provided
                        if token:
                            download_args["token"] = token

                        # Add configuration if needed
                        if selected_config:
                            download_args["name"] = selected_config

                        # Add subset if provided
                        if subset:
                            download_args["subset"] = subset

                        # Try to download the dataset with the prepared arguments
                        try:
                            from datasets import load_dataset
                            dataset = load_dataset(**download_args)
                        except ValueError as ve:
                            # Check if the error is about missing configuration
                            error_msg = str(ve)
                            if "Config name is missing" in error_msg:
                                # Extract available configs from the error message
                                import re
                                config_match = re.search(
                                    r"available configs: \[(.*?)\]", error_msg)
                                if config_match:
                                    configs_str = config_match.group(1)
                                    configs = [c.strip("'")
                                               for c in configs_str.split(", ")]

                                    self.console.print(
                                        f"[yellow]Dataset requires a configuration. Available: {', '.join(configs)}[/]")

                                    # Automatically select the first configuration
                                    selected_config = configs[0]
                                    self.console.print(
                                        f"[cyan]Automatically selecting configuration: {selected_config}[/]")

                                    # Update download arguments with the selected configuration
                                    download_args["name"] = selected_config

                                    # Try again with the configuration
                                    dataset = load_dataset(**download_args)
                                else:
                                    # If we can't extract configs from the error, raise the original error
                                    raise
                            else:
                                # If it's a different error, raise it
                                raise

                        # Mark download as complete
                        progress.update(download_task, completed=100)

                        # Make processing task visible and update it
                        progress.update(processing_task, visible=True)

                        # Process the dataset in chunks to show progress
                        # First, for streaming datasets, we need to materialize them
                        if streaming:
                            self.console.print(
                                "[cyan]Processing streaming dataset...[/]")
                            examples = []
                            total_examples = 10000  # Estimate, will be updated

                            # Process in batches with progress updates
                            for i, example in enumerate(dataset):
                                examples.append(example)
                                if i % 100 == 0:
                                    progress.update(processing_task, completed=min(
                                        i * 100 // total_examples, 99))

                                # Update total estimate based on what we've seen
                                if i == 1000:
                                    # If we've reached 1000 examples, estimate total
                                    total_examples = 10000  # Conservative estimate

                                # Limit to reasonable size to prevent memory issues
                                if i >= 10000:
                                    self.console.print(
                                        "[yellow]Warning: Dataset too large, limiting to first 10,000 examples[/]")
                                    break

                            # Convert to regular dataset
                            import pandas as pd
                            df = pd.DataFrame(examples)
                            serializable_data = {
                                "name": dataset_name,
                                "examples": examples,
                                "features": list(examples[0].keys()) if examples else [],
                                "total_examples": len(examples),
                                "download_info": {
                                    "dataset_id": dataset_id,
                                    "subset": subset,
                                    "split": split,
                                    "streaming": streaming,
                                    "config": selected_config,
                                    "download_date": datetime.now().isoformat()
                                }
                            }

                            # Cache the dataset for future use
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(serializable_data, f, indent=2)

                            # Process and save the dataset
                            progress.update(processing_task, completed=100)
                            unique_id = self._process_and_save_dataset(
                                serializable_data, dataset_id, dataset_info)

                        else:
                            # For non-streaming datasets, we already have all the data
                            progress.update(processing_task, completed=50)

                            # Convert to serializable format
                            serializable_data = {
                                "name": dataset_name,
                                "examples": dataset.to_dict() if hasattr(dataset, 'to_dict') else list(dataset),
                                "features": dataset.column_names if hasattr(dataset, 'column_names') else
                                (list(dataset[0].keys()) if dataset and len(
                                    dataset) > 0 else []),
                                "total_examples": len(dataset) if hasattr(dataset, '__len__') else "unknown",
                                "download_info": {
                                    "dataset_id": dataset_id,
                                    "subset": subset,
                                    "split": split,
                                    "streaming": streaming,
                                    "config": selected_config,
                                    "download_date": datetime.now().isoformat()
                                }
                            }

                            # Cache the dataset for future use
                            with open(cache_file, 'w', encoding='utf-8') as f:
                                json.dump(serializable_data, f, indent=2)

                            # Process and save the dataset
                            progress.update(processing_task, completed=100)
                            unique_id = self._process_and_save_dataset(
                                serializable_data, dataset_id, dataset_info)

                    # Success! Show completion message
                    self.console.print(
                        "[bold green]✓ Dataset downloaded and processed successfully![/]")

                    # Show dataset statistics
                    self.console.print("\n[bold cyan]Dataset Statistics:[/]")

                    example_count = serializable_data.get(
                        "total_examples", "unknown")
                    self.console.print(
                        f"[cyan]Total Examples:[/] {example_count}")

                    features = serializable_data.get("features", [])
                    self.console.print(
                        f"[cyan]Features:[/] {', '.join(features[:10])}{'...' if len(features) > 10 else ''}")

                    # Show dataset preview
                    self.console.print("\n[bold cyan]Dataset Preview:[/]")
                    self._show_dataset_preview(serializable_data)

                    return unique_id

                except Exception as e:
                    # Handle error case
                    if attempt < max_attempts:
                        self.console.print(
                            f"[yellow]Error during attempt {attempt}/{max_attempts}: {str(e)}[/]")
                        self.console.print(
                            f"[yellow]Retrying in 3 seconds...[/]")
                        time.sleep(3)
                    else:
                        # Last attempt failed
                        self.console.print(
                            f"[bold red]Failed to download dataset after {max_attempts} attempts[/]")
                        self.console.print(f"[red]Error: {str(e)}[/]")
                        import traceback
                        self.console.print(traceback.format_exc())
                        return None

        except Exception as e:
            self.console.print(f"[bold red]Unexpected error: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            return None

    def _process_and_save_dataset(self, dataset, dataset_id: str, dataset_info: Dict[str, Any]):
        """Process and save the downloaded dataset"""
        try:
            # Generate a unique ID for this dataset
            unique_id = str(uuid.uuid4())

            # Extract dataset metadata
            dataset_info['download_date'] = datetime.now().isoformat()
            
            # Special handling for jailbreak-classification dataset
            is_jailbreak_classification = "jailbreak-classification" in dataset_id or dataset_info.get('name', '') == 'jailbreak-classification'
            
            # Process the dataset into a standard format
            processed_data = {}
            
            # Extract examples based on dataset structure
            examples = []
            if isinstance(dataset, list):
                examples = dataset
            elif isinstance(dataset, dict) and 'examples' in dataset:
                examples = dataset['examples']
            elif isinstance(dataset, dict) and 'data' in dataset:
                examples = dataset['data']
            
            # Special handling for jailbreak-classification
            if is_jailbreak_classification:
                # For jailbreak-classification datasets, ensure proper structure
                # with prompt and type fields
                processed_examples = []
                for example in examples:
                    # Extract appropriate fields
                    if isinstance(example, dict):
                        # Get prompt content
                        prompt = example.get('prompt', example.get('input', example.get('text', '')))
                        example_type = example.get('type', 'unknown')
                        
                        processed_example = {
                            'prompt': prompt,
                            'type': example_type
                        }
                        processed_examples.append(processed_example)
                    elif isinstance(example, str):
                        # Simple string examples
                        processed_examples.append({
                            'prompt': example,
                            'type': 'unknown'
                        })
                
                examples = processed_examples
                
                # Set dataset info for jailbreak-classification format
                processed_data = {
                    'name': 'jailbreak-classification',
                    'format_type': 'classification',
                    'examples': examples,
                    '_metadata': {
                        'id': unique_id,
                        'source': dataset_id,
                        'download_date': dataset_info['download_date'],
                        'type': 'classification',
                        'format': 'jailbreak-classification',
                        'input_key': 'prompt',
                        'has_output': False
                    }
                }
            else:
                # Standard dataset processing
                processed_data = {
                    'name': dataset_info.get('name', dataset_id.split('/')[-1]),
                    'format_type': 'raw',
                    'examples': examples,
                    '_metadata': {
                        'id': unique_id,
                        'source': dataset_id,
                        'download_date': dataset_info['download_date'],
                        'type': 'raw',
                        'format': 'default'
                    }
                }
            
            # Add any additional metadata from dataset_info
            processed_data['_metadata'].update({k: v for k, v in dataset_info.items() 
                                             if k not in ['name', 'examples', '_metadata']})
            
            # Save the dataset to the local filesystem
            dir_path = Path.home() / "dravik" / "data" / "raw"
            dir_path.mkdir(exist_ok=True, parents=True)
            
            # Use a cleaned version of the dataset name for the file
            safe_name = dataset_info.get('name', '').replace('/', '_')
            file_path = dir_path / f"{safe_name}_raw.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False)
                
            self.console.print(f"[green]✓ Dataset saved to: {file_path}[/]")
            
            # Try to save to the database
            success = self.db.save_raw_dataset(
                processed_data['name'],
                dataset_id,
                str(file_path),
                processed_data
            )

            if not success:
                self.console.print(
                    "[yellow]Warning: Failed to save dataset to database, will try alternative storage methods[/]")

            # Also save to HuggingFace datasets table for better organization
            try:
                hf_success = self.db.save_huggingface_dataset(
                    dataset_name=processed_data['name'],
                    dataset_id=unique_id,
                    data=processed_data
                )
                
                if hf_success:
                    self.console.print(
                        f"[green]✓ Successfully saved to HuggingFace datasets table[/]")
                else:
                    self.console.print(
                        "[yellow]Warning: Failed to save to HuggingFace datasets table[/]")
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Error saving to HuggingFace datasets table: {str(e)}[/]")

            # Save to LanceDB for efficient storage with unique table name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            short_uuid = unique_id[:8]  # Use first 8 chars of UUID for brevity
            lance_table_name = f"raw_dataset_{processed_data['name']}_{timestamp}_{short_uuid}"

            # Enhanced LanceDB saving that ensures raw datasets are stored properly
            try:
                # Prepare data for LanceDB - optimize for raw datasets
                lance_data = self._prepare_for_lancedb(processed_data)

                # Save to LanceDB with additional metadata
                lance_success = self._save_to_lancedb(
                    lance_data, lance_table_name)

                if lance_success:
                    self.console.print(
                        f"[green]✓ Successfully saved raw dataset to LanceDB table: {lance_table_name}[/]")

                    # Register the table in a dataset registry for easier discovery
                    self._register_lancedb_dataset(
                        table_name=lance_table_name,
                        dataset_type="raw",
                        dataset_name=processed_data['name'],
                        dataset_id=unique_id,
                        metadata=processed_data
                    )
                else:
                    self.console.print(
                        "[yellow]Warning: Failed to save dataset to LanceDB[/]")
            except Exception as e:
                self.console.print(
                    f"[yellow]Error saving to LanceDB: {str(e)}[/]")

            # Also save a local copy to the raw datasets directory for easier discovery
            try:
                raw_dir = self.base_dir / "data" / "datasets" / "raw"
                raw_dir.mkdir(exist_ok=True, parents=True)

                # Create a file with the dataset name
                file_path = raw_dir / f"{processed_data['name']}.json"

                # Save the processed data to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2)

                self.console.print(
                    f"[green]Saved local copy to {file_path}[/]")
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not save local copy: {str(e)}[/]")

            return unique_id

        except Exception as e:
            self.console.print(f"[red]Error processing dataset: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            raise Exception(f"Error processing dataset: {str(e)}")

    def _save_to_lancedb(self, dataset, table_name: str) -> bool:
        """Save dataset to LanceDB with improved schema handling"""
        try:
            # Skip if dataset is empty
            if dataset is None or (hasattr(dataset, 'empty') and dataset.empty):
                self.console.print(
                    "[yellow]Warning: Empty dataset, skipping LanceDB save[/]")
                return False

            # Convert to DataFrame if needed
            if not hasattr(dataset, 'to_pandas'):
                try:
                    import pandas as pd
                    if isinstance(dataset, dict):
                        dataset = pd.DataFrame(dataset)
                    elif isinstance(dataset, list):
                        dataset = pd.DataFrame(dataset)
                    else:
                        self.console.print(
                            "[yellow]Warning: Could not convert dataset to DataFrame[/]")
                        return False
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning: Error converting to DataFrame: {str(e)}[/]")
                    return False

            # Add dataset_id column for identification
            if 'dataset_id' not in dataset.columns:
                dataset['dataset_id'] = table_name

            # Get LanceDB connection
            try:
                import lancedb
                db = lancedb.connect(self.lance_uri)
            except Exception as e:
                self.console.print(
                    f"[red]Error connecting to LanceDB: {str(e)}[/]")
                return False

            try:
                # Always create a new table with mode="overwrite" to prevent conflicts
                try:
                    # Try to create the table with "overwrite" mode
                    db.create_table(table_name, data=dataset, mode="overwrite")
                    self.console.print(
                        f"[green]✓ Created/overwritten table: {table_name}[/]")
                    return True
                except Exception as e:
                    # Check if it's an API version issue (older version might not support mode)
                    if "unexpected keyword argument 'mode'" in str(e):
                        # Older API version - try to drop the table first if it exists
                        try:
                            # Check if table exists
                            table_exists = False
                            try:
                                db.open_table(table_name)
                                table_exists = True
                            except:
                                pass

                            # Drop the table if it exists
                            if table_exists:
                                db.drop_table(table_name)
                                self.console.print(
                                    f"[yellow]Dropped existing table: {table_name}[/]")

                            # Create the table without mode
                            db.create_table(table_name, data=dataset)
                            self.console.print(
                                f"[green]✓ Created table: {table_name}[/]")
                            return True
                        except Exception as e2:
                            self.console.print(
                                f"[red]Error creating table with fallback method: {str(e2)}[/]")

                            # Last resort - use a unique table name with timestamp
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            unique_table_name = f"{table_name}_{timestamp}"
                            try:
                                db.create_table(
                                    unique_table_name, data=dataset)
                                self.console.print(
                                    f"[green]✓ Created table with unique name: {unique_table_name}[/]")
                                return True
                            except Exception as e3:
                                self.console.print(
                                    f"[red]Error creating table with unique name: {str(e3)}[/]")
                                return False
                    else:
                        # Other errors - try with unique name
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_table_name = f"{table_name}_{timestamp}"
                        try:
                            db.create_table(unique_table_name, data=dataset)
                            self.console.print(
                                f"[green]✓ Created table with unique name: {unique_table_name}[/]")
                            return True
                        except Exception as e2:
                            self.console.print(
                                f"[red]Error creating table with unique name: {str(e2)}[/]")
                            return False

            except Exception as e:
                self.console.print(
                    f"[red]Error in LanceDB operation: {str(e)}[/]")
                return False

        except Exception as e:
            self.console.print(f"[red]Error saving to LanceDB: {str(e)}[/]")
            return False

    def _show_dataset_preview(self, dataset):
        """Show a preview of the formatted dataset with support for custom keys
        and option to view the complete dataset"""
        try:
            # Handle different dataset formats
            if isinstance(dataset, str):
                # Try to parse if it's a JSON string
                try:
                    import json
                    dataset = json.loads(dataset)
                except json.JSONDecodeError:
                    self.console.print(
                        "[yellow]Warning: Dataset is in string format and could not be parsed as JSON[/]")
                    return

            if not dataset:
                self.console.print("[yellow]Warning: Empty dataset[/]")
                return

            # Create a table for the preview
            from rich.table import Table
            from rich.panel import Panel
            import inquirer

            # Get dataset information
            examples = dataset.get("examples", []) if isinstance(
                dataset, dict) else dataset
            format_type = dataset.get("format_type", "unknown") if isinstance(
                dataset, dict) else "unknown"
            metadata = dataset.get("_metadata", {}) if isinstance(
                dataset, dict) else {}
            dataset_type = metadata.get('type', 'unknown')
            
            # Get dataset name
            dataset_name = dataset.get("name", "Unnamed") if isinstance(
                dataset, dict) else "Unnamed"
            
            # Special handling for jailbreak-classification dataset
            is_jailbreak_classification = dataset_name == "jailbreak-classification" or "jailbreak-classification" in str(dataset)
            
            # Check if dataset uses custom keys
            has_custom_keys = 'input_key' in metadata
            input_key = metadata.get('input_key', 'input')
            output_key = metadata.get('output_key', 'output')
            has_output = metadata.get('has_output', True)

            # Auto-detect field names from the first example for all dataset types
            if examples and isinstance(examples[0], dict):
                available_fields = list(examples[0].keys())
                
                # Common input field names to look for
                input_candidates = ['prompt', 'input', 'question', 'text', 'instruction', 'query']
                output_candidates = ['response', 'output', 'answer', 'completion', 'target', 'label']
                
                # Find the best input field
                detected_input_key = None
                for candidate in input_candidates:
                    if candidate in available_fields:
                        detected_input_key = candidate
                        break
                
                # If no common input field found, use the first text-like field
                if not detected_input_key:
                    for field in available_fields:
                        if isinstance(examples[0].get(field), str) and examples[0].get(field).strip():
                            detected_input_key = field
                            break
                
                # Find the best output field
                detected_output_key = None
                for candidate in output_candidates:
                    if candidate in available_fields:
                        detected_output_key = candidate
                        break
                
                # Update keys if we found better ones (only if not already set by custom keys)
                if detected_input_key and not has_custom_keys:
                    input_key = detected_input_key
                    has_custom_keys = True
                if detected_output_key and not has_custom_keys:
                    output_key = detected_output_key
                    has_output = True
                elif not detected_output_key and not has_custom_keys:
                    has_output = False

            # Display basic dataset information
            total_examples = len(examples)
            features = []
            
            # Extract features from first example if available
            if total_examples > 0 and isinstance(examples[0], dict):
                features = list(examples[0].keys())
            
            self.console.print("\n[bold cyan]Dataset Statistics:[/]")
            self.console.print(f"[cyan]Total Examples:[/] {total_examples}")
            self.console.print(f"[cyan]Features:[/] {', '.join(features[:10])}{'...' if len(features) > 10 else ''}")
            
            # Display dataset preview
            self.console.print("\n[bold cyan]Dataset Preview:[/]")
            
            # Create panel with dataset info
            self.console.print(Panel.fit(
                f"[bold]Dataset: [cyan]{dataset_name}[/]\n"
                f"[bold]Format Type: [cyan]{format_type}[/]\n"
                f"[bold]Dataset Type: [cyan]{dataset_type}[/]\n"
                f"[bold]Total Examples: [cyan]{total_examples}[/]",
                title="[bold green]Dataset Information[/]",
                border_style="green"
            ))

            # Display custom key information if applicable
            if has_custom_keys:
                key_info = f"[bold]Input Key: [cyan]{input_key}[/]"
                if has_output:
                    key_info += f"\n[bold]Output Key: [cyan]{output_key}[/]"
                else:
                    key_info += "\n[bold]Output: [yellow]None (Input-only dataset)[/]"

                self.console.print(Panel.fit(
                    key_info,
                    title="[bold blue]Field Mapping[/]",
                    border_style="blue"
                ))

            # Create preview table based on format type or jailbreak classification
            preview_table = Table(
                title="Example Preview",
                show_header=True,
                header_style="bold magenta",
                border_style="blue"
            )

            # Add columns based on format type or jailbreak classification
            preview_table.add_column("Example #")
            
            if is_jailbreak_classification:
                preview_table.add_column("Input")
                preview_table.add_column("Type")
            else:
                preview_table.add_column("Input")
                
                if format_type == "standard":
                    if has_output:
                        preview_table.add_column("Output")
                elif format_type == "adversarial":
                    preview_table.add_column("Output")
                    preview_table.add_column("Category")
                elif format_type == "evaluation":
                    preview_table.add_column("Reference Outputs")
                elif has_output:  # For any other format type including unknown, add output if detected
                    preview_table.add_column("Output")

            # Add rows to the table
            max_preview = min(5, len(examples))
            for i in range(max_preview):
                example = examples[i]

                # Truncate long text
                def truncate(text, max_len=50):
                    text = str(text)
                    return text[:max_len] + "..." if len(text) > max_len else text

                # Get input text based on dataset type
                if is_jailbreak_classification:
                    input_text = truncate(example.get("prompt", example.get("input", "")))
                    example_type = example.get("type", "")
                    row = [str(i+1), input_text, example_type]
                else:
                    # Standard input handling
                    input_text = truncate(example.get(input_key, example.get("input", "")))
                    
                    # Build row based on format type
                    row = [str(i+1), input_text]
                    
                    if format_type == "standard":
                        if has_output:
                            row.append(truncate(example.get(output_key, example.get("output", ""))))
                    elif format_type == "adversarial":
                        row.append(truncate(example.get("output", "")))
                        category = example.get("metadata", {}).get("category", "")
                        row.append(category)
                    elif format_type == "evaluation":
                        reference_outputs = example.get("reference_outputs", [])
                        if reference_outputs:
                            row.append(truncate(", ".join(str(r)
                                       for r in reference_outputs)))
                        else:
                            row.append(
                                truncate(example.get("expected_output", "")))
                    elif has_output:
                        row.append(truncate(example.get(output_key, "")))

                preview_table.add_row(*row)

            # Show the preview table
            self.console.print(
                "\n[bold cyan]Preview of first few examples:[/]")
            self.console.print(preview_table)

            # Ask if user wants to view the complete dataset
            questions = [
                inquirer.List(
                    'view_option',
                    message="What would you like to do?",
                    choices=[
                        ('View Complete Dataset', 'view_complete'),
                        ('Back to Dataset List', 'back')
                    ]
                )
            ]

            answers = inquirer.prompt(questions)
            if answers and answers['view_option'] == 'view_complete':
                self._view_complete_dataset(examples, format_type, has_output, input_key, output_key, dataset_type)

            # Success message
            self.console.print(
                "\n[bold green]✓ Dataset successfully loaded![/]")
            self.console.print(
                f"[green]You can use this dataset for training or benchmarking.[/]")

        except Exception as e:
            self.console.print(
                f"[red]Error generating dataset preview: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())

    def _view_complete_dataset(self, examples, format_type, has_output, input_key, output_key, dataset_type):
        # Create a table for the complete dataset
        from rich.table import Table
        from rich.console import Console

        console = Console()

        complete_table = Table(
            title="Complete Dataset",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )

        # Add columns based on format type
        complete_table.add_column("Example #")
        complete_table.add_column("Input")

        if format_type == "standard":
            if has_output:
                complete_table.add_column("Output")
        elif format_type == "adversarial":
            complete_table.add_column("Output")
            complete_table.add_column("Category")
        elif format_type == "evaluation":
            complete_table.add_column("Reference Outputs")
        elif has_output:  # For any other format type including unknown, add output if detected
            complete_table.add_column("Output")

        # Add rows to the table
        for i, example in enumerate(examples):
            # Truncate long text
            def truncate(text, max_len=50):
                text = str(text)
                return text[:max_len] + "..." if len(text) > max_len else text

            # Get input text using the detected input key
            input_text = truncate(example.get(input_key, example.get("input", "")))

            # Build row based on format type
            row = [str(i+1), input_text]

            if format_type == "standard":
                if has_output:
                    row.append(truncate(example.get(output_key, example.get("output", ""))))
            elif format_type == "adversarial":
                row.append(truncate(example.get("output", "")))
                category = example.get("metadata", {}).get("category", "")
                row.append(category)
            elif format_type == "evaluation":
                reference_outputs = example.get("reference_outputs", [])
                if reference_outputs:
                    row.append(truncate(", ".join(str(r)
                               for r in reference_outputs)))
                else:
                    row.append(
                        truncate(example.get("expected_output", "")))
            elif has_output:
                row.append(truncate(example.get(output_key, "")))

            complete_table.add_row(*row)

        # Show the complete table
        console.print(
            "\n[bold cyan]Complete Dataset:[/]")
        console.print(complete_table)

    def format_dataset(self) -> None:
        """Format a raw dataset for training with interactive key selection"""
        try:
            raw_datasets = []

            # Get datasets from database
            db_datasets = self.db.list_datasets("raw")
            for dataset_name in db_datasets:
                dataset = self.db.get_raw_dataset(dataset_name)
                if dataset:
                    raw_datasets.append(dataset)

            # Check if we found any datasets in the database
            if not raw_datasets:
                self.console.print(
                    "[yellow]No datasets found in database, checking other sources...[/]")

            # Also check LanceDB for datasets
            if self.lance_db:
                try:
                    # Try to get all tables that start with raw_dataset_
                    try:
                        tables = self.lance_db.table_names()
                    except AttributeError:
                        try:
                            tables = self.lance_db.list_tables()
                        except:
                            tables = []

                    # Filter for raw dataset tables
                    raw_dataset_tables = [
                        t for t in tables if t.startswith('raw_dataset_')]

                    for table_name in raw_dataset_tables:
                        try:
                            # Open the table and get some data
                            table = self.lance_db.open_table(table_name)
                            # Get a sample of data (limit to 1000 rows)
                            try:
                                # First try with limit parameter (newer LanceDB versions)
                                df = table.to_pandas(limit=1000)
                            except TypeError:
                                try:
                                    # Fallback for older LanceDB versions without limit parameter
                                    df = table.to_pandas()
                                    # Manually limit rows after fetching
                                    if len(df) > 1000:
                                        df = df.head(1000)
                                except Exception as e2:
                                    self.console.print(
                                        f"[yellow]Warning: Could not load dataset from LanceDB table {table_name}: {str(e2)}[/]")
                                    continue

                            # Convert to dataset format
                            dataset_name = table_name.replace(
                                'raw_dataset_', '')
                            dataset = {
                                'name': f"lancedb_{dataset_name}",
                                'source': 'lancedb',
                                'examples': df.to_dict('records'),
                                '_metadata': {
                                    'table_name': table_name,
                                    'source': 'lancedb'
                                }
                            }

                            # Check if this dataset is already in our list
                            if not any(d.get('name') == dataset['name'] for d in raw_datasets if isinstance(d, dict)):
                                raw_datasets.append(dataset)
                        except Exception as e:
                            self.console.print(
                                f"[yellow]Warning: Could not load dataset from LanceDB table {table_name}: {str(e)}[/]")
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning: Error checking LanceDB for datasets: {str(e)}[/]")

            # Get datasets from cache directory
            cache_dir = Path.home() / "dravik" / "data" / "cache"
            if cache_dir.exists():
                for file_path in cache_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            dataset = json.load(f)
                            if isinstance(dataset, dict):
                                dataset['name'] = file_path.stem
                                dataset['source'] = str(file_path)
                                # Check if this dataset is already in our list
                                if not any(d.get('name') == dataset['name'] for d in raw_datasets if isinstance(d, dict)):
                                    raw_datasets.append(dataset)
                    except Exception as e:
                        self.console.print(
                            f"[yellow]Warning: Could not load {file_path}: {str(e)}[/]")

            # Get datasets from raw directory
            data_dir = Path.home() / "dravik" / "data" / "datasets" / "raw"
            if data_dir.exists():
                for file_path in data_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            dataset = json.load(f)
                            if isinstance(dataset, dict):
                                dataset['source'] = str(file_path)
                                # Check if this dataset is already in our list
                                if not any(d.get('name') == dataset.get('name') for d in raw_datasets if isinstance(d, dict)):
                                    raw_datasets.append(dataset)
                            elif isinstance(dataset, list):
                                # Convert list to dict format
                                dataset_dict = {
                                    'name': file_path.stem,
                                    'source': str(file_path),
                                    'examples': dataset
                                }
                                # Check if this dataset is already in our list
                                if not any(d.get('name') == dataset_dict['name'] for d in raw_datasets if isinstance(d, dict)):
                                    raw_datasets.append(dataset_dict)
                    except Exception as e:
                        self.console.print(
                            f"[yellow]Warning: Could not load {file_path}: {str(e)}[/]")

            if not raw_datasets:
                self.console.print(
                    "[yellow]No raw datasets found. Please download or import a dataset first.[/]")
                return

            # Display available datasets
            self.console.print("\n[bold cyan]Available Raw Datasets:[/]")
            for i, dataset in enumerate(raw_datasets, 1):
                if isinstance(dataset, dict):
                    name = dataset.get('name', f'Dataset {i}')
                    source = dataset.get('source', 'unknown')
                    examples = len(dataset.get('examples', [])) if isinstance(
                        dataset.get('examples'), list) else 'unknown'
                    self.console.print(
                        f"{i}. {name} (Source: {source}, Examples: {examples})")
                else:
                    self.console.print(f"{i}. Unknown format dataset")

            # Select dataset
            questions = [
                inquirer.List(
                    'dataset_index',
                    message="Select a dataset to format",
                    choices=[(f"{i}. {d.get('name', f'Dataset {i}') if isinstance(d, dict) else 'Unknown format dataset'}", i-1)
                             for i, d in enumerate(raw_datasets, 1)] + [("Cancel", None)]
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers or answers['dataset_index'] is None:
                return

            selected_dataset = raw_datasets[answers['dataset_index']]

            # Get format type
            format_type = questionary.select(
                "Select format type:",
                choices=[
                    {
                        'name': 'Standard Training Format',
                        'value': 'standard'
                    },
                    {
                        'name': 'Adversarial Training Format',
                        'value': 'adversarial'
                    },
                    {
                        'name': 'Evaluation Format',
                        'value': 'evaluation'
                    }
                ]
            ).ask()

            if not format_type:
                return

            # Process the dataset
            with self.console.status("[bold green]Formatting dataset...") as status:
                # Extract examples from the dataset
                examples = []
                if isinstance(selected_dataset, dict):
                    if 'examples' in selected_dataset:
                        examples = selected_dataset['examples']
                    elif 'data' in selected_dataset:
                        examples = selected_dataset['data']
                elif isinstance(selected_dataset, list):
                    examples = selected_dataset

                if not examples:
                    self.console.print(
                        "[red]Error: No examples found in dataset[/]")
                    return

                # Show a sample to help user identify keys
                if len(examples) > 0 and isinstance(examples[0], dict):
                    sample_example = examples[0]
                    self.console.print(
                        "\n[bold cyan]Sample Example Structure:[/]")
                    for key, value in sample_example.items():
                        value_preview = str(value)
                        if len(value_preview) > 50:
                            value_preview = value_preview[:47] + "..."
                        self.console.print(
                            f"  [green]{key}[/]: {value_preview}")

                    # Interactive key selection for input
                    available_keys = list(sample_example.keys())

                    # Allow user to select input key
                    input_key_question = [
                        inquirer.List(
                            'input_key',
                            message="Select which field contains the input/prompt:",
                            choices=[(k, k) for k in available_keys]
                        )
                    ]

                    input_key_answer = inquirer.prompt(input_key_question)
                    if not input_key_answer:
                        return

                    input_key = input_key_answer['input_key']

                    # Ask if dataset has output/response
                    has_output = inquirer.confirm(
                        message="Does this dataset include output/response fields?",
                        default=True
                    )

                    output_key = None
                    if has_output:
                        # Allow user to select output key
                        output_key_question = [
                            inquirer.List(
                                'output_key',
                                message="Select which field contains the output/response:",
                                choices=[(k, k)
                                         for k in available_keys if k != input_key]
                            )
                        ]

                        output_key_answer = inquirer.prompt(
                            output_key_question)
                        if not output_key_answer:
                            return

                        output_key = output_key_answer['output_key']

                # Format examples based on type and selected keys
                formatted_examples = []
                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]Formatting examples...", total=len(examples))

                    for example in examples:
                        try:
                            # Special handling for jailbreak datasets that might contain strings
                            if format_type == 'adversarial' and isinstance(example, str):
                                # For string examples in adversarial format, use directly
                                formatted = self._format_adversarial_example(
                                    example)
                            elif format_type == 'standard':
                                if isinstance(example, dict) and 'input_key' in locals() and input_key in example:
                                    # Use the user-selected keys
                                    formatted = self._format_standard_example_with_keys(
                                        example,
                                        input_key=input_key,
                                        output_key=output_key
                                    )
                                else:
                                    # Fall back to default formatting
                                    formatted = self._format_standard_example(
                                        example)
                            elif format_type == 'adversarial':
                                if isinstance(example, dict) and 'input_key' in locals() and input_key in example:
                                    # Use user-selected keys for adversarial examples
                                    formatted = self._format_adversarial_example_with_keys(
                                        example,
                                        input_key=input_key,
                                        output_key=output_key
                                    )
                                else:
                                    formatted = self._format_adversarial_example(
                                        example)
                            else:  # evaluation
                                if isinstance(example, dict) and 'input_key' in locals() and input_key in example:
                                    # Use user-selected keys for evaluation examples
                                    formatted = self._format_evaluation_example_with_keys(
                                        example,
                                        input_key=input_key,
                                        output_key=output_key
                                    )
                                else:
                                    formatted = self._format_evaluation_example(
                                        example)

                            if formatted:
                                formatted_examples.append(formatted)

                            progress.update(task, advance=1)
                        except Exception as e:
                            self.console.print(
                                f"[yellow]Warning: Failed to format example: {str(e)}[/]")
                            progress.update(task, advance=1)
                            continue

                if not formatted_examples:
                    self.console.print(
                        "[red]Error: No examples were successfully formatted[/]")
                    return

                # Create formatted dataset with metadata
                dataset_name = selected_dataset.get('name', 'dataset') if isinstance(
                    selected_dataset, dict) else 'dataset'
                formatted_dataset = {
                    'name': f"{dataset_name}_formatted",
                    'format_type': format_type,
                    'examples': formatted_examples,
                    '_metadata': {
                        'original_name': dataset_name,
                        'original_source': selected_dataset.get('source', 'unknown') if isinstance(selected_dataset, dict) else 'unknown',
                        'format_type': format_type,
                        'created_at': datetime.now().isoformat(),
                        'example_count': len(formatted_examples),
                        'original_example_count': len(examples)
                    }
                }

                # If custom keys were used, add them to metadata
                if 'input_key' in locals():
                    formatted_dataset['_metadata']['input_key'] = input_key
                    if 'output_key' in locals() and output_key:
                        formatted_dataset['_metadata']['output_key'] = output_key
                    formatted_dataset['_metadata']['has_output'] = has_output

                # Validate the formatted dataset
                if not self._validate_formatted_dataset(formatted_dataset):
                    return

                # Save to database
                try:
                    # Save to structured datasets table
                    success = self.db.save_structured_dataset(
                        formatted_dataset['name'],
                        formatted_dataset
                    )

                    if success:
                        self.console.print(
                            f"[green]Successfully formatted and saved dataset: {formatted_dataset['name']}[/]")
                        self.console.print(
                            f"[green]Total examples: {len(formatted_examples)}[/]")

                        # Save to LanceDB for efficient access
                        self._save_formatted_dataset_to_lancedb(
                            formatted_dataset)

                        # Show preview of formatted dataset
                        self._show_dataset_preview(formatted_dataset)
                    else:
                        self.console.print(
                            "[red]Failed to save formatted dataset to database[/]")

                except Exception as e:
                    self.console.print(
                        f"[red]Error saving formatted dataset: {str(e)}[/]")

        except Exception as e:
            self.console.print(f"[red]Error formatting dataset: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())

    def _save_formatted_dataset_to_lancedb(self, dataset):
        """Save formatted dataset to LanceDB with unique table names"""
        try:
            if not self.lance_db:
                self.console.print(
                    "[yellow]Warning: LanceDB not available, skipping LanceDB save[/]")
                return False

            # Create DataFrame from examples
            examples = dataset.get('examples', [])
            if not examples:
                self.console.print(
                    "[yellow]Warning: No examples to save to LanceDB[/]")
                return False

            # Add unique ID to each example
            for example in examples:
                if 'dataset_id' not in example:
                    example['dataset_id'] = dataset.get('name', 'unknown')

            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame(examples)

            # Always create a unique table name instead of trying to use a shared table
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            unique_table_name = f"structured_{dataset.get('name', 'dataset')}_{timestamp}_{unique_id}"

            try:
                # Create table with unique name
                self.lance_db.create_table(unique_table_name, data=df)
                self.console.print(
                    f"[green]Created table for formatted dataset: {unique_table_name}[/]")
                return True
            except Exception as e:
                self.console.print(
                    f"[red]Error creating table for formatted dataset: {str(e)}[/]")
                return False

        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Error saving formatted dataset to LanceDB: {str(e)}[/]")
            return False

    def _format_standard_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single example in standard training format"""
        # Handle string examples
        if isinstance(example, str):
            # Use the string as input and generate a simple output
            input_text = example
            output_text = "This is a response to your query."

            return {
                'input': input_text,
                'output': output_text,
                'metadata': {
                    'original_id': str(uuid.uuid4()),
                    'source': 'unknown',
                    'format_type': 'standard',
                    'original_fields': ['text']
                }
            }

        # Extract input/output with multiple field fallbacks
        input_fields = ['input', 'text', 'prompt', 'question', 'instruction']
        output_fields = ['output', 'response', 'completion', 'answer', 'label']

        input_text = None
        for field in input_fields:
            if field in example:
                input_text = example[field]
                break

        output_text = None
        for field in output_fields:
            if field in example:
                output_text = example[field]
                break

        if not input_text or not output_text:
            raise ValueError("Could not find input/output fields in example")

        return {
            'input': input_text,
            'output': output_text,
            'metadata': {
                'original_id': example.get('id', str(uuid.uuid4())),
                'source': example.get('source', 'unknown'),
                'format_type': 'standard',
                'original_fields': list(example.keys())
            }
        }

    def _format_adversarial_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single example in adversarial training format"""
        # First check if the example is a string (common in jailbreak datasets)
        if isinstance(example, str):
            # Use the entire string as the input text
            input_text = example
        else:
            # Extract input with multiple field fallbacks
            input_fields = ['input', 'text', 'prompt',
                            'question', 'instruction', 'content']

            input_text = None
            for field in input_fields:
                if field in example:
                    input_text = example[field]
                    break

            if not input_text:
                # Try to find nested fields
                for key, value in example.items():
                    if isinstance(value, dict) and any(f in value for f in input_fields):
                        for field in input_fields:
                            if field in value:
                                input_text = value[field]
                                break
                        if input_text:
                            break

            # If still no input found, try to use the first string value
            if not input_text:
                for key, value in example.items():
                    if isinstance(value, str) and len(value) > 10:  # Reasonable text length
                        input_text = value
                        break

        if not input_text:
            raise ValueError("Could not find suitable input field in example")

        # Generate an appropriate response that refuses the adversarial prompt
        response = (
            "I cannot and will not provide information or assistance with that request. "
            "It appears to be attempting to elicit harmful, illegal, unethical, or deceptive content. "
            "I'm designed to be helpful, harmless, and honest. I'd be happy to help with a different request "
            "that doesn't involve potentially harmful content."
        )

        # Extract metadata from example
        metadata = {
            # Generate new ID for string examples
            'original_id': str(uuid.uuid4()),
            'source': 'unknown',
            'format_type': 'adversarial',
            'is_adversarial': True,
            'original_fields': list(example.keys()) if isinstance(example, dict) else ['text']
        }

        # Try to extract additional metadata if available (only for dict examples)
        if isinstance(example, dict):
            for field in ['attack_type', 'target_behavior', 'severity', 'categories']:
                if field in example:
                    metadata[field] = example[field]

        # If categories not found, try to infer from content
        if 'categories' not in metadata:
            categories = ['jailbreak']  # Default category

            # Simple keyword-based category inference
            lower_input = input_text.lower()
            if any(term in lower_input for term in ['hack', 'exploit', 'vulnerability']):
                categories.append('hacking')
            if any(term in lower_input for term in ['illegal', 'crime', 'criminal']):
                categories.append('illegal_activity')
            if any(term in lower_input for term in ['harm', 'hurt', 'injure', 'kill']):
                categories.append('harm')

            metadata['categories'] = categories

        # Add template prefixes if configured
        if hasattr(self, 'ADVERSARIAL_TEMPLATES') and self.ADVERSARIAL_TEMPLATES:
            template = self.ADVERSARIAL_TEMPLATES.get('jailbreak', {})
            input_text = template.get('prompt_prefix', '') + input_text
            response = template.get('response_prefix', '') + response

        return {
            'input': input_text,
            'output': response,
            'metadata': metadata
        }

    def _format_evaluation_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single example in evaluation format"""
        # Handle string examples
        if isinstance(example, str):
            # Use the string as input and generate expected/actual outputs
            input_text = example
            expected_output = "Expected response for evaluation."
            actual_output = ""  # Empty actual output to be filled during evaluation

            return {
                'input': input_text,
                'expected_output': expected_output,
                'actual_output': actual_output,
                'metadata': {
                    'original_id': str(uuid.uuid4()),
                    'source': 'unknown',
                    'format_type': 'evaluation',
                    'metrics': {},
                    'score': 0.0,
                    'original_fields': ['text']
                }
            }

        # Get input text
        input_text = None
        for field in ['input', 'text', 'prompt', 'question']:
            if field in example:
                input_text = example[field]
                break

        if not input_text:
            raise ValueError("Could not find input field in example")

        # Get expected and actual outputs
        expected_output = example.get('expected_output',
                                      example.get('reference',
                                                  example.get('ground_truth')))

        actual_output = example.get('actual_output',
                                    example.get('response',
                                                example.get('prediction')))

        if not expected_output:
            raise ValueError("Could not find expected output field in example")

        return {
            'input': input_text,
            'expected_output': expected_output,
            'actual_output': actual_output or '',  # Allow empty actual output
            'metadata': {
                'original_id': example.get('id', str(uuid.uuid4())),
                'source': example.get('source', 'unknown'),
                'format_type': 'evaluation',
                'metrics': example.get('metrics', {}),
                'score': example.get('score', 0.0),
                'original_fields': list(example.keys())
            }
        }

    def _validate_formatted_dataset(self, dataset: Dict[str, Any]) -> bool:
        """Validate a formatted dataset"""
        try:
            # Check required top-level fields
            if not dataset.get('name'):
                self.console.print("[red]Error: Dataset name is required[/]")
                return False

            if not dataset.get('examples'):
                self.console.print(
                    "[red]Error: Dataset must contain examples[/]")
                return False

            if not dataset.get('format_type'):
                self.console.print("[red]Error: Format type is required[/]")
                return False

            # Validate examples based on format type
            format_type = dataset['format_type']
            examples = dataset['examples']

            # Check if this is an input-only dataset (no outputs)
            has_output = dataset.get('_metadata', {}).get('has_output', True)

            for i, example in enumerate(examples):
                try:
                    # Check common required fields
                    if not example.get('metadata'):
                        self.console.print(
                            f"[red]Error: Example {i} missing metadata[/]")
                        return False

                    # Format-specific validation
                    if format_type == 'standard':
                        if not example.get('input'):
                            self.console.print(
                                f"[red]Error: Example {i} missing input field[/]")
                            return False

                        # Only validate output if the dataset is supposed to have outputs
                        if has_output and not example.get('output'):
                            self.console.print(
                                f"[yellow]Warning: Example {i} missing output field but dataset has_output=true[/]")

                    elif format_type == 'adversarial':
                        if not example.get('input'):
                            self.console.print(
                                f"[red]Error: Example {i} missing input field[/]")
                            return False

                        # Adversarial examples always need some output
                        if not example.get('output'):
                            self.console.print(
                                f"[yellow]Warning: Example {i} missing output field in adversarial dataset[/]")

                    elif format_type == 'evaluation':
                        if not example.get('input'):
                            self.console.print(
                                f"[red]Error: Example {i} missing input field[/]")
                            return False

                        # For evaluation, we need at least one reference output
                        if has_output and not example.get('reference_outputs') and not example.get('expected_output'):
                            self.console.print(
                                f"[yellow]Warning: Example {i} missing reference outputs for evaluation[/]")

                except Exception as e:
                    self.console.print(
                        f"[red]Error validating example {i}: {str(e)}[/]")
                    return False

            return True
        except Exception as e:
            self.console.print(f"[red]Error validating dataset: {str(e)}[/]")
            return False

    def format_for_adversarial(self, dataset_id: str, format_type: str = "jailbreak") -> Optional[str]:
        """Format a dataset for adversarial training"""
        try:
            # Get dataset info
            dataset_info = self.db.get_raw_dataset(dataset_id)

            if not dataset_info:
                self.console.print(f"[red]Dataset {dataset_id} not found[/]")
                return None

            # Load the dataset
            with open(dataset_info['file_path'], 'r') as f:
                dataset = json.load(f)

            # Get template
            template = self.ADVERSARIAL_TEMPLATES.get(format_type)
            if not template:
                self.console.print(
                    f"[red]Unknown format type: {format_type}[/]")
                return None

            # Format the dataset
            formatted_data = []
            for item in dataset['examples']:
                # Extract text content
                text = item.get('text', item.get(
                    'content', item.get('prompt', '')))

                # Create adversarial example
                formatted_item = {
                    "original_text": text,
                    "prompt": f"{template['prompt_prefix']}{text}",
                    "response": f"{template['response_prefix']}{text}",
                    # You might want to add logic to determine category
                    "category": template['categories'][0],
                    "metadata": {
                        "source": dataset_info.get('source', 'unknown'),
                        "format_type": format_type
                    }
                }
                formatted_data.append(formatted_item)

            # Generate version ID
            version_id = f"{dataset_id}_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Save formatted dataset
            output_path = self.processed_dir / f"{version_id}.json"
            with open(output_path, 'w') as f:
                json.dump(formatted_data, f, indent=2)

            # Store in database
            formatted_info = {
                "id": version_id,
                "original_id": dataset_id,
                "format_type": "adversarial",
                "format_subtype": format_type,
                "file_path": str(output_path),
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "template": template,
                    "sample_count": len(formatted_data)
                }
            }

            self.db.save_formatted_dataset(formatted_info)

            # Store in LanceDB for faster access
            if self.lance_db:
                table_name = f"dataset_adv_{version_id}"
                df = pd.DataFrame(formatted_data)
                self.lance_db.create_table(table_name, data=df)

            self.console.print(
                f"[green]✓ Successfully formatted dataset for adversarial training[/]")
            return version_id

        except Exception as e:
            self.console.print(f"[red]Error formatting dataset: {str(e)}[/]")
            return None

    def select_dataset_for_training(self) -> Optional[Dict[str, Any]]:
        """
        Select a dataset specifically for training purposes

        Returns:
            Selected dataset info or None if cancelled
        """
        # Get list of datasets suitable for training - include both formatted and raw datasets
        formatted_datasets = self._get_formatted_datasets()
        raw_datasets = self._get_benchmark_datasets()  # This includes raw datasets too

        # Filter out any duplicates (by ID)
        dataset_ids = set()
        datasets = []

        # Add formatted datasets first (prioritize them)
        for dataset in formatted_datasets:
            dataset_ids.add(dataset['id'])
            datasets.append(dataset)

        # Add raw datasets that aren't already included
        for dataset in raw_datasets:
            if dataset['id'] not in dataset_ids:
                datasets.append(dataset)

        if not datasets:
            self.console.print(
                "[yellow]No datasets available for training.[/]")

            # Ask if user wants to format a dataset now
            if inquirer.confirm("Would you like to format a dataset for training now?", default=True):
                self.format_dataset()
                # Try getting datasets again
                formatted_datasets = self._get_formatted_datasets()
                raw_datasets = self._get_benchmark_datasets()

                # Combine datasets
                dataset_ids = set()
                datasets = []

                for dataset in formatted_datasets:
                    dataset_ids.add(dataset['id'])
                    datasets.append(dataset)

                for dataset in raw_datasets:
                    if dataset['id'] not in dataset_ids:
                        datasets.append(dataset)

                if not datasets:
                    return None

        # Display datasets with training-specific info
        selected = self.ui.display_dataset_selection(datasets)

        if selected:
            # Load full dataset info with appropriate type
            dataset_type = selected.get('type')
            dataset_info = self._load_dataset_info(
                selected['id'], dataset_type)

            if dataset_info:
                self.console.print(
                    f"[green]Selected dataset '{selected['name']}' for training (Type: {dataset_type})[/]")
                return {**selected, **dataset_info}
            else:
                self.console.print(
                    f"[yellow]Could not load complete information for dataset '{selected['name']}'[/]")

        return None

    def select_dataset_for_benchmarking(self) -> Optional[Dict[str, Any]]:
        """
        Select a dataset specifically for benchmarking purposes

        Returns:
            Selected dataset info or None if cancelled
        """
        # Get list of datasets suitable for benchmarking
        datasets = self._get_benchmark_datasets()

        if not datasets:
            self.console.print(
                "[yellow]No datasets available for benchmarking.[/]")

            # Ask if user wants to download or format a dataset now
            questions = [
                inquirer.List(
                    'action',
                    message="Would you like to:",
                    choices=[
                        ('Download a new dataset', 'download'),
                        ('Format an existing dataset', 'format'),
                        ('Cancel', 'cancel')
                    ]
                )
            ]

            answers = inquirer.prompt(questions)
            if answers and answers['action'] != 'cancel':
                if answers['action'] == 'download':
                    self.download_dataset()
                else:
                    self.format_dataset()
                # Try getting datasets again
                datasets = self._get_benchmark_datasets()
                if not datasets:
                    return None
            else:
                return None

        # Display datasets with benchmark-specific info
        selected = self.ui.display_dataset_selection(datasets)

        if selected:
            # Load full dataset info with appropriate type
            dataset_type = selected.get('type')
            
            # For HuggingFace datasets, pass the dataset name as well
            if dataset_type == 'huggingface':
                dataset_info = self._load_dataset_info(
                    selected['id'], dataset_type, dataset_name=selected['name'])
            else:
                dataset_info = self._load_dataset_info(
                    selected['id'], dataset_type)

            if dataset_info:
                self.console.print(
                    f"[green]Selected dataset '{selected['name']}' for benchmarking (Type: {dataset_type})[/]")
                # Merge the dataset metadata with the content
                return {**selected, **dataset_info}
            else:
                self.console.print(
                    f"[yellow]Could not load complete information for dataset '{selected['name']}'[/]")

        return None

    def _get_formatted_datasets(self) -> List[Dict[str, Any]]:
        """Get list of formatted datasets"""
        try:
            # Get list of formatted dataset names
            dataset_names = self.db.list_datasets("structured")

            formatted_datasets = []
            for name in dataset_names:
                # Get full dataset content
                dataset = self.db.get_dataset_content("structured", name)
                if dataset:
                    formatted_datasets.append({
                        'id': name,
                        'name': name,
                        'info': dataset.get('_metadata', {}),
                        'format': dataset.get('format_type', 'standard'),
                        'created_at': dataset.get('created_at', 'Unknown'),
                        'example_count': len(dataset.get('examples', []))
                    })

            return formatted_datasets
        except Exception as e:
            self.console.print(
                f"[yellow]Error getting formatted datasets: {str(e)}[/]")
            return []

    def _get_benchmark_datasets(self) -> List[Dict[str, Any]]:
        """Get list of datasets suitable for benchmarking"""
        try:
            # Get datasets from all sources
            raw_datasets = self.db.list_datasets("raw")
            structured_datasets = self.db.list_datasets("structured")
            poc_datasets = self.db.list_datasets("poc")

            benchmark_datasets = []

            # Process raw datasets from DB
            for name in raw_datasets:
                dataset = self.db.get_dataset_content("raw", name)
                if dataset:
                    benchmark_datasets.append({
                        'id': name,
                        'name': name,
                        'type': 'raw',
                        'created_at': dataset.get('_metadata', {}).get('download_date', 'unknown'),
                        'example_count': len(dataset.get('examples', [])) if isinstance(dataset.get('examples'), list) else 'unknown',
                        'format': 'raw'
                    })

            # Process structured datasets
            for name in structured_datasets:
                dataset = self.db.get_dataset_content("structured", name)
                if dataset:
                    benchmark_datasets.append({
                        'id': name,
                        'name': name,
                        'type': 'structured',
                        'created_at': dataset.get('_metadata', {}).get('created_at', 'unknown'),
                        'example_count': len(dataset.get('examples', [])) if isinstance(dataset.get('examples'), list) else 'unknown',
                        'format': dataset.get('format_type', 'standard')
                    })

            # Process POC datasets
            for name in poc_datasets:
                dataset = self.db.get_dataset_content("poc", name)
                if dataset:
                    benchmark_datasets.append({
                        'id': name,
                        'name': name,
                        'type': 'poc',
                        'created_at': dataset.get('_metadata', {}).get('created_at', 'unknown'),
                        'example_count': len(dataset.get('examples', [])) if isinstance(dataset.get('examples'), list) else 'unknown',
                        'format': 'poc'
                    })

            # Add HuggingFace datasets from the dedicated table
            try:
                hf_datasets_info = self.db.get_huggingface_datasets_info()
                for hf_dataset in hf_datasets_info:
                    # Check if this dataset is already in our list (avoid duplicates)
                    if not any(d['name'] == hf_dataset['name'] and d['type'] == 'huggingface' for d in benchmark_datasets):
                        benchmark_datasets.append(hf_dataset)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load HuggingFace datasets: {str(e)}[/]")

            # Get datasets from LanceDB registry
            if self.lance_db:
                try:
                    # Check if registry exists
                    try:
                        registry = self.lance_db.open_table("dataset_registry")

                        # Query registry for datasets
                        registry_df = registry.to_pandas()

                        # Include datasets of all types, not just raw
                        for _, row in registry_df.iterrows():
                            # Make sure this dataset isn't already in our list
                            dataset_name = row['dataset_name']
                            dataset_type = row['dataset_type']

                            # Add with unique identifier combining name and type
                            unique_id = f"{dataset_name}_{dataset_type}"
                            if not any(d['name'] == dataset_name and d['type'] == dataset_type for d in benchmark_datasets):
                                # Get dataset info from the actual data table
                                try:
                                    table = self.lance_db.open_table(
                                        row['table_name'])

                                    # Sample the table to get example count
                                    # Get just a few rows to check structure
                                    df_sample = table.to_pandas(limit=5)

                                    # Try to get total count by using the count API if available
                                    try:
                                        example_count = table.count()
                                    except (AttributeError, NotImplementedError):
                                        try:
                                            example_count = len(
                                                table.to_pandas())
                                        except:
                                            example_count = "unknown"

                                    benchmark_datasets.append({
                                        'id': row['dataset_id'],
                                        'name': dataset_name,
                                        'type': dataset_type,
                                        'created_at': row['created_at'],
                                        'example_count': example_count,
                                        'format': row.get('format', dataset_type),
                                        'source': 'lancedb',
                                        'table_name': row['table_name']
                                    })
                                except Exception as e:
                                    self.console.print(
                                        f"[yellow]Warning: Could not load LanceDB dataset {row['table_name']}: {str(e)}[/]")
                    except Exception as e:
                        # Registry doesn't exist or other error
                        pass

                    # Also directly check for dataset tables with any prefix
                    try:
                        tables = self.lance_db.table_names()

                        # Look for all dataset types, not just raw
                        dataset_prefixes = {
                            'raw_dataset_': 'raw',
                            'structured_': 'structured',
                            'formatted_': 'structured',
                            'adversarial_': 'adversarial',
                            'evaluation_': 'evaluation',
                            'poc_': 'poc'
                        }

                        for prefix, dataset_type in dataset_prefixes.items():
                            tables_with_prefix = [
                                t for t in tables if t.startswith(prefix)]

                            for table_name in tables_with_prefix:
                                # Extract dataset name from table name
                                # Format is prefix_NAME_TIMESTAMP_UUID
                                parts = table_name.split('_')
                                if len(parts) >= 3:
                                    # Skip prefix parts
                                    prefix_parts = prefix.split('_')
                                    prefix_len = len(
                                        prefix_parts) - 1 if prefix_parts[-1] == '' else len(prefix_parts)
                                    dataset_name = parts[prefix_len] if len(
                                        parts) > prefix_len else f"unknown_{table_name}"

                                    # Skip if already in our list (matching both name and type)
                                    if not any(d['name'] == dataset_name and d['type'] == dataset_type for d in benchmark_datasets):
                                        try:
                                            table = self.lance_db.open_table(
                                                table_name)

                                            # Try to get example count
                                            try:
                                                example_count = table.count()
                                            except (AttributeError, NotImplementedError):
                                                try:
                                                    example_count = len(
                                                        table.to_pandas())
                                                except:
                                                    example_count = "unknown"

                                            # Create unique id from table name
                                            unique_id = table_name

                                            # Create dataset entry
                                            benchmark_datasets.append({
                                                'id': unique_id,  # Use table name as ID
                                                'name': dataset_name,
                                                'type': dataset_type,
                                                'created_at': datetime.now().isoformat(),  # Use current time as fallback
                                                'example_count': example_count,
                                                'format': dataset_type,
                                                'source': 'lancedb',
                                                'table_name': table_name
                                            })
                                        except Exception as e:
                                            self.console.print(
                                                f"[yellow]Warning: Could not load LanceDB dataset {table_name}: {str(e)}[/]")
                    except Exception as e:
                        # Could not list tables
                        pass

                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning: Error checking LanceDB for datasets: {str(e)}[/]")

            # Sort by creation date (newest first)
            benchmark_datasets.sort(key=lambda x: x.get(
                'created_at', ''), reverse=True)

            return benchmark_datasets

        except Exception as e:
            self.console.print(
                f"[red]Error getting benchmark datasets: {str(e)}[/]")
            return []

    def _load_dataset_info(self, dataset_id: str, dataset_type: str = None, dataset_name: str = None) -> Optional[Dict[str, Any]]:
        """Load detailed dataset information

        Args:
            dataset_id: The ID of the dataset to load
            dataset_type: The type of dataset (raw, structured, poc, huggingface) or None to auto-detect
            dataset_name: The name of the dataset (used for HuggingFace datasets)

        Returns:
            Dataset information or None if not found
        """
        try:
            # Check if this is a LanceDB table ID (identified by table_name in the dataset metadata)
            if dataset_type == 'raw' and self.lance_db and dataset_id.startswith('raw_dataset_'):
                # This is likely a LanceDB table ID
                self.console.print(
                    f"[cyan]Loading raw dataset from LanceDB table: {dataset_id}[/]")

                try:
                    # Open the table
                    table = self.lance_db.open_table(dataset_id)

                    # Get dataset content from LanceDB
                    df = table.to_pandas()

                    if len(df) == 0:
                        self.console.print(
                            "[yellow]Warning: Dataset table is empty[/]")
                        return None

                    # Convert DataFrame to dataset format
                    dataset = {}

                    # Use DataFrame records as examples
                    examples = df.to_dict('records')

                    # Extract dataset name from the first example or table name
                    dataset_name = None
                    if len(examples) > 0 and '_dataset_name' in examples[0]:
                        dataset_name = examples[0]['_dataset_name']

                    if not dataset_name:
                        # Extract from table name
                        # Format is raw_dataset_NAME_TIMESTAMP_UUID
                        parts = dataset_id.split('_')
                        if len(parts) >= 3:
                            dataset_name = parts[2]
                        else:
                            dataset_name = 'unknown'

                    # Check if this is a jailbreak-classification dataset
                    is_jailbreak_classification = 'jailbreak-classification' in dataset_id or dataset_name == 'jailbreak-classification'

                    # Set dataset format
                    dataset['name'] = dataset_name
                    dataset['examples'] = examples
                    dataset['total_examples'] = len(examples)

                    # Extract features from example structure
                    if len(examples) > 0:
                        dataset['features'] = list(examples[0].keys())
                    else:
                        dataset['features'] = []

                    # Handle special case for jailbreak classification
                    if is_jailbreak_classification:
                        # Set specific metadata for jailbreak dataset
                        dataset['format_type'] = 'classification'
                        dataset['_metadata'] = {
                            'type': 'classification',
                            'source': 'lancedb',
                            'table_name': dataset_id,
                            'input_key': 'prompt',
                            'has_output': False
                        }
                    else:
                        # Default metadata
                        dataset['_metadata'] = {
                            'type': 'raw',
                            'source': 'lancedb',
                            'table_name': dataset_id
                        }

                    # Include metadata from other fields if available
                    if '_metadata' in df.columns:
                        try:
                            # Try to parse metadata from the first example
                            additional_metadata = json.loads(examples[0]['_metadata'])
                            if isinstance(additional_metadata, dict):
                                dataset['_metadata'].update(additional_metadata)
                        except (json.JSONDecodeError, TypeError, KeyError):
                            # Couldn't parse metadata, use as-is
                            pass

                    return dataset

                except Exception as e:
                    self.console.print(
                        f"[red]Error loading dataset from LanceDB: {str(e)}[/]")
                    import traceback
                    self.console.print(traceback.format_exc())
                    return None

            # If dataset_type is provided, use it directly
            if dataset_type:
                if dataset_type == 'huggingface':
                    # For HuggingFace datasets, use dataset_name if provided, otherwise try dataset_id
                    search_key = dataset_name if dataset_name else dataset_id
                    info = self.db.get_huggingface_dataset(search_key)
                    if info:
                        return info
                else:
                    info = self.db.get_dataset_content(dataset_type, dataset_id)
                    if info:
                        return info

            # Otherwise, try to load from all possible types
            for type_name in ["structured", "raw", "poc"]:
                info = self.db.get_dataset_content(type_name, dataset_id)
                if info:
                    return info

            # Also try HuggingFace datasets table with both dataset_id and dataset_name
            search_keys = [dataset_id]
            if dataset_name and dataset_name != dataset_id:
                search_keys.append(dataset_name)
            
            for search_key in search_keys:
                hf_info = self.db.get_huggingface_dataset(search_key)
                if hf_info:
                    return hf_info

            # If we reach here, the dataset wasn't found
            self.console.print(
                f"[yellow]Dataset {dataset_id} not found in any collection[/]")
            return None

        except Exception as e:
            self.console.print(f"[red]Error loading dataset info: {str(e)}[/]")
            return None

    def list_and_view_datasets(self) -> None:
        """List and view available datasets"""
        try:
            # Get all datasets from different sources
            raw_datasets = self.db.list_datasets("raw")
            structured_datasets = self.db.list_datasets("structured")
            poc_datasets = self.db.list_datasets("poc")
            
            # Get HuggingFace datasets
            huggingface_datasets = []
            try:
                huggingface_datasets = self.db.list_huggingface_datasets()
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load HuggingFace datasets: {e}[/]")

            if not any([raw_datasets, structured_datasets, poc_datasets, huggingface_datasets]):
                self.console.print("[yellow]No datasets found.[/]")
                return

            # Create a table for display
            from rich.table import Table
            table = Table(title="Available Datasets", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Examples", style="green")
            table.add_column("Created", style="blue")

            # Add raw datasets
            for name in raw_datasets:
                dataset = self.db.get_dataset_content("raw", name)
                if dataset:
                    example_count = len(dataset.get('examples', [])) if isinstance(
                        dataset.get('examples'), list) else 'unknown'
                    created_at = dataset.get('_metadata', {}).get(
                        'download_date', 'unknown')
                    # Store dataset type in metadata
                    if isinstance(dataset, dict) and '_metadata' in dataset:
                        dataset['_metadata']['type'] = 'raw'
                    table.add_row(name, "Raw", str(example_count), created_at)

            # Add structured datasets
            for name in structured_datasets:
                dataset = self.db.get_dataset_content("structured", name)
                if dataset:
                    example_count = len(dataset.get('examples', [])) if isinstance(
                        dataset.get('examples'), list) else 'unknown'
                    created_at = dataset.get('_metadata', {}).get(
                        'created_at', 'unknown')
                    # Store dataset type in metadata
                    if isinstance(dataset, dict) and '_metadata' in dataset:
                        dataset['_metadata']['type'] = 'structured'
                    table.add_row(name, "Structured", str(
                        example_count), created_at)

            # Add POC datasets
            for name in poc_datasets:
                dataset = self.db.get_dataset_content("poc", name)
                if dataset:
                    example_count = len(dataset.get('examples', [])) if isinstance(
                        dataset.get('examples'), list) else 'unknown'
                    created_at = dataset.get('_metadata', {}).get(
                        'created_at', 'unknown')
                    # Store dataset type in metadata
                    if isinstance(dataset, dict) and '_metadata' in dataset:
                        dataset['_metadata']['type'] = 'poc'
                    table.add_row(name, "POC", str(example_count), created_at)

            # Add HuggingFace datasets
            for name in huggingface_datasets:
                try:
                    dataset = self.db.get_huggingface_dataset(name)
                    if dataset:
                        # Get example count from the data
                        data = dataset.get('data', [])
                        example_count = len(data) if isinstance(data, list) else 'unknown'
                        created_at = dataset.get('_metadata', {}).get('created_at', 'unknown')
                        table.add_row(name, "HuggingFace", str(example_count), created_at)
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not load HuggingFace dataset {name}: {e}[/]")

            # Display the table
            self.console.print(table)

            # Ask if user wants to view a specific dataset
            all_datasets = [(name, "raw") for name in raw_datasets] + \
                [(name, "structured") for name in structured_datasets] + \
                [(name, "poc") for name in poc_datasets] + \
                [(name, "huggingface") for name in huggingface_datasets]

            if all_datasets:
                questions = [
                    inquirer.List(
                        'dataset_choice',
                        message="Select a dataset to view details",
                        choices=[(f"{name} ({type})", (name, type))
                                 for name, type in all_datasets] + [("Back", None)]
                    )
                ]

                answers = inquirer.prompt(questions)
                if answers and answers['dataset_choice']:
                    name, type = answers['dataset_choice']
                    if type == "huggingface":
                        dataset = self.db.get_huggingface_dataset(name)
                    else:
                        dataset = self.db.get_dataset_content(type, name)
                    if dataset:
                        self._show_dataset_preview(dataset)

        except Exception as e:
            self.console.print(f"[red]Error listing datasets: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())

    def export_dataset(self) -> None:
        """Export a dataset to JSON or CSV format"""
        try:
            # Get all available datasets
            raw_datasets = self.db.list_datasets("raw")
            structured_datasets = self.db.list_datasets("structured")
            poc_datasets = self.db.list_datasets("poc")
            
            # Get HuggingFace datasets
            huggingface_datasets = []
            try:
                huggingface_datasets = self.db.list_huggingface_datasets()
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load HuggingFace datasets: {e}[/]")

            if not any([raw_datasets, structured_datasets, poc_datasets, huggingface_datasets]):
                self.console.print(
                    "[yellow]No datasets available to export.[/]")
                return

            # Create dataset choices
            all_datasets = [(name, "raw") for name in raw_datasets] + \
                [(name, "structured") for name in structured_datasets] + \
                [(name, "poc") for name in poc_datasets] + \
                [(name, "huggingface") for name in huggingface_datasets]

            # Get user selection
            questions = [
                inquirer.List(
                    'dataset_choice',
                    message="Select a dataset to export",
                    choices=[(f"{name} ({type})", (name, type))
                             for name, type in all_datasets] + [("Cancel", None)]
                ),
                inquirer.List(
                    'format',
                    message="Select export format",
                    choices=[
                        ('JSON', 'json'),
                        ('CSV', 'csv')
                    ]
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers or not answers['dataset_choice']:
                return

            name, type = answers['dataset_choice']
            export_format = answers['format']

            # Get dataset content
            if type == "huggingface":
                dataset = self.db.get_huggingface_dataset(name)
            else:
                dataset = self.db.get_dataset_content(type, name)
                
            if not dataset:
                self.console.print(f"[red]Could not load dataset: {name}[/]")
                return

            # Create export directory
            export_dir = self.base_dir / "data" / "exports"
            export_dir.mkdir(exist_ok=True, parents=True)

            # Generate export filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = export_dir / f"{name}_{timestamp}.{export_format}"

            # Export based on format
            if export_format == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(dataset, f, indent=2)
            else:  # CSV
                # Convert dataset to DataFrame
                if type == "huggingface":
                    # For HuggingFace datasets, use the 'data' field
                    data = dataset.get('data', [])
                    if isinstance(data, list) and data:
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([dataset])
                elif isinstance(dataset.get('examples'), list):
                    df = pd.DataFrame(dataset['examples'])
                else:
                    df = pd.DataFrame([dataset])

                # Save to CSV
                df.to_csv(export_path, index=False)

            self.console.print(
                f"[green]✓ Dataset exported successfully to: {export_path}[/]")

        except Exception as e:
            self.console.print(f"[red]Error exporting dataset: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())

    def delete_dataset(self) -> None:
        """Delete a dataset"""
        try:
            # Get all available datasets
            raw_datasets = self.db.list_datasets("raw")
            structured_datasets = self.db.list_datasets("structured")
            poc_datasets = self.db.list_datasets("poc")
            
            # Get HuggingFace datasets
            huggingface_datasets = []
            try:
                huggingface_datasets = self.db.list_huggingface_datasets()
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load HuggingFace datasets: {e}[/]")

            if not any([raw_datasets, structured_datasets, poc_datasets, huggingface_datasets]):
                self.console.print(
                    "[yellow]No datasets available to delete.[/]")
                return

            # Create dataset choices
            all_datasets = [(name, "raw") for name in raw_datasets] + \
                [(name, "structured") for name in structured_datasets] + \
                [(name, "poc") for name in poc_datasets] + \
                [(name, "huggingface") for name in huggingface_datasets]

            # Get user selection
            questions = [
                inquirer.List(
                    'dataset_choice',
                    message="Select a dataset to delete",
                    choices=[(f"{name} ({type})", (name, type))
                             for name, type in all_datasets] + [("Cancel", None)]
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers or not answers['dataset_choice']:
                return

            name, type = answers['dataset_choice']

            # Confirm deletion
            confirm = inquirer.confirm(
                f"Are you sure you want to delete the dataset '{name}' of type '{type}'?",
                default=False
            )

            if not confirm:
                self.console.print("[yellow]Deletion cancelled.[/]")
                return

            # Delete dataset
            if type == "huggingface":
                # Delete from HuggingFace datasets table
                success = self.db.delete_huggingface_dataset(name)
            else:
                success = self.db.delete_dataset(type, name)

            if success:
                self.console.print(
                    f"[green]✓ Dataset '{name}' deleted successfully.[/]")
            else:
                self.console.print(
                    f"[red]Failed to delete dataset '{name}'.[/]")

        except Exception as e:
            self.console.print(f"[red]Error deleting dataset: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())

    def _prepare_for_lancedb(self, dataset_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare dataset for LanceDB storage

        Args:
            dataset_data: The raw dataset data

        Returns:
            DataFrame ready for LanceDB storage
        """
        try:
            import pandas as pd

            # Check if dataset contains examples
            if 'examples' in dataset_data and isinstance(dataset_data['examples'], list):
                examples = dataset_data['examples']
                
                # Special handling for jailbreak-classification dataset
                is_jailbreak_classification = dataset_data.get("name", "") == "jailbreak-classification" or "jailbreak-classification" in str(dataset_data)
                
                # Add metadata to each example
                for example in examples:
                    if isinstance(example, dict):
                        # Add dataset identification fields
                        if '_dataset_name' not in example:
                            example['_dataset_name'] = dataset_data.get(
                                'name', 'unknown')
                        if '_dataset_id' not in example:
                            example['_dataset_id'] = dataset_data.get(
                                '_metadata', {}).get('id', 'unknown')
                        if '_raw_dataset' not in example:
                            example['_raw_dataset'] = True
                            
                        # For jailbreak classification, ensure type field is preserved
                        if is_jailbreak_classification and 'type' not in example and 'prompt' in example:
                            # If we have a jailbreak classification dataset but no type field,
                            # try to infer it or set a default
                            example['type'] = 'unknown'

                # Convert to DataFrame
                df = pd.DataFrame(examples)

                # Add metadata column if not present in examples
                if '_metadata' not in df.columns and '_metadata' in dataset_data:
                    # Convert metadata to string to ensure compatibility
                    df['_metadata'] = str(dataset_data['_metadata'])
                
                # For jailbreak dataset, ensure critical columns exist
                if is_jailbreak_classification:
                    if 'prompt' not in df.columns:
                        df['prompt'] = df.get('input', '')
                    if 'type' not in df.columns:
                        df['type'] = 'unknown'

                return df
            
            # For simple list datasets
            elif isinstance(dataset_data, list) and len(dataset_data) > 0:
                # Convert to DataFrame
                df = pd.DataFrame(dataset_data)
                return df
            
            # Handle empty or invalid datasets
            self.console.print("[yellow]Warning: Invalid dataset format for LanceDB[/]")
            return pd.DataFrame({'error': ['Invalid dataset format']})

        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Error preparing dataset for LanceDB: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            # Return empty DataFrame as fallback
            return pd.DataFrame()

    def _register_lancedb_dataset(self, table_name: str, dataset_type: str, dataset_name: str,
                                  dataset_id: str, metadata: Dict[str, Any]) -> bool:
        """Register dataset in the LanceDB dataset registry for easier discovery

        Args:
            table_name: The LanceDB table name
            dataset_type: Type of dataset (raw, structured, poc)
            dataset_name: Name of the dataset
            dataset_id: Unique ID for the dataset
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            # Ensure the registry table exists
            registry_table_name = "dataset_registry"

            # Prepare registry entry
            entry = {
                'table_name': table_name,
                'dataset_type': dataset_type,
                'dataset_name': dataset_name,
                'dataset_id': dataset_id,
                'created_at': datetime.now().isoformat(),
                # Convert to string for compatibility
                'metadata': str(metadata)
            }

            # Check if table exists
            try:
                # Try to open the table - will throw an exception if it doesn't exist
                registry = self.lance_db.open_table(registry_table_name)

                # Add entry to existing registry
                import pandas as pd
                entry_df = pd.DataFrame([entry])
                registry.add(data=entry_df)

                return True
            except Exception:
                # Table doesn't exist, create it
                import pandas as pd
                entry_df = pd.DataFrame([entry])
                self.lance_db.create_table(
                    name=registry_table_name, data=entry_df)

                return True

        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not register dataset in registry: {str(e)}[/]")
            return False

    def _format_standard_example_with_keys(self, example: Dict[str, Any], input_key: str, output_key: Optional[str] = None) -> Dict[str, Any]:
        """Format a single example in standard format using custom keys specified by the user"""
        input_text = example.get(input_key, "")

        # Check if input exists and is not empty
        if not input_text:
            raise ValueError(
                f"Input field '{input_key}' is empty or not found")

        # Handle output - it might be optional if the user indicated there's no output
        output_text = ""
        if output_key and output_key in example:
            output_text = example.get(output_key, "")

        return {
            'input': input_text,
            'output': output_text,
            'metadata': {
                'original_id': example.get('id', str(uuid.uuid4())),
                'source': example.get('source', 'unknown'),
                'format_type': 'standard',
                'original_fields': list(example.keys()),
                'input_key': input_key,
                'output_key': output_key
            }
        }

    def _format_adversarial_example_with_keys(self, example: Dict[str, Any], input_key: str, output_key: Optional[str] = None) -> Dict[str, Any]:
        """Format a single example in adversarial format using custom keys specified by the user"""
        input_text = example.get(input_key, "")

        # Check if input exists and is not empty
        if not input_text:
            raise ValueError(
                f"Input field '{input_key}' is empty or not found")

        # Get template info
        template = self.ADVERSARIAL_TEMPLATES.get('jailbreak', {})
        prompt_prefix = template.get('prompt_prefix', '')

        # Handle output - it might be optional
        output_text = ""
        default_response = "I cannot comply with this request as it appears to be harmful."

        if output_key and output_key in example:
            output_text = example.get(output_key, default_response)
        else:
            output_text = default_response

        # Create formatted adversarial example
        return {
            'input': f"{prompt_prefix}{input_text}",
            'output': output_text,
            'metadata': {
                'original_id': example.get('id', str(uuid.uuid4())),
                'source': example.get('source', 'unknown'),
                'format_type': 'adversarial',
                'category': random.choice(template.get('categories', ['harmful_content'])),
                'problem_type': random.choice(self.PROBLEM_TYPES),
                'original_fields': list(example.keys()),
                'input_key': input_key,
                'output_key': output_key
            }
        }

    def _format_evaluation_example_with_keys(self, example: Dict[str, Any], input_key: str, output_key: Optional[str] = None) -> Dict[str, Any]:
        """Format a single example in evaluation format using custom keys specified by the user"""
        input_text = example.get(input_key, "")

        # Check if input exists and is not empty
        if not input_text:
            raise ValueError(
                f"Input field '{input_key}' is empty or not found")

        # Handle output - it might be optional
        reference_outputs = []
        if output_key and output_key in example:
            output_text = example.get(output_key, "")
            if output_text:
                reference_outputs.append(output_text)

        # Create formatted evaluation example
        return {
            'input': input_text,
            'reference_outputs': reference_outputs,
            'metadata': {
                'original_id': example.get('id', str(uuid.uuid4())),
                'source': example.get('source', 'unknown'),
                'format_type': 'evaluation',
                'original_fields': list(example.keys()),
                'input_key': input_key,
                'output_key': output_key
            }
        }
