"""
HuggingFace Dataset Loader

Loads datasets from the HuggingFace datasets hub
"""

import os
import logging
import tempfile
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import pyarrow as pa
from pathlib import Path
from datetime import datetime
import json

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class HuggingFaceLoader(BaseLoader):
    """
    Professional loader for HuggingFace datasets
    
    Features:
    - Smart caching to avoid repeated downloads
    - Flexible configuration options
    - Comprehensive error handling
    - Support for dataset splits
    """
    
    def __init__(self, 
                cache_dir: Optional[str] = None,
                use_auth_token: Optional[str] = None,
                streaming: bool = False,
                revision: Optional[str] = None):
        """
        Initialize HuggingFace loader
        
        Args:
            cache_dir: Optional cache directory
            use_auth_token: HuggingFace authentication token for private datasets
            streaming: Whether to use streaming mode for large datasets
            revision: Dataset revision/version to load
        """
        super().__init__(cache_dir)
        self.use_auth_token = use_auth_token
        self.streaming = streaming
        self.revision = revision
        
        # Get API token from environment if not provided
        if not self.use_auth_token:
            # First try the standard environment variable
            self.use_auth_token = os.environ.get("HUGGINGFACE_API_KEY")
            
            # If not found, try to use ApiKeyManager
            if not self.use_auth_token:
                try:
                    from utils.api_key_manager import get_api_key_manager
                    api_manager = get_api_key_manager()
                    self.use_auth_token = api_manager.get_key("huggingface")
                except (ImportError, Exception) as e:
                    logging.debug(f"Could not use ApiKeyManager: {e}")
                    # Silently fail - the loader will work without auth for public datasets
    
    def supports(self, source: str) -> bool:
        """
        Check if this loader supports the given source
        
        Args:
            source: Dataset name or path
            
        Returns:
            True if this loader can handle the source
        """
        # Consider it a HuggingFace dataset if it's a string without file extension
        # or if it has a namespace format (username/dataset)
        if not source:
            return False
            
        if "/" in source and not (source.startswith("http://") or 
                                source.startswith("https://") or 
                                source.startswith("file://")):
            return True
            
        # Not a URL or file path, likely a dataset name
        return not Path(source).suffix and not os.path.exists(source)
    
    def load(self, 
            source: str,
            split: Optional[str] = "train",
            streaming: Optional[bool] = None,
            features: Optional[List[str]] = None,
            revision: Optional[str] = None,
            **kwargs) -> Union[Dict[str, Any], pd.DataFrame, pa.Table]:
        """
        Load a dataset from HuggingFace
        
        Args:
            source: Dataset name on the HuggingFace Hub
            split: Dataset split to load ("train", "test", "validation")
            streaming: Override instance streaming setting
            features: Optional list of features to load
            revision: Optional dataset revision
            **kwargs: Additional arguments passed to load_dataset
            
        Returns:
            Loaded dataset as a dictionary or DataFrame
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("The 'datasets' library is required. Install with: pip install datasets")
        
        # Set defaults
        streaming_mode = self.streaming if streaming is None else streaming
        revision_str = self.revision if revision is None else revision
        
        # Read cache to avoid re-downloading if possible
        cache_file = self._get_cache_path(source, split, revision_str)
        
        if cache_file.exists():
            logger.info(f"Loading cached HuggingFace dataset: {cache_file}")
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                return data
            except Exception as e:
                logger.warning(f"Failed to load cached dataset: {e}")
        
        logger.info(f"Loading dataset from HuggingFace: {source}")
        
        try:
            # Check for SSL verification setting
            verify_ssl = os.environ.get("HF_HUB_DISABLE_SSL_VERIFICATION", "0") != "1"
            if not verify_ssl:
                logger.warning("SSL verification is disabled for HuggingFace Hub requests")
                # Apply patch to huggingface_hub to disable SSL verification
                # This is a workaround for SSL certificate verification issues
                import huggingface_hub.utils._http as hf_http
                # Save original function to restore later if needed
                original_get_session = getattr(hf_http, "_get_session", None)
                
                def patched_get_session(*args, **kwargs):
                    session = original_get_session(*args, **kwargs)
                    session.verify = False
                    return session
                
                # Apply the patch if original function exists
                if original_get_session is not None:
                    setattr(hf_http, "_get_session", patched_get_session)
                
                # Also set verification for the datasets library
                import datasets.config
                datasets.config.HF_DATASETS_OFFLINE = False
                datasets.config.HF_DATASETS_TRUST_REMOTE_CODE = True
                
                # Silence warnings
                import requests.packages.urllib3
                requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            
            # Build arguments dict
            load_args = {
                "path": source,
                "streaming": streaming_mode
            }
            
            if split:
                load_args["split"] = split
                
            if self.use_auth_token:
                load_args["use_auth_token"] = self.use_auth_token
                
            if revision_str:
                load_args["revision"] = revision_str
                
            # Add cache_dir if not streaming
            if not streaming_mode and self.cache_dir:
                load_args["cache_dir"] = str(self.cache_dir)
                
            # Add any additional kwargs
            load_args.update(kwargs)
            
            # Load the dataset
            dataset = load_dataset(**load_args)
            
            # If streaming, convert to table or DataFrame
            if streaming_mode:
                # Convert to list, then DataFrame
                logger.info("Converting streaming dataset to DataFrame")
                # Limit to first 10000 examples for very large datasets
                max_examples = kwargs.get("max_examples", 10000)
                
                # Select only requested features if specified
                if features:
                    data_iter = (
                        {k: ex[k] for k in features if k in ex}
                        for i, ex in enumerate(dataset)
                        if i < max_examples
                    )
                else:
                    data_iter = (ex for i, ex in enumerate(dataset) if i < max_examples)
                
                # Convert to list of dicts then to DataFrame
                data_list = list(data_iter)
                df = pd.DataFrame(data_list)
                
                # Save to cache if not too large
                if len(df) <= max_examples and not kwargs.get("skip_cache", False):
                    try:
                        if not cache_file.parent.exists():
                            cache_file.parent.mkdir(parents=True, exist_ok=True)
                        df.to_parquet(cache_file)
                        logger.info(f"Cached dataset to {cache_file}")
                    except Exception as e:
                        logger.warning(f"Failed to cache dataset: {e}")
                
                return df
            else:
                # Handle non-streaming dataset, which is likely a DatasetDict or Dataset
                
                # If it's a specific split, convert to table
                if hasattr(dataset, "to_pandas"):
                    df = dataset.to_pandas()
                    
                    # Filter columns if features specified
                    if features:
                        available_features = [f for f in features if f in df.columns]
                        df = df[available_features]
                    
                    # Save to cache
                    if not kwargs.get("skip_cache", False):
                        try:
                            if not cache_file.parent.exists():
                                cache_file.parent.mkdir(parents=True, exist_ok=True)
                            df.to_parquet(cache_file)
                            logger.info(f"Cached dataset to {cache_file}")
                        except Exception as e:
                            logger.warning(f"Failed to cache dataset: {e}")
                    
                    return df
                
                # Handle DatasetDict by returning the requested split
                if hasattr(dataset, "get") and split in dataset:
                    split_dataset = dataset.get(split)
                    df = split_dataset.to_pandas()
                    
                    # Filter columns if features specified
                    if features:
                        available_features = [f for f in features if f in df.columns]
                        df = df[available_features]
                    
                    # Save to cache
                    if not kwargs.get("skip_cache", False):
                        try:
                            if not cache_file.parent.exists():
                                cache_file.parent.mkdir(parents=True, exist_ok=True)
                            df.to_parquet(cache_file)
                            logger.info(f"Cached dataset to {cache_file}")
                        except Exception as e:
                            logger.warning(f"Failed to cache dataset: {e}")
                    
                    return df
                
                # If we can't convert to DataFrame, convert to dict
                logger.warning("Could not convert dataset to DataFrame, returning as dict")
                try:
                    result = {}
                    for split_name, split_data in dataset.items():
                        # Convert each split to dict
                        split_dict = {}
                        data_dict = split_data.to_dict()
                        
                        # Filter features if specified
                        if features:
                            data_dict = {k: v for k, v in data_dict.items() if k in features}
                        
                        for key, value in data_dict.items():
                            split_dict[key] = value
                            
                        result[split_name] = split_dict
                        
                    # Don't cache dict format
                    return result
                except Exception as e:
                    logger.error(f"Failed to convert dataset to dict: {e}")
                    # Return the original dataset as fallback
                    return dataset
                
        except Exception as e:
            logger.error(f"Error loading dataset {source} from HuggingFace: {e}")
            raise
    
    def list_datasets(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List available datasets matching filters
        
        Args:
            filter_by: Dictionary of filters
            
        Returns:
            List of matching datasets
        """
        try:
            from datasets import list_datasets, get_dataset_config_names
        except ImportError:
            raise ImportError("The 'datasets' library is required. Install with: pip install datasets")
        
        try:
            # List datasets with or without authentication
            auth_token = self.use_auth_token
            datasets_list = list_datasets(use_auth_token=auth_token)
            
            # Apply filters if specified
            if filter_by:
                filtered_list = []
                for ds_info in datasets_list:
                    match = True
                    for key, value in filter_by.items():
                        if not hasattr(ds_info, key) or getattr(ds_info, key) != value:
                            match = False
                            break
                    if match:
                        filtered_list.append(ds_info)
                return filtered_list
            
            return datasets_list
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []
    
    def get_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a dataset
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Dictionary with dataset information
        """
        try:
            from datasets import load_dataset_builder
        except ImportError:
            raise ImportError("The 'datasets' library is required. Install with: pip install datasets")
        
        try:
            # Load dataset builder
            builder = load_dataset_builder(
                dataset_name, 
                revision=self.revision,
                use_auth_token=self.use_auth_token
            )
            
            # Get dataset info
            info = builder.info
            
            # Convert to dictionary
            result = {
                "name": dataset_name,
                "description": info.description,
                "citation": info.citation,
                "homepage": info.homepage,
                "license": info.license,
                "features": {
                    name: str(feature) 
                    for name, feature in info.features.items()
                } if hasattr(info, "features") else {},
                "splits": {
                    name: {"num_examples": split_info.num_examples}
                    for name, split_info in info.splits.items()
                } if hasattr(info, "splits") else {},
                "version": str(info.version) if hasattr(info, "version") else None,
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting info for dataset {dataset_name}: {e}")
            return {"name": dataset_name, "error": str(e)}
    
    def _get_cache_path(self, source: str, split: str, revision: Optional[str] = None) -> Path:
        """
        Get path for caching dataset
        
        Args:
            source: Dataset name
            split: Dataset split
            revision: Optional revision
            
        Returns:
            Path for caching
        """
        cache_dir = self._ensure_cache_dir()
        
        # Create a safe file name from the source
        safe_name = source.replace("/", "_").replace("-", "_").replace(".", "_")
        safe_split = split.replace("/", "_") if split else "default"
        
        # Include revision in filename if provided
        if revision:
            safe_rev = revision.replace("/", "_").replace(".", "_")
            filename = f"{safe_name}_{safe_split}_{safe_rev}.parquet"
        else:
            filename = f"{safe_name}_{safe_split}.parquet"
            
        return cache_dir / filename
