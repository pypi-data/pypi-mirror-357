"""Utility functions for training operations"""
from typing import Dict, List, Any

def validate_training_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize a training configuration
    
    Args:
        config: Training configuration
        
    Returns:
        Validated configuration or list of errors
    """
    errors = []
    
    # Required fields
    required = ["model_id", "approach", "dataset", "training_params"]
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate approach
    if "approach" in config:
        valid_approaches = ["lora", "qlora", "full"]
        if config["approach"] not in valid_approaches:
            errors.append(f"Invalid approach: {config['approach']}. Must be one of {valid_approaches}")
    
    # Validate training parameters
    if "training_params" in config:
        params = config["training_params"]
        
        # Required parameters
        if "epochs" not in params:
            params["epochs"] = 3
        if "batch_size" not in params:
            params["batch_size"] = 8
        if "learning_rate" not in params:
            params["learning_rate"] = 2e-5
            
        # Parameter ranges
        if params["epochs"] < 1 or params["epochs"] > 50:
            errors.append(f"Invalid epochs: {params['epochs']}. Must be between 1 and 50")
        if params["batch_size"] < 1 or params["batch_size"] > 128:
            errors.append(f"Invalid batch_size: {params['batch_size']}. Must be between 1 and 128")
        if params["learning_rate"] < 1e-7 or params["learning_rate"] > 1e-2:
            errors.append(f"Invalid learning_rate: {params['learning_rate']}. Must be between 1e-7 and 1e-2")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True, "config": config}

def get_available_models() -> List[Dict[str, Any]]:
    """Get list of available models for fine-tuning"""
    return [
        {
            "id": "mistralai/Mistral-7B-v0.1",
            "display_name": "Mistral 7B",
            "description": "High-quality 7B parameter model",
            "size_gb": 14,
            "compatible_approaches": ["lora", "qlora"]
        },
        {
            "id": "meta-llama/Llama-2-7b-hf",
            "display_name": "Llama 2 7B",
            "description": "Meta's Llama 2 7B base model",
            "size_gb": 14,
            "compatible_approaches": ["lora", "qlora", "full"]
        },
        {
            "id": "meta-llama/Llama-2-13b-hf",
            "display_name": "Llama 2 13B",
            "description": "Meta's Llama 2 13B base model (requires more resources)",
            "size_gb": 26,
            "compatible_approaches": ["lora", "qlora"]
        },
        {
            "id": "stabilityai/stablelm-base-alpha-7b",
            "display_name": "StableLM 7B",
            "description": "Stability AI's 7B parameter base model",
            "size_gb": 14,
            "compatible_approaches": ["lora", "qlora", "full"]
        },
        {
            "id": "HuggingFaceH4/zephyr-7b-beta",
            "display_name": "Zephyr 7B",
            "description": "High-quality instruction-tuned model",
            "size_gb": 14,
            "compatible_approaches": ["lora", "qlora"]
        }
    ]
