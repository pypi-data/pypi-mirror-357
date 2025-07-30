#!/usr/bin/env python3
"""Utility script to clean up LanceDB tables"""
import os
import sys
from pathlib import Path
import lancedb
from rich.console import Console
import inquirer
from typing import List, Dict, Any
import json

class LanceDBCleanup:
    def __init__(self):
        self.console = Console()
        self.lancedb_path = str(Path.home() / "dravik" / "data" / "lancedb")
        
    def connect_to_lancedb(self):
        """Connect to LanceDB with error handling"""
        try:
            db = lancedb.connect(self.lancedb_path)
            self.console.print("[green]✓ Successfully connected to LanceDB[/]")
            return db
        except Exception as e:
            self.console.print(f"[red]Error connecting to LanceDB: {str(e)}[/]")
            sys.exit(1)
    
    def list_tables(self, db) -> List[str]:
        """List all tables in LanceDB"""
        try:
            # Try new API method first
            tables = db.table_names()
        except AttributeError:
            try:
                # Fallback to old API method
                tables = db.list_tables()
            except Exception as e:
                self.console.print(f"[red]Error listing tables: {str(e)}[/]")
                return []
        
        return tables
    
    def get_table_info(self, db: lancedb.LanceDB, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table"""
        try:
            table = db.open_table(table_name)
            return {
                "name": table_name,
                "schema": table.schema,
                "count": len(table),
                "size": self._get_table_size(table_name)
            }
        except Exception as e:
            self.console.print(f"[red]Error getting table info: {str(e)}[/]")
            return {}
    
    def _get_table_size(self, table_name: str) -> str:
        """Get the size of a table in human-readable format"""
        try:
            table_path = Path(self.lancedb_path) / f"{table_name}.lance"
            if not table_path.exists():
                return "Unknown"
            
            size_bytes = sum(f.stat().st_size for f in table_path.rglob("*") if f.is_file())
            
            # Convert to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.2f} TB"
        except Exception:
            return "Unknown"
    
    def drop_table(self, db: lancedb.LanceDB, table_name: str) -> bool:
        """Drop a specific table"""
        try:
            db.drop_table(table_name)
            self.console.print(f"[green]✓ Successfully dropped table: {table_name}[/]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error dropping table {table_name}: {str(e)}[/]")
            return False
    
    def cleanup_tables(self):
        """Main cleanup function with interactive menu"""
        self.console.print("[bold blue]LanceDB Table Cleanup Utility[/]")
        self.console.print("[dim]This will help you manage and clean up LanceDB tables.[/]\n")
        
        # Connect to LanceDB
        db = self.connect_to_lancedb()
        
        while True:
            # List all tables
            tables = self.list_tables(db)
            if not tables:
                self.console.print("[yellow]No tables found in LanceDB.[/]")
                break
            
            # Create table choices with info
            table_choices = []
            for table_name in tables:
                info = self.get_table_info(db, table_name)
                if info:
                    table_choices.append(
                        (f"{table_name} ({info['count']} rows, {info['size']})", table_name)
                    )
            
            # Add exit option
            table_choices.append(("Exit", None))
            
            # Get user selection
            questions = [
                inquirer.List(
                    'table_choice',
                    message="Select a table to manage",
                    choices=table_choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or not answers['table_choice']:
                break
            
            selected_table = answers['table_choice']
            
            # Show table actions
            action_questions = [
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=[
                        ("View Table Info", "info"),
                        ("Drop Table", "drop"),
                        ("Back to Table List", "back")
                    ]
                )
            ]
            
            action_answers = inquirer.prompt(action_questions)
            if not action_answers:
                continue
            
            action = action_answers['action']
            
            if action == "info":
                info = self.get_table_info(db, selected_table)
                if info:
                    self.console.print("\n[bold]Table Information:[/]")
                    self.console.print(f"Name: {info['name']}")
                    self.console.print(f"Row Count: {info['count']}")
                    self.console.print(f"Size: {info['size']}")
                    self.console.print("\n[bold]Schema:[/]")
                    self.console.print(json.dumps(info['schema'], indent=2))
                    self.console.print("\n[dim]Press Enter to continue...[/]")
                    input()
            
            elif action == "drop":
                # Confirm deletion
                if inquirer.confirm(
                    f"Are you sure you want to drop table '{selected_table}'? This action cannot be undone.",
                    default=False
                ):
                    self.drop_table(db, selected_table)
                    self.console.print("\n[dim]Press Enter to continue...[/]")
                    input()
            
            # If action is "back", continue the loop
    
    def drop_all_tables(self):
        """Drop all tables in LanceDB with confirmation"""
        db = self.connect_to_lancedb()
        tables = self.list_tables(db)
        
        if not tables:
            self.console.print("[yellow]No tables found in LanceDB.[/]")
            return
        
        self.console.print(f"\n[bold red]Found {len(tables)} tables in LanceDB:[/]")
        for table in tables:
            info = self.get_table_info(db, table)
            self.console.print(f"- {table} ({info.get('count', 'unknown')} rows, {info.get('size', 'unknown')})")
        
        if inquirer.confirm(
            "\n[bold red]Are you sure you want to drop ALL tables? This action cannot be undone!",
            default=False
        ):
            success_count = 0
            for table in tables:
                if self.drop_table(db, table):
                    success_count += 1
            
            self.console.print(f"\n[green]Successfully dropped {success_count} out of {len(tables)} tables.[/]")
        else:
            self.console.print("\n[yellow]Operation cancelled.[/]")

def main():
    """Main entry point"""
    cleanup = LanceDBCleanup()
    
    # Show menu
    questions = [
        inquirer.List(
            'action',
            message="Select an action",
            choices=[
                ("Manage Tables Interactively", "interactive"),
                ("Drop All Tables", "drop_all"),
                ("Exit", "exit")
            ]
        )
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return
    
    action = answers['action']
    
    if action == "interactive":
        cleanup.cleanup_tables()
    elif action == "drop_all":
        cleanup.drop_all_tables()
    
    cleanup.console.print("\n[dim]Press Enter to exit...[/]")
    input()

if __name__ == "__main__":
    main() 