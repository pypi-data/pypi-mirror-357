"""
Dataset Version Management
"""

import hashlib
import re
from typing import Optional, Union, Dict, Any
from datetime import datetime

class DatasetVersion:
    """
    Professional version management for datasets
    
    Supports:
    - Semantic versioning (MAJOR.MINOR.PATCH)
    - Hash-based versioning
    - Automatic version generation
    - Version comparison
    """
    
    VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$')
    
    def __init__(self, version: Optional[str] = None):
        """
        Initialize version
        
        Args:
            version: Optional version string (auto-generated if None)
        """
        self._hash = None
        
        if not version:
            # Generate initial version
            self._major = 0
            self._minor = 1
            self._patch = 0
            self._label = None
            self._build = None
            self._timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        else:
            # Try to parse as semantic version
            match = self.VERSION_PATTERN.match(version)
            
            if match:
                self._major = int(match.group(1))
                self._minor = int(match.group(2))
                self._patch = int(match.group(3))
                self._label = match.group(4)
                self._build = match.group(5)
                self._timestamp = None
            else:
                # Treat as custom version string or hash
                self._version_string = version
                self._major = None
                self._minor = None
                self._patch = None
                self._label = None
                self._build = None
                self._timestamp = None
                
                if len(version) == 40 and all(c in '0123456789abcdef' for c in version.lower()):
                    self._hash = version.lower()
    
    def bump_major(self) -> 'DatasetVersion':
        """
        Bump major version
        
        Returns:
            DatasetVersion with incremented major version
        """
        if self._major is not None:
            self._major += 1
            self._minor = 0
            self._patch = 0
            self._timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return self
    
    def bump_minor(self) -> 'DatasetVersion':
        """
        Bump minor version
        
        Returns:
            DatasetVersion with incremented minor version
        """
        if self._minor is not None:
            self._minor += 1
            self._patch = 0
            self._timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return self
    
    def bump_patch(self) -> 'DatasetVersion':
        """
        Bump patch version
        
        Returns:
            DatasetVersion with incremented patch version
        """
        if self._patch is not None:
            self._patch += 1
            self._timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return self
    
    def auto_generate_hash(self, dataset) -> str:
        """
        Generate a hash based on dataset content
        
        Args:
            dataset: Dataset to hash
            
        Returns:
            Generated hash string
        """
        # Create a hash of the dataset content
        hasher = hashlib.sha1()
        
        # Add dataset name and basic info
        hasher.update(dataset.name.encode())
        
        # Try to hash data content
        if hasattr(dataset, 'to_dict'):
            # Get a sample of the data to hash (first few rows)
            data_sample = str(dataset.head(10)).encode()
            hasher.update(data_sample)
        
        # Add information about structure
        if hasattr(dataset, 'schema') and dataset.schema:
            hasher.update(str(dataset.schema).encode())
        
        # Add information about columns
        if hasattr(dataset, '_columns'):
            hasher.update(str(dataset._columns).encode())
        
        # Add timestamp
        hasher.update(datetime.now().isoformat().encode())
        
        self._hash = hasher.hexdigest()
        return self._hash
    
    @property
    def semantic(self) -> Optional[str]:
        """Get semantic version string"""
        if self._major is not None:
            version = f"{self._major}.{self._minor}.{self._patch}"
            if self._label:
                version += f"-{self._label}"
            if self._build:
                version += f"+{self._build}"
            return version
        return None
    
    def __str__(self) -> str:
        """Get version string"""
        if self._major is not None:
            return self.semantic
        elif self._hash:
            if self._timestamp:
                return f"{self._hash[:10]}_{self._timestamp}"
            return self._hash[:10]
        elif hasattr(self, '_version_string'):
            return self._version_string
        else:
            # Fallback to timestamp
            return datetime.now().strftime('v%Y%m%d%H%M%S')
    
    def __eq__(self, other: Union[str, 'DatasetVersion']) -> bool:
        """Check if versions are equal"""
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, DatasetVersion):
            return str(self) == str(other)
        return False
    
    def __lt__(self, other: Union[str, 'DatasetVersion']) -> bool:
        """Check if this version is less than other"""
        if isinstance(other, str):
            other = DatasetVersion(other)
            
        if self._major is not None and other._major is not None:
            # Compare semantic versions
            if self._major != other._major:
                return self._major < other._major
            if self._minor != other._minor:
                return self._minor < other._minor
            return self._patch < other._patch
        
        # Fall back to string comparison
        return str(self) < str(other)

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary"""
        result = {"version_str": str(self)}
        
        if self._major is not None:
            result.update({
                "major": self._major,
                "minor": self._minor,
                "patch": self._patch
            })
            
            if self._label:
                result["label"] = self._label
            if self._build:
                result["build"] = self._build
                
        if self._hash:
            result["hash"] = self._hash
            
        if self._timestamp:
            result["timestamp"] = self._timestamp
            
        return result
