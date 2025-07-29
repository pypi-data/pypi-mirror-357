"""Utility for managing model dependencies"""
import sys
import subprocess
import logging
import importlib
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manager for handling model dependencies"""
    
    # Model architecture to required packages mapping
    MODEL_DEPENDENCIES = {
        "gemma": ["sentencepiece>=0.1.97"],
        "gemma-3": ["sentencepiece>=0.1.99", "transformers>=4.38.0"],  # Gemma-3 needs newer transformers
        "gemma3": ["sentencepiece>=0.1.99", "transformers>=4.38.0"],   # Alternative naming
        "llama": ["sentencepiece>=0.1.97"],
        "mistral": ["sentencepiece>=0.1.97"],
        "mixtral": ["sentencepiece>=0.1.97"],
        "phi": ["sentencepiece>=0.1.97"],
        "qwen": ["tiktoken>=0.5.0"],
        "gpt-neox": ["sentencepiece>=0.1.97"],
    }
    
    # Special installation commands for certain packages
    SPECIAL_INSTALL_COMMANDS = {
        "transformers_gemma3": [sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/huggingface/transformers.git"]
    }
    
    @staticmethod
    def check_dependency(package_name: str) -> bool:
        """
        Check if a dependency is installed
        
        Args:
            package_name: Name of the package to check
            
        Returns:
            True if installed, False otherwise
        """
        try:
            # Strip version requirements to get base package name
            base_name = package_name.split(">=")[0].split("==")[0].strip()
            importlib.import_module(base_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_package(package_spec: str) -> bool:
        """
        Install a Python package using pip
        
        Args:
            package_spec: Package specification (name and optional version)
            
        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            logger.info(f"Installing {package_spec}...")
            cmd = [sys.executable, "-m", "pip", "install", package_spec]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Successfully installed {package_spec}")
                return True
            else:
                logger.error(f"Failed to install {package_spec}: {stderr}")
                return False
        except Exception as e:
            logger.error(f"Error installing {package_spec}: {e}")
            return False
    
    @staticmethod
    def check_transformers_version_for_model(model_name: str) -> bool:
        """
        Check if the installed transformers version is compatible with a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if compatible, False if needs update
        """
        try:
            # Import transformers to check version
            import transformers
            import re
            
            current_version = transformers.__version__
            logger.info(f"Current transformers version: {current_version}")
            
            # For Gemma-3 models, we need 4.38.0 or higher
            if "gemma-3" in model_name.lower() or "gemma3" in model_name.lower():
                current_parts = [int(x) for x in current_version.split('.')[:3]]
                required_parts = [4, 38, 0]
                
                if current_parts < required_parts:
                    logger.warning(f"Transformers version {current_version} is too old for Gemma-3 models")
                    logger.warning(f"Need transformers >= 4.38.0 (or latest from GitHub)")
                    return False
            
            return True
        except ImportError:
            logger.warning("Transformers not installed")
            return False
        except Exception as e:
            logger.error(f"Error checking transformers version: {e}")
            return False
    
    @staticmethod
    def update_transformers_for_gemma3() -> bool:
        """
        Update transformers to support Gemma-3 models
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Updating transformers to support Gemma-3 models...")
        
        # First try the latest release version
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "transformers>=4.38.0"]
            logger.info(f"Running: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info("Successfully updated transformers to latest release")
                return True
            else:
                logger.warning(f"Failed to update transformers to latest release: {process.stderr}")
        except Exception as e:
            logger.error(f"Error updating transformers: {e}")
        
        # If that fails, try from GitHub
        try:
            cmd = DependencyManager.SPECIAL_INSTALL_COMMANDS["transformers_gemma3"]
            logger.info(f"Installing transformers from GitHub: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info("Successfully installed transformers from GitHub")
                
                # Reload transformers module
                if 'transformers' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['transformers'])
                
                return True
            else:
                logger.error(f"Failed to install transformers from GitHub: {process.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error installing transformers from GitHub: {e}")
            return False
    
    @staticmethod
    def ensure_gemma3_support() -> bool:
        """
        Ensure support for Gemma-3 models
        
        Returns:
            True if support is available or was successfully added
        """
        try:
            # Try to import the Gemma tokenizer module specifically
            from importlib.util import find_spec
            
            # Check if the module exists
            if find_spec('transformers.models.gemma.tokenization_gemma') is None:
                logger.warning("Gemma tokenizer module not found in transformers")
                
                # Update transformers
                if not DependencyManager.update_transformers_for_gemma3():
                    logger.error("Failed to update transformers for Gemma-3 support")
                    return False
                
                # Check again
                if find_spec('transformers.models.gemma.tokenization_gemma') is None:
                    logger.error("Still cannot find Gemma tokenizer module after update")
                    return False
            
            return True
        except ImportError:
            logger.warning("Could not check for Gemma tokenizer module")
            return False
    
    @staticmethod
    def ensure_model_dependencies(model_name: str) -> bool:
        """
        Ensure all dependencies for a given model are installed
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if all dependencies are installed or successfully installed,
            False if any dependency could not be installed
        """
        model_name_lower = model_name.lower()
        required_packages = []
        
        # Special handling for Gemma-3
        if "gemma-3" in model_name_lower or "gemma3" in model_name_lower:
            if not DependencyManager.ensure_gemma3_support():
                logger.warning("Could not ensure Gemma-3 support")
                # Continue anyway to install other dependencies
        
        # Find packages required for this model
        for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
            if arch.lower() in model_name_lower:
                required_packages.extend(packages)
        
        if not required_packages:
            logger.info(f"No specific dependencies identified for model: {model_name}")
            return True
        
        logger.info(f"Checking dependencies for model: {model_name}")
        
        # Check and install missing dependencies
        all_installed = True
        for package_spec in required_packages:
            base_package = package_spec.split(">=")[0].split("==")[0].strip()
            
            if not DependencyManager.check_dependency(base_package):
                logger.info(f"Dependency {base_package} is missing")
                if not DependencyManager.install_package(package_spec):
                    all_installed = False
            else:
                logger.info(f"Dependency {base_package} is already installed")
        
        return all_installed
    
    @staticmethod
    def get_installation_commands(model_name: str) -> List[str]:
        """
        Get pip install commands for a model's dependencies
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of pip install commands
        """
        model_name = model_name.lower()
        required_packages = []
        
        # Find packages required for this model
        for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
            if arch.lower() in model_name:
                required_packages.extend(packages)
        
        return [f"pip install {package}" for package in required_packages]


if __name__ == "__main__":
    """CLI for installing model dependencies"""
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Install dependencies for specific models")
    parser.add_argument("model", help="Model name to install dependencies for")
    
    args = parser.parse_args()
    
    # Get and install dependencies
    success = DependencyManager.ensure_model_dependencies(args.model)
    
    if success:
        print(f"All dependencies for {args.model} are installed!")
    else:
        print(f"Some dependencies for {args.model} could not be installed.")
        print("Please try to install them manually with:")
        for cmd in DependencyManager.get_installation_commands(args.model):
            print(f"  {cmd}")
