#!/usr/bin/env python3
"""Utility script to fix LanceDB table issues for structured datasets"""
import os
import sys
from pathlib import Path
import lancedb
import pandas as pd
import json
from rich.console import Console
import inquirer
import time

class LanceDBTableFixer:
    def __init__(self):
        self.console = Console()
        self.base_dir = Path.home() / "dravik"
        self.lancedb_path = str(self.base_dir / "data" / "lancedb")
        self.db = None
        
    def connect(self):
        """Connect to LanceDB with error handling"""
        try:
            self.db = lancedb.connect(self.lancedb_path)
            self.console.print("[green]✓ Successfully connected to LanceDB[/]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error connecting to LanceDB: {str(e)}[/]")
            return False
            
    def list_tables(self):
        """List all tables in LanceDB"""
        try:
            # Try new API method first
            try:
                tables = self.db.table_names()
            except AttributeError:
                # Fallback to old API method
                tables = self.db.list_tables()
            
            self.console.print(f"[green]Found {len(tables)} tables in LanceDB:[/]")
            for table in tables:
                self.console.print(f"- {table}")
                
            return tables
        except Exception as e:
            self.console.print(f"[red]Error listing tables: {str(e)}[/]")
            return []
    
    def fix_structured_datasets_table(self):
        """Fix the structured_datasets table issue"""
        if not self.db:
            if not self.connect():
                return False
        
        try:
            # Check if the table exists
            table_exists = False
            try:
                # Try both API methods
                try:
                    self.db.open_table("structured_datasets")
                    table_exists = True
                except Exception:
                    try:
                        if "structured_datasets" in self.list_tables():
                            table_exists = True
                    except Exception:
                        pass
            except Exception as e:
                self.console.print(f"[yellow]Error checking table existence: {str(e)}[/]")
            
            # If table exists, drop it with confirmation
            if table_exists:
                self.console.print("[yellow]Table 'structured_datasets' already exists[/]")
                
                # Ask for confirmation before dropping
                if inquirer.confirm(
                    "Do you want to drop the existing 'structured_datasets' table? This action cannot be undone!",
                    default=False
                ):
                    try:
                        self.db.drop_table("structured_datasets")
                        self.console.print("[green]Successfully dropped 'structured_datasets' table[/]")
                    except Exception as e:
                        self.console.print(f"[red]Error dropping table: {str(e)}[/]")
                        return False
                else:
                    self.console.print("[yellow]Operation cancelled[/]")
                    return False
            
            # Create an empty placeholder table with proper schema
            try:
                # Create a minimal dataframe with the expected schema
                df = pd.DataFrame({
                    'dataset_id': ['placeholder'],
                    'name': ['placeholder'],
                    'format_type': ['standard'],
                    'created_at': [time.strftime('%Y-%m-%d %H:%M:%S')],
                    'example_count': [0],
                    'input': [''],
                    'output': ['']
                })
                
                # Create the table
                self.db.create_table("structured_datasets", data=df)
                self.console.print("[green]Successfully created empty 'structured_datasets' table[/]")
                
                # Delete the placeholder data if needed
                try:
                    table = self.db.open_table("structured_datasets")
                    table.delete("dataset_id = 'placeholder'")
                    self.console.print("[green]Removed placeholder data from table[/]")
                except Exception:
                    pass
                
                return True
            except Exception as e:
                self.console.print(f"[red]Error creating table: {str(e)}[/]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error fixing structured_datasets table: {str(e)}[/]")
            return False
    
    def fix_lance_tables(self):
        """Main function to fix all tables"""
        if not self.connect():
            return
            
        all_tables = self.list_tables()
        
        # Show menu of available operations
        questions = [
            inquirer.List(
                'action',
                message="Select an action to perform",
                choices=[
                    ('Fix structured_datasets table', 'fix_structured'),
                    ('Drop and recreate all tables', 'drop_all'),
                    ('Drop individual table', 'drop_one'),
                    ('Exit', 'exit')
                ]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
            
        action = answers['action']
        
        if action == 'fix_structured':
            self.fix_structured_datasets_table()
        elif action == 'drop_all':
            if inquirer.confirm(
                "Are you sure you want to drop ALL tables? This action cannot be undone!",
                default=False
            ):
                for table in all_tables:
                    try:
                        self.db.drop_table(table)
                        self.console.print(f"[green]Dropped table: {table}[/]")
                    except Exception as e:
                        self.console.print(f"[red]Error dropping table {table}: {str(e)}[/]")
        elif action == 'drop_one':
            if not all_tables:
                self.console.print("[yellow]No tables available to drop[/]")
                return
                
            # Select a table to drop
            questions = [
                inquirer.List(
                    'table',
                    message="Select a table to drop",
                    choices=[(table, table) for table in all_tables] + [("Cancel", None)]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or not answers['table']:
                return
                
            table = answers['table']
            
            if inquirer.confirm(
                f"Are you sure you want to drop table '{table}'? This action cannot be undone!",
                default=False
            ):
                try:
                    self.db.drop_table(table)
                    self.console.print(f"[green]Successfully dropped table: {table}[/]")
                except Exception as e:
                    self.console.print(f"[red]Error dropping table: {str(e)}[/]")

def main():
    """Main function"""
    fixer = LanceDBTableFixer()
    fixer.fix_lance_tables()
    
    fixer.console.print("\n[dim]Press Enter to exit...[/]")
    input()

if __name__ == "__main__":
    main() 