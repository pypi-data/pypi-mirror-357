# Custom Model Handlers for Dravik Benchmarking

This guide explains how to create and use custom model handlers with the Dravik benchmarking system.

## Overview

Dravik allows you to integrate your own custom models or APIs into the benchmarking system. This enables:

- Benchmarking your own models against industry standards like OpenAI and Google models
- Testing custom endpoints or private deployments
- Creating specialized handlers for unique model architectures or APIs

## Creating a Custom Model Handler

### Step 1: Create a Handler Class

Create a Python file with a class that implements the required methods:

```python
import asyncio
from typing import Dict, Any, List

class MyCustomHandler:
    """Custom model handler for my API"""
    
    def __init__(self, model_name: str = "my-model", api_key: str = None, **kwargs):
        """Initialize the handler
        
        Args:
            model_name: Name of the model to use
            api_key: API key for accessing the model
            **kwargs: Additional parameters passed from configuration
        """
        self.model_name = model_name
        self.api_key = api_key
        # Store any other configuration
        self.config = kwargs
    
    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a prompt and return a response
        
        This is the REQUIRED method that will be called by the benchmark system.
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Dictionary with response information
        """
        # Call your API or model here
        # ...
        
        # Return a standardized response
        return {
            "success": True,  # Whether the request was successful
            "response": "Your model's response text goes here",  # The generated text
            "model": self.model_name,  # Model identifier
            "provider": "your-provider-name",  # Provider name (your company/system)
            "version": "1.0"  # Version identifier
        }
    
    # OPTIONAL: Implement list_models to enable model discovery
    @staticmethod
    async def list_models() -> List[str]:
        """Return a list of available models
        
        Returns:
            List of model names
        """
        return ["model-1", "model-2", "model-3"]
    
    # OPTIONAL: Implement a simpler generate method
    async def generate(self, prompt: str) -> str:
        """Generate a response to the prompt
        
        Args:
            prompt: The prompt to process
            
        Returns:
            The generated text response
        """
        result = await self.test_prompt(prompt)
        return result.get("response", "Error generating response")
```

### Step 2: Save Your Handler File

Save your handler file in one of these locations:

1. The `examples/` directory in the Dravik project
2. Any directory that's in your Python path

### Step 3: Register Your Custom Model

There are two ways to register your custom model:

#### Option 1: Register via CLI (Recommended)

1. Run the Dravik CLI
2. Select `Benchmarking` from the main menu
3. Select `Register Custom Model`
4. Follow the prompts:
   - **Model Name**: A unique name to identify your model
   - **Module Path**: Path to your module (without .py extension)
     - If in examples dir: `examples.your_file_name` (no `.py`)
     - If elsewhere: `full.path.to.your.module`
   - **Class Name**: Name of your handler class
   - **Parameters**: Any parameters needed to initialize your handler

#### Option 2: Register Programmatically

```python
from benchmarks.models.model_loader import ModelLoader

model_loader = ModelLoader(verbose=True)
model_loader.register_custom_model(
    "my-custom-model",  # Name for your model
    {
        "module_path": "examples.my_custom_handler",  # Module path without .py
        "class_name": "MyCustomHandler",              # Class name
        "params": {                                   # Parameters for __init__
            "model_name": "my-model-name",
            "api_key": "your-api-key",
            "endpoint_url": "https://your-api-endpoint.com"
        },
        "provider": "custom",
        "version": "1.0"
    }
)
```

## Using Your Custom Model

Once registered, your model will appear in:

1. The model selection list when running benchmarks
2. API response comparisons with other models

## Example: Creating a Handler for an OpenAI-compatible API Server

Here's a complete example of a handler for a self-hosted OpenAI-compatible API server:

```python
import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, List

class OpenAICompatibleHandler:
    """Handler for an OpenAI-compatible API server"""
    
    def __init__(self, 
                 endpoint_url: str, 
                 api_key: str = None, 
                 model_name: str = "gpt-3.5-turbo",
                 timeout: int = 30,
                 verbose: bool = False):
        """Initialize the handler
        
        Args:
            endpoint_url: URL of the API endpoint (e.g., http://localhost:8000/v1)
            api_key: API key (if required)
            model_name: Name of the model to use
            timeout: Request timeout in seconds
            verbose: Whether to print verbose output
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.verbose = verbose
    
    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a prompt and return a response
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Dictionary with response information
        """
        start_time = time.time()
        
        try:
            # Build the chat completions endpoint URL
            url = f"{self.endpoint_url.rstrip('/')}/chat/completions"
            
            # Set up headers with API key if provided
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Build the request payload
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            if self.verbose:
                print(f"Sending request to {url}")
                
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=headers,
                    timeout=self.timeout
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract the response text from OpenAI-compatible format
                        response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        return {
                            "success": True,
                            "response": response_text,
                            "model": self.model_name,
                            "provider": "custom-openai",
                            "version": "1.0",
                            "response_time": response_time
                        }
                    else:
                        error_text = await response.text()
                        
                        return {
                            "success": False,
                            "error": f"API error ({response.status}): {error_text}",
                            "model": self.model_name,
                            "provider": "custom-openai",
                            "version": "1.0",
                            "response_time": response_time
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "model": self.model_name,
                "provider": "custom-openai",
                "version": "1.0",
                "response_time": time.time() - start_time
            }
    
    async def list_models(self) -> List[str]:
        """Return a list of available models
        
        Returns:
            List of model names
        """
        try:
            # Build the models endpoint URL
            url = f"{self.endpoint_url.rstrip('/')}/models"
            
            # Set up headers with API key if provided
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract model IDs from OpenAI-compatible format
                        models = [model.get("id") for model in data.get("data", [])]
                        return models or ["gpt-3.5-turbo"]  # Fallback if empty
                    else:
                        return ["gpt-3.5-turbo"]  # Default model as fallback
                        
        except Exception as e:
            if self.verbose:
                print(f"Error listing models: {e}")
            return ["gpt-3.5-turbo"]  # Default model as fallback
```

## Reference Implementation

Dravik includes a complete example in `examples/custom_benchmark_handler.py` which:

1. Shows all required and optional methods
2. Provides an example implementation with API calls
3. Demonstrates error handling
4. Includes detailed comments for customization

## Troubleshooting

### Module Import Errors

If you see errors like `ModuleNotFoundError: No module named 'path.to'`:

- Make sure you're using dots (.) in the module path, not slashes (/)
- Don't include the .py extension in the module path
- If your module is in the `examples/` directory, use `examples.your_file_name`
- If your module is elsewhere, make sure the directory is in your Python path

### Handler Initialization Errors

If your handler fails to initialize:

- Check that all required parameters are being passed
- Make sure your `__init__` method properly handles optional parameters
- Add verbose logging in your handler to debug initialization issues

### API Connection Errors

If your handler can't connect to your API:

- Verify endpoint URLs and API keys
- Add timeout handling and retries for more robust connections
- Use try/except blocks to gracefully handle connection failures

## Best Practices

1. **Error Handling**: Always include robust error handling in your handler
2. **Async Implementation**: Use `async/await` for all methods to enable concurrent benchmarking
3. **Standardized Responses**: Follow the response format in the examples
4. **Verbose Mode**: Include a verbose option that logs detailed information when troubleshooting
5. **Flexible Parameters**: Make your handler configurable through parameters 