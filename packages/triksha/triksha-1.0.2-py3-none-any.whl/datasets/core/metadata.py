"""
Dataset Metadata Management
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import json

class DatasetMetadata:
    """
    Professional metadata management for datasets
    
    Handles tracking and versioning of dataset metadata including:
    - Dataset source, creation time, and version
    - Data schema information
    - Processing history
    - Quality metrics
    - Usage statistics
    """
    
    def __init__(self, initial_metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize metadata container
        
        Args:
            initial_metadata: Optional initial metadata
        """
        self._metadata = {
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "schema_version": "1.0",
            "processing_history": [],
        }
        
        if initial_metadata:
            self.update(initial_metadata)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key
        
        Args:
            key: Metadata key
            default: Default value if key doesn't exist
            
        Returns:
            Metadata value or default
        """
        return self._metadata.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set metadata value
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value
        self._metadata["modified_at"] = datetime.now().isoformat()
    
    def update(self, metadata_dict: Dict[str, Any]) -> None:
        """
        Update metadata with dictionary
        
        Args:
            metadata_dict: Dictionary of metadata to update
        """
        self._metadata.update(metadata_dict)
        self._metadata["modified_at"] = datetime.now().isoformat()
    
    def add_processing_step(self, 
                           step_name: str, 
                           description: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a processing step to the history
        
        Args:
            step_name: Name of the processing step
            description: Description of what was done
            parameters: Optional parameters used
        """
        if "processing_history" not in self._metadata:
            self._metadata["processing_history"] = []
            
        step = {
            "step_name": step_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        if parameters:
            step["parameters"] = parameters
            
        self._metadata["processing_history"].append(step)
        self._metadata["modified_at"] = datetime.now().isoformat()
    
    def keys(self) -> Set[str]:
        """Get all metadata keys"""
        return set(self._metadata.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return self._metadata.copy()
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert metadata to JSON string
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return json.dumps(self._metadata, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DatasetMetadata':
        """
        Create metadata from JSON string
        
        Args:
            json_str: JSON string
            
        Returns:
            DatasetMetadata instance
        """
        try:
            metadata_dict = json.loads(json_str)
            return cls(metadata_dict)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")
    
    @classmethod
    def from_file(cls, filepath: str) -> 'DatasetMetadata':
        """
        Load metadata from file
        
        Args:
            filepath: Path to metadata file
            
        Returns:
            DatasetMetadata instance
        """
        try:
            with open(filepath, 'r') as f:
                metadata_dict = json.load(f)
            return cls(metadata_dict)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Could not load metadata from file: {e}")
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save metadata to file
        
        Args:
            filepath: Path to save metadata
        """
        with open(filepath, 'w') as f:
            json.dump(self._metadata, f, indent=2)
    
    def __repr__(self) -> str:
        """String representation of metadata"""
        return f"DatasetMetadata(keys={list(self._metadata.keys())})"
