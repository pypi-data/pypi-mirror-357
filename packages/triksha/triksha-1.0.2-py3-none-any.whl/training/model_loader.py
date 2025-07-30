"""
Model loader for training models using various backends.
"""
from typing import Dict, Any, Optional, Tuple, Union
from pathlib import Path
import os
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

logger = logging.getLogger(__name__)

class ModelLoader:
    """Load and prepare models for training and inference"""
    
    def __init__(self, model_name_or_path: str, 
                 device: str = "auto",
                 quantization: Optional[str] = None,
                 load_in_8bit: bool = False,
                 load_in_4bit: bool = False,
                 trust_remote_code: bool = True,
                 token: Optional[str] = None):
        """
        Initialize model loader
        
        Args:
            model_name_or_path: The model identifier or path
            device: Device to load the model on ('cpu', 'cuda', 'auto')
            quantization: Quantization method ('int8', 'int4', None)
            load_in_8bit: Whether to load in 8-bit precision
            load_in_4bit: Whether to load in 4-bit precision
            trust_remote_code: Whether to trust remote code
            token: HuggingFace API token for private models
        """
        self.model_name_or_path = model_name_or_path
        self.device = device
        self.quantization = quantization
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        self.trust_remote_code = trust_remote_code
        self.token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        
        # Check device settings
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
        logger.info(f"Using device: {self.device}")
        
    def load_tokenizer(self) -> AutoTokenizer:
        """Load the tokenizer for the model"""
        logger.info(f"Loading tokenizer for model: {self.model_name_or_path}")
        
        # Check for SentencePiece
        try:
            import sentencepiece
            logger.info("SentencePiece library found")
        except ImportError:
            logger.warning("SentencePiece library not found, may cause issues for some tokenizers")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name_or_path,
                trust_remote_code=self.trust_remote_code,
                use_auth_token=self.token
            )
            
            # Ensure padding token for models without one
            if tokenizer.pad_token is None:
                if tokenizer.eos_token is not None:
                    tokenizer.pad_token = tokenizer.eos_token
                else:
                    logger.warning("No EOS token found for padding, using a default")
                    tokenizer.pad_token = tokenizer.eos_token = "</s>"
                    
            return tokenizer
            
        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            raise
            
    def load_model(self) -> AutoModelForCausalLM:
        """Load the model with appropriate settings"""
        logger.info(f"Loading model: {self.model_name_or_path}")
        
        # Setup quantization options
        quantization_config = None
        if self.load_in_8bit or self.quantization == "int8":
            logger.info("Using 8-bit quantization")
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
        elif self.load_in_4bit or self.quantization == "int4":
            logger.info("Using 4-bit quantization")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name_or_path,
                trust_remote_code=self.trust_remote_code,
                quantization_config=quantization_config,
                device_map=self.device if self.device != "cpu" else None,
                use_auth_token=self.token
            )
            
            # Move to device if CPU
            if self.device == "cpu" and not quantization_config:
                model = model.to(self.device)
                
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
            
    def load(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load both model and tokenizer"""
        tokenizer = self.load_tokenizer()
        model = self.load_model()
        return model, tokenizer
