"""
Dataset Deletion Manager

This module provides robust functionality for safely deleting datasets,
with support for both raw and formatted datasets.
"""

import os
import logging
import shutil
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import json
import sqlite3
from datetime import datetime
import pandas as pd

# Import registry for integration
from .registry import DatasetRegistry

logger = logging.getLogger(__name__)

class DatasetDeletionManager:
    """
    Professional dataset deletion manager
    
    Features:
    - Safe deletion of datasets with confirmation
    - Support for both raw and formatted datasets
    - Backup functionality before deletion
    - Audit logging of all deletion operations
    - Recycle bin for temporary storage of deleted datasets
    """
    
    def __init__(self, 
                registry: Optional[DatasetRegistry] = None,
                data_dir: Optional[str] = None,
                keep_backups: bool = True):
        """
        Initialize dataset deletion manager
        
        Args:
            registry: Optional DatasetRegistry to integrate with
            data_dir: Base directory for dataset storage
            keep_backups: Whether to create backups before deletion
        """
        self.registry = registry or DatasetRegistry()
        
        # Set up directories
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to project data directory
            self.data_dir = Path(os.environ.get("DRAVIK_DATA_DIR", "data"))
            
        # Create deletion log directory and recycle bin
        self.backups_dir = self.data_dir / "backups"
        self.recycle_bin = self.data_dir / "recycle_bin"
        self.logs_dir = self.data_dir / "deletion_logs"
        
        for directory in [self.backups_dir, self.recycle_bin, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        self.keep_backups = keep_backups
        
        # Initialize deletion log database
        self.db_path = self.logs_dir / "deletion_log.db"
        self._setup_database()
    
    def _setup_database(self) -> None:
        """Set up the deletion log database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS deletion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id TEXT,
            dataset_name TEXT,
            dataset_type TEXT,
            deleted_at TEXT,
            backed_up INTEGER,
            backup_path TEXT,
            deleted_by TEXT,
            reason TEXT,
            permanent INTEGER
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS restored_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id TEXT,
            restored_at TEXT,
            restored_by TEXT,
            original_deletion_id INTEGER,
            FOREIGN KEY (original_deletion_id) REFERENCES deletion_log(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def delete_dataset(self,
                      dataset_id: str,
                      dataset_type: str = "formatted",
                      permanent: bool = False,
                      reason: Optional[str] = None,
                      deleted_by: Optional[str] = None) -> bool:
        """
        Delete a dataset
        
        Args:
            dataset_id: ID of the dataset to delete
            dataset_type: Type of dataset ('raw' or 'formatted')
            permanent: Whether to permanently delete or move to recycle bin
            reason: Optional reason for deletion
            deleted_by: Optional username who initiated deletion
            
        Returns:
            True if deletion was successful
        """
        # Verify the dataset exists
        dataset_info = None
        storage_path = None
        
        if dataset_type == "formatted":
            # Check the registry for formatted datasets
            datasets = self.registry.list_datasets(active_only=True)
            dataset_info = next((d for d in datasets if d['id'] == dataset_id), None)
            
            if not dataset_info:
                logger.warning(f"Formatted dataset {dataset_id} not found in registry")
                return False
                
            storage_path = dataset_info.get('storage_path')
            if not storage_path or not Path(storage_path).exists():
                logger.warning(f"Storage path for dataset {dataset_id} not found or invalid")
                # Still proceed with deletion from registry
        
        elif dataset_type == "raw":
            # For raw datasets, check in the raw data directory
            raw_data_dir = self.data_dir / "raw"
            potential_paths = list(raw_data_dir.glob(f"*{dataset_id}*"))
            
            if not potential_paths:
                logger.warning(f"Raw dataset {dataset_id} not found")
                return False
                
            # Use the most specific match
            storage_path = str(sorted(potential_paths, key=lambda p: p.name.count(dataset_id))[-1])
            dataset_info = {
                "id": dataset_id,
                "name": Path(storage_path).stem,
                "storage_path": storage_path
            }
        else:
            logger.error(f"Unsupported dataset type: {dataset_type}")
            return False
        
        # Create backup if requested
        backup_path = None
        if self.keep_backups and storage_path:
            try:
                backup_path = self._create_backup(storage_path, dataset_id, dataset_type)
                logger.info(f"Created backup of {dataset_id} at {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup for {dataset_id}: {e}")
        
        # Delete or move the dataset files
        if storage_path and Path(storage_path).exists():
            try:
                if permanent:
                    # Permanently delete
                    if Path(storage_path).is_dir():
                        shutil.rmtree(storage_path)
                    else:
                        Path(storage_path).unlink()
                    logger.info(f"Permanently deleted {dataset_type} dataset files at {storage_path}")
                else:
                    # Move to recycle bin
                    recycle_path = self._move_to_recycle_bin(storage_path, dataset_id, dataset_type)
                    logger.info(f"Moved {dataset_type} dataset to recycle bin: {recycle_path}")
            except Exception as e:
                logger.error(f"Error deleting dataset files: {e}")
                # Continue with metadata deletion even if file deletion fails
        
        # Update registry for formatted datasets
        if dataset_type == "formatted":
            try:
                # Mark as inactive in registry
                self.registry.delete_dataset(dataset_id, delete_files=False)  # We handled files above
                logger.info(f"Marked dataset {dataset_id} as inactive in registry")
            except Exception as e:
                logger.error(f"Error updating registry: {e}")
                return False
        
        # Log the deletion
        self._log_deletion(
            dataset_id=dataset_id,
            dataset_name=dataset_info.get("name", dataset_id),
            dataset_type=dataset_type,
            backed_up=backup_path is not None,
            backup_path=str(backup_path) if backup_path else None,
            deleted_by=deleted_by,
            reason=reason,
            permanent=permanent
        )
        
        return True
    
    def _create_backup(self, 
                      storage_path: str, 
                      dataset_id: str, 
                      dataset_type: str) -> Path:
        """Create a backup of the dataset before deletion"""
        storage_path = Path(storage_path)
        
        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backups_dir / f"{dataset_type}_{dataset_id}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the dataset files to backup
        if storage_path.is_dir():
            # Copy entire directory
            backup_path = backup_dir / storage_path.name
            shutil.copytree(storage_path, backup_path)
        else:
            # Copy single file
            backup_path = backup_dir / storage_path.name
            shutil.copy2(storage_path, backup_path)
            
        # Add metadata about the backup
        metadata = {
            "dataset_id": dataset_id,
            "dataset_type": dataset_type,
            "original_path": str(storage_path),
            "backed_up_at": timestamp,
            "backed_up_files": [f.name for f in backup_dir.glob("**/*") if f.is_file()]
        }
        
        # Save metadata
        with open(backup_dir / "backup_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        return backup_dir
    
    def _move_to_recycle_bin(self, 
                            storage_path: str, 
                            dataset_id: str, 
                            dataset_type: str) -> Path:
        """Move dataset to recycle bin instead of permanent deletion"""
        storage_path = Path(storage_path)
        
        # Create timestamped directory in recycle bin
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recycle_path = self.recycle_bin / f"{dataset_type}_{dataset_id}_{timestamp}"
        recycle_path.mkdir(parents=True, exist_ok=True)
        
        # Move the dataset files to recycle bin
        if storage_path.is_dir():
            # Move entire directory
            target_path = recycle_path / storage_path.name
            shutil.move(str(storage_path), target_path)
        else:
            # Move single file
            target_path = recycle_path / storage_path.name
            shutil.move(str(storage_path), target_path)
            
        # Add metadata about the deletion
        metadata = {
            "dataset_id": dataset_id,
            "dataset_type": dataset_type,
            "original_path": str(storage_path),
            "deleted_at": timestamp,
            "expiry_date": (datetime.now() + pd.Timedelta(days=30)).strftime("%Y-%m-%d")
        }
        
        # Save metadata
        with open(recycle_path / "deletion_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        return recycle_path
    
    def _log_deletion(self,
                     dataset_id: str,
                     dataset_name: str,
                     dataset_type: str,
                     backed_up: bool,
                     backup_path: Optional[str],
                     deleted_by: Optional[str],
                     reason: Optional[str],
                     permanent: bool) -> None:
        """Log deletion to the database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        INSERT INTO deletion_log
        (dataset_id, dataset_name, dataset_type, deleted_at, backed_up, 
         backup_path, deleted_by, reason, permanent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dataset_id, dataset_name, dataset_type, 
            datetime.now().isoformat(), int(backed_up),
            backup_path, deleted_by or "unknown", reason or "", int(permanent)
        ))
        
        conn.commit()
        conn.close()
    
    def restore_dataset(self, 
                       dataset_id: str, 
                       dataset_type: str = "formatted",
                       restored_by: Optional[str] = None) -> bool:
        """
        Restore a deleted dataset from recycle bin
        
        Args:
            dataset_id: ID of the dataset to restore
            dataset_type: Type of dataset ('raw' or 'formatted')
            restored_by: Optional username who initiated restoration
            
        Returns:
            True if restoration was successful
        """
        # Find the dataset in the recycle bin
        pattern = f"{dataset_type}_{dataset_id}_*"
        recycle_items = list(self.recycle_bin.glob(pattern))
        
        if not recycle_items:
            logger.warning(f"Dataset {dataset_id} not found in recycle bin")
            return False
            
        # Sort by timestamp (newest first)
        recycle_items.sort(key=lambda x: x.name.split('_')[-1], reverse=True)
        recycle_path = recycle_items[0]
        
        # Load metadata
        metadata_path = recycle_path / "deletion_metadata.json"
        if not metadata_path.exists():
            logger.warning(f"Metadata not found for {dataset_id} in recycle bin")
            return False
            
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            
        original_path = metadata.get("original_path")
        if not original_path:
            logger.warning(f"Original path not found in metadata for {dataset_id}")
            return False
            
        # Ensure original path directory exists
        original_path = Path(original_path)
        original_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Find the dataset file(s) in the recycle bin
        dataset_files = [f for f in recycle_path.glob("**/*") 
                        if f.is_file() and f.name != "deletion_metadata.json"]
        
        if not dataset_files:
            logger.warning(f"No dataset files found in recycle bin for {dataset_id}")
            return False
            
        # Restore the files
        try:
            # If it was a directory, we need to recreate it
            if len(dataset_files) > 1 or dataset_files[0].is_dir():
                # Check if the file in recycle bin is a directory (entire dataset directory was moved)
                potential_dir = next((f for f in recycle_path.glob("*") if f.is_dir()), None)
                if potential_dir:
                    # Move the entire directory back
                    shutil.move(str(potential_dir), original_path)
                else:
                    # Recreate the directory and move files individually
                    original_path.mkdir(exist_ok=True)
                    for file in dataset_files:
                        shutil.move(str(file), original_path / file.name)
            else:
                # Move the single file back
                shutil.move(str(dataset_files[0]), original_path)
                
            logger.info(f"Restored {dataset_type} dataset {dataset_id} to {original_path}")
        except Exception as e:
            logger.error(f"Error restoring dataset: {e}")
            return False
            
        # For formatted datasets, reactivate in registry
        if dataset_type == "formatted":
            try:
                # Update the registry database directly since there's no reactivate method
                conn = sqlite3.connect(self.registry.db_path)
                c = conn.cursor()
                
                c.execute('''
                UPDATE datasets SET is_active = 1 WHERE id = ?
                ''', (dataset_id,))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Reactivated dataset {dataset_id} in registry")
            except Exception as e:
                logger.error(f"Error updating registry: {e}")
                # Continue even if registry update fails
        
        # Log the restoration
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Find the original deletion record
        c.execute('''
        SELECT id FROM deletion_log 
        WHERE dataset_id = ? AND dataset_type = ?
        ORDER BY deleted_at DESC LIMIT 1
        ''', (dataset_id, dataset_type))
        
        deletion_id = c.fetchone()
        deletion_id = deletion_id[0] if deletion_id else None
        
        # Log restoration
        c.execute('''
        INSERT INTO restored_datasets
        (dataset_id, restored_at, restored_by, original_deletion_id)
        VALUES (?, ?, ?, ?)
        ''', (
            dataset_id, datetime.now().isoformat(), 
            restored_by or "unknown", deletion_id
        ))
        
        conn.commit()
        conn.close()
        
        # Clean up the recycle bin entry
        try:
            shutil.rmtree(recycle_path)
        except Exception as e:
            logger.warning(f"Error cleaning up recycle bin entry: {e}")
            
        return True
    
    def empty_recycle_bin(self, days_old: int = 30) -> int:
        """
        Permanently delete datasets in recycle bin older than specified days
        
        Args:
            days_old: Delete items older than this many days
            
        Returns:
            Number of items deleted
        """
        # Calculate the cutoff date
        cutoff_date = datetime.now() - pd.Timedelta(days=days_old)
        
        # Find items in the recycle bin
        deleted_count = 0
        
        for item in self.recycle_bin.glob("*"):
            if not item.is_dir():
                continue
                
            # Try to determine the deletion date from the directory name
            try:
                # Format is typically {type}_{id}_{timestamp}
                timestamp_str = item.name.split('_')[-1]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if timestamp < cutoff_date:
                    # Old enough to delete
                    shutil.rmtree(item)
                    deleted_count += 1
                    logger.info(f"Permanently deleted {item.name} from recycle bin")
            except (ValueError, IndexError):
                # If we can't parse the timestamp, check the metadata
                metadata_path = item / "deletion_metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                            
                        deleted_at = metadata.get("deleted_at")
                        if deleted_at:
                            timestamp = datetime.strptime(deleted_at, "%Y%m%d_%H%M%S")
                            
                            if timestamp < cutoff_date:
                                # Old enough to delete
                                shutil.rmtree(item)
                                deleted_count += 1
                                logger.info(f"Permanently deleted {item.name} from recycle bin")
                    except Exception:
                        # Skip items with parsing issues
                        pass
        
        return deleted_count
    
    def get_deletion_history(self, 
                           dataset_id: Optional[str] = None,
                           dataset_type: Optional[str] = None) -> pd.DataFrame:
        """
        Get deletion history
        
        Args:
            dataset_id: Optional filter by dataset ID
            dataset_type: Optional filter by dataset type
            
        Returns:
            DataFrame with deletion history
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM deletion_log"
        params = []
        
        if dataset_id or dataset_type:
            query += " WHERE"
            
            if dataset_id:
                query += " dataset_id = ?"
                params.append(dataset_id)
                
                if dataset_type:
                    query += " AND dataset_type = ?"
                    params.append(dataset_type)
            elif dataset_type:
                query += " dataset_type = ?"
                params.append(dataset_type)
                
        query += " ORDER BY deleted_at DESC"
        
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
            
        conn.close()
        
        # Convert timestamp
        if 'deleted_at' in df.columns:
            df['deleted_at'] = pd.to_datetime(df['deleted_at'])
            
        return df
    
    def get_recycle_bin_contents(self) -> pd.DataFrame:
        """
        Get list of datasets in the recycle bin
        
        Returns:
            DataFrame with recycle bin contents
        """
        contents = []
        
        for item in self.recycle_bin.glob("*"):
            if not item.is_dir():
                continue
                
            # Extract dataset type and ID from directory name
            parts = item.name.split('_')
            if len(parts) >= 3:
                dataset_type = parts[0]
                dataset_id = parts[1]
                timestamp_str = parts[2]
                
                # Try to parse timestamp
                try:
                    deleted_at = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    deleted_at = None
                    
                # Check for metadata
                metadata_path = item / "deletion_metadata.json"
                original_path = None
                expiry_date = None
                
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                            
                        original_path = metadata.get("original_path")
                        expiry_date = metadata.get("expiry_date")
                        
                        # Use metadata values if available
                        if "dataset_id" in metadata:
                            dataset_id = metadata["dataset_id"]
                        if "dataset_type" in metadata:
                            dataset_type = metadata["dataset_type"]
                        if "deleted_at" in metadata:
                            try:
                                deleted_at = datetime.strptime(
                                    metadata["deleted_at"], "%Y%m%d_%H%M%S"
                                )
                            except ValueError:
                                pass
                    except Exception:
                        # Skip metadata parsing errors
                        pass
                        
                contents.append({
                    "dataset_id": dataset_id,
                    "dataset_type": dataset_type,
                    "deleted_at": deleted_at,
                    "original_path": original_path,
                    "expiry_date": expiry_date,
                    "recycle_path": str(item)
                })
                
        # Convert to DataFrame
        df = pd.DataFrame(contents)
        
        # Sort by deleted_at (newest first)
        if not df.empty and 'deleted_at' in df.columns:
            df = df.sort_values('deleted_at', ascending=False)
            
        return df
