#!/usr/bin/env python3
"""Test script for CustomAPI model integration."""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from benchmarks.models.handlers.custom_api_handler import CustomAPIHandler
from benchmarks.models.model_loader import ModelLoader


async def test_custom_api_with_curl():
    """Test CustomAPIHandler with curl command approach."""
    print("Testing CustomAPIHandler with curl command...")
    
    # This is a template example - curl to OpenAI API
    # In a real scenario, replace with your actual API endpoint
    curl_command = """
    curl -s -X POST https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": {prompt}}],
      "max_tokens": {max_tokens},
      "temperature": {temperature}
    }'
    """
    
    # Create handler with curl command
    handler = CustomAPIHandler(
        name="test-curl-custom-api",
        curl_command=curl_command,
        json_path="choices[0].message.content",
        verbose=True
    )
    
    # Test if OPENAI_API_KEY is available in environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found in environment, skipping test")
        return
    
    # Test generation
    print("Testing generation with curl command...")
    prompt = "What are the benefits of using a custom API approach?"
    
    try:
        response = await handler.generate("ignored-model-id", prompt, max_tokens=100, temperature=0.7)
        print("\nGenerated response:")
        print("-------------------")
        print(response)
        print("-------------------")
    except Exception as e:
        print(f"Error generating response: {e}")


async def test_custom_api_with_http():
    """Test CustomAPIHandler with direct HTTP approach."""
    print("\nTesting CustomAPIHandler with direct HTTP...")
    
    # Only run this test if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found in environment, skipping test")
        return
    
    # Create handler with HTTP endpoint
    handler = CustomAPIHandler(
        name="test-http-custom-api",
        endpoint_url="https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
        },
        http_method="POST",
        json_path="choices[0].message.content",
        verbose=True
    )
    
    # Test generation
    print("Testing generation with HTTP request...")
    prompt = "Compare using curl vs direct HTTP requests for API integration"
    
    try:
        # Note: the payload will be adjusted by the handler
        response = await handler.generate("ignored-model-id", prompt, 
                                         max_tokens=150,
                                         temperature=0.7,
                                         model="gpt-3.5-turbo",
                                         messages=[{"role": "user", "content": prompt}])
        print("\nGenerated response:")
        print("-------------------")
        print(response)
        print("-------------------")
    except Exception as e:
        print(f"Error generating response: {e}")


async def test_model_loader_integration():
    """Test ModelLoader integration with CustomAPIHandler."""
    print("\nTesting ModelLoader integration with CustomAPIHandler...")
    
    # Create model loader
    loader = ModelLoader(verbose=True)
    
    # Only continue if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found in environment, skipping test")
        return
    
    # Register a custom API model with HTTP configuration
    model_name = "test-custom-api-model"
    model_config = {
        "type": "custom-api",
        "endpoint_url": "https://api.openai.com/v1/chat/completions",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
        },
        "http_method": "POST",
        "json_path": "choices[0].message.content"
    }
    
    success = loader.register_custom_model(model_name, model_config)
    if not success:
        print("Failed to register Custom API model config")
        return
    
    print(f"Registered custom API model: {model_name}")
    
    # Load the handler
    handler = loader.load_handler(model_name)
    if not handler:
        print("Failed to load Custom API handler")
        return
    
    print("Successfully loaded Custom API handler")
    
    # Test the handler
    prompt = "What are the advantages of using a custom API handler for LLM integration?"
    
    try:
        response = await handler.generate("ignored-model-id", prompt, 
                                         max_tokens=150,
                                         temperature=0.7,
                                         model="gpt-3.5-turbo",
                                         messages=[{"role": "user", "content": prompt}])
        print("\nGenerated response via ModelLoader:")
        print("-----------------------------------")
        print(response)
        print("-----------------------------------")
    except Exception as e:
        print(f"Error generating response: {e}")


if __name__ == "__main__":
    # Run the tests
    async def main():
        await test_custom_api_with_curl()
        await test_custom_api_with_http()
        await test_model_loader_integration()
    
    asyncio.run(main()) 