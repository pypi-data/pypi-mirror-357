"""
Base Dataset Loader

Abstract base class for all dataset loaders
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
import pyarrow as pa

logger = logging.getLogger(__name__)

class BaseLoader(ABC):
    """
    Abstract base class for dataset loaders
    
    All loaders must implement the load method to convert
    data from a source into a format suitable for the Dataset class.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize loader
        
        Args:
            cache_dir: Optional directory to cache downloaded data
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def load(self, source: str, **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
        """
        Load dataset from a source
        
        Args:
            source: Source identifier (path, URL, dataset name, etc.)
            **kwargs: Additional loader-specific arguments
            
        Returns:
            Loaded data in a format usable by the Dataset class
        """
        pass
    
    @abstractmethod
    def supports(self, source: str) -> bool:
        """
        Check if this loader supports the given source
        
        Args:
            source: Source identifier to check
            
        Returns:
            True if this loader can handle the source
        """
        pass
    
    def _ensure_cache_dir(self) -> Path:
        """Ensure cache directory exists"""
        if not self.cache_dir:
            import tempfile
            self.cache_dir = Path(tempfile.gettempdir()) / "dravik_dataset_cache"
            
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir
