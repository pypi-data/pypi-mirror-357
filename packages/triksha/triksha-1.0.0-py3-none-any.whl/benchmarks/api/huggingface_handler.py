"""Handler for HuggingFace API interactions"""
import os
import json
import asyncio
import time
import requests
from typing import List, Dict, Any, Optional

class HuggingFaceHandler:
    """Handler for HuggingFace API interactions"""
    
    def __init__(self, 
                 model_id: str, 
                 api_key: Optional[str] = None,
                 inference_params: Optional[Dict[str, Any]] = None,
                 verbose: bool = False):
        """Initialize HuggingFace model handler
        
        Args:
            model_id: HuggingFace model ID (e.g., 'meta-llama/Llama-2-7b')
            api_key: HuggingFace API key
            inference_params: Parameters for inference
            verbose: Whether to output verbose logs
        """
        self.model_id = model_id
        self.api_key = api_key or os.environ.get('HF_API_TOKEN') or os.environ.get('HUGGINGFACE_API_KEY')
        self.inference_params = inference_params or {}
        self.verbose = verbose
        
        # Default parameters if not provided
        if 'temperature' not in self.inference_params:
            self.inference_params['temperature'] = 0.7
        if 'max_length' not in self.inference_params:
            self.inference_params['max_length'] = 512
        if 'top_p' not in self.inference_params:
            self.inference_params['top_p'] = 0.9
            
        if self.verbose:
            print(f"Initialized HuggingFace handler for model: {model_id}")
            if self.api_key:
                print(f"API key provided")
            print(f"Inference parameters: {self.inference_params}")
    
    @staticmethod
    async def list_models() -> List[str]:
        """List available HuggingFace models for text generation
        
        Returns:
            List of popular HuggingFace model IDs
        """
        # This is a static list of popular models - in a real implementation,
        # you might query the HuggingFace API for a more complete list
        return [
            "meta-llama/Llama-2-7b",
            "meta-llama/Llama-2-13b",
            "mistralai/Mistral-7B-v0.1",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "tiiuae/falcon-7b",
            "tiiuae/falcon-40b",
            "bigscience/bloom",
            "google/gemma-7b",
            "stabilityai/stablelm-tuned-alpha-7b",
            "EleutherAI/pythia-12b",
            "google/flan-t5-xxl"
        ]
    
    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Test a prompt using HuggingFace Inference API
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Dictionary with response information
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "HuggingFace API key is required but not provided",
                "model": self.model_id,
                "provider": "huggingface",
                "version": "inference-api"
            }
            
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Build the payload
            payload = {
                "inputs": prompt,
                "parameters": self.inference_params
            }
            
            api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
            
            if self.verbose:
                print(f"Sending request to HuggingFace Inference API for model: {self.model_id}")
                print(f"Prompt: {prompt[:50]}...")
            
            # Make the request - using requests here because the HF API can be slow
            # and asyncio might timeout. For production use, consider implementing
            # with proper async handling and timeouts.
            response = requests.post(api_url, headers=headers, json=payload)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse the response based on model type
                # The HF API returns different formats depending on the model
                if isinstance(result, list) and len(result) > 0:
                    if 'generated_text' in result[0]:
                        # Text generation format
                        response_text = result[0]['generated_text']
                    else:
                        # Handle other formats (e.g., some models return [{"text": "..."}])
                        response_text = result[0].get('text', str(result))
                elif isinstance(result, dict):
                    # Some models return a direct dictionary
                    if 'generated_text' in result:
                        response_text = result['generated_text']
                    else:
                        # Just convert to string if we can't find a standard field
                        response_text = str(result)
                else:
                    # If we received something else, just convert to string
                    response_text = str(result)
                
                # If the response starts with the prompt, remove it to get just the generation
                if response_text.startswith(prompt):
                    response_text = response_text[len(prompt):].strip()
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model_id,
                    "provider": "huggingface",
                    "version": "inference-api",
                    "response_time": elapsed_time
                }
            else:
                # Handle error response
                error_detail = response.text
                try:
                    error_json = response.json()
                    if 'error' in error_json:
                        error_detail = error_json['error']
                except:
                    pass
                
                return {
                    "success": False,
                    "error": f"API Error ({response.status_code}): {error_detail}",
                    "model": self.model_id,
                    "provider": "huggingface",
                    "version": "inference-api",
                    "response_time": elapsed_time
                }
                
        except Exception as e:
            if self.verbose:
                print(f"Error in HuggingFace test_prompt: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "model": self.model_id,
                "provider": "huggingface",
                "version": "inference-api",
                "response_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using HuggingFace Inference API
        
        This is a simpler interface that just returns the text.
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Generated text response
        """
        result = await self.test_prompt(prompt)
        return result.get("response", f"Error: {result.get('error', 'Unknown error')}") 