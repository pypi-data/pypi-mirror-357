"""
Dataset processing utilities for working with training datasets.
This module contains tools for formatting, analyzing, and preparing datasets
for model fine-tuning with a focus on handling adversarial prompts.
"""

import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from .dataset_formatter import DatasetFormatter

logger = logging.getLogger(__name__)

class DatasetProcessor:
    """
    Utility class for processing and preparing datasets for training
    with support for adversarial training and model-specific formatting.
    """
    
    # Templates for different model architectures
    MODEL_TEMPLATES = {
        "default": {
            "name": "Default Format",
            "instruction_format": "{instruction}",
            "input_format": "{instruction}\n\n{input}",
            "completion_format": "{completion}",
            "safeguard_format": "I cannot assist with {problem_type} as it may {harm_description}. Consider {alternative} instead."
        },
        "llama2": {
            "name": "Llama 2",
            "instruction_format": "[INST] {instruction} [/INST]",
            "input_format": "[INST] {instruction} [/INST]\n\n{input}",
            "completion_format": "{completion}",
            "safeguard_format": "I cannot provide assistance with {problem_type} as it could {harm_description}."
        },
        "llama3": {
            "name": "Llama 3",
            "instruction_format": "<|start_header|>user<|end_header|>\n{instruction}<|eot_id|><|start_header|>assistant<|end_header|>\n",
            "input_format": "<|start_header|>user<|end_header|>\n{instruction}\n\n{input}<|eot_id|><|start_header|>assistant<|end_header|>\n",
            "completion_format": "{completion}<|eot_id|>",
            "safeguard_format": "I cannot assist with {problem_type} as it could {harm_description}."
        },
        "mistral": {
            "name": "Mistral",
            "instruction_format": "<s>[INST] {instruction} [/INST]",
            "input_format": "<s>[INST] {instruction}\n\n{input} [/INST]",
            "completion_format": "{completion}</s>",
            "safeguard_format": "I cannot assist with {problem_type} as it may {harm_description}."
        },
        "mixtral": {
            "name": "Mixtral",
            "instruction_format": "<s>[INST] {instruction} [/INST]",
            "input_format": "<s>[INST] {instruction}\n\n{input} [/INST]",
            "completion_format": "{completion}</s>",
            "safeguard_format": "I cannot assist with {problem_type} as it may {harm_description}."
        },
        "vicuna": {
            "name": "Vicuna",
            "instruction_format": "USER: {instruction}\nASSISTANT: ",
            "input_format": "USER: {instruction}\n\n{input}\nASSISTANT: ",
            "completion_format": "{completion}",
            "safeguard_format": "I apologize, but I cannot assist with {problem_type} as it could {harm_description}. Instead, I'd recommend {alternative}."
        },
        "gemma": {
            "name": "Gemma",
            "instruction_format": "<start_of_turn>user\n{instruction}<end_of_turn>\n<start_of_turn>model\n",
            "input_format": "<start_of_turn>user\n{instruction}\n\n{input}<end_of_turn>\n<start_of_turn>model\n",
            "completion_format": "{completion}<end_of_turn>",
            "safeguard_format": "I cannot assist with {problem_type} as it could potentially {harm_description}."
        },
        "phi": {
            "name": "Phi",
            "instruction_format": "User: {instruction}\n\nAssistant: ",
            "input_format": "User: {instruction}\n{input}\n\nAssistant: ",
            "completion_format": "{completion}",
            "safeguard_format": "I'm unable to help with {problem_type}. This could {harm_description}. Perhaps consider {alternative}."
        },
        "custom": {
            "name": "Custom Format",
            "instruction_format": "{instruction}",
            "input_format": "{instruction}\n\n{input}",
            "completion_format": "{completion}",
            "safeguard_format": "I cannot assist with {problem_type} as it may {harm_description}. Consider {alternative} instead."
        }
    }
    
    @classmethod
    def get_model_formats(cls) -> Dict[str, Dict[str, str]]:
        """Get available model format templates"""
        return cls.MODEL_TEMPLATES
    
    @classmethod
    def get_model_format(cls, model_name: str) -> Dict[str, str]:
        """Get the appropriate format template based on model name"""
        model_name_lower = model_name.lower()
        
        # Check for architecture matches
        if "llama-3" in model_name_lower or "llama3" in model_name_lower:
            return cls.MODEL_TEMPLATES["llama3"]
        elif "llama" in model_name_lower:
            return cls.MODEL_TEMPLATES["llama2"]
        elif "mistral" in model_name_lower and "mixtral" not in model_name_lower:
            return cls.MODEL_TEMPLATES["mistral"] 
        elif "mixtral" in model_name_lower:
            return cls.MODEL_TEMPLATES["mixtral"]
        elif "vicuna" in model_name_lower:
            return cls.MODEL_TEMPLATES["vicuna"]
        elif "gemma" in model_name_lower:
            return cls.MODEL_TEMPLATES["gemma"]
        elif "phi" in model_name_lower:
            return cls.MODEL_TEMPLATES["phi"]
            
        # Default format
        return cls.MODEL_TEMPLATES["default"]
    
    @classmethod
    def format_dataset(cls,
                    input_path: str,
                    prompt_field: str,
                    model_name: str = None,
                    model_format: Dict[str, str] = None,
                    response_style: str = "varied",
                    output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Format a dataset for training with proper prompt/response structure
        
        Args:
            input_path: Path to input dataset file
            prompt_field: Field containing prompts/instructions
            model_name: Name of model for automatic format selection
            model_format: Custom format template (overrides model_name)
            response_style: Style of responses (varied, consistent, strict)
            output_path: Optional path to save the formatted dataset
            
        Returns:
            Formatted dataset
        """
        # Load dataset
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}
            
        # Determine model format
        if not model_format:
            if model_name:
                model_format = cls.get_model_format(model_name)
            else:
                model_format = cls.MODEL_TEMPLATES["default"]
        
        # Configure response options
        response_config = {
            "style": response_style,
            "include_prompt_context": True
        }
        
        # Format dataset
        formatted_dataset = DatasetFormatter.format_dataset_with_responses(
            dataset,
            prompt_field,
            model_format,
            response_config
        )
        
        # Save if output path provided
        if output_path and "error" not in formatted_dataset:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_dataset, f, indent=2)
        
        return formatted_dataset
    
    @classmethod
    def analyze_dataset(cls, dataset_path: str) -> Dict[str, Any]:
        """
        Analyze a dataset to determine structure and content
        
        Args:
            dataset_path: Path to dataset file
            
        Returns:
            Analysis information
        """
        return DatasetFormatter.analyze_dataset(dataset_path)
    
    @classmethod
    def preview_dataset(cls, dataset_path: str, num_samples: int = 3) -> List[Dict[str, Any]]:
        """
        Preview examples from a dataset
        
        Args:
            dataset_path: Path to dataset file
            num_samples: Number of samples to preview
            
        Returns:
            List of sample examples
        """
        try:
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            examples = []
            
            # Extract examples based on dataset structure
            if isinstance(dataset, list):
                examples = dataset
            elif isinstance(dataset, dict) and "examples" in dataset:
                examples = dataset["examples"]
                
            if not examples:
                return [{"error": "No examples found in dataset"}]
                
            # Get random samples
            if len(examples) <= num_samples:
                samples = examples
            else:
                samples = random.sample(examples, num_samples)
                
            return samples
            
        except Exception as e:
            return [{"error": f"Error previewing dataset: {str(e)}"}]
    
    @classmethod
    def detect_adversarial_prompts(cls, dataset_path: str, prompt_field: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect adversarial prompts in a dataset
        
        Args:
            dataset_path: Path to dataset file
            prompt_field: Field containing prompts (auto-detect if None)
            
        Returns:
            Analysis with counts and examples of adversarial prompts
        """
        try:
            # First analyze the dataset to determine structure
            analysis = cls.analyze_dataset(dataset_path)
            
            # Handle error in analysis
            if "error" in analysis:
                return analysis
            
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            # Determine prompt field if not provided
            if not prompt_field:
                prompt_field = analysis.get("likely_prompt_field")
                
            if not prompt_field:
                return {"error": "Could not determine prompt field automatically"}
            
            # Get examples
            examples = []
            if isinstance(dataset, list):
                examples = dataset
            elif isinstance(dataset, dict) and "examples" in dataset:
                examples = dataset["examples"]
                
            if not examples:
                return {"error": "No examples found in dataset"}
            
            # Detect adversarial prompts
            adversarial_examples = []
            benign_examples = []
            
            for example in examples:
                if isinstance(example, dict) and prompt_field in example:
                    prompt = example[prompt_field]
                    if DatasetFormatter.is_adversarial_prompt(prompt):
                        adversarial_examples.append(example)
                    else:
                        benign_examples.append(example)
            
            # Create result
            result = {
                "total_examples": len(examples),
                "adversarial_count": len(adversarial_examples),
                "benign_count": len(benign_examples),
                "adversarial_percentage": len(adversarial_examples) / len(examples) * 100 if examples else 0,
                "prompt_field": prompt_field,
                "sample_adversarial": adversarial_examples[:5] if len(adversarial_examples) > 5 else adversarial_examples
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Error detecting adversarial prompts: {str(e)}"}
    
    @classmethod
    def convert_dataset_format(cls, dataset_path: str, output_path: str, output_format: str = "alpaca") -> bool:
        """
        Convert a dataset from one format to another
        
        Args:
            dataset_path: Path to dataset file
            output_path: Path to save converted dataset
            output_format: Format to convert to (alpaca, openai, etc.)
            
        Returns:
            Success status
        """
        try:
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            # Get examples
            examples = []
            if isinstance(dataset, list):
                examples = dataset
            elif isinstance(dataset, dict) and "examples" in dataset:
                examples = dataset["examples"]
                
            if not examples:
                logger.error("No examples found in dataset")
                return False
            
            # Convert examples based on output format
            converted_examples = []
            
            if output_format == "alpaca":
                for example in examples:
                    instruction, input_text, output = DatasetFormatter.extract_example_parts(example)
                    converted_examples.append({
                        "instruction": instruction,
                        "input": input_text if input_text else "",
                        "output": output
                    })
                    
                # Create final dataset
                converted_dataset = {
                    "name": dataset.get("name", "converted_dataset"),
                    "description": f"Converted from {dataset_path}",
                    "created_at": datetime.now().isoformat(),
                    "examples": converted_examples
                }
                
            elif output_format == "openai":
                for example in examples:
                    instruction, input_text, output = DatasetFormatter.extract_example_parts(example)
                    
                    if input_text:
                        user_content = f"{instruction}\n\n{input_text}"
                    else:
                        user_content = instruction
                        
                    converted_examples.append({
                        "messages": [
                            {"role": "user", "content": user_content},
                            {"role": "assistant", "content": output}
                        ]
                    })
                    
                # OpenAI format is just a list of examples
                converted_dataset = converted_examples
                
            else:
                logger.error(f"Unsupported output format: {output_format}")
                return False
            
            # Save converted dataset
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(converted_dataset, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error converting dataset: {e}")
            return False
    
    @classmethod
    def merge_datasets(cls, dataset_paths: List[str], output_path: str) -> bool:
        """
        Merge multiple datasets into one
        
        Args:
            dataset_paths: List of paths to dataset files
            output_path: Path to save merged dataset
            
        Returns:
            Success status
        """
        try:
            all_examples = []
            
            # Load and merge all datasets
            for path in dataset_paths:
                with open(path, 'r', encoding='utf-8') as f:
                    dataset = json.load(f)
                
                # Extract examples
                examples = []
                if isinstance(dataset, list):
                    examples = dataset
                elif isinstance(dataset, dict) and "examples" in dataset:
                    examples = dataset["examples"]
                    
                if examples:
                    all_examples.extend(examples)
            
            if not all_examples:
                logger.error("No examples found in any dataset")
                return False
                
            # Create merged dataset
            merged_dataset = {
                "name": "merged_dataset",
                "description": f"Merged from {len(dataset_paths)} datasets",
                "created_at": datetime.now().isoformat(),
                "sources": dataset_paths,
                "examples": all_examples
            }
            
            # Save merged dataset
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_dataset, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error merging datasets: {e}")
            return False
    
    @classmethod
    def generate_synthetic_adversarial_examples(cls, count: int = 100, model_format: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic adversarial examples
        
        Args:
            count: Number of examples to generate
            model_format: Model format template
            
        Returns:
            List of adversarial examples
        """
        # Use default format if none provided
        if not model_format:
            model_format = cls.MODEL_TEMPLATES["default"]
            
        examples = []
        
        for _ in range(count):
            example = DatasetFormatter.generate_adversarial_example(
                DatasetFormatter.PROBLEM_TYPES,
                DatasetFormatter.HARM_DESCRIPTIONS,
                DatasetFormatter.ALTERNATIVES,
                model_format
            )
            examples.append(example)
            
        return examples
    
    @classmethod
    def create_adversarial_dataset(cls, 
                                count: int = 100, 
                                model_name: str = None,
                                output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a dataset of synthetic adversarial examples
        
        Args:
            count: Number of examples to generate
            model_name: Name of model for format selection
            output_path: Optional path to save dataset
            
        Returns:
            Generated dataset
        """
        # Get model format
        model_format = None
        if model_name:
            model_format = cls.get_model_format(model_name)
        else:
            model_format = cls.MODEL_TEMPLATES["default"]
            
        # Generate examples
        examples = cls.generate_synthetic_adversarial_examples(count, model_format)
        
        # Create dataset
        dataset = {
            "name": "synthetic_adversarial_dataset",
            "description": f"Synthetic adversarial dataset with {count} examples",
            "created_at": datetime.now().isoformat(),
            "model_format": model_format["name"],
            "examples": examples
        }
        
        # Save if output path provided
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2)
        
        return dataset
    
    @classmethod
    def format_single_prompt(cls, prompt: str, model_name: str = None) -> Dict[str, str]:
        """
        Format a single prompt for a specific model
        
        Args:
            prompt: The prompt to format
            model_name: Name of model for format selection
            
        Returns:
            Dictionary with formatted input
        """
        # Get model format
        model_format = None
        if model_name:
            model_format = cls.get_model_format(model_name)
        else:
            model_format = cls.MODEL_TEMPLATES["default"]
            
        # Format prompt
        formatted_input = model_format["instruction_format"].format(instruction=prompt)
        
        return {
            "formatted_prompt": formatted_input,
            "model_format": model_format["name"],
            "original_prompt": prompt
        }
