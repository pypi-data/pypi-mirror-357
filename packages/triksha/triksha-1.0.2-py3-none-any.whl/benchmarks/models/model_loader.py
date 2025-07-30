"""Model loading utilities for benchmarks"""
import torch
import gc
import os
import json
import importlib.util
import sys
from typing import Dict, Any, Optional, Tuple, List
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from huggingface_hub import model_info
from huggingface_hub.utils import RepositoryNotFoundError
from rich.console import Console
from .base_handler import ModelHandler

class ModelLoader:
    """Model loading and management for benchmarking"""
    
    def __init__(self, config_dir: Optional[str] = None, verbose: bool = False):
        """Initialize model loader"""
        self.verbose = verbose
        self.console = Console()
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.config_dir = config_dir or os.path.expanduser("~/.dravik/models")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Try to get HF token
        self.hf_token = None
        try:
            from utils.env_loader import get_api_key
            self.hf_token = get_api_key("huggingface", verbose=verbose)
        except (ImportError, Exception) as e:
            if verbose:
                self.console.print("[yellow]Could not load HuggingFace token[/]")
                
        # Store custom model configurations
        self.custom_model_configs = {}
        
        # Internal cache of loaded handlers
        self._handler_cache = {}
    
    def _log(self, message: str, level: str = "info"):
        """Log messages based on verbosity"""
        if not self.verbose:
            return
            
        if level == "info":
            self.console.print(f"[blue]{message}[/]")
        elif level == "success":
            self.console.print(f"[green]{message}[/]")
        elif level == "warning":
            self.console.print(f"[yellow]{message}[/]")
        elif level == "error":
            self.console.print(f"[red]{message}[/]")
    
    def _clean_memory(self):
        """Clean up GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
    
    def load_model(self, model_name: str) -> bool:
        """Load model with memory optimization"""
        try:
            self._log(f"Loading model: {model_name}...")
            
            # Set token if available
            token_kwargs = {"token": self.hf_token} if self.hf_token else {}
            
            # Load tokenizer
            if self.tokenizer is None:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    **token_kwargs
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            if self.model is None:
                # Configure quantization
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )

                # Load model with quantization
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True,
                    **token_kwargs
                )
                
                self._log(f"Successfully loaded model: {model_name}", "success")
            
            return True
            
        except Exception as e:
            self._log(f"Error loading model {model_name}: {str(e)}", "error")
            self._clean_memory()
            return False
    
    def get_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """Get loaded model and tokenizer"""
        return self.model, self.tokenizer
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
            
        self._clean_memory()
        self._log("Model unloaded from memory", "info")
        
    def register_custom_model(self, model_name: str, config: Dict[str, Any]):
        """Register a custom model configuration.
        
        Args:
            model_name: Name to identify the custom model
            config: Model configuration dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate configuration
            if not isinstance(config, dict):
                self._log(f"Config must be a dictionary", level="error")
                return False
                
            # Check required fields based on model type
            model_type = config.get("type", "").lower()
            
            if model_type == "custom-api":
                # For custom API models, check for endpoint URL or curl command
                if not config.get("endpoint_url") and not config.get("curl_command"):
                    self._log("Custom API models require either endpoint_url or curl_command", level="error")
                    return False
                    
            elif model_type == "ollama":
                # For Ollama models, check for model ID
                if not config.get("model_id"):
                    self._log("Ollama models require model_id", level="error")
                    return False
                    
            else:
                # Default model checks
                if not config.get("model_id"):
                    self._log(f"Model configuration requires 'model_id' field", level="error")
                    return False
            
            # Store the configuration
            self.custom_model_configs[model_name] = config
            
            # Save to disk
            return self.save_custom_model_config(model_name, config)
            
        except Exception as e:
            self._log(f"Error registering custom model: {str(e)}", level="error")
            return False
    
    def get_custom_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a registered custom model"""
        config_path = os.path.join(self.config_dir, f"{model_name}.json")
        if not os.path.exists(config_path):
            if self.verbose:
                self.console.print(f"Model configuration not found: {config_path}")
            return None
        
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            if self.verbose:
                self.console.print(f"Error loading model configuration: {e}")
            return None
    
    def save_custom_model_config(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Save a configuration for a custom model.
        
        Args:
            model_name: Name of the custom model
            config: Configuration dictionary
            
        Returns:
            True if saved successfully, False otherwise
        """
        # Ensure config directory exists
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Error creating config directory {self.config_dir}: {e}[/]")
            return False
        
        config_path = os.path.join(self.config_dir, f"{model_name}.json")
        
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            # Verify the file was created
            if os.path.exists(config_path):
                if self.verbose:
                    self.console.print(f"[green]Saved configuration for {model_name} to {config_path}[/]")
                return True
            else:
                if self.verbose:
                    self.console.print(f"[yellow]Warning: File not found after saving: {config_path}[/]")
                return False
                
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Error saving model configuration to {config_path}: {e}[/]")
            return False
    
    def delete_custom_model(self, model_name: str) -> bool:
        """Delete a custom model configuration.
        
        Args:
            model_name: Name of the custom model
            
        Returns:
            True if deleted successfully, False otherwise
        """
        config_path = os.path.join(self.config_dir, f"{model_name}.json")
        
        try:
            if os.path.exists(config_path):
                os.remove(config_path)
                return True
            return False
        except Exception as e:
            if self.verbose:
                self.console.print(f"Error deleting model configuration: {e}")
            return False
    
    def load_handler(self, model_name: str) -> Optional[ModelHandler]:
        """Load a model handler for the specified model.
        
        Args:
            model_name: Name of the model to load handler for
            
        Returns:
            ModelHandler instance or None if model not found
        """
        # If handler is already cached, return it
        if model_name in self._handler_cache:
            return self._handler_cache[model_name]
            
        try:
            # Handle guardrail models specially
            if model_name.startswith("guardrail:"):
                guardrail_name = model_name.replace("guardrail:", "")
                from .handlers.guardrail_handler import GuardrailHandler
                
                handler = GuardrailHandler(
                    guardrail_name=guardrail_name,
                    verbose=self.verbose
                )
                
                # Cache and return the handler
                self._handler_cache[model_name] = handler
                return handler
            
            # Get model configuration
            config = self.get_custom_model_config(model_name)
            if not config:
                self._log(f"No configuration found for model {model_name}", level="error")
                return None
                
            model_type = config.get("type", "").lower()
            
            # Create the appropriate handler based on model type
            if model_type == "custom-api":
                from .handlers.custom_api_handler import CustomAPIHandler
                
                # Extract parameters for CustomAPIHandler
                handler = CustomAPIHandler(
                    name=model_name,
                    endpoint_url=config.get("endpoint_url"),
                    curl_command=config.get("curl_command"),
                    headers=config.get("headers"),
                    http_method=config.get("http_method", "POST"),
                    json_path=config.get("json_path"),
                    verbose=self.verbose
                )
                
            elif model_type == "ollama":
                from .handlers.ollama_handler import OllamaHandler
                
                # Extract parameters for OllamaHandler
                handler = OllamaHandler(
                    base_url=config.get("base_url"),
                    verbose=self.verbose
                )
                
            elif model_type == "openai":
                from .handlers.openai_handler import OpenAIHandler
                
                # Create OpenAI handler
                handler = OpenAIHandler(
                    api_key=config.get("api_key"),
                    api_base=config.get("api_base"),
                    api_version=config.get("api_version"),
                    verbose=self.verbose
                )
                
            elif model_type == "huggingface":
                from .handlers.huggingface_handler import HuggingFaceHandler
                
                # Create HuggingFace handler
                handler = HuggingFaceHandler(
                    api_key=config.get("api_key", self.hf_token),
                    verbose=self.verbose
                )
                
            elif model_type == "gemini":
                from .handlers.gemini_handler import GeminiHandler
                
                # Create Gemini handler
                handler = GeminiHandler(
                    api_key=config.get("api_key"),
                    verbose=self.verbose
                )
                
            elif model_type == "anthropic":
                from .handlers.anthropic_handler import AnthropicHandler
                
                # Create Anthropic handler
                handler = AnthropicHandler(
                    api_key=config.get("api_key"),
                    verbose=self.verbose
                )
                
            elif model_type == "python":
                # Check if there's a class or path
                if "class_path" in config:
                    # Load dynamically from Python module
                    module_path = config["class_path"].split(".")
                    class_name = module_path.pop()
                    module_name = ".".join(module_path)
                    
                    try:
                        module = importlib.import_module(module_name)
                        handler_class = getattr(module, class_name)
                        handler = handler_class(**config.get("params", {}))
                    except (ImportError, AttributeError) as e:
                        self._log(f"Error loading Python handler: {str(e)}", level="error")
                        return None
                elif "file_path" in config:
                    # Load from a file
                    file_path = config["file_path"]
                    class_name = config.get("class_name", "CustomModelHandler")
                    
                    try:
                        spec = importlib.util.spec_from_file_location("custom_module", file_path)
                        custom_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(custom_module)
                        
                        handler_class = getattr(custom_module, class_name)
                        handler = handler_class(**config.get("params", {}))
                    except (ImportError, AttributeError) as e:
                        self._log(f"Error loading handler from file: {str(e)}", level="error")
                        return None
                else:
                    self._log("Python handler requires either class_path or file_path", level="error")
                    return None
            else:
                self._log(f"Unknown model type: {model_type}", level="error")
                return None
                
            # Cache and return the handler
            self._handler_cache[model_name] = handler
            return handler
            
        except Exception as e:
            self._log(f"Error loading handler for {model_name}: {str(e)}", level="error")
            import traceback
            traceback.print_exc()
            return None
    
    def list_custom_models(self) -> List[str]:
        """List all registered custom models"""
        models = []
        
        # First check models registered in memory
        in_memory_models = list(self.custom_model_configs.keys())
        if in_memory_models and self.verbose:
            self.console.print(f"Found {len(in_memory_models)} custom models in memory")
            
        # Then check models saved on disk
        try:
            if os.path.exists(self.config_dir):
                disk_models = []
                for filename in os.listdir(self.config_dir):
                    if filename.endswith(".json"):
                        model_name = filename.replace(".json", "")
                        disk_models.append(model_name)
                        
                if disk_models and self.verbose:
                    self.console.print(f"Found {len(disk_models)} custom models on disk in {self.config_dir}")
                
                # Combine the lists (disk models take precedence)
                models = list(set(in_memory_models + disk_models))
            else:
                if self.verbose:
                    self.console.print(f"Custom model directory not found: {self.config_dir}")
                models = in_memory_models
        except Exception as e:
            if self.verbose:
                self.console.print(f"[yellow]Error listing custom models from disk: {e}[/]")
            # Fall back to in-memory models
            models = in_memory_models
        
        if not models and self.verbose:
            self.console.print("[yellow]No custom models found in memory or on disk[/]")
            
        return models
        
    async def list_all_model_options(self) -> Dict[str, List[str]]:
        """List all available model options"""
        result = {
            "huggingface": [],
            "openai": [],
            "gemini": [],
            "custom": self.list_custom_models()
        }
        
        # Get OpenAI models
        try:
            from ..api.openai_handler import OpenAIHandler
            openai_models = await OpenAIHandler.list_available_models()
            result["openai"] = openai_models
        except Exception as e:
            self._log(f"Error listing OpenAI models: {str(e)}", "error")
            
        # Get Gemini models
        try:
            from ..api.gemini_handler import GeminiHandler
            gemini_models = GeminiHandler.list_available_models()
            result["gemini"] = gemini_models
        except Exception as e:
            self._log(f"Error listing Gemini models: {str(e)}", "error")
            
        # For custom models that have a list_models method, try to list them
        for model_name, config in self.custom_model_configs.items():
            try:
                from ..api.custom_handler import CustomHandler
                custom_models = await CustomHandler.list_available_models(config)
                if custom_models and len(custom_models) > 1 and custom_models != ["custom-model"]:
                    # If we got a meaningful list, append it
                    result["custom"].extend(custom_models)
            except Exception:
                # Just ignore errors here
                pass
                
        return result
