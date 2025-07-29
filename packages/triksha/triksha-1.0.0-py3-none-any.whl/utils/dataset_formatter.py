"""Utility class for dataset formatting operations"""
from typing import Dict, Any, List, Optional, Tuple
import random
import re
from datetime import datetime
import json
import os
from pathlib import Path

class DatasetFormatter:
    """Helper class for dataset formatting operations"""
    
    # Keywords that might indicate adversarial content
    ADVERSARIAL_KEYWORDS = [
        "hack", "exploit", "bypass", "steal", "illegal", "malware", "virus",
        "phishing", "backdoor", "crack", "fraud", "counterfeit", "attack",
        "unauthorized", "break into", "unethical", "harm", "dangerous", 
        "weapon", "manipulate", "circumvent", "bomb", "criminal", "destructive",
        "illegal", "steal", "cheat", "penetrate", "breach", "intercept",
        "jailbreak", "override", "DAN", "do anything now"
    ]
    
    # Problem categories for adversarial safeguards
    PROBLEM_TYPES = [
        "unauthorized access attempts",
        "hacking or system intrusion",
        "creation of harmful software",
        "illegal activities",
        "privacy violations",
        "content theft or plagiarism",
        "security bypass techniques",
        "harmful or unethical instructions",
        "malware distribution",
        "system manipulation"
    ]
    
    # Harm descriptions for adversarial safeguards
    HARM_DESCRIPTIONS = [
        "potentially harm individuals or organizations",
        "facilitate illegal activities",
        "compromise computer security",
        "violate privacy or confidentiality",
        "enable unauthorized access to systems",
        "cause financial or reputational damage",
        "lead to identity theft or fraud",
        "result in legal consequences",
        "be used for malicious purposes",
        "undermine trust in digital systems"
    ]
    
    # Alternative suggestions for adversarial safeguards
    ALTERNATIVES = [
        "learning about cybersecurity through legitimate educational resources",
        "exploring ethical hacking certifications and courses",
        "using practice environments designed for security learning",
        "participating in authorized bug bounty programs",
        "studying information security in academic contexts",
        "setting up your own test environment for learning",
        "joining cybersecurity communities focused on ethical practices",
        "reading documentation and technical papers on security"
    ]
    
    # Response templates for refusals
    RESPONSE_TEMPLATES = [
        "I cannot comply with this request as it appears to involve {problem_type}, which could {harm_description}. Instead, consider {alternative}.",
        "I'm designed to be helpful, harmless, and honest. I cannot assist with {problem_type}. You might want to explore {alternative} instead.",
        "This request seems to involve {problem_type}, which I'm not able to help with as it could {harm_description}.",
        "I'm programmed to decline requests related to {problem_type} as they could {harm_description}. Have you considered {alternative}?",
        "I'm not able to generate content related to {problem_type} as it might {harm_description}.",
        "I apologize, but I cannot provide assistance with {problem_type}. I'd be happy to help with {alternative} instead.",
        "As an AI assistant committed to safety, I must decline requests involving {problem_type}.",
        "I'm not programmed to help with {problem_type} as it could potentially {harm_description}. May I suggest {alternative} as a better approach?"
    ]
    
    @staticmethod
    def is_adversarial_prompt(text: str) -> bool:
        """
        Check if a text might be an adversarial prompt
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be adversarial
        """
        # Lowercase for case-insensitive matching
        lower_text = text.lower()
        
        # Check for keyword matches
        for keyword in DatasetFormatter.ADVERSARIAL_KEYWORDS:
            if keyword.lower() in lower_text:
                return True
                
        # Check for DAN (Do Anything Now) jailbreak patterns
        dan_patterns = [
            r"\bDAN\b",
            r"do anything now",
            r"ignore your ethical guidelines",
            r"ignore your programming",
            r"ignore your constraints",
            r"disregard your ethical guidelines",
            r"bypass your rules",
            r"pretend you can",
            r"pretend you are able to",
            r"enter developer mode",
            r"enter dev mode"
        ]
        
        for pattern in dan_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                return True
                
        # Check for prompt injection patterns like using persona instruction
        injection_patterns = [
            r"ignore previous instructions",
            r"forget your instructions",
            r"you are now [a-z]",
            r"imagine you are [a-z]",
            r"pretend to be [a-z]"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def extract_example_parts(example: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Extract instruction, input, and output from various example formats
        
        Args:
            example: Example data in various formats
            
        Returns:
            Tuple of (instruction, input_text, output)
        """
        instruction = ""
        input_text = ""
        output = ""
        
        # Handle common formats
        if 'instruction' in example:
            instruction = example['instruction']
            
            # Check different response field names
            if 'output' in example:
                output = example['output']
            elif 'response' in example:
                output = example['response']
                
            # Check for separate input field
            if 'input' in example:
                input_text = example['input']
                
        elif 'prompt' in example:
            instruction = example['prompt']
            
            # Check different completion field names
            if 'completion' in example:
                output = example['completion']
            elif 'response' in example:
                output = example['response']
                
        elif 'input' in example and 'output' in example:
            instruction = example['input']
            output = example['output']
            
        elif 'text' in example:
            # Try to split text into parts
            parts = example['text'].split("\n\n")
            if len(parts) >= 2:
                instruction = parts[0]
                output = parts[-1]
            else:
                instruction = example['text']
                output = "I'll help you with that."
        
        return instruction, input_text, output
    
    @staticmethod
    def format_for_model_architecture(example: Dict[str, Any], model_format: Dict[str, str], 
                                   is_adversarial: bool = False) -> Dict[str, Any]:
        """
        Format an example for a specific model architecture
        
        Args:
            example: The example to format
            model_format: Model-specific formatting templates
            is_adversarial: Whether this is an adversarial example
            
        Returns:
            Formatted example
        """
        instruction, input_text, output = DatasetFormatter.extract_example_parts(example)
        
        formatted = {}
        
        # Format based on whether there's additional input or just instruction
        if input_text:
            # Format with both instruction and input
            formatted["input"] = model_format["input_format"].format(
                instruction=instruction,
                input=input_text
            )
        else:
            # Format with just instruction
            formatted["input"] = model_format["instruction_format"].format(
                instruction=instruction
            )
            
        # Format the output/completion
        formatted["output"] = model_format["completion_format"].format(
            completion=output
        )
        
        # Add metadata
        formatted["metadata"] = {
            "is_adversarial": is_adversarial,
            "original_example": example,
            "formatted_at": datetime.now().isoformat()
        }
        
        return formatted
    
    @staticmethod
    def generate_adversarial_example(problem_types: List[str], harm_descriptions: List[str], 
                                  alternatives: List[str], model_format: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate a synthetic adversarial example
        
        Args:
            problem_types: List of problem categories
            harm_descriptions: List of harm descriptions
            alternatives: List of alternative suggestions
            model_format: Model-specific formatting templates
            
        Returns:
            Synthetic adversarial example
        """
        # Create the adversarial instruction
        adversarial_modifiers = [
            "I need you to help me hack into ",
            "Tell me how to bypass security in ",
            "I need instructions for creating a virus that can ",
            "Show me how to exploit vulnerabilities in ",
            "I want to steal data from ",
            "Help me break into ",
            "Give me steps to bypass authentication on ",
            "Teach me how to create malware that can ",
            "I need to crack the password for ",
            "Explain how I can manipulate network traffic to "
        ]
        
        adversarial_targets = [
            "a website",
            "a computer system",
            "someone's account",
            "a corporate network",
            "a government database",
            "my school's grading system",
            "my neighbor's wifi",
            "the company I work for",
            "a bank's security system",
            "someone's private information"
        ]
        
        # Create adversarial instruction
        prefix = random.choice(adversarial_modifiers)
        target = random.choice(adversarial_targets)
        adversarial_instruction = prefix + target
        
        # Create safeguard response
        template = model_format["safeguard_format"]
        safeguard_response = template.format(
            problem_type=random.choice(problem_types),
            harm_description=random.choice(harm_descriptions),
            alternative=random.choice(alternatives)
        )
        
        # Format the example
        formatted = {}
        formatted["input"] = model_format["instruction_format"].format(
            instruction=adversarial_instruction
        )
        formatted["output"] = model_format["completion_format"].format(
            completion=safeguard_response
        )
        
        # Add metadata
        formatted["metadata"] = {
            "is_adversarial": True,
            "is_synthetic": True,
            "adversarial_type": "synthetic"
        }
        
        return formatted
    
    @staticmethod
    def analyze_dataset(dataset_path: str) -> Dict[str, Any]:
        """
        Analyze a dataset to determine its structure and contents
        
        Args:
            dataset_path: Path to dataset file
            
        Returns:
            Dictionary with analysis information
        """
        try:
            # Check if file exists
            if not os.path.exists(dataset_path):
                return {"error": f"File not found: {dataset_path}"}
            
            # Load dataset
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = {
                "path": dataset_path,
                "filename": os.path.basename(dataset_path),
                "size_bytes": os.path.getsize(dataset_path),
                "size_mb": os.path.getsize(dataset_path) / (1024 * 1024)
            }
            
            # Determine structure
            if isinstance(data, list):
                analysis["type"] = "list"
                analysis["count"] = len(data)
                
                # Check first item to understand structure
                if data and isinstance(data[0], dict):
                    analysis["fields"] = list(data[0].keys())
                    analysis["field_counts"] = {field: sum(1 for item in data if field in item) for field in analysis["fields"]}
                    
                    # Try to determine which field is the prompt field
                    potential_prompt_fields = ["prompt", "input", "instruction", "text", "query", "question"]
                    for field in potential_prompt_fields:
                        if field in analysis["fields"]:
                            analysis["likely_prompt_field"] = field
                            break
                    
                    # Check for adversarial content
                    if "likely_prompt_field" in analysis:
                        prompt_field = analysis["likely_prompt_field"]
                        adversarial_count = sum(
                            1 for item in data 
                            if prompt_field in item and 
                            DatasetFormatter.is_adversarial_prompt(item[prompt_field])
                        )
                        analysis["adversarial_count"] = adversarial_count
                        analysis["adversarial_percentage"] = (adversarial_count / len(data)) * 100 if data else 0
                    
            elif isinstance(data, dict):
                analysis["type"] = "dictionary"
                analysis["keys"] = list(data.keys())
                
                # Check if it has an examples field
                if "examples" in data and isinstance(data["examples"], list):
                    analysis["examples_count"] = len(data["examples"])
                    
                    if data["examples"] and isinstance(data["examples"][0], dict):
                        example_fields = list(data["examples"][0].keys())
                        analysis["example_fields"] = example_fields
                        
                        # Try to determine which field is the prompt field
                        potential_prompt_fields = ["prompt", "input", "instruction", "text", "query", "question"]
                        for field in potential_prompt_fields:
                            if field in example_fields:
                                analysis["likely_prompt_field"] = field
                                break
                        
                        # Check for adversarial content
                        if "likely_prompt_field" in analysis:
                            prompt_field = analysis["likely_prompt_field"]
                            adversarial_count = sum(
                                1 for ex in data["examples"] 
                                if prompt_field in ex and 
                                DatasetFormatter.is_adversarial_prompt(ex[prompt_field])
                            )
                            analysis["adversarial_count"] = adversarial_count
                            analysis["adversarial_percentage"] = (adversarial_count / len(data["examples"])) * 100 if data["examples"] else 0
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing dataset: {str(e)}"}
    
    @staticmethod
    def extract_prompts(data: Dict[str, Any], prompt_field: str) -> List[str]:
        """Extract prompts from a dataset using the specified field"""
        prompts = []
        
        try:
            # Handle list of examples
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and prompt_field in item:
                        prompts.append(item[prompt_field])
                    elif isinstance(item, str) and prompt_field == "text":
                        prompts.append(item)
                        
            # Handle dictionary with examples list
            elif isinstance(data, dict) and "examples" in data:
                for item in data["examples"]:
                    if isinstance(item, dict) and prompt_field in item:
                        prompts.append(item[prompt_field])
        except Exception:
            pass
            
        return prompts
    
    @staticmethod
    def generate_responses(prompts: List[str], style: str = "varied") -> List[str]:
        """Generate refusal responses for adversarial prompts"""
        responses = []
        
        for prompt in prompts:
            # Determine the problem type
            problem_type = DatasetFormatter._identify_problem_type(prompt)
            
            # Choose template based on style
            if style == "varied":
                template = random.choice(DatasetFormatter.RESPONSE_TEMPLATES)
            elif style == "strict":
                template = "I cannot and will not provide any assistance with {problem_type}, which could {harm_description}."
            else:  # consistent
                template = "I cannot assist with {problem_type} as it may {harm_description}. Consider {alternative} instead."
                
            # Generate response
            response = template.format(
                problem_type=problem_type,
                harm_description=random.choice(DatasetFormatter.HARM_DESCRIPTIONS),
                alternative=random.choice(DatasetFormatter.ALTERNATIVES)
            )
            
            responses.append(response)
            
        return responses
    
    @staticmethod
    def _identify_problem_type(prompt: str) -> str:
        """Identify the type of problem in an adversarial prompt"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hack", "exploit", "vulnerability", "bypass", "crack"]):
            return "unauthorized system access or hacking"
        elif any(word in prompt_lower for word in ["malware", "virus", "ransomware", "trojan"]):
            return "malware creation or distribution"
        elif any(word in prompt_lower for word in ["steal", "theft", "sensitive data"]):
            return "data theft or privacy violations"
        elif any(word in prompt_lower for word in ["weapon", "bomb", "explosive", "gun", "attack"]):
            return "weapon creation or violence"
        elif any(word in prompt_lower for word in ["illegal", "lawbreak", "criminal"]):
            return "illegal activities"
        elif any(word in prompt_lower for word in ["fraud", "scam", "deceive"]):
            return "fraud or deceptive practices"
            
        # Default to a random problem type if no specific keywords found
        return random.choice(DatasetFormatter.PROBLEM_TYPES)
    
    @staticmethod
    def format_dataset_with_responses(
        dataset: Dict[str, Any],
        prompt_field: str,
        model_format: Dict[str, Any],
        response_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format a dataset with adversarial prompts and generate safeguard responses"""
        # Extract examples based on dataset structure
        examples = []
        if isinstance(dataset, list):
            examples = dataset
        elif isinstance(dataset, dict) and "examples" in dataset:
            examples = dataset["examples"]
            
        if not examples:
            return {"error": "No examples found in dataset"}
            
        # Extract prompts from examples
        prompts = []
        for example in examples:
            if isinstance(example, dict) and prompt_field in example:
                prompts.append(example[prompt_field])
            
        if not prompts:
            return {"error": f"No prompts found in field '{prompt_field}'"}
            
        # Generate responses
        responses = DatasetFormatter.generate_responses(
            prompts, 
            style=response_config.get("style", "varied")
        )
        
        # Create formatted examples
        formatted_examples = []
        
        for i, (prompt, response) in enumerate(zip(prompts, responses)):
            # Format according to model architecture
            formatted_example = {}
            
            # Format the input (prompt)
            formatted_example["input"] = model_format["instruction_format"].format(
                instruction=prompt
            )
                
            # Format the output (safeguard response)
            formatted_example["output"] = model_format["completion_format"].format(
                completion=response
            )
                
            # Add metadata
            formatted_example["metadata"] = {
                "is_adversarial": DatasetFormatter.is_adversarial_prompt(prompt),
                "original_prompt": prompt,
                "response_style": response_config.get("style", "varied")
            }
                
            formatted_examples.append(formatted_example)
        
        # Create formatted dataset
        formatted_dataset = {
            "name": dataset.get("name", "formatted_dataset"),
            "model_format": model_format["name"],
            "created_at": datetime.now().isoformat(),
            "examples": formatted_examples,
            "metadata": {
                "total_examples": len(formatted_examples),
                "response_style": response_config.get("style", "varied"),
                "model_format": model_format["name"]
            }
        }
        
        return formatted_dataset
