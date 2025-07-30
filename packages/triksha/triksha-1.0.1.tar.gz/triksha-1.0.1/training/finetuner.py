import os
import torch
import sys
import subprocess
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import logging
from datetime import datetime
import re
import traceback
from dataclasses import dataclass
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    TrainerCallback
)
from peft import (
    LoraConfig, 
    get_peft_model, 
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import load_dataset, Dataset
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("finetuning.log")
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FinetuningConfig:
    """Configuration for fine-tuning"""
    model_name: str
    output_dir: str
    training_type: str = "qlora"  # "full", "lora", or "qlora"
    dataset_path: str = "training_data.json"  # Simplified relative path, will be searched in multiple directories
    dataset_type: str = "poc"  # "full" or "poc" or custom
    learning_rate: float = 2e-4
    batch_size: int = 1
    epochs: int = 3
    max_steps: int = -1
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 0.3
    warmup_ratio: float = 0.03
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    use_8bit: bool = True
    use_4bit: bool = False
    evaluation_strategy: str = "steps"
    eval_steps: int = 200
    save_steps: int = 200
    save_total_limit: int = 3
    logging_steps: int = 50
    device_map: str = "auto"
    torch_dtype: torch.dtype = torch.float16
    seed: int = 42
    enable_cpu_offload: bool = True  # Enable CPU offloading by default
    max_memory: Optional[Dict[str, str]] = None  # Custom memory configuration

class Finetuner:
    """Handles fine-tuning of language models"""
    
    # Model architecture to package mapping
    MODEL_ARCHITECTURE_PACKAGES = {
        "gemma3_": "git+https://github.com/huggingface/transformers.git",
        "gemma_": "transformers>=4.36.0",
        "llama3": "transformers>=4.37.0",
        "mixtral": "transformers>=4.36.0",
        "falcon": "transformers>=4.33.0",
        "phi": "transformers>=4.34.0",
        "qwen": "transformers>=4.35.0"
    }
    
    # Map models to their required tokenizer dependencies
    MODEL_REQUIRED_DEPENDENCIES = {
        "gemma": ["sentencepiece>=0.1.97"],
        "qwen": ["tiktoken>=0.5.0"],
        "phi": ["sentencepiece>=0.1.97"],
        "mistral": ["sentencepiece>=0.1.97"],
        "mixtral": ["sentencepiece>=0.1.97"],
        "llama": ["sentencepiece>=0.1.97"],
        "gemma3": ["sentencepiece>=0.1.97"],
    }
    
    def __init__(self, config: FinetuningConfig):
        """Initialize with fine-tuning configuration"""
        self.config = config
        self.model = None
        self.tokenizer = None
        self.trainer = None
        self.callbacks = None
        
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Set random seed for reproducibility
        torch.manual_seed(self.config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.seed)
        
        # Set up Hugging Face authentication early
        self._setup_huggingface_auth()
    
    def _setup_huggingface_auth(self):
        """Set up authentication with Hugging Face Hub"""
        try:
            import os
            from huggingface_hub import login, HfFolder
            
            # Check if already logged in
            if HfFolder.get_token() is not None:
                logger.info("Already authenticated with Hugging Face Hub")
                return True
                
            # Look for token in environment variables with various possible names
            token = None
            possible_env_vars = ["HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_TOKEN"]
            
            for var in possible_env_vars:
                if var in os.environ:
                    token = os.environ[var]
                    logger.info(f"Using Hugging Face token from {var} environment variable")
                    break
            
            if token:
                # Login with the token
                login(token=token)
                logger.info("Successfully authenticated with Hugging Face Hub")
                return True
            else:
                logger.warning("No Hugging Face token found in environment variables")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up Hugging Face authentication: {e}")
            return False
    
    def _check_transformers_version(self) -> Tuple[str, bool]:
        """
        Check current transformers version and determine if it needs an update
        
        Returns:
            Tuple of (current_version, needs_update)
        """
        try:
            import importlib.metadata
            import re
            current_version = importlib.metadata.version('transformers')
            logger.info(f"Current transformers version: {current_version}")
            
            # Get model architecture from model name
            model_architecture = self._get_model_architecture()
            
            # Check if model requires specific transformers version
            required_package = None
            for arch_prefix, package_req in self.MODEL_ARCHITECTURE_PACKAGES.items():
                if arch_prefix.lower() in model_architecture.lower():
                    required_package = package_req
                    break
            
            if required_package:
                if "git+" in required_package:
                    # For git installation, we'd need to update regardless of version
                    logger.info(f"Model {model_architecture} requires transformers from source: {required_package}")
                    return current_version, True
                else:
                    # Extract version requirement
                    version_match = re.search(r'>=([0-9\.]+)', required_package)
                    if version_match:
                        required_version = version_match.group(1)
                        # Compare versions
                        current_parts = [int(x) for x in current_version.split('.')[:3]]
                        required_parts = [int(x) for x in required_version.split('.')[:3]]
                        
                        needs_update = current_parts < required_parts
                        logger.info(f"Required transformers version: >={required_version} (needs update: {needs_update})")
                        return current_version, needs_update
            
            # If we don't have specific requirements, assume it's okay
            return current_version, False
            
        except Exception as e:
            logger.warning(f"Error checking transformers version: {e}")
            return "unknown", False
    
    def _get_model_architecture(self) -> str:
        """
        Extract the model architecture from model name
        
        Returns:
            Model architecture identifier
        """
        model_name = self.config.model_name.lower()
        
        # Extract architecture from common model naming patterns
        if "gemma-3" in model_name:
            return "gemma3_text"
        elif "gemma" in model_name:
            return "gemma_text"
        elif "llama-3" in model_name or "llama3" in model_name:
            return "llama3"
        elif "llama-2" in model_name or "llama2" in model_name:
            return "llama2"
        elif "mistral" in model_name:
            return "mistral"
        elif "mixtral" in model_name:
            return "mixtral"
        elif "falcon" in model_name:
            return "falcon"
        elif "phi" in model_name:
            return "phi"
        elif "qwen" in model_name:
            return "qwen"
        
        # Generic fallback
        return "generic"
    
    def _update_transformers(self, from_source: bool = False) -> bool:
        """
        Update transformers package
        
        Args:
            from_source: Whether to install from GitHub source
            
        Returns:
            Success status
        """
        try:
            cmd = None
            if from_source:
                cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'git+https://github.com/huggingface/transformers.git']
                logger.info("Installing transformers from source...")
            else:
                cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'transformers']
                logger.info("Upgrading transformers package...")
            
            # Run the pip install command
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("Successfully updated transformers package")
                
                # Reload transformers module to use the new version
                if 'transformers' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['transformers'])
                
                return True
            else:
                logger.error(f"Failed to update transformers: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating transformers: {e}")
            return False
    
    def _check_and_install_dependencies(self) -> bool:
        """
        Check if required dependencies for the model architecture are installed and install them if missing
        
        Returns:
            Success status
        """
        try:
            model_arch = self._get_model_architecture().lower()
            required_deps = []
            
            # Find dependencies for this model architecture
            for arch_prefix, deps in self.MODEL_REQUIRED_DEPENDENCIES.items():
                if arch_prefix.lower() in model_arch:
                    required_deps.extend(deps)
                    logger.info(f"Model {model_arch} requires dependencies: {deps}")
            
            if not required_deps:
                return True  # No special dependencies needed
            
            # Check if dependencies are installed
            missing_deps = []
            for dep in required_deps:
                package_name = dep.split(">=")[0].split("==")[0].strip()
                try:
                    import importlib
                    importlib.import_module(package_name)
                    logger.info(f"Dependency {package_name} is already installed")
                except ImportError:
                    missing_deps.append(dep)
                    logger.warning(f"Missing required dependency: {dep}")
            
            # Install missing dependencies
            if missing_deps:
                logger.info(f"Installing missing dependencies: {missing_deps}")
                for dep in missing_deps:
                    try:
                        cmd = [sys.executable, '-m', 'pip', 'install', dep]
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        stdout, stderr = process.communicate()
                        
                        if process.returncode == 0:
                            logger.info(f"Successfully installed {dep}")
                        else:
                            logger.error(f"Failed to install {dep}: {stderr}")
                            return False
                    except Exception as e:
                        logger.error(f"Error installing {dep}: {e}")
                        return False
            
            # If we have missing dependencies and successfully installed them, 
            # we need to reload related modules
            if missing_deps:
                try:
                    # Try to reload transformers module if it's already imported
                    if 'transformers' in sys.modules:
                        import importlib
                        importlib.reload(sys.modules['transformers'])
                        logger.info("Reloaded transformers module to recognize newly installed dependencies")
                except Exception as e:
                    logger.warning(f"Error reloading modules after dependency installation: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False
    
    def set_callbacks(self, callbacks):
        """Set callbacks for training progress updates"""
        self.callbacks = callbacks
    
    def load_model(self) -> None:
        """Load the base model and tokenizer with robust error handling and universal compatibility"""
        logger.info(f"Loading model: {self.config.model_name}")
        
        # Check and install required dependencies for the model architecture
        deps_installed = self._check_and_install_dependencies()
        if not deps_installed:
            logger.warning("Some dependencies could not be installed automatically.")
            logger.info("Please manually install the required dependencies with:")
            
            # Get model architecture and required dependencies
            model_arch = self._get_model_architecture().lower()
            for arch_prefix, deps in self.MODEL_REQUIRED_DEPENDENCIES.items():
                if arch_prefix.lower() in model_arch:
                    for dep in deps:
                        logger.info(f"  pip install {dep}")
        
        try:
            # First attempt: Use the robust universal ModelLoader
            logger.info("Using universal ModelLoader for robust model loading")
            
            # Import the loader factory
            from .model_loader_factory import ModelLoaderFactory
            
            # Configure quantization settings
            quantization_config = None
            if self.config.training_type in ["lora", "qlora"]:
                if self.config.use_4bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_use_double_quant_nested=True,
                        llm_int8_enable_fp32_cpu_offload=self.config.enable_cpu_offload
                    )
                elif self.config.use_8bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_enable_fp32_cpu_offload=self.config.enable_cpu_offload
                    )
            
            # Setup device mapping for memory optimization
            device_map = self.config.device_map
            max_memory = self._setup_memory_configuration()
            
            # Load model and tokenizer using the factory
            self.model, self.tokenizer = ModelLoaderFactory.load_model_and_tokenizer(
                model_name=self.config.model_name,
                device_map=device_map,
                quantization_config=quantization_config,
                torch_dtype=self.config.torch_dtype,
                auto_fix_issues=True
            )
            
            # Handle pad token if not set
            if self.tokenizer.pad_token is None:
                if self.tokenizer.eos_token:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    logger.info("Set pad_token to eos_token")
                elif hasattr(self.tokenizer, "unk_token") and self.tokenizer.unk_token:
                    self.tokenizer.pad_token = self.tokenizer.unk_token
                    logger.info("Set pad_token to unk_token")
                else:
                    logger.warning("No pad token found, setting pad_token to a special token")
                    self.tokenizer.pad_token = "[PAD]"
            
            # Set up LoRA if needed
            if self.config.training_type in ["lora", "qlora"]:
                logger.info(f"Setting up {self.config.training_type.upper()} fine-tuning")
                if self.config.use_8bit or self.config.use_4bit:
                    self.model = prepare_model_for_kbit_training(self.model)
                
                peft_config = LoraConfig(
                    task_type=TaskType.CAUSAL_LM,
                    inference_mode=False,
                    r=self.config.lora_r,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                    target_modules=self._get_target_modules(),
                )
                
                self.model = get_peft_model(self.model, peft_config)
                self.model.print_trainable_parameters()
            
            logger.info("Model loaded successfully using universal loader")
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error loading model with universal loader: {error_message}")
            
            # Fall back to traditional loading method
            logger.info("Falling back to traditional loading method...")
            
            # Check transformers version compatibility
            current_version, needs_update = self._check_transformers_version()
            
            # If update is needed, inform the user and offer to update
            if needs_update:
                update_message = (
                    f"Your transformers version ({current_version}) might be too old for model {self.config.model_name}.\n"
                    f"The model may require a newer version or installing from source."
                )
                logger.warning(update_message)
                
                # In a real CLI scenario, we'd ask for user confirmation here
                # For now, we'll attempt the update automatically
                model_arch = self._get_model_architecture()
                from_source = any(p.startswith('git+') for a, p in self.MODEL_ARCHITECTURE_PACKAGES.items() if a.lower() in model_arch.lower())
                
                logger.info(f"Attempting to update transformers {'from source' if from_source else 'to latest version'}...")
                update_success = self._update_transformers(from_source=from_source)
                
                if update_success:
                    logger.info("Transformers updated successfully. Continuing with model loading.")
                else:
                    logger.warning("Could not update transformers automatically. Trying to load model with current version.")
            
            # Verify authentication is set up for potentially gated models
            try:
                from huggingface_hub import HfFolder
                
                if HfFolder.get_token() is None:
                    logger.warning(
                        "No Hugging Face token found. If you're trying to access a gated model, "
                        "this will fail. Please set HF_TOKEN environment variable."
                    )
            except:
                # Continue even if huggingface_hub is not available
                pass
            
            # Configure quantization settings
            quantization_config = None
            if self.config.training_type in ["lora", "qlora"]:
                if self.config.use_4bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_use_double_quant_nested=True,  # Enable nested quantization
                        llm_int8_enable_fp32_cpu_offload=self.config.enable_cpu_offload  # Enable CPU offloading
                    )
                elif self.config.use_8bit:
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_enable_fp32_cpu_offload=self.config.enable_cpu_offload  # Enable CPU offloading
                    )
            
            # Load tokenizer with robust error handling
            try:
                logger.info(f"Loading tokenizer for model: {self.config.model_name}")
                
                # Try to handle common tokenizer errors before they happen
                try:
                    # Check for sentencepiece specifically for models that need it
                    model_arch = self._get_model_architecture().lower()
                    if any(arch in model_arch for arch in ["gemma", "llama", "mistral", "mixtral", "phi"]):
                        try:
                            import sentencepiece
                            logger.info("SentencePiece library found")
                        except ImportError:
                            raise ImportError(
                                "This model requires the SentencePiece library but it was not found in your environment. "
                                "Please install it with: pip install sentencepiece"
                            )
                            
                    # Special handling for Gemma-3 tokenizer
                    if "gemma3" in model_arch or "gemma-3" in model_arch:
                        try:
                            # Check if the specific module is available
                            from importlib.util import find_spec
                            if find_spec('transformers.models.gemma.tokenization_gemma') is None:
                                logger.warning("Gemma tokenizer module not found in transformers")
                                # Try to fix it
                                from utils.transformers_fix import fix_transformers_installation
                                if not fix_transformers_installation():
                                    raise ImportError(
                                        "The Gemma tokenizer module is not available in your transformers installation. "
                                        "Please update transformers: pip install --upgrade git+https://github.com/huggingface/transformers.git"
                                    )
                        except ImportError as e:
                            logger.error(f"Error checking for Gemma tokenizer module: {e}")
                            raise
                            
                except ImportError as e:
                    logger.error(f"Dependency error: {e}")
                    raise
                        
                # Now try to load the tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_name,
                    trust_remote_code=True,
                    use_fast=False  # Use slow tokenizer for better compatibility
                )
                
                # Handle pad token if not set
                if self.tokenizer.pad_token is None:
                    if self.tokenizer.eos_token:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                    elif hasattr(self.tokenizer, "unk_token") and self.tokenizer.unk_token:
                        self.tokenizer.pad_token = self.tokenizer.unk_token
                    else:
                        logger.warning("No pad token found, setting pad_token to a special token")
                        self.tokenizer.pad_token = "[PAD]"
                
                logger.info(f"Tokenizer loaded successfully. Vocab size: {len(self.tokenizer)}")
            except ImportError as e:
                # Specific handling for import errors (missing dependencies)
                error_message = str(e)
                logger.error(f"Dependency error: {error_message}")
                
                # Suggest pip installation command for the missing dependency
                if "sentencepiece" in error_message.lower():
                    logger.error("SentencePiece library is required but not installed.")
                    logger.info("Please install it with: pip install sentencepiece")
                elif "tokenizers" in error_message.lower():
                    logger.info("Please install it with: pip install tokenizers")
                elif "tiktoken" in error_message.lower():
                    logger.info("Please install it with: pip install tiktoken")
                
                raise
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error loading tokenizer: {error_message}")
                
                if "model type" in error_message.lower() and "does not recognize this architecture" in error_message.lower():
                    # Handle architecture not recognized error
                    self._handle_unsupported_architecture(error_message)
                    raise ValueError(f"Could not load tokenizer: {error_message}")
                else:
                    # Re-raise other errors
                    raise
            
            # Setup device mapping for memory optimization
            device_map = self.config.device_map
            max_memory = self._setup_memory_configuration()
            
            logger.info(f"Device map: {device_map}")
            logger.info(f"Memory configuration: {max_memory}")
            
            # Enhanced error handling for model loading
            try:
                logger.info(f"Loading model: {self.config.model_name} with quantization: {quantization_config}")
                
                # Use a more robust model loading approach
                self.model = self._load_model_with_fallbacks(
                    model_id=self.config.model_name,
                    quantization_config=quantization_config,
                    device_map=device_map,
                    max_memory=max_memory
                )
                
                # Set up LoRA if needed
                if self.config.training_type in ["lora", "qlora"]:
                    logger.info(f"Setting up {self.config.training_type.upper()} fine-tuning")
                    if self.config.use_8bit or self.config.use_4bit:
                        self.model = prepare_model_for_kbit_training(self.model)
                    
                    peft_config = LoraConfig(
                        task_type=TaskType.CAUSAL_LM,
                        inference_mode=False,
                        r=self.config.lora_r,
                        lora_alpha=self.config.lora_alpha,
                        lora_dropout=self.config.lora_dropout,
                        target_modules=self._get_target_modules(),
                    )
                    
                    self.model = get_peft_model(self.model, peft_config)
                    self.model.print_trainable_parameters()
                
                logger.info("Model loaded successfully")
                
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error loading model: {error_message}")
                
                if "model type" in error_message.lower() and "does not recognize this architecture" in error_message.lower():
                    # Handle architecture not recognized error
                    self._handle_unsupported_architecture(error_message)
                    raise ValueError(f"Could not load model: {error_message}")
                else:
                    # Re-raise other errors
                    raise

    def _load_model_with_fallbacks(self, model_id: str, quantization_config=None, device_map="auto", max_memory=None):
        """
        Load model with multiple fallback strategies
        
        Args:
            model_id: Hugging Face model ID
            quantization_config: Quantization configuration
            device_map: Device mapping strategy
            max_memory: Memory configuration
            
        Returns:
            Loaded model
        """
        try:
            # First attempt: Standard loading
            logger.info(f"Attempting to load model {model_id} (standard approach)")
            return AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map=device_map,
                max_memory=max_memory,
                trust_remote_code=True,
                torch_dtype=self.config.torch_dtype
            )
        except (ValueError, RuntimeError, ImportError) as e:
            logger.warning(f"Initial model loading failed: {e}")
            logger.info("Trying with more aggressive memory settings...")
            
            # Second attempt: More aggressive offloading
            try:
                return AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=quantization_config,
                    device_map="auto",
                    offload_folder="offload_folder",
                    offload_state_dict=True,
                    trust_remote_code=True,
                    torch_dtype=self.config.torch_dtype,
                    low_cpu_mem_usage=True
                )
            except Exception as e2:
                logger.warning(f"Second attempt failed: {e2}")
                
                # Third attempt: Try with safetensors loading explicit
                try:
                    logger.info("Attempting to load with safetensors disabled...")
                    return AutoModelForCausalLM.from_pretrained(
                        model_id,
                        quantization_config=quantization_config,
                        device_map="auto",
                        trust_remote_code=True,
                        torch_dtype=self.config.torch_dtype,
                        use_safetensors=False,
                        low_cpu_mem_usage=True
                    )
                except Exception as e3:
                    logger.warning(f"Third attempt failed: {e3}")
                    
                    # Final attempt: Try with minimum settings and return errors from all attempts
                    try:
                        logger.info("Final attempt with minimal settings...")
                        return AutoModelForCausalLM.from_pretrained(
                            model_id,
                            trust_remote_code=True,
                            torch_dtype=torch.float16,
                            device_map={"": "cpu"},  # Force CPU
                            low_cpu_mem_usage=True
                        )
                    except Exception as e4:
                        # Raise comprehensive error with all attempts
                        error_message = (
                            f"Failed to load model {model_id} after multiple attempts:\n"
                            f"- Attempt 1: {str(e)}\n"
                            f"- Attempt 2: {str(e2)}\n"
                            f"- Attempt 3: {str(e3)}\n"
                            f"- Attempt 4: {str(e4)}"
                        )
                        logger.error(error_message)
                        raise ValueError(error_message) from e4
    
    def _handle_unsupported_architecture(self, error_message: str):
        """
        Handle cases of unsupported model architecture with clear guidance
        
        Args:
            error_message: The original error message
        """
        # Extract model type from error message
        model_type_match = re.search(r"model type [`\"']([^`\"']+)[`\"']", error_message)
        model_type = model_type_match.group(1) if model_type_match else "unknown"
        
        # Provide helpful information about the error
        logger.error(f"Model architecture '{model_type}' not supported by current transformers version.")
        logger.info(
            "\n=== MODEL COMPATIBILITY ISSUE ===\n"
            f"The model '{self.config.model_name}' has architecture '{model_type}' which is not supported by your current transformers version.\n\n"
            "You have two options to fix this:\n"
            "1. Update transformers to the latest release: pip install --upgrade transformers\n"
            "2. Install transformers directly from GitHub: pip install git+https://github.com/huggingface/transformers.git\n"
            "\nAfter updating, restart your application and try again."
        )
        
        # Check if it's a known model type with specific version requirements
        for arch_prefix, package_req in self.MODEL_ARCHITECTURE_PACKAGES.items():
            if arch_prefix.lower() in model_type.lower():
                logger.info(f"Model type '{model_type}' requires: {package_req}")
                break
    
    def _setup_memory_configuration(self) -> Dict[str, str]:
        """Set up memory configuration for model loading"""
        # If custom memory configuration is provided, use it
        if self.config.max_memory:
            return self.config.max_memory
            
        # Otherwise create a sensible default based on available hardware
        max_memory = {}
        
        try:
            # Check GPU memory
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    # Reserve 90% of GPU memory
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)  # in GB
                    max_memory[i] = f"{int(gpu_memory * 0.9)}GiB"
                    
            # Reserve CPU memory
            import psutil
            system_memory = psutil.virtual_memory().total / (1024**3)  # in GB
            max_memory["cpu"] = f"{int(system_memory * 0.5)}GB"  # Use 50% of CPU memory
            
            logger.info(f"Automatic memory configuration: {max_memory}")
            return max_memory
        except Exception as e:
            logger.warning(f"Error setting up memory configuration: {e}")
            # Fallback to a simpler configuration
            if torch.cuda.is_available():
                return {0: "8GiB", "cpu": "16GB"}
            else:
                return {"cpu": "16GB"}

    def _get_target_modules(self) -> List[str]:
        """Get target modules for LoRA based on model architecture with expanded module patterns"""
        # Extract model architecture from name
        model_arch = self._get_model_architecture().lower()
        
        # New comprehensive target modules by architecture
        if "gemma3" in model_arch or "gemma-3" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_up", "down_proj", "up_proj"]
        elif "gemma" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        elif "llama3" in model_arch or "llama-3" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_up", "down_proj", "up_proj"]
        elif "llama2" in model_arch or "llama-2" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        elif "mistral" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        elif "mixtral" in model_arch:
            return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj", "w1", "w2", "w3"]
        elif "falcon" in model_arch:
            return ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"]
        elif "phi" in model_arch:
            return ["Wqkv", "out_proj", "fc1", "fc2"]
        elif "gpt" in model_arch:
            return ["attn.c_attn", "attn.c_proj", "mlp.c_fc", "mlp.c_proj"]
        elif "qwen" in model_arch:
            return ["c_attn", "c_proj", "w1", "w2"]
        else:
            # Generic fallback for unknown architectures
            return [
                "query", "key", "value", "q_proj", "k_proj", "v_proj", "o_proj", 
                "gate_proj", "up_proj", "down_proj", "out_proj", "fc1", "fc2",
                "dense", "attention", "self_attention", "layer_norm", "linear"
            ]
    
    def load_dataset(self) -> Dict[str, Dataset]:
        """Load and prepare dataset for fine-tuning"""
        logger.info(f"Loading dataset: {self.config.dataset_path} (type: {self.config.dataset_type})")
        
        # Path handling based on dataset type
        if self.config.dataset_type == "full":
            # Look for any of the structured datasets
            import glob
            structured_datasets = glob.glob("data/structured/*.json")
            if structured_datasets:
                dataset_path = structured_datasets[0]  # Use the first available structured dataset
                logger.info(f"Using structured dataset: {dataset_path}")
            else:
                raise ValueError("No structured datasets found in data/structured/ directory")
        elif self.config.dataset_type == "poc":
            # Look for any of the poc datasets
            import glob
            poc_datasets = glob.glob("data/poc/*.json")
            if poc_datasets:
                dataset_path = poc_datasets[0]  # Use the first available POC dataset
                logger.info(f"Using POC dataset: {dataset_path}")
            else:
                raise ValueError("No POC datasets found in data/poc/ directory")
        elif self.config.dataset_type.startswith("structured_"):
            # Extract the dataset name from the type
            dataset_name = self.config.dataset_type.replace("structured_", "")
            dataset_path = f"data/structured/{dataset_name}.json"
            if not os.path.exists(dataset_path):
                # Try with the full qualified name format
                possible_files = glob.glob(f"data/structured/*{dataset_name}*.json")
                if possible_files:
                    dataset_path = possible_files[0]
                else:
                    raise ValueError(f"Structured dataset '{dataset_name}' not found")
        elif self.config.dataset_type.startswith("poc_"):
            # Extract the dataset name from the type
            dataset_name = self.config.dataset_type.replace("poc_", "")
            dataset_path = f"data/poc/{dataset_name}.json"
            if not os.path.exists(dataset_path):
                # Try with the full qualified name format
                possible_files = glob.glob(f"data/poc/*{dataset_name}*.json")
                if possible_files:
                    dataset_path = possible_files[0]
                else:
                    raise ValueError(f"POC dataset '{dataset_name}' not found")
        else:
            # Use the provided path
            dataset_path = self.config.dataset_path
        
        try:
            # Check if it's a local file or a relative path in standard data directories
            if os.path.exists(dataset_path):
                # Local file exists directly
                logger.info(f"Loading local dataset file: {dataset_path}")
                file_path = dataset_path
            else:
                # Try common data directories for relative paths
                potential_paths = [
                    dataset_path,  # Original path
                    os.path.join("data", dataset_path),  # Check in data/
                    os.path.join("data", "structured", os.path.basename(dataset_path)),  # Check in data/structured/
                    os.path.join("data", "poc", os.path.basename(dataset_path)),  # Check in data/poc/
                    os.path.join("datasets", dataset_path)  # Check in datasets/
                ]
                
                # Try all potential paths
                found = False
                for path in potential_paths:
                    if os.path.exists(path):
                        logger.info(f"Found dataset at: {path}")
                        file_path = path
                        found = True
                        break
                
                # If not found locally, check if it's a HuggingFace dataset ID
                if not found:
                    # Check if it looks like a HuggingFace dataset ID (no slashes or file extensions)
                    is_hf_dataset = "/" not in dataset_path and "." not in os.path.basename(dataset_path)
                    
                    if is_hf_dataset:
                        logger.info(f"Attempting to load from HuggingFace Hub: {dataset_path}")
                        # Load from HuggingFace datasets
                        dataset = load_dataset(dataset_path)
                        if "train" in dataset and "validation" in dataset:
                            train_dataset = dataset["train"]
                            val_dataset = dataset["validation"]
                        else:
                            # Split dataset if no validation set
                            split_dataset = dataset["train"].train_test_split(test_size=0.1)
                            train_dataset = split_dataset["train"]
                            val_dataset = split_dataset["test"]
                        
                        # Tokenize datasets
                        train_dataset = self._tokenize_dataset(train_dataset)
                        val_dataset = self._tokenize_dataset(val_dataset)
                        
                        logger.info(f"HuggingFace dataset loaded: {len(train_dataset)} training examples, {len(val_dataset)} validation examples")
                        return {"train": train_dataset, "validation": val_dataset}
                    else:
                        # It's a file path that doesn't exist
                        raise ValueError(f"Dataset file not found: {dataset_path}. Checked in: {', '.join(potential_paths)}")
            
            # Load local JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert to dataset format expected by HF
            formatted_data = []
            if isinstance(data, list):
                formatted_data = [{"text": self._format_example(item)} for item in data]
            elif isinstance(data, dict) and "examples" in data:
                formatted_data = [{"text": self._format_example(item)} for item in data["examples"]]
            
            train_val_split = int(0.9 * len(formatted_data))
            train_data = formatted_data[:train_val_split]
            val_data = formatted_data[train_val_split:]
            
            train_dataset = Dataset.from_list(train_data)
            val_dataset = Dataset.from_list(val_data)
            
            # Tokenize datasets
            train_dataset = self._tokenize_dataset(train_dataset)
            val_dataset = self._tokenize_dataset(val_dataset)
            
            logger.info(f"Dataset loaded: {len(train_dataset)} training examples, {len(val_dataset)} validation examples")
            return {"train": train_dataset, "validation": val_dataset}
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _format_example(self, example: Union[str, Dict]) -> str:
        """Format a single training example"""
        if isinstance(example, str):
            return example
        elif isinstance(example, dict):
            if "input" in example and "output" in example:
                return f"### Input:\n{example['input']}\n\n### Output:\n{example['output']}"
            elif "instruction" in example and "response" in example:
                if "input" in example and example["input"]:
                    return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['response']}"
                else:
                    return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"
            elif "prompt" in example and "completion" in example:
                return f"{example['prompt']}{example['completion']}"
            else:
                # Try to extract text field or stringify the example
                return example.get("text", str(example))
        return str(example)
    
    def _tokenize_dataset(self, dataset: Dataset) -> Dataset:
        """Tokenize dataset for training"""
        logger.info("Tokenizing dataset...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=2048,
                padding="max_length",
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        return tokenized_dataset
    
    def setup_training(self, train_dataset: Dataset, val_dataset: Dataset) -> None:
        """Set up the training process"""
        logger.info("Setting up training...")
        
        # Configure training arguments
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.config.output_dir, f"{timestamp}")
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            eval_accumulation_steps=self.config.gradient_accumulation_steps,
            evaluation_strategy=self.config.evaluation_strategy,
            eval_steps=self.config.eval_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            learning_rate=self.config.learning_rate,
            weight_decay=0.01,
            max_grad_norm=self.config.max_grad_norm,
            warmup_ratio=self.config.warmup_ratio,
            logging_dir=os.path.join(output_dir, "logs"),
            logging_steps=self.config.logging_steps,
            report_to=["tensorboard"],
            max_steps=self.config.max_steps if self.config.max_steps > 0 else None,
            fp16=True,
            seed=self.config.seed,
            data_seed=self.config.seed
        )
        
        # Create data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Define a custom callback that wraps our callbacks
        if self.callbacks:
            class EpochCallback(TrainerCallback):
                def __init__(self, callbacks):
                    self.callbacks = callbacks
                
                def on_epoch_begin(self, args, state, control, **kwargs):
                    epoch = state.epoch
                    total_epochs = args.num_train_epochs
                    steps = state.max_steps
                    self.callbacks.on_epoch_begin(int(epoch), int(total_epochs), steps)
                    
                def on_epoch_end(self, args, state, control, **kwargs):
                    epoch = state.epoch
                    metrics = {"loss": state.log_history[-1]["loss"] if state.log_history else 0}
                    self.callbacks.on_epoch_end(int(epoch), metrics)
            
            callbacks = [EpochCallback(self.callbacks)]
        else:
            callbacks = []
        
        # Create trainer with callbacks
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            callbacks=callbacks
        )
        
        logger.info(f"Training setup complete. Output directory: {output_dir}")
    
    def train(self) -> Dict[str, Any]:
        """Run the training process with progress tracking"""
        logger.info("Starting training...")
        
        # Create active training file with initial information
        active_file = os.path.join(self.trainer.args.output_dir, "training_active.json")
        try:
            with open(active_file, 'w') as f:
                json.dump({
                    "model_name": self.config.model_name,
                    "dataset_type": self.config.dataset_type,
                    "approach": self.config.training_type,
                    "created_at": datetime.now().isoformat(),
                    "status": "in_progress",
                    "progress": {
                        "current_epoch": 0,
                        "total_epochs": self.config.epochs,
                        "current_step": 0,
                        "total_steps": self.trainer.state.max_steps,
                        "start_time": datetime.now().isoformat()
                    }
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not create active training file: {e}")
        
        # Notify train begin if callback exists
        if self.callbacks:
            self.callbacks.on_train_begin()
            
        # Monkey-patch the trainer to capture training steps
        original_training_step = self.trainer.training_step
        
        def patched_training_step(*args, **kwargs):
            # Get state from trainer
            state = self.trainer.state
            step = state.global_step
            max_steps = state.max_steps or 0
            
            # Extract loss and learning rate
            if hasattr(state, "log_history") and state.log_history:
                last_log = state.log_history[-1] if state.log_history else {}
                loss = last_log.get("loss", 0.0)
                lr = last_log.get("learning_rate", 0.0)
            else:
                loss = 0.0
                lr = 0.0
                
            # Update active training file with progress
            try:
                # Calculate epoch
                epoch = state.epoch if hasattr(state, "epoch") else 0
                if max_steps > 0:
                    epoch = int(step / max_steps * self.config.epochs)
                
                # Calculate elapsed time
                start_time = None
                if os.path.exists(active_file):
                    try:
                        with open(active_file, 'r') as f:
                            data = json.load(f)
                            if "progress" in data and "start_time" in data["progress"]:
                                start_time_str = data["progress"]["start_time"]
                                start_time = datetime.fromisoformat(start_time_str)
                    except:
                        pass
                
                elapsed_time = "Unknown"
                if start_time:
                    elapsed = datetime.now() - start_time
                    elapsed_time = str(elapsed).split('.')[0]  # Format as HH:MM:SS
                
                # Update progress
                progress = {
                    "current_epoch": int(epoch) + 1,  # Add 1 to make it 1-based
                    "total_epochs": self.config.epochs,
                    "current_step": step,
                    "total_steps": max_steps,
                    "current_loss": float(loss),
                    "learning_rate": float(lr),
                    "elapsed_time": elapsed_time
                }
                
                with open(active_file, 'w') as f:
                    json.dump({
                        "model_name": self.config.model_name,
                        "dataset_type": self.config.dataset_type,
                        "approach": self.config.training_type,
                        "created_at": datetime.now().isoformat(),
                        "status": "in_progress",
                        "progress": progress
                    }, f, indent=2)
            except Exception as e:
                logger.warning(f"Could not update active training file: {e}")
                
            # Call step callback
            if self.callbacks:
                self.callbacks.on_step(step, max_steps, loss, lr)
                
            # Call original method
            return original_training_step(*args, **kwargs)
            
        # Replace method
        self.trainer.training_step = patched_training_step
        
        try:
            # Original training code continues
            train_result = self.trainer.train()
            
            # Save trained model
            logger.info("Saving final model...")
            self.trainer.save_model()
            self.trainer.save_state()
            
            # Calculate and log metrics
            metrics = train_result.metrics
            self.trainer.log_metrics("train", metrics)
            self.trainer.save_metrics("train", metrics)
            
            # Evaluate on validation set
            logger.info("Running final evaluation...")
            eval_metrics = self.trainer.evaluate()
            self.trainer.log_metrics("eval", eval_metrics)
            self.trainer.save_metrics("eval", eval_metrics)
            
            # Save tokenizer
            self.tokenizer.save_pretrained(self.trainer.args.output_dir)
            
            # Remove active file and create completed info file
            try:
                if os.path.exists(active_file):
                    os.remove(active_file)
                    
                # Save final training info
                with open(os.path.join(self.trainer.args.output_dir, "training_info.json"), 'w') as f:
                    json.dump({
                        "model_name": self.config.model_name,
                        "dataset_type": self.config.dataset_type,
                        "approach": self.config.training_type,
                        "created_at": datetime.now().isoformat(),
                        "status": "completed",
                        "metrics": {
                            "train_metrics": metrics,
                            "eval_metrics": eval_metrics,
                        },
                        "config": {
                            "learning_rate": self.config.learning_rate,
                            "batch_size": self.config.batch_size,
                            "epochs": self.config.epochs,
                            "model_name": self.config.model_name,
                            "training_type": self.config.training_type
                        }
                    }, f, indent=2)
            except Exception as e:
                logger.warning(f"Could not save final training info: {e}")
                
            # Notify train end if callback exists
            if self.callbacks:
                self.callbacks.on_train_end(self.trainer.args.output_dir)
            
            logger.info(f"Training complete! Model saved to {self.trainer.args.output_dir}")
            
            # Return results
            return {
                "output_dir": self.trainer.args.output_dir,
                "train_metrics": metrics,
                "eval_metrics": eval_metrics,
                "model_name": self.config.model_name,
                "training_type": self.config.training_type,
                "learning_rate": self.config.learning_rate,
                "batch_size": self.config.batch_size,
                "epochs": self.config.epochs
            }
        except Exception as e:
            # Handle training errors
            error_msg = str(e)
            logger.error(f"Training error: {error_msg}")
            
            # Save error information
            try:
                error_file = os.path.join(self.trainer.args.output_dir, "training_error.json")
                with open(error_file, 'w') as f:
                    json.dump({
                        "model_name": self.config.model_name,
                        "dataset_type": self.config.dataset_type,
                        "approach": self.config.training_type,
                        "created_at": datetime.now().isoformat(),
                        "status": "failed",
                        "error": error_msg,
                        "traceback": traceback.format_exc()
                    }, f, indent=2)
                    
                # Remove active file if exists
                if os.path.exists(active_file):
                    os.remove(active_file)
            except Exception as save_error:
                logger.error(f"Could not save error information: {save_error}")
                
            # Re-raise the exception
            raise
    
    def run_finetuning(self) -> Dict[str, Any]:
        """Run the full fine-tuning pipeline"""
        try:
            # Load model and tokenizer
            self.load_model()
            
            # Load dataset
            datasets = self.load_dataset()
            
            # Setup training
            self.setup_training(datasets["train"], datasets["validation"])
            
            # Run training
            results = self.train()
            
            return results
        except ImportError as e:
            # Handle dependency errors gracefully with clear instructions
            error_msg = str(e)
            logger.error(f"Dependency error: {error_msg}")
            
            # Provide clear guidance for installing missing packages
            if "sentencepiece" in error_msg.lower():
                logger.info(
                    "\n=== MISSING DEPENDENCY ===\n"
                    "The SentencePiece library is required for this model but it wasn't found.\n"
                    "Please install it with: pip install sentencepiece\n"
                    "After installing, restart your application and try again."
                )
            elif "tiktoken" in error_msg.lower():
                logger.info(
                    "\n=== MISSING DEPENDENCY ===\n"
                    "The tiktoken library is required for this model but it wasn't found.\n"
                    "Please install it with: pip install tiktoken\n"
                    "After installing, restart your application and try again."
                )
            else:
                # Generic guidance for other missing packages
                package_match = re.search(r"No module named '([^']+)'", error_msg)
                if package_match:
                    missing_package = package_match.group(1)
                    logger.info(
                        f"\n=== MISSING DEPENDENCY ===\n"
                        f"The {missing_package} package is required but it wasn't found.\n"
                        f"Please install it with: pip install {missing_package}\n"
                        f"After installing, restart your application and try again."
                    )
            
            # Re-raise the exception with improved message
            raise ImportError(f"Missing dependency for model {self.config.model_name}. See log for installation instructions.") from e
        except Exception as e:
            # Handle other errors
            logger.error(f"Error in fine-tuning pipeline: {e}")
            raise
