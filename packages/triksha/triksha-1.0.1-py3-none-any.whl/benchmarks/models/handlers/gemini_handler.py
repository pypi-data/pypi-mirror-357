import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional

from ..base_handler import ModelHandler


class GeminiHandler(ModelHandler):
    """Model handler for Google's Gemini models."""
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """Initialize the Gemini handler.
        
        Args:
            api_key: Google API key. If not provided, will use GOOGLE_API_KEY environment variable.
            verbose: Whether to output verbose logging information.
        """
        if api_key:
            self.api_key = api_key
        else:
            # Try to get API key from ApiKeyManager first, then fall back to environment
            try:
                from utils.api_key_manager import get_api_key_manager
                api_manager = get_api_key_manager()
                self.api_key = api_manager.get_key("gemini")
            except ImportError:
                # Fall back to environment variable
                self.api_key = os.environ.get("GOOGLE_API_KEY")
                
        self.verbose = verbose
        
        # Verify that we have an API key
        if not self.api_key:
            raise ValueError("Google API key is required. Please provide api_key parameter, set GOOGLE_API_KEY environment variable, or configure it in API key settings.")
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available Gemini models.
        
        Returns:
            List of dictionaries containing model information.
        """
        # Gemini models are hardcoded since there's no API to list them
        return [
            {"id": "gemini-pro", "name": "Gemini Pro", "provider": "gemini"},
            {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "provider": "gemini"},
            {"id": "gemini-ultra", "name": "Gemini Ultra", "provider": "gemini"},
        ]
    
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate a response from the given prompt using the specified model.
        
        Args:
            model_id: ID of the model to use (e.g., "gemini-pro")
            prompt: The prompt to generate a response for
            **kwargs: Additional parameters such as max_tokens, temperature, etc.
            
        Returns:
            Generated text response
        """
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Construct the API URL
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Add other parameters if provided
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature"]:
                if key == "top_p":
                    payload["generationConfig"]["topP"] = value
                elif key == "top_k":
                    payload["generationConfig"]["topK"] = value
        
        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ValueError(f"Error generating response: {response.status} - {text}")
                
                data = await response.json()
                
                # Extract the response text
                try:
                    if "candidates" in data and len(data["candidates"]) > 0:
                        content = data["candidates"][0]["content"]
                        if "parts" in content and len(content["parts"]) > 0:
                            return content["parts"][0].get("text", "")
                except Exception as e:
                    if self.verbose:
                        print(f"Error extracting response from Gemini: {e}")
                    return ""
                
                return ""
    
    async def test_prompt(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """Test a prompt against the model and return detailed information.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to test
            
        Returns:
            Dictionary containing success status, response, and metadata
        """
        try:
            # Construct the API URL
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
            
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 1000,
                    "temperature": 0.7
                }
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"Error {response.status}: {response_data.get('error', {}).get('message', 'Unknown error')}",
                            "metadata": {
                                "status_code": response.status,
                                "headers": dict(response.headers)
                            }
                        }
                    
                    # Extract metadata
                    metadata = {
                        "model": model_id,
                        "headers": dict(response.headers),
                        "usage": response_data.get("usageMetadata", {})
                    }
                    
                    # Extract the response text
                    try:
                        if "candidates" in response_data and len(response_data["candidates"]) > 0:
                            content = response_data["candidates"][0]["content"]
                            if "parts" in content and len(content["parts"]) > 0:
                                return {
                                    "success": True,
                                    "response": content["parts"][0].get("text", ""),
                                    "metadata": metadata
                                }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Error extracting response: {str(e)}",
                            "metadata": metadata
                        }
                    
                    return {
                        "success": False,
                        "error": "No response candidates found",
                        "metadata": metadata
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"error_type": type(e).__name__}
            } 