import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
import time

from ..base_handler import ModelHandler


class OllamaHandler(ModelHandler):
    """Model handler for Ollama models running locally."""
    
    def __init__(self, base_url: str = "http://localhost:11434", verbose: bool = False):
        """Initialize the Ollama handler.
        
        Args:
            base_url: Base URL for the Ollama API. If not provided, uses OLLAMA_HOST environment variable
                or defaults to http://localhost:11434
            verbose: Whether to output verbose logging information.
        """
        super().__init__(verbose=verbose)
        self.base_url = base_url.rstrip('/')
        self.session = None
        
        # Track loaded models
        self._loaded_models = set()
    
    def is_model_loaded(self, model_id: str) -> bool:
        """Check if a model is loaded in Ollama.
        
        Args:
            model_id: Name of the model to check
            
        Returns:
            bool: True if the model is loaded, False otherwise
        """
        return model_id in self._loaded_models
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
    async def _close_session(self):
        """Close the aiohttp session if it exists"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _fetch_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from Ollama.
        
        Returns:
            List of model dictionaries
        """
        try:
            if self.verbose:
                print(f"Fetching available models from Ollama at {self.base_url}")
                
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    if self.verbose:
                        print(f"Error fetching models: {response.status}")
                    return []
                    
                data = await response.json()
                models = data.get("models", [])
                
                if self.verbose:
                    print(f"Found {len(models)} models")
                    
                # Update available models
                self.available_models = models
                
                # Mark all models as loaded
                for model in models:
                    self._loaded_models.add(model["name"])
                    
                return models
        except Exception as e:
            if self.verbose:
                print(f"Error fetching models: {str(e)}")
            return []
    
    async def _ensure_model_loaded(self, model_id: str) -> bool:
        """Ensure a model is loaded in Ollama.
        
        Args:
            model_id: Name of the model to load
            
        Returns:
            bool: True if the model is loaded or successfully loaded, False otherwise
        """
        # Check if we've already verified this model
        if model_id in self._loaded_models:
            return True
            
        try:
            if self.verbose:
                print(f"Checking if model {model_id} is available in Ollama")
                
            # First fetch available models if we haven't done so
            if not self.available_models:
                await self._fetch_models()
                
            # Check if model is in available models
            if model_id in [model["name"] for model in self.available_models]:
                self._loaded_models.add(model_id)
                return True
            
            # If not found, pull the model
            if self.verbose:
                print(f"Model {model_id} not found, attempting to pull it")
                
            api_url = f"{self.base_url}/api/pull"
            payload = {"name": model_id}
            
            async with self.session.post(api_url, json=payload) as response:
                if response.status != 200:
                    if self.verbose:
                        error_text = await response.text()
                        print(f"Error pulling model: {error_text}")
                    return False
                
                # Model pulled successfully
                self._loaded_models.add(model_id)
                return True
        except Exception as e:
            if self.verbose:
                print(f"Error ensuring model is loaded: {str(e)}")
            return False
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models in Ollama.
        
        Returns:
            List of dictionaries containing model information.
        """
        try:
            await self._ensure_session()
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "id": model["name"],
                            "name": model["name"],
                            "provider": "ollama",
                            "modified_at": model.get("modified_at", ""),
                            "size": model.get("size", 0)
                        }
                        for model in data.get("models", [])
                    ]
                else:
                    error_text = await response.text()
                    raise Exception(f"Error listing models: {error_text}")
        except Exception as e:
            if self.verbose:
                print(f"Error listing Ollama models: {str(e)}")
            return []
    
    async def generate(self, model_id: str, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """Generate a response from the given prompt using the specified model.
        
        Args:
            model_id: Name of the model to use
            prompt: The prompt to generate a response for
            max_tokens: Maximum number of tokens to generate (optional)
            temperature: Temperature for generation (optional)
            
        Returns:
            Generated text response
        """
        try:
            await self._ensure_session()
            
            if self.verbose:
                print(f"Generating with Ollama model {model_id} at {self.base_url}")
            
            # Prepare the request payload
            payload = {
                "model": model_id,
                "prompt": prompt
            }
            
            # Add optional parameters if specified in the Ollama format
            options = {}
            if max_tokens is not None:
                options["num_predict"] = max_tokens
            if temperature is not None:
                options["temperature"] = temperature
            
            # Only add options if there are any
            if options:
                payload["options"] = options
                
            if self.verbose:
                print(f"Sending request to {self.base_url}/api/generate with model {model_id}")
                
            # Make the API request with streaming
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    error_msg = f"Error from Ollama API: HTTP {response.status} - {error_text}"
                    if self.verbose:
                        print(error_msg)
                    raise Exception(error_msg)
                
                # Process the streaming response
                full_response = ""
                metadata = {}
                chunk_count = 0
                
                # Read and process the response stream
                if self.verbose:
                    print("Processing streaming response from Ollama")
                    
                async for line in response.content:
                    if not line:
                        continue
                        
                    try:
                        # Decode the line to text
                        line_text = line.decode('utf-8').strip()
                        chunk = json.loads(line_text)
                        chunk_count += 1
                        
                        # Extract the response text
                        if "response" in chunk:
                            token = chunk["response"]
                            full_response += token
                            
                        # If this is the final chunk, save metadata
                        if chunk.get("done", False):
                            metadata = {
                                "model": chunk.get("model"),
                                "created_at": chunk.get("created_at"),
                                "total_duration": chunk.get("total_duration"),
                                "load_duration": chunk.get("load_duration"),
                                "prompt_eval_count": chunk.get("prompt_eval_count"),
                                "prompt_eval_duration": chunk.get("prompt_eval_duration"),
                                "eval_count": chunk.get("eval_count"),
                                "eval_duration": chunk.get("eval_duration"),
                                "done_reason": chunk.get("done_reason")
                            }
                            
                            if self.verbose:
                                elapsed = time.time() - start_time
                                print(f"Ollama generation complete: {chunk_count} chunks received in {elapsed:.2f}s")
                                print(f"Response length: {len(full_response)} characters")
                            
                    except json.JSONDecodeError as e:
                        if self.verbose:
                            print(f"Error decoding JSON chunk: {str(e)}")
                            print(f"Problem line: {line}")
                        continue
                    except Exception as e:
                        if self.verbose:
                            print(f"Error processing chunk: {str(e)}")
                        continue
                
                if self.verbose:
                    print(f"Completed Ollama generation with {chunk_count} chunks")
                
                return full_response.strip()
                
        except Exception as e:
            error_msg = f"Error generating with Ollama: {str(e)}"
            if self.verbose:
                print(error_msg)
                import traceback
                traceback.print_exc()
            raise Exception(error_msg)
            
        finally:
            # Don't close the session here - it will be reused
            pass
    
    async def test_prompt(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """Test a prompt against the model and return detailed information.
        
        Args:
            model_id: Name of the model to use
            prompt: The prompt to test
            
        Returns:
            Dictionary containing success status, response, and metadata
        """
        try:
            # Ensure the model is loaded
            if not await self._ensure_model_loaded(model_id):
                return {
                    "success": False,
                    "error": f"Failed to load model {model_id}",
                    "metadata": {"model": model_id}
                }
            
            # Prepare request
            api_url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model_id,
                "prompt": prompt,
                "options": {
                    "num_predict": 1000,
                    "temperature": 0.7
                }
            }
            
            # Make the API request
            async with self.session.post(api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Error {response.status}: {error_text}",
                        "metadata": {
                            "status_code": response.status,
                            "model": model_id
                        }
                    }
                
                # Handle response format
                content_type = response.headers.get("Content-Type", "")
                
                if "text/event-stream" in content_type:
                    # Stream format - accumulate text and metadata
                    full_text = ""
                    total_eval_duration = 0
                    eval_count = 0
                    
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        if not line:
                            continue
                            
                        if line.startswith("data: "):
                            line = line[6:]  # Remove "data: " prefix
                            
                        try:
                            chunk = json.loads(line)
                            response_chunk = chunk.get("response", "")
                            full_text += response_chunk
                            
                            # Collect metadata
                            if "eval_duration" in chunk:
                                total_eval_duration += chunk["eval_duration"]
                                eval_count += 1
                        except json.JSONDecodeError:
                            continue
                            
                    # Calculate average eval duration
                    avg_eval_duration = total_eval_duration / eval_count if eval_count > 0 else 0
                    
                    return {
                        "success": True,
                        "response": full_text,
                        "metadata": {
                            "model": model_id,
                            "avg_eval_duration": avg_eval_duration,
                            "eval_count": eval_count
                        }
                    }
                else:
                    # Single JSON response
                    data = await response.json()
                    return {
                        "success": True,
                        "response": data.get("response", ""),
                        "metadata": {
                            "model": model_id,
                            "eval_duration": data.get("eval_duration", 0),
                            "total_duration": data.get("total_duration", 0)
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "model": model_id,
                    "error_type": type(e).__name__
                }
            } 

    async def close(self):
        """Close any open resources"""
        await self._close_session() 