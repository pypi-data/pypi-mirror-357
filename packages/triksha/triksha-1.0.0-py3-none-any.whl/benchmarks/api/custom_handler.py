"""Handler for custom API interactions"""
import os
import json
import asyncio
import time
import importlib
import sys
from typing import List, Dict, Any, Optional
import inspect
from pathlib import Path

class CustomHandler:
    """Handler for custom API interactions"""
    
    def __init__(self, model_name: str = None, config: Dict[str, Any] = None, verbose: bool = False):
        """Initialize custom model handler
        
        Args:
            model_name: Name of the custom model
            config: Configuration dictionary with necessary parameters
            verbose: Whether to output verbose logs
        """
        self.verbose = verbose
        self.model_name = model_name or "custom-model"
        self.provider = config.get("provider", "custom")
        self.model_version = config.get("version", "unknown")
        self.config = config or {}
        self.custom_module = None
        self.custom_handler = None
        
        if self.verbose:
            print(f"Initializing custom handler for {self.model_name}")
        
        # Initialize the handler based on the provided configuration
        if "module_path" in self.config:
            self._initialize_custom_module()
            
    def _log(self, message: str, level: str = "info"):
        """Log messages based on verbosity"""
        if not self.verbose:
            return
            
        prefix = {
            "info": "[INFO]",
            "warning": "[WARNING]", 
            "error": "[ERROR]",
            "success": "[SUCCESS]"
        }.get(level, "[INFO]")
        
        print(f"{prefix} {message}")
            
    def _initialize_custom_module(self):
        """Initialize custom module from the provided module path"""
        try:
            module_path = self.config.get("module_path")
            class_name = self.config.get("class_name")
            
            if not module_path or not class_name:
                raise ValueError("Both module_path and class_name must be provided in config")
            
            # Check if the module exists in the examples directory first
            examples_dir = Path(__file__).parent.parent.parent / "examples"
            examples_module_path = str(examples_dir / f"{module_path}.py")
            
            if os.path.exists(examples_module_path):
                # Add examples directory to sys.path if not already present
                if str(examples_dir) not in sys.path:
                    sys.path.insert(0, str(examples_dir))
                
                # Extract the filename without .py as the module name
                module_name = os.path.basename(module_path)
                self._log(f"Loading module from examples directory: {module_name}", "info")
                module = importlib.import_module(module_name)
            else:
                # Try to import the module directly
                self._log(f"Importing module: {module_path}", "info")
                module = importlib.import_module(module_path)
            
            # Get the specified class
            if not hasattr(module, class_name):
                raise ValueError(f"Class {class_name} not found in module {module_path}")
                
            handler_class = getattr(module, class_name)
            
            # Initialize the handler with config parameters
            init_params = {}
            if "params" in self.config:
                init_params = self.config["params"]
            
            self._log(f"Initializing {class_name} with params: {init_params}", "info")
            self.custom_handler = handler_class(**init_params)
            self.custom_module = module
            
            self._log(f"Successfully initialized custom handler: {class_name}", "success")
            
        except ModuleNotFoundError as e:
            self._log(f"Error: Module '{module_path}' not found. Please check the module path.", "error")
            raise ValueError(f"Module not found: {module_path}. Make sure the module exists and is in the Python path.") from e
        except Exception as e:
            self._log(f"Error initializing custom module: {str(e)}", "error")
            raise
    
    @staticmethod
    async def list_available_models(config: Dict[str, Any] = None) -> List[str]:
        """List available models from the custom handler"""
        if not config or "module_path" not in config or "class_name" not in config:
            return ["custom-model"]
            
        try:
            module_path = config.get("module_path")
            class_name = config.get("class_name")
            
            # Try to import the module
            try:
                # Check if the module exists in the examples directory first
                examples_dir = Path(__file__).parent.parent.parent / "examples"
                examples_module_path = str(examples_dir / f"{module_path}.py")
                
                if os.path.exists(examples_module_path):
                    # Add examples directory to sys.path if not already present
                    if str(examples_dir) not in sys.path:
                        sys.path.insert(0, str(examples_dir))
                    
                    # Extract the filename without .py as the module name
                    module_name = os.path.basename(module_path)
                    module = importlib.import_module(module_name)
                else:
                    # Try to import the module directly
                    module = importlib.import_module(module_path)
            except ModuleNotFoundError:
                print(f"Warning: Module '{module_path}' not found. Cannot list models.")
                return ["custom-model"]
            
            # Get the specified class
            if not hasattr(module, class_name):
                return ["custom-model"]
                
            handler_class = getattr(module, class_name)
            
            # Check if the class has a list_models method
            if hasattr(handler_class, "list_models") and callable(getattr(handler_class, "list_models")):
                # Check if it's a static or class method
                method = getattr(handler_class, "list_models")
                if inspect.ismethod(method) and getattr(method, "__self__", None) is handler_class:
                    # It's a class method or static method
                    return await method()
                else:
                    # It's an instance method, need to instantiate
                    init_params = {}
                    if "params" in config:
                        init_params = config["params"]
                    handler = handler_class(**init_params)
                    return await handler.list_models()
            
            return ["custom-model"]
        
        except Exception as e:
            print(f"Error listing custom models: {e}")
            return ["custom-model"]

    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Test a prompt using the custom handler"""
        if not self.custom_handler:
            return {
                "success": False,
                "error": "Custom handler not initialized",
                "model": self.model_name,
                "provider": self.provider,
                "version": self.model_version
            }
        
        try:
            # Check if the custom handler has a compatible method
            if hasattr(self.custom_handler, "test_prompt") and callable(getattr(self.custom_handler, "test_prompt")):
                # Use the handler's test_prompt method if it exists
                result = await self.custom_handler.test_prompt(prompt)
                if isinstance(result, dict):
                    # If the result is already a dictionary, add missing fields and return
                    if "success" not in result:
                        result["success"] = True
                    if "model" not in result:
                        result["model"] = self.model_name
                    if "provider" not in result:
                        result["provider"] = self.provider
                    if "version" not in result:
                        result["version"] = self.model_version
                    return result
                else:
                    # If the result is not a dictionary (e.g., just a string), wrap it
                    response = str(result)
                    return {
                        "success": True,
                        "response": response,
                        "model": self.model_name,
                        "provider": self.provider,
                        "version": self.model_version
                    }
            
            # If the handler has a generate method, use that instead
            elif hasattr(self.custom_handler, "generate") and callable(getattr(self.custom_handler, "generate")):
                response = await self.custom_handler.generate(prompt)
                return {
                    "success": True,
                    "response": response,
                    "model": self.model_name,
                    "provider": self.provider,
                    "version": self.model_version
                }
                
            # If neither method exists, raise an error
            else:
                raise ValueError("Custom handler does not have test_prompt or generate method")
                
        except Exception as e:
            self._log(f"Error in test_prompt: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name, 
                "provider": self.provider,
                "version": self.model_version
            } 