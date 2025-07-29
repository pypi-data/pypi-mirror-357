"""
Utility functions for training workflows, including dependency management
and dataset preparation.
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import importlib.util

from .dependency_manager import DependencyManager
from .dataset_processor import DatasetProcessor
from .dataset_formatter import DatasetFormatter

logger = logging.getLogger(__name__)

class TrainingPreparationError(Exception):
    """Exception raised for errors in training preparation"""
    pass

def verify_model_dependencies(model_name: str, auto_install: bool = False) -> bool:
    """
    Verify that all dependencies required for a model are installed
    
    Args:
        model_name: Name of the model
        auto_install: Whether to automatically install missing dependencies
        
    Returns:
        True if all dependencies are available, False otherwise
    """
    logger.info(f"Verifying dependencies for model: {model_name}")
    
    # Check for required dependencies
    required_deps = []
    for arch, deps in DependencyManager.MODEL_DEPENDENCIES.items():
        if arch.lower() in model_name.lower():
            required_deps.extend(deps)
    
    if not required_deps:
        logger.info(f"No specific dependencies identified for model: {model_name}")
        return True
    
    # Check if each dependency is installed
    missing_deps = []
    for dep in required_deps:
        package_name = dep.split(">=")[0].split("==")[0].strip()
        if not DependencyManager.check_dependency(package_name):
            missing_deps.append(dep)
            logger.warning(f"Missing dependency: {dep}")
    
    # If there are missing dependencies and auto_install is enabled
    if missing_deps and auto_install:
        logger.info("Attempting to install missing dependencies...")
        for dep in missing_deps:
            if not DependencyManager.install_package(dep):
                logger.error(f"Failed to install dependency: {dep}")
                return False
        
        # Recheck dependencies
        for dep in missing_deps:
            package_name = dep.split(">=")[0].split("==")[0].strip()
            if not DependencyManager.check_dependency(package_name):
                logger.error(f"Dependency still missing after installation attempt: {package_name}")
                return False
        
        logger.info("All dependencies successfully installed")
        return True
    
    # Return True if there are no missing dependencies
    return len(missing_deps) == 0

def prepare_dataset_for_training(
    dataset_path: str, 
    model_name: str,
    prompt_field: Optional[str] = None,
    response_style: str = "varied",
    output_path: Optional[str] = None
) -> str:
    """
    Prepare a dataset for training with a specific model
    
    Args:
        dataset_path: Path to the dataset file
        model_name: Name of the model for formatting
        prompt_field: Field containing prompts (auto-detect if None)
        response_style: Style of responses to generate
        output_path: Path to save the formatted dataset
        
    Returns:
        Path to the prepared dataset
    """
    logger.info(f"Preparing dataset {dataset_path} for model {model_name}")
    
    # Make sure the dataset exists
    if not os.path.exists(dataset_path):
        error = f"Dataset file not found: {dataset_path}"
        logger.error(error)
        raise TrainingPreparationError(error)
    
    # Auto-detect prompt field if not specified
    if prompt_field is None:
        analysis = DatasetProcessor.analyze_dataset(dataset_path)
        if "error" in analysis:
            error = f"Error analyzing dataset: {analysis['error']}"
            logger.error(error)
            raise TrainingPreparationError(error)
        
        prompt_field = analysis.get("likely_prompt_field")
        if not prompt_field:
            error = "Could not auto-detect prompt field in dataset"
            logger.error(error)
            raise TrainingPreparationError(error)
        
        logger.info(f"Auto-detected prompt field: {prompt_field}")
    
    # Create output path if not specified
    if output_path is None:
        dataset_dir = os.path.dirname(dataset_path)
        dataset_name = os.path.splitext(os.path.basename(dataset_path))[0]
        output_path = os.path.join(dataset_dir, f"{dataset_name}_{model_name.split('/')[-1]}_formatted.json")
    
    # Format dataset for the model
    formatted_dataset = DatasetProcessor.format_dataset(
        input_path=dataset_path,
        prompt_field=prompt_field,
        model_name=model_name,
        response_style=response_style,
        output_path=output_path
    )
    
    if "error" in formatted_dataset:
        error = f"Error formatting dataset: {formatted_dataset['error']}"
        logger.error(error)
        raise TrainingPreparationError(error)
    
    logger.info(f"Dataset formatted and saved to: {output_path}")
    return output_path

def prepare_adversarial_dataset(
    model_name: str,
    count: int = 100,
    output_path: Optional[str] = None
) -> str:
    """
    Create an adversarial dataset for training
    
    Args:
        model_name: Name of the model for formatting
        count: Number of examples to generate
        output_path: Path to save the dataset
        
    Returns:
        Path to the created dataset
    """
    logger.info(f"Creating adversarial dataset with {count} examples for model {model_name}")
    
    # Create output path if not specified
    if output_path is None:
        output_dir = Path.home() / "dravik" / "data" / "adversarial"
        output_dir.mkdir(exist_ok=True, parents=True)
        output_path = str(output_dir / f"adversarial_{model_name.split('/')[-1]}.json")
    
    # Create the dataset
    dataset = DatasetProcessor.create_adversarial_dataset(
        count=count,
        model_name=model_name,
        output_path=output_path
    )
    
    logger.info(f"Adversarial dataset created with {len(dataset['examples'])} examples")
    logger.info(f"Dataset saved to: {output_path}")
    
    return output_path

def verify_huggingface_token() -> bool:
    """
    Check if a Hugging Face token is available in the environment
    
    Returns:
        True if a token is available, False otherwise
    """
    try:
        from huggingface_hub import HfFolder, HfApi
        import os
        
        # First check if token is already set in HfFolder
        token = HfFolder.get_token()
        if token is not None:
            # Validate the token is working
            try:
                api = HfApi()
                # Try a simple operation to validate token
                api.whoami(token=token)
                return True
            except:
                logger.warning("Hugging Face token found but appears to be invalid")
                # Token invalid, continue to check environment
                
        # Check environment variables
        for var in ["HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_TOKEN"]:
            if var in os.environ and os.environ[var]:
                token = os.environ[var]
                try:
                    # Set the token in the HF folder
                    from huggingface_hub import login
                    login(token=token, write_token=True)
                    # Validate token works
                    api = HfApi()
                    api.whoami(token=token)
                    return True
                except:
                    logger.warning(f"Found token in {var} but it appears to be invalid")
                    # Continue checking other variables
        
        return False
    except ImportError:
        logger.warning("huggingface_hub package not installed, cannot verify token")
        return False

def setup_environment_for_training(
    model_name: str,
    auto_install_deps: bool = False,
    require_hf_token: bool = True
) -> Dict[str, bool]:
    """
    Set up the environment for training by checking dependencies and authentication
    
    Args:
        model_name: Name of the model to train
        auto_install_deps: Whether to automatically install missing dependencies
        require_hf_token: Whether to require a Hugging Face token
        
    Returns:
        Dictionary with status of each check
    """
    status = {
        "dependencies": False,
        "hf_token": False,
        "torch_available": False,
        "cuda_available": False
    }
    
    # Check dependencies
    try:
        status["dependencies"] = verify_model_dependencies(model_name, auto_install_deps)
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
    
    # Check HF token
    if require_hf_token:
        try:
            status["hf_token"] = verify_huggingface_token()
        except Exception as e:
            logger.error(f"Error checking Hugging Face token: {e}")
    else:
        status["hf_token"] = True  # Not required
    
    # Check torch
    try:
        import torch
        status["torch_available"] = True
        status["cuda_available"] = torch.cuda.is_available()
    except ImportError:
        logger.warning("PyTorch not installed")
    
    # Log status
    logger.info("Environment check results:")
    for check, result in status.items():
        logger.info(f"  {check}: {'✓' if result else '✗'}")
    
    return status
