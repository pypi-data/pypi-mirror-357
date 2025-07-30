"""
API Key Manager for Dravik

This module provides centralized API key management for the Dravik framework.
It handles loading, storing, and retrieving API keys from a common location.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("api_key_manager")

# Constants for API key names
OPENAI_KEY = "OPENAI_API_KEY"
GOOGLE_KEY = "GOOGLE_API_KEY"
HUGGINGFACE_KEY = "HUGGINGFACE_API_KEY"
ANTHROPIC_KEY = "ANTHROPIC_API_KEY"

# Map of human-readable names to environment variable names
KEY_MAPPING = {
    "openai": OPENAI_KEY,
    "google": GOOGLE_KEY,
    "gemini": GOOGLE_KEY,  # Alias for Google
    "huggingface": HUGGINGFACE_KEY,
    "hf": HUGGINGFACE_KEY,  # Alias for HuggingFace
    "anthropic": ANTHROPIC_KEY
}

class ApiKeyManager:
    """
    Centralized API key management for Dravik.
    
    This class provides methods to load, store, and retrieve API keys
    from a common location, ensuring consistent access across the application.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the API key manager.
        
        Args:
            config_dir: Optional custom configuration directory. If not provided,
                        defaults to ~/.dravik/config
        """
        if config_dir is None:
            self.config_dir = Path.home() / "dravik" / "config"
        else:
            self.config_dir = config_dir
            
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.keys_path = self.config_dir / "api_keys.json"
        
        # Cache of loaded keys
        self._api_keys = {}
        
        # Load keys at initialization
        self._load_keys()
    
    def _load_keys(self) -> Dict[str, str]:
        """
        Load API keys from storage.
        
        Returns:
            Dictionary of loaded API keys
        """
        if self.keys_path.exists():
            try:
                with open(self.keys_path, 'r') as f:
                    self._api_keys = json.load(f)
                    
                # Apply loaded keys to environment if not already set
                for key_name, key_value in self._api_keys.items():
                    if key_value and not os.environ.get(key_name):
                        os.environ[key_name] = key_value
                        
                return self._api_keys
            except Exception as e:
                logger.error(f"Error loading API keys: {e}")
                
        return {}
    
    def _save_keys(self) -> bool:
        """
        Save API keys to storage.
        
        Returns:
            True if keys were saved successfully, False otherwise
        """
        try:
            with open(self.keys_path, 'w') as f:
                json.dump(self._api_keys, f, indent=2)
                
            # Set file permissions to restrict access (Unix only)
            try:
                os.chmod(self.keys_path, 0o600)
            except:
                pass
                
            return True
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
            return False
    
    def get_key(self, key_name: str) -> Optional[str]:
        """
        Get an API key by name.
        
        Args:
            key_name: Name of the API key (can be alias or environment variable name)
            
        Returns:
            The API key value, or None if not found
        """
        # Normalize key name
        env_var = KEY_MAPPING.get(key_name.lower(), key_name)
        
        # Check environment first
        api_key = os.environ.get(env_var)
        
        # If not in environment, check stored keys
        if not api_key and env_var in self._api_keys:
            api_key = self._api_keys[env_var]
            if api_key:
                # Update environment
                os.environ[env_var] = api_key
        
        return api_key
    
    def store_key(self, key_name: str, key_value: str) -> bool:
        """
        Store an API key.
        
        Args:
            key_name: Name of the API key (can be alias or environment variable name)
            key_value: Value of the API key
            
        Returns:
            True if key was stored successfully, False otherwise
        """
        if not key_value:
            return False
            
        # Normalize key name
        env_var = KEY_MAPPING.get(key_name.lower(), key_name)
        
        # Update in-memory cache
        self._api_keys[env_var] = key_value
        
        # Update environment
        os.environ[env_var] = key_value
        
        # Save to disk
        return self._save_keys()
    
    def list_keys(self) -> Dict[str, Dict[str, Any]]:
        """
        List all configured API keys with their status.
        
        Returns:
            Dictionary of API keys with their status information
        """
        result = {}
        
        for display_name, env_var in KEY_MAPPING.items():
            # Skip aliases
            if display_name in ["gemini", "hf"]:
                continue
                
            # Get key from environment or stored keys
            key_value = os.environ.get(env_var) or self._api_keys.get(env_var, "")
            
            # Add to result with status information
            result[display_name] = {
                "env_var": env_var,
                "configured": bool(key_value),
                "source": "environment" if os.environ.get(env_var) else "stored" if self._api_keys.get(env_var) else "none",
                "mask": mask_api_key(key_value) if key_value else ""
            }
            
        return result
    
    def delete_key(self, key_name: str) -> bool:
        """
        Delete an API key.
        
        Args:
            key_name: Name of the API key (can be alias or environment variable name)
            
        Returns:
            True if key was deleted successfully, False otherwise
        """
        # Normalize key name
        env_var = KEY_MAPPING.get(key_name.lower(), key_name)
        
        # Remove from cache
        if env_var in self._api_keys:
            del self._api_keys[env_var]
            
            # Save to disk
            return self._save_keys()
            
        return False
    
    def get_key_with_prompt(self, key_name: str, prompt_function=None) -> Optional[str]:
        """
        Get an API key, prompting the user if it's not found.
        
        Args:
            key_name: Name of the API key (can be alias or environment variable name)
            prompt_function: Function to prompt the user for the key if not found
                             Should take (key_name, env_var) and return a string
            
        Returns:
            The API key value, or None if not found and user did not provide one
        """
        # Normalize key name
        env_var = KEY_MAPPING.get(key_name.lower(), key_name)
        display_name = key_name.lower()
        
        # Try to get key
        api_key = self.get_key(env_var)
        
        # If not found and prompt function provided, ask user
        if not api_key and prompt_function:
            key_value = prompt_function(display_name, env_var)
            if key_value:
                self.store_key(env_var, key_value)
                api_key = key_value
                
        return api_key

# Utility functions

def mask_api_key(key: str) -> str:
    """Mask an API key for display purposes"""
    if not key:
        return ""
        
    if len(key) <= 8:
        return "••••••••"
    else:
        return key[:4] + "•" * (len(key) - 8) + key[-4:]

# Singleton instance
_instance = None

def get_api_key_manager() -> ApiKeyManager:
    """Get the singleton instance of ApiKeyManager"""
    global _instance
    if _instance is None:
        _instance = ApiKeyManager()
    return _instance 