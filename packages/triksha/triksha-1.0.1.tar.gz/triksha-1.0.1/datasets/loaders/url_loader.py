"""
URL Dataset Loader

Loads datasets from remote URLs (HTTP, HTTPS, FTP)
"""

import os
import logging
import tempfile
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import pyarrow as pa
from pathlib import Path
import json
import requests
import io
import re
from urllib.parse import urlparse

from .base_loader import BaseLoader
from .file_loader import FileLoader

logger = logging.getLogger(__name__)

class UrlLoader(BaseLoader):
    """
    Professional loader for URL-based datasets
    
    Features:
    - Support for HTTP(S) and FTP URLs
    - Automatic format detection based on URL or content
    - Customizable request parameters
    - Caching to prevent redundant downloads
    - Support for authentication
    """
    
    def __init__(self, 
                cache_dir: Optional[str] = None,
                request_timeout: int = 60,
                headers: Optional[Dict[str, str]] = None):
        """
        Initialize URL loader
        
        Args:
            cache_dir: Optional cache directory
            request_timeout: Request timeout in seconds
            headers: Optional HTTP headers
        """
        super().__init__(cache_dir)
        self.request_timeout = request_timeout
        self.headers = headers or {}
        
        # Initialize file loader for handling different formats
        self.file_loader = FileLoader(cache_dir=cache_dir)
    
    def supports(self, source: str) -> bool:
        """
        Check if this loader supports the given source
        
        Args:
            source: URL
            
        Returns:
            True if this loader can handle the source
        """
        if not source:
            return False
            
        # Check if it's a URL
        try:
            parsed = urlparse(source)
            return parsed.scheme in ['http', 'https', 'ftp']
        except:
            return False
    
    def load(self, 
            source: str,
            file_format: Optional[str] = None,
            cache: bool = True,
            auth: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
        """
        Load a dataset from a URL
        
        Args:
            source: URL to the dataset
            file_format: Optional format override
            cache: Whether to cache the downloaded file
            auth: Optional authentication (username/password)
            params: Optional URL parameters
            **kwargs: Additional options passed to the pandas reader
            
        Returns:
            Loaded dataset as a dictionary or DataFrame
        """
        # Parse URL
        parsed_url = urlparse(source)
        
        # Determine cache path if caching is enabled
        cache_path = None
        if cache:
            cache_dir = self._ensure_cache_dir()
            url_hash = self._hash_url(source)
            
            # Use URL filename if available, otherwise use hash
            url_filename = os.path.basename(parsed_url.path)
            if url_filename and '.' in url_filename:
                cache_path = cache_dir / f"{url_hash}_{url_filename}"
            else:
                # Determine extension based on file_format or guess from URL
                extension = self._guess_extension(source, file_format)
                cache_path = cache_dir / f"{url_hash}{extension}"
        
        # Check if cached version exists
        if cache and cache_path and cache_path.exists():
            logger.info(f"Loading {source} from cache at {cache_path}")
            return self.file_loader.load(
                str(cache_path),
                file_format=file_format,
                **kwargs
            )
        
        # Download the file
        logger.info(f"Downloading dataset from {source}")
        
        try:
            # Handle different URL schemes
            if parsed_url.scheme in ['http', 'https']:
                content = self._download_http(source, auth, params)
            elif parsed_url.scheme == 'ftp':
                content = self._download_ftp(source, auth)
            else:
                raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
                
            # Save to cache if enabled
            if cache and cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_path, 'wb') as f:
                    f.write(content)
                logger.info(f"Cached downloaded content to {cache_path}")
                
                # Load from the cache file
                return self.file_loader.load(
                    str(cache_path),
                    file_format=file_format,
                    **kwargs
                )
            else:
                # Load directly from memory
                extension = self._guess_extension(source, file_format)
                return self._load_from_memory(content, extension, **kwargs)
                
        except Exception as e:
            logger.error(f"Error downloading dataset from {source}: {e}")
            raise
    
    def _download_http(self, 
                      url: str, 
                      auth: Optional[Dict[str, str]] = None,
                      params: Optional[Dict[str, Any]] = None) -> bytes:
        """Download content using HTTP(S)"""
        # Prepare request
        headers = self.headers.copy()
        
        # Set up auth
        auth_tuple = None
        if auth and 'username' in auth and 'password' in auth:
            auth_tuple = (auth['username'], auth['password'])
            
        # Make request
        response = requests.get(
            url,
            headers=headers,
            auth=auth_tuple,
            params=params,
            timeout=self.request_timeout
        )
        
        # Check for successful response
        response.raise_for_status()
        
        return response.content
    
    def _download_ftp(self, 
                     url: str, 
                     auth: Optional[Dict[str, str]] = None) -> bytes:
        """Download content using FTP"""
        from ftplib import FTP
        from io import BytesIO
        
        parsed = urlparse(url)
        
        # Extract host, path and filename
        host = parsed.netloc
        path_parts = parsed.path.strip('/').split('/')
        filename = path_parts[-1]
        directory = '/'.join(path_parts[:-1])
        
        # Prepare FTP client
        ftp = FTP(host)
        
        # Login
        if auth and 'username' in auth and 'password' in auth:
            ftp.login(auth['username'], auth['password'])
        else:
            ftp.login()
            
        # Change to directory if needed
        if directory:
            ftp.cwd(directory)
            
        # Download file
        buffer = BytesIO()
        ftp.retrbinary(f'RETR {filename}', buffer.write)
        ftp.quit()
        
        return buffer.getvalue()
    
    def _guess_extension(self, url: str, format_override: Optional[str] = None) -> str:
        """Guess file extension from URL or format override"""
        if format_override:
            return f".{format_override.lower()}"
            
        # Try to extract extension from URL
        parsed = urlparse(url)
        path = parsed.path
        
        # Look for known extensions
        for ext in self.file_loader.SUPPORTED_FORMATS.keys():
            if path.endswith(ext):
                return ext
                
        # Check for format hints in the URL
        if 'csv' in path.lower():
            return '.csv'
        elif 'json' in path.lower():
            return '.json'
        elif 'excel' in path.lower() or 'xls' in path.lower():
            return '.xlsx'
        elif 'parquet' in path.lower() or 'pq' in path.lower():
            return '.parquet'
            
        # Default to CSV if we can't determine
        return '.csv'
    
    def _load_from_memory(self, 
                         content: bytes, 
                         extension: str, 
                         **kwargs) -> Union[Dict[str, Any], pd.DataFrame]:
        """Load data directly from memory"""
        # Create a file-like object
        buffer = io.BytesIO(content)
        
        # Use appropriate pandas reader based on extension
        if extension in ['.csv', '.tsv', '.txt']:
            return pd.read_csv(buffer, **kwargs)
        elif extension in ['.json', '.jsonl']:
            # Check if it's JSON or JSONL
            try:
                content_str = content.decode('utf-8')
                first_char = content_str.strip()[0]
                if first_char == '[':
                    # Likely JSON array
                    return pd.read_json(buffer, **kwargs)
                elif first_char == '{':
                    # Check if it's a JSON object or JSONL
                    if '\n' in content_str and content_str.strip().count('{') > 1:
                        # Likely JSONL
                        return pd.read_json(buffer, lines=True, **kwargs)
                    else:
                        # Single JSON object
                        return pd.read_json(buffer, **kwargs)
                else:
                    # Default to regular JSON
                    return pd.read_json(buffer, **kwargs)
            except:
                # Fall back to standard read_json
                buffer.seek(0)
                return pd.read_json(buffer, **kwargs)
        elif extension in ['.xlsx', '.xls']:
            return pd.read_excel(buffer, **kwargs)
        elif extension in ['.parquet', '.pq']:
            return pd.read_parquet(buffer, **kwargs)
        elif extension in ['.feather', '.arrow']:
            return pd.read_feather(buffer, **kwargs)
        else:
            # Default to CSV for unknown types
            return pd.read_csv(buffer, **kwargs)
    
    def _hash_url(self, url: str) -> str:
        """Create a hash from a URL for caching"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
