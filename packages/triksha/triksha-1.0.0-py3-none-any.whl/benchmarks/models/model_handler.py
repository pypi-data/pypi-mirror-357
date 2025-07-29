"""
Model handler for managing interactions with local and API-based models.
This serves as the interface between benchmark templates and actual model implementations.
"""
from typing import Dict, Any, List, Optional, Union
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

class ModelHandler:
    """Unified handler for local and external models"""
    
    def __init__(
        self, 
        model_path: str,
        api_based: bool = False,
        provider: str = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        streaming: bool = False,
        verbose: bool = False,
        custom_config: Dict[str, Any] = None
    ):
        """
        Initialize model handler
        
        Args:
            model_path: Path or identifier for the model
            api_based: Whether this is an API-based model
            provider: Provider name for API models
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            streaming: Whether to stream responses
            verbose: Whether to log detailed information
            custom_config: Configuration for custom model handler
        """
        self.model_path = model_path
        self.api_based = api_based
        self.provider = provider
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.streaming = streaming
        self.verbose = verbose
        self.custom_config = custom_config or {}
        
        self.model = None
        self.tokenizer = None
        self.api_handler = None
        
        # Initialize the appropriate model
        if not api_based:
            self._initialize_local_model()
        else:
            self._initialize_api_handler()
    
    def _log(self, message: str, level: str = "info"):
        """Log messages based on verbosity"""
        if not self.verbose:
            return
            
        from rich.console import Console
        console = Console()
        
        if level == "info":
            console.print(f"[blue]{message}[/]")
        elif level == "success":
            console.print(f"[green]{message}[/]")
        elif level == "warning":
            console.print(f"[yellow]{message}[/]")
        elif level == "error":
            console.print(f"[red]{message}[/]")
        else:
            console.print(message)
    
    def _initialize_local_model(self):
        """Initialize local transformer model"""
        try:
            self._log(f"Loading local model: {self.model_path}")
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Ensure padding token is properly set
            if self.tokenizer.pad_token is None:
                if self.tokenizer.eos_token is not None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    self._log("Set pad_token to eos_token", "info")
                else:
                    self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                    self._log("Added custom [PAD] token", "info")
            
            # Load model with recommended settings for generation
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
                # Fix for LoRA weights loading warnings
                low_cpu_mem_usage=True,
                offload_state_dict=True
            )
            
            # Ensure model is compatible with tokenizer padding
            if self.model.config.pad_token_id is None:
                self.model.config.pad_token_id = self.tokenizer.pad_token_id
            
            self._log(f"Model loaded successfully on {device}", "success")
            
        except Exception as e:
            self._log(f"Error loading model: {str(e)}", "error")
            raise
    
    def _initialize_api_handler(self):
        """Initialize API-based model handler"""
        if not self.provider:
            raise ValueError("Provider must be specified for API-based models")
            
        provider = self.provider.lower()
        self._log(f"Initializing API handler for {provider}")
        
        try:
            if provider == "openai":
                from ..api.openai_handler import OpenAIHandler
                self.api_handler = OpenAIHandler(model_name=self.model_path, verbose=self.verbose)
            elif provider == "gemini":
                from ..api.gemini_handler import GeminiHandler
                self.api_handler = GeminiHandler(model_name=self.model_path, verbose=self.verbose)
            elif provider == "custom":
                from ..api.custom_handler import CustomHandler
                self.api_handler = CustomHandler(
                    model_name=self.model_path, 
                    config=self.custom_config, 
                    verbose=self.verbose
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
            self._log(f"API handler initialized for {provider}/{self.model_path}", "success")
            
        except Exception as e:
            self._log(f"Error initializing API handler: {str(e)}", "error")
            raise
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response to the given prompt"""
        if self.api_based:
            return await self._generate_api_response(prompt)
        else:
            return await self._generate_local_response(prompt)
    
    async def _generate_api_response(self, prompt: str) -> str:
        """Generate response using API-based model"""
        if not self.api_handler:
            raise ValueError("API handler not initialized")
            
        try:
            response = await self.api_handler.test_prompt(prompt)
            return response.get("response", "")
        except Exception as e:
            self._log(f"Error generating API response: {str(e)}", "error")
            return f"Error: {str(e)}"
    
    async def _generate_local_response(self, prompt: str) -> str:
        """Generate response using local model"""
        if not self.model or not self.tokenizer:
            raise ValueError("Local model not initialized")
            
        try:
            # Create a loop for async generation
            loop = asyncio.get_event_loop()
            
            # Prepare inputs with explicit attention mask
            tokenized_inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
            inputs = {
                "input_ids": tokenized_inputs["input_ids"].to(self.model.device),
                "attention_mask": tokenized_inputs["attention_mask"].to(self.model.device)
            }
            
            if self.streaming:
                # Setup streamer for non-blocking generation
                streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)
                generation_kwargs = {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"],
                    "max_new_tokens": self.max_new_tokens,
                    "temperature": self.temperature,
                    "streamer": streamer,
                    "pad_token_id": self.tokenizer.pad_token_id,
                }
                
                # Start generation in a separate thread
                thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
                thread.start()
                
                # Collect generated text
                generated_text = ""
                for text in streamer:
                    generated_text += text
                
                # Wait for generation to complete
                thread.join()
                
                return generated_text
            else:
                # Run generation in the thread pool
                def _generate():
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs["input_ids"],
                            attention_mask=inputs["attention_mask"],
                            max_new_tokens=self.max_new_tokens,
                            temperature=self.temperature,
                            do_sample=self.temperature > 0,
                            pad_token_id=self.tokenizer.pad_token_id,
                        )
                    return outputs
                
                # Run generation in executor
                outputs = await loop.run_in_executor(None, _generate)
                
                # Decode and return text
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Remove the prompt from the generated text
                prompt_tokens = self.tokenizer.encode(prompt, return_tensors="pt")[0]
                prompt_length = len(prompt_tokens)
                response_text = self.tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True)
                
                return response_text.strip()
                
        except Exception as e:
            self._log(f"Error generating local response: {str(e)}", "error")
            return f"Error: {str(e)}"
