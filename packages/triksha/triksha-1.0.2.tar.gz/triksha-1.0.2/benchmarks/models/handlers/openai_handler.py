import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional

from ..base_handler import ModelHandler


class OpenAIHandler(ModelHandler):
    """Model handler for OpenAI models."""
    
    def __init__(self, api_key: Optional[str] = None, org_id: Optional[str] = None, verbose: bool = False):
        """Initialize the OpenAI handler.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable.
            org_id: OpenAI organization ID. If not provided, will use OPENAI_ORG_ID environment variable.
            verbose: Whether to output verbose logging information.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.org_id = org_id or os.environ.get("OPENAI_ORG_ID")
        self.verbose = verbose
        
        # Verify that we have an API key
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please provide api_key or set OPENAI_API_KEY environment variable.")
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available OpenAI models.
        
        Returns:
            List of dictionaries containing model information.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.openai.com/v1/models", headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ValueError(f"Error fetching models: {response.status} - {text}")
                
                data = await response.json()
                
                # Filter to include only chat models
                chat_models = []
                
                # Hardcode the models we know work well for chat
                known_chat_models = [
                    {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
                    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "openai"},
                    {"id": "gpt-4-1106-preview", "name": "GPT-4 Turbo Preview", "provider": "openai"},
                    {"id": "gpt-4-0125-preview", "name": "GPT-4 Turbo 0125", "provider": "openai"},
                    {"id": "gpt-4-vision-preview", "name": "GPT-4 Vision", "provider": "openai"},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
                    {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16K", "provider": "openai"},
                ]
                
                # Add any models from the API that contain 'gpt' and are owned by OpenAI
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    
                    # Skip if not a GPT model
                    if "gpt" not in model_id.lower():
                        continue
                    
                    # Check if model is already in our known list
                    if any(km["id"] == model_id for km in known_chat_models):
                        continue
                    
                    # Add the model
                    chat_models.append({
                        "id": model_id,
                        "name": model_id,
                        "provider": "openai"
                    })
                
                # Return combined list of models
                return known_chat_models + chat_models
    
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate a response from the given prompt using the specified model.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to generate a response for
            **kwargs: Additional parameters such as max_tokens, temperature, etc.
            
        Returns:
            Generated text response
        """
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add other parameters if provided
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature"]:
                payload[key] = value
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", 
                                    headers=headers, 
                                    json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ValueError(f"Error generating response: {response.status} - {text}")
                
                data = await response.json()
                
                # Extract the response text
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    return message.get("content", "")
                
                return ""
    
    async def test_prompt(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """Test a prompt against the model and return detailed information.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to test
            
        Returns:
            Dictionary containing success status, response, and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.openai.com/v1/chat/completions", 
                                        headers=headers, 
                                        json=payload) as response:
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
                        "model": response_data.get("model", ""),
                        "id": response_data.get("id", ""),
                        "usage": response_data.get("usage", {}),
                        "created": response_data.get("created", 0),
                        "headers": dict(response.headers)
                    }
                    
                    # Extract the response text
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        message = response_data["choices"][0].get("message", {})
                        return {
                            "success": True,
                            "response": message.get("content", ""),
                            "metadata": metadata
                        }
                    
                    return {
                        "success": False,
                        "error": "No response choices found",
                        "metadata": metadata
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"error_type": type(e).__name__}
            } 