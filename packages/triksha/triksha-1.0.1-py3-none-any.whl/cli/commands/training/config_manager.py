"""Configuration management for training operations"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from datetime import datetime
from uuid import uuid4

class ConfigManager:
    """Manages training configurations"""
    
    def __init__(self, db, config, configs_dir: Path):
        """Initialize config manager"""
        self.db = db
        self.config = config
        self.console = Console()
        self.configs_dir = configs_dir
        self.configs_dir.mkdir(exist_ok=True, parents=True)
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """List all saved training configurations"""
        configs = []
        
        try:
            # List all JSON files in the configs directory
            for config_file in self.configs_dir.glob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        
                        # Ensure the config has required fields
                        if "name" in config_data and "model_id" in config_data:
                            configs.append(config_data)
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not load config {config_file.name}: {str(e)}[/]")
        except Exception as e:
            self.console.print(f"[bold red]Error listing configs: {str(e)}[/]")
        
        return configs
    
    def get_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific config by ID"""
        configs = self.list_configs()
        
        for config in configs:
            if config.get("id") == config_id:
                return config
        
        return None
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save a training configuration"""
        try:
            # Ensure the config has an ID
            if "id" not in config:
                config["id"] = str(uuid4())
            
            # Add creation timestamp if not present
            if "created_at" not in config:
                config["created_at"] = datetime.now().isoformat()
            
            # Create a safe filename
            safe_name = config["name"].replace(" ", "_").replace("/", "_")
            config_path = self.configs_dir / f"{safe_name}.json"
            
            # Save the config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.console.print(f"[green]Configuration saved: {config_path.name}[/]")
            return True
        
        except Exception as e:
            self.console.print(f"[bold red]Error saving config: {str(e)}[/]")
            return False
    
    def delete_config(self, config_id: str) -> bool:
        """Delete a training configuration"""
        try:
            configs = self.list_configs()
            
            for config in configs:
                if config.get("id") == config_id:
                    # Find the file to delete
                    safe_name = config["name"].replace(" ", "_").replace("/", "_")
                    config_path = self.configs_dir / f"{safe_name}.json"
                    
                    if config_path.exists():
                        config_path.unlink()
                        self.console.print(f"[green]Deleted configuration: {config_path.name}[/]")
                        return True
            
            self.console.print(f"[yellow]Config with ID {config_id} not found[/]")
            return False
        
        except Exception as e:
            self.console.print(f"[bold red]Error deleting config: {str(e)}[/]")
            return False
    
    def import_config(self, source_path: str) -> bool:
        """Import a configuration from a file"""
        try:
            source_path = Path(source_path)
            
            if not source_path.exists():
                self.console.print(f"[bold red]Source file not found: {source_path}[/]")
                return False
            
            # Load the config
            with open(source_path, 'r') as f:
                config = json.load(f)
            
            # Validate the config
            if "name" not in config or "model_id" not in config:
                self.console.print("[bold red]Invalid configuration format[/]")
                return False
            
            # Generate a new ID to avoid conflicts
            config["id"] = str(uuid4())
            
            # Save the config
            return self.save_config(config)
        
        except Exception as e:
            self.console.print(f"[bold red]Error importing config: {str(e)}[/]")
            return False
    
    def export_config(self, config_id: str, target_path: str) -> bool:
        """Export a configuration to a file"""
        try:
            config = self.get_config(config_id)
            
            if not config:
                self.console.print(f"[bold red]Config with ID {config_id} not found[/]")
                return False
            
            # Ensure target directory exists
            target_path = Path(target_path)
            target_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Save the config
            with open(target_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.console.print(f"[green]Configuration exported to: {target_path}[/]")
            return True
        
        except Exception as e:
            self.console.print(f"[bold red]Error exporting config: {str(e)}[/]")
            return False
