"""Dataset management commands for the Dravik CLI"""
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from .dataset_handler import DatasetHandler
from .dataset_ui import DatasetUI

class DatasetCommands:
    """Main command class for dataset operations"""
    
    def __init__(self, db, config):
        """Initialize dataset commands"""
        self.db = db
        self.config = config
        self.console = Console()
        self.handler = DatasetHandler(db, config)
        self.ui = DatasetUI(self.console)
    
    def download_dataset(self):
        """Download a dataset from HuggingFace"""
        self.console.print(Panel(
            "[bold]Download Dataset[/]\n\n"
            "Download a dataset from HuggingFace for training or benchmarking.",
            title="[cyan]DATASET DOWNLOAD[/]",
            border_style="cyan"
        ))
        
        # Get dataset info from user
        dataset_info = self.ui.get_huggingface_dataset_info()
        if not dataset_info:
            return
        
        # Download the dataset
        dataset_id = self.handler.download_from_huggingface(
            dataset_info['dataset_id'],
            dataset_info['subset']
        )
        
        if dataset_id:
            self.ui.show_operation_result(
                True,
                "Dataset download",
                f"Dataset ID: {dataset_id}"
            )
        else:
            self.ui.show_operation_result(
                False,
                "Dataset download"
            )
    
    def format_dataset(self):
        """Format a dataset for adversarial training"""
        self.console.print(Panel(
            "[bold]Format Dataset[/]\n\n"
            "Format a dataset for adversarial training and model safeguarding.",
            title="[green]DATASET FORMATTING[/]",
            border_style="green"
        ))
        
        # List available datasets
        datasets = self.handler.list_datasets(dataset_type="raw")
        
        # Let user select a dataset
        dataset_id = self.ui.select_dataset(datasets, "format")
        if not dataset_id:
            return
        
        # Get formatting options
        format_options = self.ui.get_adversarial_format_options()
        if not format_options:
            return
        
        # Format the dataset
        version_id = self.handler.format_for_adversarial(
            dataset_id,
            format_options['format_type']
        )
        
        if version_id:
            self.ui.show_operation_result(
                True,
                "Dataset formatting",
                f"Version ID: {version_id}"
            )
        else:
            self.ui.show_operation_result(
                False,
                "Dataset formatting"
            )
    
    def view_datasets(self):
        """View available datasets"""
        self.console.print(Panel(
            "[bold]View Datasets[/]\n\n"
            "View and inspect available datasets.",
            title="[blue]DATASET VIEWER[/]",
            border_style="blue"
        ))
        
        # Display all datasets
        self.handler.display_datasets()
        
        # Let user select a dataset to view in detail
        datasets = self.handler.list_datasets()
        dataset_id = self.ui.select_dataset(datasets, "view in detail")
        if not dataset_id:
            return
        
        # Load and display dataset preview
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        if dataset:
            # Load a few samples
            with open(dataset['path'], 'r') as f:
                import json
                data = json.load(f)
                samples = data[:5] if isinstance(data, list) else [data]
            
            self.ui.display_dataset_preview(dataset, samples)
    
    def export_dataset(self):
        """Export a dataset"""
        self.console.print(Panel(
            "[bold]Export Dataset[/]\n\n"
            "Export a dataset to JSON or CSV format.",
            title="[magenta]DATASET EXPORT[/]",
            border_style="magenta"
        ))
        
        # List available datasets
        datasets = self.handler.list_datasets()
        
        # Let user select a dataset
        dataset_id = self.ui.select_dataset(datasets, "export")
        if not dataset_id:
            return
        
        # Get export options
        export_options = self.ui.get_export_options()
        if not export_options:
            return
        
        # Export the dataset
        output_path = self.handler.export_dataset(
            dataset_id,
            format=export_options['format'],
            output_path=export_options['output_path']
        )
        
        if output_path:
            self.ui.show_operation_result(
                True,
                "Dataset export",
                f"Exported to: {output_path}"
            )
        else:
            self.ui.show_operation_result(
                False,
                "Dataset export"
            )
    
    def delete_dataset(self):
        """Delete a dataset"""
        self.console.print(Panel(
            "[bold]Delete Dataset[/]\n\n"
            "Delete a dataset and its associated files.",
            title="[red]DATASET DELETION[/]",
            border_style="red"
        ))
        
        # List available datasets
        datasets = self.handler.list_datasets()
        
        # Let user select a dataset
        dataset_id = self.ui.select_dataset(datasets, "delete")
        if not dataset_id:
            return
        
        # Get dataset info
        dataset = next((d for d in datasets if d['id'] == dataset_id), None)
        if not dataset:
            self.ui.show_operation_result(False, "Dataset deletion", "Dataset not found")
            return
        
        # Confirm deletion
        confirm, delete_files = self.ui.confirm_deletion(dataset['name'])
        if not confirm:
            return
        
        # Delete the dataset
        success = self.handler.delete_dataset(dataset_id, delete_files)
        
        self.ui.show_operation_result(
            success,
            "Dataset deletion",
            f"Deleted dataset: {dataset['name']}"
        ) 