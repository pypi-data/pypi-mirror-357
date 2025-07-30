#!/usr/bin/env python3
"""
Simple script to fix LanceDB table issues by dropping problematic tables
"""
import os
import sys
from pathlib import Path
import lancedb
import pandas as pd

# Set up the console output
try:
    from rich.console import Console
    console = Console()
    def log_success(msg): console.print(f"[green]{msg}[/]")
    def log_error(msg): console.print(f"[red]{msg}[/]")
    def log_info(msg): console.print(f"[blue]{msg}[/]")
except ImportError:
    def log_success(msg): print(f"SUCCESS: {msg}")
    def log_error(msg): print(f"ERROR: {msg}")
    def log_info(msg): print(f"INFO: {msg}")

def fix_lancedb():
    """Fix common LanceDB issues"""
    log_info("Starting LanceDB table fix...")
    
    # Connect to LanceDB
    lancedb_path = str(Path.home() / "dravik" / "data" / "lancedb")
    log_info(f"Connecting to LanceDB at {lancedb_path}")
    
    try:
        db = lancedb.connect(lancedb_path)
        log_success("Connected to LanceDB")
        
        # List tables
        table_names = []
        try:
            try:
                table_names = db.table_names()
            except AttributeError:
                table_names = db.list_tables()
        except Exception as e:
            log_error(f"Error listing tables: {str(e)}")
            return False
        
        log_info(f"Found {len(table_names)} tables")
        
        # Drop problematic tables
        problematic_tables = ['raw_datasets', 'structured_datasets']
        
        for table in problematic_tables:
            if table in table_names:
                log_info(f"Found problematic table: {table}")
                try:
                    db.drop_table(table)
                    log_success(f"Successfully dropped table: {table}")
                except Exception as e:
                    log_error(f"Failed to drop table {table}: {str(e)}")
        
        # Create simple placeholder dataframe
        df = pd.DataFrame({
            'id': ['placeholder'],
            'value': ['placeholder'],
            'timestamp': [123456789]
        })
        
        # Create placeholder tables with reserved names to prevent conflicts
        placeholder_tables = ['raw_datasets_reserved', 'structured_datasets_reserved']
        
        for table in placeholder_tables:
            try:
                try:
                    # Try with 'overwrite' mode first
                    db.create_table(table, data=df, mode="overwrite")
                except Exception as mode_error:
                    # If mode parameter is not supported, drop and recreate
                    if "unexpected keyword argument 'mode'" in str(mode_error):
                        if table in table_names:
                            db.drop_table(table)
                        db.create_table(table, data=df)
                    else:
                        raise mode_error
                        
                log_success(f"Created placeholder table: {table}")
            except Exception as e:
                log_error(f"Failed to create placeholder table {table}: {str(e)}")
                
        log_success("LanceDB fix completed")
        return True
    
    except Exception as e:
        log_error(f"Error connecting to LanceDB: {str(e)}")
        return False

def fix_jailbreak_classification_datasets(lancedb_path=None):
    """Fix jailbreak-classification datasets in LanceDB"""
    import lancedb
    import pandas as pd
    import json
    from pathlib import Path
    
    # Set default LanceDB path if not provided
    if lancedb_path is None:
        lancedb_path = str(Path.home() / "dravik" / "data" / "lancedb")
    
    log_info("Checking for jailbreak-classification datasets to fix...")
    
    try:
        # Connect to LanceDB
        db = lancedb.connect(lancedb_path)
        log_success("Connected to LanceDB")
        
        # List tables
        table_names = []
        try:
            try:
                table_names = db.table_names()
            except AttributeError:
                table_names = db.list_tables()
        except Exception as e:
            log_error(f"Error listing tables: {str(e)}")
            return False
        
        # Find jailbreak-classification tables
        jailbreak_tables = [t for t in table_names if 'jailbreak-classification' in t.lower()]
        log_info(f"Found {len(jailbreak_tables)} potential jailbreak classification tables")
        
        for table_name in jailbreak_tables:
            try:
                log_info(f"Processing table: {table_name}")
                
                # Open the table
                table = db.open_table(table_name)
                
                # Get the data
                df = table.to_pandas()
                
                if len(df) == 0:
                    log_info(f"Table {table_name} is empty, skipping")
                    continue
                
                # Check if this is a jailbreak-classification dataset with missing fields
                needs_update = False
                if 'prompt' not in df.columns or 'type' not in df.columns:
                    log_info(f"Table {table_name} needs structure update")
                    needs_update = True
                
                if needs_update:
                    # Create fixed DataFrame
                    fixed_df = df.copy()
                    
                    # Ensure prompt column exists
                    if 'prompt' not in fixed_df.columns:
                        fixed_df['prompt'] = fixed_df.get('input', fixed_df.get('text', ''))
                        log_info("Added 'prompt' column")
                    
                    # Ensure type column exists
                    if 'type' not in fixed_df.columns:
                        fixed_df['type'] = 'unknown'
                        log_info("Added 'type' column")
                    
                    # Create new table with fixed structure
                    new_table_name = f"{table_name}_fixed"
                    try:
                        db.create_table(new_table_name, data=fixed_df)
                        log_success(f"Created fixed table: {new_table_name}")
                        
                        # Optionally rename/replace the old table
                        try:
                            db.drop_table(table_name)
                            db.rename_table(new_table_name, table_name)
                            log_success(f"Replaced original table with fixed version")
                        except Exception as e:
                            log_error(f"Could not replace original table: {str(e)}")
                    except Exception as e:
                        log_error(f"Error creating fixed table: {str(e)}")
                else:
                    log_info(f"Table {table_name} already has correct structure")
            
            except Exception as e:
                log_error(f"Error processing table {table_name}: {str(e)}")
        
        log_success("Jailbreak classification dataset fix completed")
        return True
    
    except Exception as e:
        log_error(f"Error connecting to LanceDB: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_lancedb()
    if success:
        log_success("LanceDB tables fixed successfully")
        
        # Also fix jailbreak-classification datasets
        jailbreak_success = fix_jailbreak_classification_datasets()
        if jailbreak_success:
            log_success("Jailbreak classification datasets fixed successfully")
        else:
            log_error("Failed to fix jailbreak classification datasets")
    else:
        log_error("Failed to fix LanceDB tables") 