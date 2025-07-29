import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional

from ..base_handler import ModelHandler


class HuggingFaceHandler(ModelHandler):
    """Model handler for HuggingFace Hub models."""
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """Initialize the HuggingFace handler.
        
        Args:
            api_key: HuggingFace API key. If not provided, will use HF_API_TOKEN environment variable.
            verbose: Whether to output verbose logging information.
        """
        self.api_key = api_key or os.environ.get("HF_API_TOKEN")
        self.verbose = verbose
        
        # Don't raise an error immediately, just store the state
        self.is_available = bool(self.api_key)
        
        # Track loaded models
        self._loaded_models = set()
    
    def is_model_loaded(self, model_id: str) -> bool:
        """Check if a model is already loaded.
        
        Args:
            model_id: ID of the model to check
            
        Returns:
            bool: True if the model is loaded, False otherwise
        """
        return model_id in self._loaded_models
    
    async def _load_model(self, model_id: str) -> bool:
        """Load a model from HuggingFace.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            bool: True if the model was loaded successfully, False otherwise
        """
        try:
            if self.verbose:
                print(f"Loading model {model_id} from HuggingFace Hub...")
            
            # Check if we're using API or local inference
            if self._use_local_inference():
                # Load model locally using transformers
                return await self._load_model_locally(model_id)
            else:
                # Verify model availability on HF Hub API
                return await self._verify_model_on_hub(model_id)
        except Exception as e:
            if self.verbose:
                print(f"Error loading model {model_id}: {str(e)}")
            return False
    
    async def _load_model_locally(self, model_id: str) -> bool:
        """Load a model locally using transformers.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            bool: True if the model was loaded successfully, False otherwise
        """
        try:
            # Import here to avoid dependency if not using local inference
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            import torch
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.verbose:
                print(f"Loading model {model_id} from HuggingFace Hub...")
                print(f"Loading model on device: {device}")
            
            # Load the tokenizer
            tokenizer = await asyncio.to_thread(
                AutoTokenizer.from_pretrained, 
                model_id,
                token=self.api_key
            )
            
            # Use lower precision for larger models to save memory
            torch_dtype = torch.float16 if device == "cuda" else torch.float32
            
            # Load the model with proper settings to avoid device placement issues
            # Note: device_map="auto" will use accelerate to handle device placement
            model_kwargs = {
                "torch_dtype": torch_dtype,
                "low_cpu_mem_usage": True,
                "token": self.api_key,
                "device_map": "auto"  # Let accelerate handle device placement
            }
            
            # Load the model in a non-blocking way
            model = await asyncio.to_thread(
                AutoModelForCausalLM.from_pretrained,
                model_id,
                **model_kwargs
            )
            
            # Create pipeline for text generation - don't specify device when using accelerate
            pipeline_kwargs = {
                "model": model,
                "tokenizer": tokenizer,
            }
            
            # Only specify device if not using accelerate
            if not hasattr(model, "hf_device_map"):
                # If model doesn't have a device map, we can specify device
                if device == "cuda":
                    pipeline_kwargs["device"] = 0
                else:
                    pipeline_kwargs["device"] = -1
            
            # Create the generation pipeline
            generator = await asyncio.to_thread(
                pipeline,
                "text-generation",
                **pipeline_kwargs
            )
            
            # Store the pipeline in instance variable for later use
            if not hasattr(self, "_local_models"):
                self._local_models = {}
            
            self._local_models[model_id] = {
                "generator": generator,
                "tokenizer": tokenizer,
                "model": model
            }
            
            # Mark model as loaded
            self._loaded_models.add(model_id)
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error loading model locally: {str(e)}")
            return False
    
    async def _verify_model_on_hub(self, model_id: str) -> bool:
        """Verify a model's availability on HuggingFace Hub.
        
        Args:
            model_id: ID of the model to verify
            
        Returns:
            bool: True if the model is available, False otherwise
        """
        try:
            # Verify model is available on HuggingFace Hub
            api_url = f"https://huggingface.co/api/models/{model_id}"
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        # Model exists and is accessible
                        self._loaded_models.add(model_id)
                        return True
                    else:
                        if self.verbose:
                            print(f"Model not accessible: {model_id}, status: {response.status}")
                        return False
                        
        except Exception as e:
            if self.verbose:
                print(f"Error verifying model on hub: {str(e)}")
            return False
    
    def _use_local_inference(self) -> bool:
        """Determine whether to use local inference or the HuggingFace API.
        
        This checks environment variables and configuration to decide.
        
        Returns:
            bool: True if local inference should be used, False otherwise
        """
        # Check for explicit configuration
        if hasattr(self, "use_local_inference"):
            return self.use_local_inference
        
        # Check environment variable
        env_setting = os.environ.get("HF_USE_LOCAL_INFERENCE", "").lower()
        if env_setting in ("1", "true", "yes"):
            return True
        if env_setting in ("0", "false", "no"):
            return False
        
        # Default based on available resources and transformers installation
        try:
            import torch
            import transformers
            has_dependencies = True
        except ImportError:
            has_dependencies = False
        
        # Use local inference if we have the dependencies and either:
        # 1. We have a GPU available, or
        # 2. The HF_LOCAL_INFERENCE_FORCE_CPU environment variable is set
        if has_dependencies:
            has_gpu = False
            try:
                import torch
                has_gpu = torch.cuda.is_available()
            except:
                pass
                
            force_cpu = os.environ.get("HF_LOCAL_INFERENCE_FORCE_CPU", "").lower() in ("1", "true", "yes")
            
            return has_gpu or force_cpu
        
        # Default to API if dependencies aren't available
        return False
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List recommended HuggingFace models for chat.
        
        Returns:
            List of dictionaries containing model information.
        """
        # HuggingFace has a lot of models, so we'll just return a curated list of
        # popular chat models
        return [
            {"id": "meta-llama/Llama-2-70b-chat-hf", "name": "Llama 2 70B Chat", "provider": "huggingface"},
            {"id": "meta-llama/Llama-2-13b-chat-hf", "name": "Llama 2 13B Chat", "provider": "huggingface"},
            {"id": "meta-llama/Llama-2-7b-chat-hf", "name": "Llama 2 7B Chat", "provider": "huggingface"},
            {"id": "mistralai/Mistral-7B-Instruct-v0.2", "name": "Mistral 7B Instruct", "provider": "huggingface"},
            {"id": "tiiuae/falcon-7b-instruct", "name": "Falcon 7B Instruct", "provider": "huggingface"},
            {"id": "tiiuae/falcon-40b-instruct", "name": "Falcon 40B Instruct", "provider": "huggingface"},
            {"id": "google/gemma-7b-it", "name": "Gemma 7B Instruct", "provider": "huggingface"},
            {"id": "meta-llama/Meta-Llama-3-8B-Instruct", "name": "Llama 3 8B Instruct", "provider": "huggingface"},
            {"id": "Microsoft/Phi-2", "name": "Phi-2", "provider": "huggingface"},
        ]
    
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate a response from the given prompt using the specified model.
        
        Args:
            model_id: ID of the model to use (e.g., "meta-llama/Llama-2-7b-chat-hf")
            prompt: The prompt to generate a response for
            **kwargs: Additional parameters such as max_tokens, temperature, etc.
            
        Returns:
            Generated text response
        """
        # Check for API key before making the request
        if not self.api_key:
            raise ValueError("HuggingFace API key is required. Please provide api_key or set HF_API_TOKEN environment variable.")
        
        # Load the model if not loaded
        if not self.is_model_loaded(model_id):
            success = await self._load_model(model_id)
            if not success:
                raise ValueError(f"Failed to load model {model_id}")
        
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Check if we're using local inference
        if self._use_local_inference() and hasattr(self, "_local_models") and model_id in self._local_models:
            return await self._generate_locally(model_id, prompt, max_tokens, temperature, **kwargs)
        else:
            return await self._generate_with_api(model_id, prompt, max_tokens, temperature, **kwargs)
    
    async def _generate_locally(self, model_id: str, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate text using a locally loaded model.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to generate a response for
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            if self.verbose:
                print(f"Generating with local model: {model_id}")
                
            # Get the local model
            model_data = self._local_models[model_id]
            generator = model_data["generator"]
            
            # Set up generation parameters
            gen_kwargs = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": temperature > 0.0,
                "early_stopping": True,
            }
            
            # Add other parameters if provided
            for key, value in kwargs.items():
                if key == "top_p":
                    gen_kwargs["top_p"] = value
                elif key == "top_k":
                    gen_kwargs["top_k"] = value
                elif key in ["repetition_penalty", "presence_penalty", "frequency_penalty"]:
                    gen_kwargs["repetition_penalty"] = value
            
            # Generate the response
            result = await asyncio.to_thread(
                generator,
                prompt,
                **gen_kwargs
            )
            
            # Extract the generated text
            generated_text = result[0]["generated_text"]
            
            # Remove the prompt from the beginning if present
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            return generated_text
            
        except Exception as e:
            if self.verbose:
                print(f"Error generating locally: {str(e)}")
            # Fall back to API if local generation fails
            return await self._generate_with_api(model_id, prompt, max_tokens, temperature, **kwargs)
    
    async def _generate_with_api(self, model_id: str, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate text using the HuggingFace Inference API.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to generate a response for
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        # Construct the API URL for the Inference API
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        # Set up headers with authorization
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the request payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        # Add other parameters if provided
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature"]:
                if key == "top_p":
                    payload["parameters"]["top_p"] = value
                elif key == "top_k":
                    payload["parameters"]["top_k"] = value
                elif key in ["repetition_penalty", "presence_penalty", "frequency_penalty"]:
                    payload["parameters"]["repetition_penalty"] = value
        
        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ValueError(f"Error generating response: {response.status} - {text}")
                
                data = await response.json()
                
                # HuggingFace API can return different formats depending on the model
                # Handle all potential formats
                if isinstance(data, list) and len(data) > 0:
                    # Case 1: Array of responses
                    first_result = data[0]
                    
                    if isinstance(first_result, dict):
                        # Case 1.1: Dictionary with 'generated_text' key
                        if "generated_text" in first_result:
                            return first_result["generated_text"]
                        
                        # Case 1.2: Dictionary with other keys
                        for key in ["text", "response", "answer", "output"]:
                            if key in first_result:
                                return first_result[key]
                    
                    # Case 1.3: String in array
                    if isinstance(first_result, str):
                        return first_result
                
                # Case 2: Direct dictionary
                if isinstance(data, dict):
                    # Case 2.1: Dictionary with 'generated_text' key
                    if "generated_text" in data:
                        return data["generated_text"]
                    
                    # Case 2.2: Dictionary with other keys
                    for key in ["text", "response", "answer", "output"]:
                        if key in data:
                            return data[key]
                
                # Case 3: Direct string
                if isinstance(data, str):
                    return data
                
                # If none of the above, try to convert to string
                return str(data)
    
    async def test_prompt(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """Test a prompt against the model and return detailed information.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to test
            
        Returns:
            Dictionary containing success status, response, and metadata
        """
        try:
            # Construct the API URL for the Inference API
            api_url = f"https://api-inference.huggingface.co/models/{model_id}"
            
            # Set up headers with authorization
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Error {response.status}: {error_text}",
                            "metadata": {
                                "status_code": response.status,
                                "headers": dict(response.headers)
                            }
                        }
                    
                    response_data = await response.json()
                    
                    # Extract metadata
                    metadata = {
                        "model": model_id,
                        "headers": dict(response.headers)
                    }
                    
                    # Extract the response text
                    generated_text = ""
                    
                    # Handle different response formats
                    if isinstance(response_data, list) and len(response_data) > 0:
                        first_result = response_data[0]
                        
                        if isinstance(first_result, dict):
                            if "generated_text" in first_result:
                                generated_text = first_result["generated_text"]
                            else:
                                for key in ["text", "response", "answer", "output"]:
                                    if key in first_result:
                                        generated_text = first_result[key]
                                        break
                        elif isinstance(first_result, str):
                            generated_text = first_result
                    elif isinstance(response_data, dict):
                        if "generated_text" in response_data:
                            generated_text = response_data["generated_text"]
                        else:
                            for key in ["text", "response", "answer", "output"]:
                                if key in response_data:
                                    generated_text = response_data[key]
                                    break
                    elif isinstance(response_data, str):
                        generated_text = response_data
                    
                    if generated_text:
                        return {
                            "success": True,
                            "response": generated_text,
                            "metadata": metadata
                        }
                    
                    return {
                        "success": False,
                        "error": "Could not extract generated text from response",
                        "metadata": metadata,
                        "raw_response": response_data
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"error_type": type(e).__name__}
            } 