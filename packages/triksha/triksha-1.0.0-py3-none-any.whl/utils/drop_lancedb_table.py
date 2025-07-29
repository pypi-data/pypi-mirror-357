#!/usr/bin/env python3
"""Simple utility to drop LanceDB tables - more direct than the cleanup utility"""
import os
import sys
from pathlib import Path
import lancedb
from rich.console import Console
import argparse
import time

def main():
    """Drop LanceDB tables by name or pattern"""
    console = Console()
    parser = argparse.ArgumentParser(description="Drop tables from LanceDB")
    parser.add_argument("--table", help="Table name to drop (use 'all' to drop all tables)")
    parser.add_argument("--drop-structured", action="store_true", help="Drop all tables with 'structured_datasets' in the name")
    parser.add_argument("--drop-all", action="store_true", help="Drop all tables (use with caution)")
    parser.add_argument("--list", action="store_true", help="List all tables in the database")
    parser.add_argument("--fix", action="store_true", help="Fix issues with raw_datasets and structured_datasets tables")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Connect to LanceDB
    lancedb_path = str(Path.home() / "dravik" / "data" / "lancedb")
    console.print(f"Connecting to LanceDB at {lancedb_path}")
    
    try:
        db = lancedb.connect(lancedb_path)
        console.print("[green]Connected to LanceDB[/]")
        
        # Get list of tables
        try:
            table_names = db.table_names()
        except AttributeError:
            try:
                table_names = db.list_tables()
            except Exception as e:
                console.print(f"[red]Error listing tables: {str(e)}[/]")
                return
        
        console.print(f"[blue]Found {len(table_names)} tables[/]")
        
        # List tables with details
        if args.list or args.fix:
            console.print("\n[bold]Tables in the database:[/]")
            for i, table in enumerate(sorted(table_names), 1):
                try:
                    t = db.open_table(table)
                    row_count = len(t)
                    console.print(f"[cyan]{i}. {table}[/] - [yellow]{row_count} rows[/]")
                except Exception as e:
                    console.print(f"[cyan]{i}. {table}[/] - [red]Error getting info: {str(e)}[/]")
        
        # Fix structured_datasets and raw_datasets issues
        if args.fix:
            # Look for problematic tables
            raw_tables = [t for t in table_names if 'raw_dataset' in t]
            structured_tables = [t for t in table_names if 'structured_dataset' in t]
            
            console.print(f"\n[yellow]Found {len(raw_tables)} raw dataset tables[/]")
            console.print(f"[yellow]Found {len(structured_tables)} structured dataset tables[/]")
            
            # Check for the main problematic tables
            if 'raw_datasets' in table_names:
                console.print("[red]Found 'raw_datasets' table (potential conflict)[/]")
                try:
                    console.print("Dropping 'raw_datasets' table...")
                    db.drop_table('raw_datasets')
                    console.print("[green]Successfully dropped 'raw_datasets' table[/]")
                except Exception as e:
                    console.print(f"[red]Error dropping 'raw_datasets' table: {str(e)}[/]")
            
            if 'structured_datasets' in table_names:
                console.print("[red]Found 'structured_datasets' table (potential conflict)[/]")
                try:
                    console.print("Dropping 'structured_datasets' table...")
                    db.drop_table('structured_datasets')
                    console.print("[green]Successfully dropped 'structured_datasets' table[/]")
                except Exception as e:
                    console.print(f"[red]Error dropping 'structured_datasets' table: {str(e)}[/]")
            
            # Create placeholder tables to "reserve" the names to avoid conflicts
            console.print("\n[yellow]Creating placeholder tables to avoid conflicts...[/]")
            
            try:
                import pandas as pd
                
                # Create minimal placeholder data
                placeholder_df = pd.DataFrame({
                    'id': ['placeholder'],
                    'value': ['placeholder'],
                    'timestamp': [time.time()]
                })
                
                # Create raw_datasets placeholder
                try:
                    # Use 'create_table' with the 'overwrite' mode to ensure it works
                    db.create_table('raw_datasets_reserved', data=placeholder_df, mode="overwrite")
                    console.print("[green]Created 'raw_datasets_reserved' placeholder table[/]")
                except Exception as e:
                    console.print(f"[red]Error creating raw_datasets placeholder: {str(e)}[/]")
                
                # Create structured_datasets placeholder
                try:
                    db.create_table('structured_datasets_reserved', data=placeholder_df, mode="overwrite")
                    console.print("[green]Created 'structured_datasets_reserved' placeholder table[/]")
                except Exception as e:
                    console.print(f"[red]Error creating structured_datasets placeholder: {str(e)}[/]")
                    
                console.print("\n[green]Fix completed - future datasets will use unique names[/]")
            except ImportError:
                console.print("[red]Error: pandas not installed. Cannot create placeholder tables.[/]")
            except Exception as e:
                console.print(f"[red]Error during fix: {str(e)}[/]")
        
        # Drop specific table
        if args.table and args.table != 'all':
            if args.table in table_names:
                try:
                    db.drop_table(args.table)
                    console.print(f"[green]Successfully dropped table: {args.table}[/]")
                except Exception as e:
                    console.print(f"[red]Error dropping table {args.table}: {str(e)}[/]")
            else:
                console.print(f"[yellow]Table '{args.table}' not found[/]")
        
        # Drop all tables with 'structured_datasets' in the name
        if args.drop_structured:
            structured_tables = [t for t in table_names if 'structured_dataset' in t]
            console.print(f"[blue]Found {len(structured_tables)} tables with 'structured_dataset' in the name[/]")
            
            for table in structured_tables:
                try:
                    db.drop_table(table)
                    console.print(f"[green]Successfully dropped table: {table}[/]")
                except Exception as e:
                    console.print(f"[red]Error dropping table {table}: {str(e)}[/]")
        
        # Drop all tables
        if args.drop_all or (args.table and args.table == 'all'):
            console.print(f"[yellow]Dropping all {len(table_names)} tables...[/]")
            
            for table in table_names:
                try:
                    db.drop_table(table)
                    console.print(f"[green]Successfully dropped table: {table}[/]")
                except Exception as e:
                    console.print(f"[red]Error dropping table {table}: {str(e)}[/]")
        
    except Exception as e:
        console.print(f"[red]Error connecting to LanceDB: {str(e)}[/]")

if __name__ == "__main__":
    main() 