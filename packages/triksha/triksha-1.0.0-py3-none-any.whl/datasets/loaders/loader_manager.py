"""
Dataset Loader Manager

Manages and dispatches to appropriate loaders based on source type
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Type
from pathlib import Path
import pandas as pd
import pyarrow as pa

from .base_loader import BaseLoader
from .file_loader import FileLoader
from .url_loader import UrlLoader
from .huggingface_loader import HuggingFaceLoader

logger = logging.getLogger(__name__)

class LoaderManager:
    """
    Manager for dataset loaders
    
    Automatically selects the appropriate loader based on the source type.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the loader manager
        
        Args:
            cache_dir: Optional directory to use for caching
        """
        self.cache_dir = cache_dir
        
        # Initialize loaders
        self.loaders = {
            "file": FileLoader(cache_dir=cache_dir),
            "url": UrlLoader(cache_dir=cache_dir),
            "huggingface": HuggingFaceLoader(cache_dir=cache_dir)
        }
        
        # Registry of additional custom loaders
        self._custom_loaders = {}
    
    def load(self, 
            source: str,
            loader_type: Optional[str] = None,
            **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
        """
        Load a dataset from a source
        
        Args:
            source: Source identifier (path, URL, dataset name)
            loader_type: Optional explicit loader type to use
            **kwargs: Additional options passed to the loader
            
        Returns:
            Loaded dataset
        """
        # Use explicit loader if specified
        if loader_type and loader_type in self.loaders:
            logger.info(f"Using explicitly specified loader: {loader_type}")
            return self.loaders[loader_type].load(source, **kwargs)
        elif loader_type and loader_type in self._custom_loaders:
            logger.info(f"Using custom loader: {loader_type}")
            return self._custom_loaders[loader_type].load(source, **kwargs)
        
        # Auto-detect the appropriate loader
        for name, loader in {**self.loaders, **self._custom_loaders}.items():
            if loader.supports(source):
                logger.info(f"Auto-detected loader: {name}")
                return loader.load(source, **kwargs)
                
        # If no loader was found, try the file loader as fallback
        logger.warning(f"No suitable loader found for {source}, trying file loader as fallback")
        try:
            return self.loaders["file"].load(source, **kwargs)
        except Exception as e:
            raise ValueError(f"No suitable loader found for source: {source}. Error: {e}")
    
    def register_loader(self, name: str, loader: BaseLoader) -> None:
        """
        Register a custom loader
        
        Args:
            name: Name to register the loader under
            loader: Loader instance
        """
        if not isinstance(loader, BaseLoader):
            raise TypeError("Loader must be an instance of BaseLoader")
            
        self._custom_loaders[name] = loader
        logger.info(f"Registered custom loader: {name}")
    
    def unregister_loader(self, name: str) -> bool:
        """
        Unregister a custom loader
        
        Args:
            name: Name of the loader to unregister
            
        Returns:
            True if the loader was unregistered
        """
        if name in self._custom_loaders:
            del self._custom_loaders[name]
            logger.info(f"Unregistered custom loader: {name}")
            return True
        return False
    
    def get_available_loaders(self) -> List[str]:
        """
        Get a list of all available loaders
        
        Returns:
            List of loader names
        """
        return list(self.loaders.keys()) + list(self._custom_loaders.keys())


# Create a singleton instance for easy access
default_loader_manager = LoaderManager()

def load_dataset(source: str, **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
    """
    Convenience function to load a dataset from any source
    
    Args:
        source: Source identifier (file path, URL, dataset name)
        **kwargs: Additional options for the loader
        
    Returns:
        Loaded dataset
    """
    return default_loader_manager.load(source, **kwargs)
