"""Dataset handling for training operations with HuggingFace integration and adversarial formatting"""
import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich import box
import lancedb
from datasets import load_dataset
import pandas as pd
from datetime import datetime
import sqlite3
import hashlib

class DatasetHandler:
    """Enhanced dataset handler with HuggingFace integration and adversarial training support"""
    
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
    
    def __init__(self, db, config):
        """Initialize dataset handler with enhanced database support"""
        self.db = db
        self.config = config
        self.console = Console()
        
        # Setup directories
        self.base_dir = Path.home() / "dravik"
        self.datasets_dir = self.base_dir / "data" / "datasets"
        self.raw_dir = self.datasets_dir / "raw"
        self.processed_dir = self.datasets_dir / "processed"
        
        # Create directories
        for dir_path in [self.datasets_dir, self.raw_dir, self.processed_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize database tables
        self._init_database()
        
        # Initialize LanceDB connection
        try:
            self.lance_uri = str(self.base_dir / "data" / "lancedb")
            self.lance_db = lancedb.connect(self.lance_uri)
            self.console.print("[green]✓ Connected to LanceDB[/]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not connect to LanceDB: {str(e)}[/]")
            self.lance_db = None
    
    def _init_database(self):
        """Initialize database tables for dataset management"""
        try:
            cursor = self.db.cursor()
            
            # Create datasets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    source TEXT NOT NULL,
                    dataset_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    samples INTEGER DEFAULT 0,
                    path TEXT,
                    huggingface_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Create dataset_versions table for tracking processed versions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dataset_versions (
                    id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    version_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
                )
            """)
            
            self.db.commit()
            
        except Exception as e:
            self.console.print(f"[red]Error initializing database: {str(e)}[/]")
    
    def download_from_huggingface(self, dataset_id: str, subset: Optional[str] = None) -> Optional[str]:
        """Download a dataset from HuggingFace"""
        try:
            self.console.print(f"[cyan]Downloading dataset {dataset_id} from HuggingFace...[/]")
            
            # Generate a unique local ID for the dataset
            local_id = hashlib.sha256(f"{dataset_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Download using HuggingFace datasets library
            dataset = load_dataset(dataset_id, subset) if subset else load_dataset(dataset_id)
            
            # Save to local file
            output_path = self.raw_dir / f"{local_id}.json"
            dataset.save_to_disk(str(output_path))
            
            # Get basic dataset info
            sample_count = sum(split.num_rows for split in dataset.values())
            
            # Store in database
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO datasets (
                    id, name, description, source, dataset_type, format,
                    samples, path, huggingface_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                local_id,
                dataset_id.split('/')[-1],
                f"Downloaded from HuggingFace: {dataset_id}",
                "huggingface",
                "raw",
                "json",
                sample_count,
                str(output_path),
                dataset_id,
                json.dumps({"subset": subset} if subset else {})
            ))
            self.db.commit()
            
            self.console.print(f"[green]✓ Successfully downloaded dataset with {sample_count} samples[/]")
            return local_id
            
        except Exception as e:
            self.console.print(f"[red]Error downloading dataset: {str(e)}[/]")
            return None
    
    def format_for_adversarial(self, dataset_id: str, format_type: str = "jailbreak") -> Optional[str]:
        """Format a dataset for adversarial training"""
        try:
            # Get dataset info
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
            dataset_info = cursor.fetchone()
            
            if not dataset_info:
                self.console.print(f"[red]Dataset {dataset_id} not found[/]")
                return None
            
            # Load the dataset
            if dataset_info[3] == "huggingface":  # source column
                dataset = load_dataset("json", data_files=dataset_info[7])  # path column
            else:
                with open(dataset_info[7], 'r') as f:
                    dataset = json.load(f)
            
            # Get template
            template = self.ADVERSARIAL_TEMPLATES.get(format_type)
            if not template:
                self.console.print(f"[red]Unknown format type: {format_type}[/]")
                return None
            
            # Format the dataset
            formatted_data = []
            for item in dataset:
                # Extract text content (adjust field names based on your dataset structure)
                text = item.get('text', item.get('content', item.get('prompt', '')))
                
                # Create adversarial example
                formatted_item = {
                    "original_text": text,
                    "prompt": f"{template['prompt_prefix']}{text}",
                    "response": f"{template['response_prefix']}{text}",
                    "category": template['categories'][0],  # You might want to add logic to determine category
                    "metadata": {
                        "source": dataset_info[3],
                        "format_type": format_type
                    }
                }
                formatted_data.append(formatted_item)
            
            # Generate version ID
            version_id = hashlib.sha256(f"{dataset_id}_adv_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Save formatted dataset
            output_path = self.processed_dir / f"{version_id}.json"
            with open(output_path, 'w') as f:
                json.dump(formatted_data, f, indent=2)
            
            # Store version in database
            cursor.execute("""
                INSERT INTO dataset_versions (
                    id, dataset_id, version_type, format, path, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                dataset_id,
                "adversarial",
                "json",
                str(output_path),
                json.dumps({"format_type": format_type, "template": template})
            ))
            self.db.commit()
            
            # Store in LanceDB for faster access
            if self.lance_db:
                table_name = f"dataset_adv_{version_id}"
                df = pd.DataFrame(formatted_data)
                self.lance_db.create_table(table_name, data=df)
            
            self.console.print(f"[green]✓ Successfully formatted dataset for adversarial training[/]")
            return version_id
            
        except Exception as e:
            self.console.print(f"[red]Error formatting dataset: {str(e)}[/]")
            return None
    
    def list_datasets(self, dataset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available datasets with optional filtering"""
        try:
            cursor = self.db.cursor()
            
            if dataset_type:
                cursor.execute("""
                    SELECT d.*, COUNT(dv.id) as versions 
                    FROM datasets d 
                    LEFT JOIN dataset_versions dv ON d.id = dv.dataset_id 
                    WHERE d.dataset_type = ?
                    GROUP BY d.id
                """, (dataset_type,))
            else:
                cursor.execute("""
                    SELECT d.*, COUNT(dv.id) as versions 
                    FROM datasets d 
                    LEFT JOIN dataset_versions dv ON d.id = dv.dataset_id 
                    GROUP BY d.id
                """)
            
            columns = [desc[0] for desc in cursor.description]
            datasets = []
            
            for row in cursor.fetchall():
                dataset = dict(zip(columns, row))
                
                # Add version information
                if dataset['versions'] > 0:
                    cursor.execute("""
                        SELECT version_type, COUNT(*) as count 
                        FROM dataset_versions 
                        WHERE dataset_id = ? 
                        GROUP BY version_type
                    """, (dataset['id'],))
                    dataset['version_info'] = dict(cursor.fetchall())
                
                datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            self.console.print(f"[red]Error listing datasets: {str(e)}[/]")
            return []
    
    def display_datasets(self):
        """Display datasets in a formatted table"""
        datasets = self.list_datasets()
        
        if not datasets:
            self.console.print("[yellow]No datasets found[/]")
            return
        
        table = Table(title="Available Datasets", box=box.ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Samples", justify="right", style="green")
        table.add_column("Versions", justify="right", style="yellow")
        table.add_column("Source", style="magenta")
        
        for dataset in datasets:
            versions = dataset.get('versions', 0)
            version_info = dataset.get('version_info', {})
            version_str = f"{versions} ({', '.join(f'{k}:{v}' for k,v in version_info.items())})" if versions > 0 else "0"
            
            table.add_row(
                dataset['id'],
                dataset['name'],
                dataset['dataset_type'],
                str(dataset['samples']),
                version_str,
                dataset['source']
            )
        
        self.console.print(table)
    
    def export_dataset(self, dataset_id: str, version_id: Optional[str] = None, 
                      format: str = "json", output_path: Optional[str] = None) -> Optional[str]:
        """Export a dataset to JSON or CSV format"""
        try:
            # Get dataset info
            cursor = self.db.cursor()
            
            if version_id:
                cursor.execute("""
                    SELECT d.*, dv.path as version_path, dv.format as version_format 
                    FROM datasets d 
                    JOIN dataset_versions dv ON d.id = dv.dataset_id 
                    WHERE dv.id = ?
                """, (version_id,))
                result = cursor.fetchone()
                if not result:
                    self.console.print(f"[red]Dataset version {version_id} not found[/]")
                    return None
                source_path = result['version_path']
            else:
                cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
                result = cursor.fetchone()
                if not result:
                    self.console.print(f"[red]Dataset {dataset_id} not found[/]")
                    return None
                source_path = result['path']
            
            # Generate output path if not provided
            if not output_path:
                filename = f"{result['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
                output_path = str(self.base_dir / "data" / "exports" / filename)
            
            # Load data
            with open(source_path, 'r') as f:
                data = json.load(f)
            
            # Export based on format
            if format == "json":
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            elif format == "csv":
                # Flatten the data structure
                flattened_data = []
                for item in data:
                    if isinstance(item, dict):
                        flat_item = {}
                        for k, v in item.items():
                            if isinstance(v, (dict, list)):
                                flat_item[k] = json.dumps(v)
                            else:
                                flat_item[k] = v
                        flattened_data.append(flat_item)
                    else:
                        flattened_data.append({"value": str(item)})
                
                # Write CSV
                if flattened_data:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                        writer.writeheader()
                        writer.writerows(flattened_data)
            else:
                self.console.print(f"[red]Unsupported export format: {format}[/]")
                return None
            
            self.console.print(f"[green]✓ Dataset exported to: {output_path}[/]")
            return output_path
            
        except Exception as e:
            self.console.print(f"[red]Error exporting dataset: {str(e)}[/]")
            return None
    
    def delete_dataset(self, dataset_id: str, delete_files: bool = True) -> bool:
        """Delete a dataset and optionally its files"""
        try:
            cursor = self.db.cursor()
            
            # Get dataset info
            cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
            dataset = cursor.fetchone()
            
            if not dataset:
                self.console.print(f"[red]Dataset {dataset_id} not found[/]")
                return False
            
            # Get all versions
            cursor.execute("SELECT * FROM dataset_versions WHERE dataset_id = ?", (dataset_id,))
            versions = cursor.fetchall()
            
            if delete_files:
                # Delete version files
                for version in versions:
                    try:
                        Path(version['path']).unlink(missing_ok=True)
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not delete version file {version['path']}: {str(e)}[/]")
                
                # Delete main dataset file
                try:
                    Path(dataset['path']).unlink(missing_ok=True)
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not delete dataset file {dataset['path']}: {str(e)}[/]")
                
                # Delete LanceDB tables if they exist
                if self.lance_db:
                    try:
                        table_name = f"dataset_{dataset_id}"
                        if table_name in self.lance_db.list_tables():
                            self.lance_db.drop_table(table_name)
                        
                        # Delete version tables
                        for version in versions:
                            table_name = f"dataset_adv_{version['id']}"
                            if table_name in self.lance_db.list_tables():
                                self.lance_db.drop_table(table_name)
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not delete LanceDB tables: {str(e)}[/]")
            
            # Delete from database
            cursor.execute("DELETE FROM dataset_versions WHERE dataset_id = ?", (dataset_id,))
            cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
            self.db.commit()
            
            self.console.print(f"[green]✓ Successfully deleted dataset {dataset_id}[/]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error deleting dataset: {str(e)}[/]")
            return False
