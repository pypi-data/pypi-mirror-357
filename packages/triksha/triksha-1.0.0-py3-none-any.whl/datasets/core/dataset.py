"""
Core Dataset class for Dravik ML operations
"""

import os
import json
import hashlib
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Iterator, Tuple
from pathlib import Path
from datetime import datetime
from pandas import DataFrame
import pyarrow as pa
import pyarrow.parquet as pq
from ..loaders.base_loader import BaseLoader
from .metadata import DatasetMetadata
from .version import DatasetVersion

logger = logging.getLogger(__name__)

class Dataset:
    """
    Professional-grade Dataset implementation with comprehensive
    management, versioning, and transformation capabilities.
    
    Features:
    - Streaming support for large datasets
    - Automatic versioning
    - Data validation
    - Schema enforcement
    - Export to various formats
    - Metadata tracking
    - Performance optimizations
    """
    
    def __init__(self, 
                 name: str, 
                 data: Optional[Union[Dict, DataFrame, pa.Table]] = None,
                 source: Optional[str] = None,
                 version: Optional[str] = None,
                 description: Optional[str] = None,
                 path: Optional[str] = None,
                 schema: Optional[pa.Schema] = None,
                 columns: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a dataset with data or path
        
        Args:
            name: Unique name for the dataset
            data: Optional data in various formats
            source: Source of the dataset (local, huggingface, url, etc.)
            version: Version string (auto-generated if None)
            description: Human-readable description
            path: Path for storage/retrieval
            schema: PyArrow schema for validation
            columns: List of column names if data is not structured yet
            metadata: Additional metadata dictionary
        """
        self.name = name
        self._data = None
        self._arrow_table = None
        self._dataframe = None
        self._source = source
        self._path = Path(path) if path else None
        self._schema = schema
        self._is_streaming = False
        self._stream_iterator = None
        self._columns = columns or []
        
        # Set up metadata tracking
        self.metadata = DatasetMetadata()
        if metadata:
            self.metadata.update(metadata)
        
        # Add default metadata
        self.metadata.set("created_at", datetime.now().isoformat())
        self.metadata.set("name", name)
        self.metadata.set("description", description or "")
        
        # Initialize versioning
        self.version = DatasetVersion(version)
        
        # Load the data if provided
        if data is not None:
            self.load_data(data)
            # Generate a version hash based on data content
            if not version:
                self.version.auto_generate_hash(self)
        
        self._initialized = True
    
    def load_data(self, data: Union[Dict, DataFrame, pa.Table]) -> None:
        """
        Load data into the dataset from various formats
        
        Args:
            data: Data in dictionary, pandas DataFrame or PyArrow Table format
        """
        if isinstance(data, dict):
            self._data = data
            # Convert to DataFrame for operations
            try:
                if "data" in data and isinstance(data["data"], list):
                    self._dataframe = pd.DataFrame(data["data"])
                elif all(isinstance(v, list) for v in data.values()):
                    self._dataframe = pd.DataFrame(data)
                else:
                    # Handle nested dictionary
                    self._dataframe = pd.json_normalize(data)
                
                # Create PyArrow table for efficient operations
                self._arrow_table = pa.Table.from_pandas(self._dataframe)
                
            except Exception as e:
                logger.warning(f"Could not convert dict to DataFrame: {e}")
                
        elif isinstance(data, pd.DataFrame):
            self._dataframe = data
            self._arrow_table = pa.Table.from_pandas(data)
            self._data = data.to_dict("list")
            
        elif isinstance(data, pa.Table):
            self._arrow_table = data
            self._dataframe = data.to_pandas()
            self._data = self._dataframe.to_dict("list")
            
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        
        # Extract column names if available
        if self._dataframe is not None:
            self._columns = list(self._dataframe.columns)
        
        # Update metadata
        self.metadata.set("num_rows", self.num_rows)
        self.metadata.set("num_columns", self.num_columns)
        self.metadata.set("column_names", self._columns)
    
    @property
    def num_rows(self) -> int:
        """Get the number of rows in the dataset"""
        if self._dataframe is not None:
            return len(self._dataframe)
        elif self._arrow_table is not None:
            return self._arrow_table.num_rows
        elif self._data is not None and len(self._data) > 0:
            if isinstance(next(iter(self._data.values())), list):
                return len(next(iter(self._data.values())))
        return 0
    
    @property
    def num_columns(self) -> int:
        """Get the number of columns in the dataset"""
        return len(self._columns)
    
    @property
    def schema(self) -> pa.Schema:
        """Get the schema of the dataset"""
        if self._arrow_table is not None:
            return self._arrow_table.schema
        elif self._schema is not None:
            return self._schema
        elif self._dataframe is not None:
            return pa.Schema.from_pandas(self._dataframe)
        return None
    
    def head(self, n: int = 5) -> Union[DataFrame, Dict]:
        """
        Return the first n rows of the dataset
        
        Args:
            n: Number of rows to return
            
        Returns:
            First n rows as DataFrame or dict
        """
        if self._dataframe is not None:
            return self._dataframe.head(n)
        elif self._data is not None:
            result = {}
            for key, values in self._data.items():
                if isinstance(values, list) and len(values) > 0:
                    result[key] = values[:min(n, len(values))]
                else:
                    result[key] = values
            return result
        return None
    
    def sample(self, n: int = 5) -> Union[DataFrame, Dict]:
        """
        Return a random sample of n rows
        
        Args:
            n: Number of rows to sample
            
        Returns:
            Random sample as DataFrame or dict
        """
        if self._dataframe is not None:
            return self._dataframe.sample(min(n, len(self._dataframe)))
        elif self._arrow_table is not None:
            # Sample from PyArrow table
            indices = np.random.choice(self._arrow_table.num_rows, 
                                     min(n, self._arrow_table.num_rows), 
                                     replace=False)
            return self._arrow_table.take(indices).to_pandas()
        return self.head(n)
    
    def to_pandas(self) -> DataFrame:
        """Convert dataset to pandas DataFrame"""
        if self._dataframe is not None:
            return self._dataframe
        elif self._arrow_table is not None:
            return self._arrow_table.to_pandas()
        elif self._data is not None:
            return pd.DataFrame(self._data)
        return pd.DataFrame()
    
    def to_pyarrow(self) -> pa.Table:
        """Convert dataset to PyArrow Table"""
        if self._arrow_table is not None:
            return self._arrow_table
        elif self._dataframe is not None:
            return pa.Table.from_pandas(self._dataframe)
        elif self._data is not None:
            return pa.Table.from_pandas(pd.DataFrame(self._data))
        return None
    
    def to_dict(self) -> Dict:
        """Convert dataset to dictionary"""
        if self._data is not None:
            return self._data
        elif self._dataframe is not None:
            return self._dataframe.to_dict("list")
        elif self._arrow_table is not None:
            return self._arrow_table.to_pandas().to_dict("list")
        return {}
    
    def save(self, path: Optional[str] = None, format: str = "parquet") -> str:
        """
        Save dataset to disk in specified format
        
        Args:
            path: Path to save dataset (defaults to self._path)
            format: Format to save in ('parquet', 'csv', 'jsonl')
            
        Returns:
            Path where dataset was saved
        """
        if path:
            save_path = Path(path)
        elif self._path:
            save_path = self._path
        else:
            # Default path in project data directory
            save_path = Path(os.environ.get("DRAVIK_DATA_DIR", "data")) / "datasets" / f"{self.name}_{self.version}"
        
        # Create directory if it doesn't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add extension if it's not there
        if not save_path.name.endswith(f".{format}"):
            save_path = save_path.with_suffix(f".{format}")
        
        # Save in the specified format
        if format == "parquet":
            table = self.to_pyarrow()
            if table:
                # Add metadata before saving
                metadata = {
                    "name": self.name,
                    "version": str(self.version),
                    "created_at": self.metadata.get("created_at"),
                    "rows": str(self.num_rows),
                    "columns": ",".join(self._columns)
                }
                # Convert metadata to bytes
                for key, value in metadata.items():
                    table = table.replace_schema_metadata({
                        **table.schema.metadata, 
                        key.encode(): str(value).encode()
                    })
                pq.write_table(table, save_path)
        
        elif format == "csv":
            df = self.to_pandas()
            df.to_csv(save_path, index=False)
            
        elif format == "jsonl":
            df = self.to_pandas()
            with open(save_path, 'w') as f:
                for _, row in df.iterrows():
                    f.write(json.dumps(row.to_dict()) + '\n')
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save metadata file alongside dataset
        metadata_path = save_path.with_suffix(".metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
        
        return str(save_path)
    
    @classmethod
    def load(cls, path: str, format: Optional[str] = None) -> 'Dataset':
        """
        Load dataset from disk
        
        Args:
            path: Path to the dataset file
            format: Format override (auto-detected from extension if None)
            
        Returns:
            Loaded Dataset object
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        
        # Auto-detect format from extension if not provided
        if not format:
            suffix = path_obj.suffix.lower()
            if suffix == '.parquet':
                format = 'parquet'
            elif suffix == '.csv':
                format = 'csv'
            elif suffix in ['.jsonl', '.json']:
                format = 'jsonl'
            else:
                raise ValueError(f"Could not determine format from file extension: {suffix}")
        
        # Load metadata if available
        metadata = {}
        metadata_path = path_obj.with_suffix(".metadata.json")
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        # Load data based on format
        if format == 'parquet':
            table = pq.read_table(path)
            # Extract metadata from parquet file
            table_metadata = table.schema.metadata
            name = table_metadata.get(b'name', b'').decode() or path_obj.stem
            version = table_metadata.get(b'version', b'').decode()
            
            return cls(name=name, data=table, path=path, 
                       metadata=metadata, version=version)
        
        elif format == 'csv':
            df = pd.read_csv(path)
            return cls(name=path_obj.stem, data=df, path=path, metadata=metadata)
        
        elif format == 'jsonl':
            # Read jsonl line by line
            rows = []
            with open(path, 'r') as f:
                for line in f:
                    rows.append(json.loads(line.strip()))
            df = pd.DataFrame(rows)
            return cls(name=path_obj.stem, data=df, path=path, metadata=metadata)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def stream(self, batch_size: int = 1000) -> Iterator[Union[DataFrame, Dict]]:
        """
        Create a data streaming iterator for processing large datasets
        
        Args:
            batch_size: Number of rows per batch
            
        Returns:
            Iterator yielding batches of data
        """
        if self._arrow_table is not None:
            # Stream from PyArrow table in batches
            num_batches = (self._arrow_table.num_rows + batch_size - 1) // batch_size
            for i in range(num_batches):
                start = i * batch_size
                end = min(start + batch_size, self._arrow_table.num_rows)
                yield self._arrow_table.slice(start, end - start).to_pandas()
        
        elif self._dataframe is not None:
            # Stream from pandas DataFrame in batches
            for i in range(0, len(self._dataframe), batch_size):
                yield self._dataframe.iloc[i:i+batch_size]
        
        elif self._data is not None:
            # Stream from dictionary in batches
            num_rows = self.num_rows
            for i in range(0, num_rows, batch_size):
                batch = {}
                for key, values in self._data.items():
                    if isinstance(values, list):
                        batch[key] = values[i:min(i+batch_size, num_rows)]
                    else:
                        batch[key] = values
                yield batch
    
    def filter(self, condition_callable) -> 'Dataset':
        """
        Filter dataset rows based on a condition function
        
        Args:
            condition_callable: Function that takes a row and returns boolean
            
        Returns:
            New filtered Dataset
        """
        if self._dataframe is not None:
            if callable(condition_callable):
                filtered_df = self._dataframe[self._dataframe.apply(condition_callable, axis=1)]
            else:
                filtered_df = self._dataframe[condition_callable]  # For pandas.Series conditions
                
            return Dataset(
                name=f"{self.name}_filtered",
                data=filtered_df,
                source=self._source,
                version=f"{self.version}_filtered",
                metadata=self.metadata.to_dict()
            )
        else:
            # Fall back to pandas for filtering
            return self.filter(condition_callable)
    
    def transform(self, transformer_callable) -> 'Dataset':
        """
        Apply a transformation function to the dataset
        
        Args:
            transformer_callable: Function that transforms the dataset
            
        Returns:
            New transformed Dataset
        """
        if self._dataframe is not None:
            transformed_df = transformer_callable(self._dataframe)
            return Dataset(
                name=f"{self.name}_transformed",
                data=transformed_df,
                source=self._source,
                version=f"{self.version}_transformed",
                metadata=self.metadata.to_dict()
            )
        elif self._arrow_table is not None:
            # Convert to pandas for transformation
            transformed_df = transformer_callable(self._arrow_table.to_pandas())
            return Dataset(
                name=f"{self.name}_transformed",
                data=transformed_df,
                source=self._source,
                version=f"{self.version}_transformed",
                metadata=self.metadata.to_dict()
            )
        else:
            raise ValueError("Dataset cannot be transformed without DataFrame or Arrow Table")
    
    def summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the dataset
        
        Returns:
            Dictionary with dataset summary information
        """
        summary = {
            "name": self.name,
            "version": str(self.version),
            "rows": self.num_rows,
            "columns": self.num_columns,
            "column_names": self._columns,
            "memory_usage": None,
            "source": self._source,
            "created_at": self.metadata.get("created_at"),
            "description": self.metadata.get("description")
        }
        
        # Add memory usage if available
        if self._dataframe is not None:
            summary["memory_usage"] = self._dataframe.memory_usage(deep=True).sum()
        
        # Add data types
        if self._dataframe is not None:
            summary["dtypes"] = {col: str(dtype) for col, dtype in self._dataframe.dtypes.items()}
        
        # Add statistics if available
        if self._dataframe is not None and self.num_rows > 0:
            try:
                # Only compute stats for numeric columns
                numeric_cols = self._dataframe.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    stats = self._dataframe[numeric_cols].describe().to_dict()
                    summary["statistics"] = stats
            except Exception as e:
                logger.warning(f"Could not compute statistics: {e}")
        
        return summary
    
    def __repr__(self) -> str:
        """String representation of the dataset"""
        return f"Dataset(name='{self.name}', rows={self.num_rows}, columns={self.num_columns}, version={self.version})"
    
    def __len__(self) -> int:
        """Get the number of rows in the dataset"""
        return self.num_rows
