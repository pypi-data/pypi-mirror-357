"""
File Dataset Loader

Loads datasets from local files in various formats
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import pyarrow as pa
import json
import yaml
from pathlib import Path
import csv

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class FileLoader(BaseLoader):
    """
    Professional loader for file-based datasets
    
    Features:
    - Support for multiple file formats (CSV, JSON, JSONL, Excel, Parquet, Feather, etc.)
    - Smart format detection
    - Customizable loading options
    - Comprehensive error handling
    """
    
    # Supported file extensions and their corresponding pandas read functions
    SUPPORTED_FORMATS = {
        '.csv': 'read_csv',
        '.tsv': 'read_csv',
        '.json': 'read_json',
        '.jsonl': 'read_json',
        '.xlsx': 'read_excel',
        '.xls': 'read_excel',
        '.parquet': 'read_parquet',
        '.pq': 'read_parquet',
        '.feather': 'read_feather',
        '.arrow': 'read_feather',
        '.pickle': 'read_pickle',
        '.pkl': 'read_pickle',
        '.yaml': None,  # Custom handling
        '.yml': None,   # Custom handling
        '.txt': 'read_csv',  # Default to CSV for .txt
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize file loader
        
        Args:
            cache_dir: Optional directory to cache processed data
        """
        super().__init__(cache_dir)
    
    def supports(self, source: str) -> bool:
        """
        Check if this loader supports the given source
        
        Args:
            source: File path
            
        Returns:
            True if this loader can handle the source
        """
        # Check if it's a file path and if the extension is supported
        if not source:
            return False
            
        path = Path(source)
        
        # Must be a file path that exists
        if not path.is_file() and not source.startswith("file://"):
            return False
            
        # Get file extension and check if supported
        extension = path.suffix.lower()
        return extension in self.SUPPORTED_FORMATS
    
    def load(self, 
            source: str,
            file_format: Optional[str] = None,
            encoding: str = 'utf-8',
            **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
        """
        Load a dataset from a file
        
        Args:
            source: File path
            file_format: Optional format override
            encoding: File encoding
            **kwargs: Additional options passed to the pandas reader
            
        Returns:
            Loaded dataset as DataFrame or dictionary
        """
        path = Path(source)
        
        # Handle file:// URLs
        if source.startswith("file://"):
            path = Path(source.replace("file://", "", 1))
        
        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        # Determine file format
        extension = path.suffix.lower()
        if file_format:
            # User-specified format takes precedence
            format_key = f".{file_format.lower()}"
        else:
            format_key = extension
            
        # Verify format is supported
        if format_key not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {format_key}")
            
        # Get appropriate reader function
        reader_name = self.SUPPORTED_FORMATS[format_key]
        
        # Special handling for specific formats
        try:
            if format_key in ['.yaml', '.yml']:
                return self._load_yaml(path, encoding)
            elif format_key in ['.json', '.jsonl']:
                # Determine if it's regular JSON or JSONL
                if self._is_jsonl(path):
                    return pd.read_json(path, lines=True, encoding=encoding, **kwargs)
                else:
                    return pd.read_json(path, encoding=encoding, **kwargs)
            elif format_key in ['.tsv']:
                # Handle TSV files with tab delimiter
                kwargs['delimiter'] = kwargs.get('delimiter', '\t')
                return pd.read_csv(path, encoding=encoding, **kwargs)
            elif format_key in ['.txt']:
                # Try to infer delimiter for text files
                return self._load_delimited_text(path, encoding, **kwargs)
            else:
                # Use the standard pandas reader for other formats
                reader = getattr(pd, reader_name)
                return reader(path, **kwargs)
                
        except Exception as e:
            logger.error(f"Error loading file {path}: {e}")
            raise
    
    def _load_yaml(self, path: Path, encoding: str = 'utf-8') -> Dict[str, Any]:
        """Load YAML file to dictionary"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                data = yaml.safe_load(f)
            
            # Convert to DataFrame if it's a list of records
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            
            return data
        except Exception as e:
            logger.error(f"Error loading YAML file {path}: {e}")
            raise
    
    def _is_jsonl(self, path: Path) -> bool:
        """Detect if file is JSONL format"""
        try:
            with open(path, 'r') as f:
                first_line = f.readline().strip()
                second_line = f.readline().strip()
                
                # If there's only one line and it starts with [ and ends with ],
                # it's likely a JSON array
                if not second_line and first_line.startswith('[') and first_line.endswith(']'):
                    return False
                    
                # If the first line is a valid JSON object, and there's a second line,
                # it's likely JSONL
                try:
                    json.loads(first_line)
                    return bool(second_line)
                except json.JSONDecodeError:
                    # If the first line isn't valid JSON, check if the whole file is valid JSON
                    try:
                        with open(path, 'r') as f2:
                            json.load(f2)
                        return False
                    except json.JSONDecodeError:
                        # Neither approach worked, default to False
                        return False
        except Exception:
            # Default to False if we can't determine
            return False
    
    def _load_delimited_text(self, path: Path, encoding: str, **kwargs) -> pd.DataFrame:
        """Load delimited text file with intelligent delimiter detection"""
        # Try to detect delimiter if not specified
        if 'delimiter' not in kwargs and 'sep' not in kwargs:
            with open(path, 'r', encoding=encoding) as f:
                sample = f.readline()
                
                # Count potential delimiters
                delimiters = [',', '\t', '|', ';', ' ']
                counts = {d: sample.count(d) for d in delimiters}
                
                # Use the delimiter with the most occurrences
                best_delimiter = max(counts.items(), key=lambda x: x[1])[0]
                
                # Default to comma if no clear winner
                if counts[best_delimiter] <= 1:
                    best_delimiter = ','
                
                kwargs['delimiter'] = best_delimiter
                
        # Check for header row
        if 'header' not in kwargs:
            # Try to infer if there's a header by checking first row
            with open(path, 'r', encoding=encoding) as f:
                sniffer = csv.Sniffer()
                try:
                    sample = f.read(1024)
                    has_header = sniffer.has_header(sample)
                    kwargs['header'] = 0 if has_header else None
                except:
                    # Default to header=0 if detection fails
                    kwargs['header'] = 0
        
        return pd.read_csv(path, encoding=encoding, **kwargs)
    
    def save(self, 
            data: Union[pd.DataFrame, Dict[str, Any], pa.Table],
            target_path: str,
            file_format: Optional[str] = None,
            **kwargs) -> str:
        """
        Save data to a file
        
        Args:
            data: Data to save
            target_path: Target file path
            file_format: Optional format override
            **kwargs: Additional options passed to the pandas writer
            
        Returns:
            Path where the file was saved
        """
        path = Path(target_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine file format
        extension = path.suffix.lower()
        if file_format:
            # User-specified format takes precedence
            format_key = f".{file_format.lower()}"
        else:
            format_key = extension
            
        # Convert to DataFrame if needed
        if isinstance(data, dict):
            # If it's a nested dictionary, may need special handling
            if any(isinstance(v, dict) for v in data.values()):
                # Flatten nested dictionary for pandas
                flat_data = []
                for k, v in data.items():
                    if isinstance(v, dict):
                        row = {"id": k, **v}
                        flat_data.append(row)
                    else:
                        flat_data.append({"id": k, "value": v})
                df = pd.DataFrame(flat_data)
            else:
                # Simple dictionary
                df = pd.DataFrame([data])
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dictionaries
            df = pd.DataFrame(data)
        elif isinstance(data, pa.Table):
            # Convert PyArrow table to pandas
            df = data.to_pandas()
        else:
            # Assume it's already a DataFrame
            df = data
            
        # Save to file based on format
        try:
            if format_key in ['.yaml', '.yml']:
                if isinstance(data, pd.DataFrame):
                    data_dict = df.to_dict(orient='records')
                    with open(path, 'w') as f:
                        yaml.dump(data_dict, f, default_flow_style=False)
                else:
                    with open(path, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False)
            elif format_key in ['.jsonl']:
                df.to_json(path, orient='records', lines=True, **kwargs)
            elif format_key in ['.json']:
                df.to_json(path, orient='records', **kwargs)
            elif format_key in ['.csv']:
                df.to_csv(path, index=False, **kwargs)
            elif format_key in ['.tsv']:
                df.to_csv(path, sep='\t', index=False, **kwargs)
            elif format_key in ['.parquet', '.pq']:
                df.to_parquet(path, **kwargs)
            elif format_key in ['.feather', '.arrow']:
                df.to_feather(path, **kwargs)
            elif format_key in ['.pickle', '.pkl']:
                df.to_pickle(path, **kwargs)
            elif format_key in ['.xlsx', '.xls']:
                df.to_excel(path, index=False, **kwargs)
            else:
                raise ValueError(f"Unsupported file format for saving: {format_key}")
        except Exception as e:
            logger.error(f"Error saving file {path}: {e}")
            raise
            
        return str(path)
    
    def list_files(self, 
                directory: str, 
                pattern: str = "*.*",
                recursive: bool = True) -> List[str]:
        """
        List files in a directory matching a pattern
        
        Args:
            directory: Directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        path = Path(directory)
        
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory not found: {directory}")
            
        # Get supported extensions
        supported_exts = list(self.SUPPORTED_FORMATS.keys())
        
        # Apply glob pattern
        if recursive:
            all_files = list(path.glob(f"**/{pattern}"))
        else:
            all_files = list(path.glob(pattern))
            
        # Filter to only include files with supported extensions
        supported_files = [
            str(f) for f in all_files 
            if f.is_file() and f.suffix.lower() in supported_exts
        ]
        
        return supported_files
