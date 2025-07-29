"""
Dataset Registry System
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set, Union
from pathlib import Path
import shutil
import sqlite3
from datetime import datetime
import pandas as pd

from .dataset import Dataset
from .metadata import DatasetMetadata
from .version import DatasetVersion

logger = logging.getLogger(__name__)

class DatasetRegistry:
    """
    Professional dataset registry for tracking and managing datasets
    
    Features:
    - Persistent dataset catalog
    - Version tracking
    - Metadata storage and retrieval
    - Search and filtering capabilities
    - Audit logging
    """
    
    def __init__(self, 
                registry_path: Optional[str] = None,
                auto_discover: bool = True):
        """
        Initialize dataset registry
        
        Args:
            registry_path: Path to store registry data
            auto_discover: Whether to automatically discover datasets
        """
        # Set up paths
        if registry_path:
            self.registry_dir = Path(registry_path)
        else:
            # Default to project data directory
            base_dir = Path(os.environ.get("DRAVIK_DATA_DIR", "data"))
            self.registry_dir = base_dir / "registry"
            
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up registry database
        self.db_path = self.registry_dir / "datasets.db"
        self._setup_database()
        
        # Cache for faster lookups
        self._dataset_cache = {}
        self._metadata_cache = {}
        
        # Auto-discover datasets if requested
        if auto_discover:
            self.discover_datasets()
            
    def _setup_database(self) -> None:
        """Set up the registry database schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create datasets table
        c.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            storage_path TEXT,
            format TEXT,
            source TEXT,
            num_rows INTEGER,
            num_columns INTEGER,
            description TEXT,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # Create dataset versions table for tracking version history
        c.execute('''
        CREATE TABLE IF NOT EXISTS dataset_versions (
            dataset_id TEXT NOT NULL,
            version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            storage_path TEXT,
            num_rows INTEGER,
            description TEXT,
            PRIMARY KEY (dataset_id, version),
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
        ''')
        
        # Create metadata table
        c.execute('''
        CREATE TABLE IF NOT EXISTS dataset_metadata (
            dataset_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (dataset_id, key),
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
        ''')
        
        # Create usage log table
        c.execute('''
        CREATE TABLE IF NOT EXISTS dataset_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
        ''')
        
        # Create tags table
        c.execute('''
        CREATE TABLE IF NOT EXISTS dataset_tags (
            dataset_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (dataset_id, tag),
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def register_dataset(self, 
                        dataset: Dataset, 
                        tags: Optional[List[str]] = None,
                        overwrite: bool = False) -> str:
        """
        Register a dataset in the registry
        
        Args:
            dataset: Dataset to register
            tags: Optional list of tags
            overwrite: Whether to overwrite existing dataset
            
        Returns:
            Dataset ID
        """
        # Generate a unique ID for the dataset
        dataset_id = f"{dataset.name.lower().replace(' ', '_')}_{str(dataset.version)}"
        
        # Check if dataset already exists
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id FROM datasets WHERE id = ?", (dataset_id,))
        existing = c.fetchone()
        
        if existing and not overwrite:
            conn.close()
            raise ValueError(f"Dataset '{dataset_id}' already exists. Use overwrite=True to replace it.")
            
        current_time = datetime.now().isoformat()
        
        # Save dataset to storage
        storage_path = self._save_dataset_to_storage(dataset)
        
        # Get dataset information
        metadata = dataset.metadata.to_dict()
        num_rows = dataset.num_rows
        num_columns = dataset.num_columns
        
        # Register in database
        if existing:
            # Update existing record
            c.execute('''
            UPDATE datasets
            SET version = ?, updated_at = ?, storage_path = ?, 
                format = ?, num_rows = ?, num_columns = ?, description = ?
            WHERE id = ?
            ''', (
                str(dataset.version), current_time, str(storage_path),
                storage_path.suffix[1:] if storage_path else None,
                num_rows, num_columns, metadata.get('description', ''),
                dataset_id
            ))
        else:
            # Insert new record
            c.execute('''
            INSERT INTO datasets
            (id, name, version, created_at, updated_at, storage_path, 
             format, source, num_rows, num_columns, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_id, dataset.name, str(dataset.version),
                current_time, current_time, str(storage_path),
                storage_path.suffix[1:] if storage_path else None,
                metadata.get('source', None),
                num_rows, num_columns, metadata.get('description', '')
            ))
            
        # Add version history
        c.execute('''
        INSERT OR REPLACE INTO dataset_versions
        (dataset_id, version, created_at, storage_path, num_rows, description)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            dataset_id, str(dataset.version), current_time,
            str(storage_path), num_rows, metadata.get('description', '')
        ))
        
        # Save metadata
        for key, value in metadata.items():
            # Skip complex values that won't serialize well
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, (str, int, float, bool, type(None))):
                value = str(value)
                
            c.execute('''
            INSERT OR REPLACE INTO dataset_metadata
            (dataset_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (dataset_id, key, value, current_time))
            
        # Add tags
        if tags:
            for tag in tags:
                c.execute('''
                INSERT OR IGNORE INTO dataset_tags
                (dataset_id, tag)
                VALUES (?, ?)
                ''', (dataset_id, tag))
                
        # Log operation
        c.execute('''
        INSERT INTO dataset_usage
        (dataset_id, operation, timestamp, details)
        VALUES (?, ?, ?, ?)
        ''', (
            dataset_id, 
            "register" if not existing else "update", 
            current_time,
            json.dumps({"version": str(dataset.version)})
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self._dataset_cache[dataset_id] = dataset
        self._metadata_cache[dataset_id] = metadata
        
        return dataset_id
    
    def _save_dataset_to_storage(self, dataset: Dataset) -> Path:
        """
        Save dataset to persistent storage
        
        Args:
            dataset: Dataset to save
            
        Returns:
            Path where dataset was saved
        """
        # Create storage directory
        storage_dir = self.registry_dir / "datasets" / dataset.name
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine filename with version
        version_str = str(dataset.version).replace('.', '_').replace('/', '_')
        filename = f"{dataset.name}_{version_str}.parquet"
        storage_path = storage_dir / filename
        
        # Save dataset
        dataset.save(str(storage_path), format="parquet")
        
        return storage_path
    
    def get_dataset(self, 
                  dataset_id: str, 
                  version: Optional[str] = None) -> Optional[Dataset]:
        """
        Retrieve a dataset from the registry
        
        Args:
            dataset_id: Dataset ID
            version: Optional specific version
            
        Returns:
            Dataset object or None if not found
        """
        # Check cache first
        cache_key = f"{dataset_id}_{version}" if version else dataset_id
        if cache_key in self._dataset_cache:
            return self._dataset_cache[cache_key]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if version:
            # Get specific version
            c.execute('''
            SELECT d.name, dv.version, dv.storage_path, d.description
            FROM datasets d
            JOIN dataset_versions dv ON d.id = dv.dataset_id
            WHERE d.id = ? AND dv.version = ?
            ''', (dataset_id, version))
        else:
            # Get latest version
            c.execute('''
            SELECT name, version, storage_path, description
            FROM datasets
            WHERE id = ? AND is_active = 1
            ''', (dataset_id,))
            
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        name, version, storage_path, description = row
        
        if not storage_path or not Path(storage_path).exists():
            logger.warning(f"Dataset file not found: {storage_path}")
            return None
        
        # Load dataset from storage
        try:
            dataset = Dataset.load(storage_path)
            
            # Get metadata
            metadata = self.get_dataset_metadata(dataset_id)
            if metadata:
                dataset.metadata.update(metadata)
                
            # Update cache
            self._dataset_cache[cache_key] = dataset
            
            # Log usage
            self._log_dataset_usage(dataset_id, "retrieve")
            
            return dataset
        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_id}: {e}")
            return None
    
    def get_dataset_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get metadata for a dataset
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dictionary of metadata
        """
        if dataset_id in self._metadata_cache:
            return self._metadata_cache[dataset_id]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
        SELECT key, value
        FROM dataset_metadata
        WHERE dataset_id = ?
        ''', (dataset_id,))
        
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return {}
        
        metadata = {}
        for key, value in rows:
            # Try to parse JSON values
            if value and (value.startswith('{') or value.startswith('[')):
                try:
                    metadata[key] = json.loads(value)
                    continue
                except json.JSONDecodeError:
                    pass
            metadata[key] = value
            
        # Cache the result
        self._metadata_cache[dataset_id] = metadata
        
        return metadata
    
    def list_datasets(self, 
                     tags: Optional[List[str]] = None,
                     source: Optional[str] = None,
                     active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List available datasets
        
        Args:
            tags: Optional filter by tags
            source: Optional filter by source
            active_only: Whether to show only active datasets
            
        Returns:
            List of dataset information dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        c = conn.cursor()
        
        query = '''
        SELECT d.id, d.name, d.version, d.created_at, d.updated_at,
               d.storage_path, d.format, d.source, d.num_rows,
               d.num_columns, d.description
        FROM datasets d
        '''
        
        params = []
        where_clauses = []
        
        if active_only:
            where_clauses.append("d.is_active = 1")
            
        if source:
            where_clauses.append("d.source = ?")
            params.append(source)
            
        if tags:
            placeholders = ', '.join(['?'] * len(tags))
            query += f'''
            JOIN (
                SELECT dataset_id, COUNT(tag) as tag_count
                FROM dataset_tags
                WHERE tag IN ({placeholders})
                GROUP BY dataset_id
                HAVING tag_count = {len(tags)}
            ) t ON d.id = t.dataset_id
            '''
            params.extend(tags)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        c.execute(query, params)
        rows = c.fetchall()
        
        result = []
        for row in rows:
            # Convert row to dict
            dataset_info = dict(row)
            
            # Add tags
            c.execute('''
            SELECT tag FROM dataset_tags WHERE dataset_id = ?
            ''', (row['id'],))
            dataset_info['tags'] = [tag[0] for tag in c.fetchall()]
            
            result.append(dataset_info)
            
        conn.close()
        return result
    
    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for datasets by name, description, or tags
        
        Args:
            query: Search query string
            
        Returns:
            List of matching datasets
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Use LIKE for simple text search
        search_term = f"%{query}%"
        
        c.execute('''
        SELECT DISTINCT d.id, d.name, d.version, d.created_at, d.description
        FROM datasets d
        LEFT JOIN dataset_tags t ON d.id = t.dataset_id
        WHERE d.name LIKE ? 
           OR d.description LIKE ?
           OR t.tag LIKE ?
        AND d.is_active = 1
        ''', (search_term, search_term, search_term))
        
        rows = c.fetchall()
        
        result = []
        for row in rows:
            # Convert row to dict
            dataset_info = dict(row)
            
            # Add tags
            c.execute('''
            SELECT tag FROM dataset_tags WHERE dataset_id = ?
            ''', (row['id'],))
            dataset_info['tags'] = [tag[0] for tag in c.fetchall()]
            
            result.append(dataset_info)
            
        conn.close()
        return result
    
    def delete_dataset(self, 
                      dataset_id: str, 
                      delete_files: bool = False) -> bool:
        """
        Delete a dataset from the registry
        
        Args:
            dataset_id: Dataset ID
            delete_files: Whether to delete the actual data files
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get storage path if we're deleting files
        if delete_files:
            c.execute("SELECT storage_path FROM datasets WHERE id = ?", (dataset_id,))
            row = c.fetchone()
            storage_path = row[0] if row else None
        
        # Mark as inactive instead of actually deleting
        c.execute("UPDATE datasets SET is_active = 0 WHERE id = ?", (dataset_id,))
        
        # Log deletion
        current_time = datetime.now().isoformat()
        c.execute('''
        INSERT INTO dataset_usage
        (dataset_id, operation, timestamp, details)
        VALUES (?, ?, ?, ?)
        ''', (
            dataset_id, "delete", current_time,
            json.dumps({"delete_files": delete_files})
        ))
        
        conn.commit()
        conn.close()
        
        # Delete files if requested
        if delete_files and storage_path and Path(storage_path).exists():
            try:
                Path(storage_path).unlink()
                # Also try to delete metadata file
                metadata_path = Path(storage_path).with_suffix(".metadata.json")
                if metadata_path.exists():
                    metadata_path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete dataset files: {e}")
                return False
        
        # Clear from cache
        if dataset_id in self._dataset_cache:
            del self._dataset_cache[dataset_id]
        if dataset_id in self._metadata_cache:
            del self._metadata_cache[dataset_id]
            
        return True
    
    def add_dataset_tags(self, dataset_id: str, tags: List[str]) -> bool:
        """
        Add tags to a dataset
        
        Args:
            dataset_id: Dataset ID
            tags: List of tags to add
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if dataset exists
        c.execute("SELECT id FROM datasets WHERE id = ?", (dataset_id,))
        if not c.fetchone():
            conn.close()
            return False
            
        # Add tags
        for tag in tags:
            c.execute('''
            INSERT OR IGNORE INTO dataset_tags
            (dataset_id, tag)
            VALUES (?, ?)
            ''', (dataset_id, tag))
            
        conn.commit()
        conn.close()
        return True
    
    def remove_dataset_tags(self, dataset_id: str, tags: List[str]) -> bool:
        """
        Remove tags from a dataset
        
        Args:
            dataset_id: Dataset ID
            tags: List of tags to remove
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if dataset exists
        c.execute("SELECT id FROM datasets WHERE id = ?", (dataset_id,))
        if not c.fetchone():
            conn.close()
            return False
            
        # Remove tags
        for tag in tags:
            c.execute('''
            DELETE FROM dataset_tags
            WHERE dataset_id = ? AND tag = ?
            ''', (dataset_id, tag))
            
        conn.commit()
        conn.close()
        return True
    
    def discover_datasets(self, 
                         directories: Optional[List[str]] = None) -> List[str]:
        """
        Discover datasets in the filesystem
        
        Args:
            directories: Optional list of directories to search
            
        Returns:
            List of discovered dataset IDs
        """
        search_dirs = []
        
        if directories:
            search_dirs = [Path(d) for d in directories]
        else:
            # Default search locations
            base_dir = Path(os.environ.get("DRAVIK_DATA_DIR", "data"))
            search_dirs = [
                base_dir / "datasets",
                Path("datasets"),
                Path.cwd() / "datasets",
                Path.home() / "dravik" / "datasets"
            ]
            
        discovered_ids = []
        
        for search_dir in search_dirs:
            if not search_dir.exists() or not search_dir.is_dir():
                continue
                
            # Look for parquet files
            for parquet_file in search_dir.glob("**/*.parquet"):
                try:
                    # Try to load as dataset
                    dataset = Dataset.load(str(parquet_file))
                    
                    # Register
                    dataset_id = self.register_dataset(dataset)
                    discovered_ids.append(dataset_id)
                except Exception as e:
                    logger.warning(f"Failed to load discovered dataset {parquet_file}: {e}")
                    
        return discovered_ids
    
    def get_dataset_versions(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a dataset
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            List of version information
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
        SELECT version, created_at, storage_path, num_rows, description
        FROM dataset_versions
        WHERE dataset_id = ?
        ORDER BY created_at DESC
        ''', (dataset_id,))
        
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def _log_dataset_usage(self, 
                          dataset_id: str, 
                          operation: str, 
                          details: Optional[Dict[str, Any]] = None) -> None:
        """Log dataset usage"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        current_time = datetime.now().isoformat()
        details_json = json.dumps(details) if details else None
        
        c.execute('''
        INSERT INTO dataset_usage
        (dataset_id, operation, timestamp, details)
        VALUES (?, ?, ?, ?)
        ''', (dataset_id, operation, current_time, details_json))
        
        conn.commit()
        conn.close()
    
    def get_usage_history(self, dataset_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get usage history for datasets
        
        Args:
            dataset_id: Optional dataset ID to filter by
            
        Returns:
            DataFrame with usage history
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT u.id, u.dataset_id, d.name as dataset_name, 
               u.operation, u.timestamp, u.details
        FROM dataset_usage u
        JOIN datasets d ON u.dataset_id = d.id
        '''
        
        if dataset_id:
            query += " WHERE u.dataset_id = ?"
            df = pd.read_sql_query(query, conn, params=(dataset_id,))
        else:
            df = pd.read_sql_query(query, conn)
            
        conn.close()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Parse details JSON
        def parse_details(details):
            if not details:
                return {}
            try:
                return json.loads(details)
            except:
                return {}
                
        df['details_parsed'] = df['details'].apply(parse_details)
        
        return df
    
    def export_registry_summary(self, format: str = 'csv') -> str:
        """
        Export a summary of the dataset registry
        
        Args:
            format: Output format ('csv' or 'json')
            
        Returns:
            Path to the exported file
        """
        # Get all datasets
        datasets = self.list_datasets(active_only=False)
        
        if not datasets:
            return None
            
        # Create DataFrame
        df = pd.DataFrame(datasets)
        
        # Format timestamps
        for col in ['created_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                
        # Export to requested format
        export_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = self.registry_dir / f"registry_export_{export_time}.{format}"
        
        if format == 'csv':
            df.to_csv(export_path, index=False)
        elif format == 'json':
            df.to_json(export_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        return str(export_path)
