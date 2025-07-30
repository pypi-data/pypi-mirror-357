"""
Factory for the ModelLoader to support universal model loading across different architectures.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, Tuple
import torch

from .model_loader import ModelLoader

logger = logging.getLogger(__name__)

class ModelLoaderFactory:
    """
    Factory class to create and manage model loaders for different architectures.
    This provides simplified integration with the existing finetuning system.
    """
    
    @staticmethod
    def load_model_and_tokenizer(
        model_name: str, 
        device_map: str = "auto",
        quantization_config: Optional[Dict[str, Any]] = None,
        torch_dtype: torch.dtype = torch.float16,
        auto_fix_issues: bool = True
    ) -> Tuple[Any, Any]:
        """
        Load a model and tokenizer with automatic architecture detection and error correction
        
        Args:
            model_name: HuggingFace model name or path
            device_map: Device mapping strategy
            quantization_config: Optional quantization configuration
            torch_dtype: Torch data type
            auto_fix_issues: Whether to automatically fix common issues
            
        Returns:
            Tuple of (model, tokenizer)
        """
        logger.info(f"Loading model {model_name} using universal ModelLoader")
        
        # Create loader with appropriate options
        loader = ModelLoader(
            model_name_or_path=model_name,
            device_map=device_map,
            auto_fix_issues=auto_fix_issues
        )
        
        try:
            # First check dependencies
            if not loader.check_and_install_dependencies():
                logger.warning(f"Some dependencies for {model_name} could not be installed automatically")
                logger.info("Continuing with model loading anyway...")
            
            # Load model and tokenizer with all the error handling and recovery logic
            model, tokenizer = loader.load_model_and_tokenizer(
                quantization_config=quantization_config,
                torch_dtype=torch_dtype
            )
            
            logger.info(f"Successfully loaded model {model_name} using universal loader")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Error loading model with universal loader: {e}")
            # Re-raise to let the caller handle it
            raise
