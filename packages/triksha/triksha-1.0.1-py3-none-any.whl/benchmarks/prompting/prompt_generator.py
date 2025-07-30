"""Prompt generation utilities for benchmarks"""
import torch
import random
from typing import List, Optional
from rich.console import Console
from ..models.model_loader import ModelLoader
from .templates import JAILBREAK_TEMPLATES, JAILBREAK_TOPICS, SYSTEM_PROMPT, FALLBACK_PROMPTS

class PromptGenerator:
    """Generate test prompts for benchmarking"""
    
    def __init__(self, model_path: str, verbose: bool = False):
        """Initialize prompt generator"""
        self.model_path = model_path
        self.verbose = verbose
        self.console = Console()
        self.model_loader = ModelLoader(verbose=verbose)
        self.templates = JAILBREAK_TEMPLATES
        self.topics = JAILBREAK_TOPICS
        self.system_prompt = SYSTEM_PROMPT
        self.fallback_prompts = FALLBACK_PROMPTS
    
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
    
    def generate_prompts(self, num_prompts: int = 5) -> List[str]:
        """Generate prompts using the model"""
        self._log(f"Generating {num_prompts} test prompts...")
        
        # Try to load the model
        if not self.model_loader.load_model(self.model_path):
            self._log("Failed to load model, using fallback prompts", "warning")
            return self.fallback_prompts
        
        model, tokenizer = self.model_loader.get_model_and_tokenizer()
        if not model or not tokenizer:
            return self.fallback_prompts
        
        # Generate prompts with the model
        prompts = []
        try:
            with torch.inference_mode():
                for i in range(num_prompts):
                    self._log(f"Generating prompt {i+1}/{num_prompts}...", "info")
                    template = random.choice(self.templates)
                    topic = random.choice(self.topics)
                    
                    # Construct full prompt
                    full_prompt = f"{self.system_prompt}\n\nTask: {template.format(topic=topic)}\n\nGenerated prompt:"
                    
                    # Tokenize and generate
                    inputs = tokenizer(
                        full_prompt,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    )
                    
                    # Get device and move inputs
                    device = next(model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    
                    # Generate output
                    outputs = model.generate(
                        **inputs,
                        max_length=200,
                        temperature=0.95,
                        top_p=0.75,
                        do_sample=True,
                        num_return_sequences=1,
                        pad_token_id=tokenizer.pad_token_id,
                        repetition_penalty=1.2
                    )
                    
                    # Process output
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    generated_prompt = generated_text.split("Generated prompt:")[-1].strip()
                    
                    if generated_prompt:
                        prompts.append(generated_prompt)
                        self._log(f"Generated: {generated_prompt[:100]}...", "success")
                    else:
                        self._log("Generated empty prompt, skipping", "warning")
            
            # Unload model to free memory
            self.model_loader.unload_model()
            
            # Return prompts or fallbacks if empty
            return prompts if prompts else self.fallback_prompts
            
        except Exception as e:
            self._log(f"Error generating prompts: {str(e)}", "error")
            self.model_loader.unload_model()
            return self.fallback_prompts
    
    def get_fallback_prompts(self, num_prompts: Optional[int] = None) -> List[str]:
        """Get fallback prompts if generation fails"""
        prompts = self.fallback_prompts
        
        if num_prompts is not None:
            if len(prompts) >= num_prompts:
                return prompts[:num_prompts]
            else:
                # Pad with repetitions if needed
                return prompts + (prompts * (num_prompts // len(prompts) + 1))[:num_prompts-len(prompts)]
        
        return prompts
