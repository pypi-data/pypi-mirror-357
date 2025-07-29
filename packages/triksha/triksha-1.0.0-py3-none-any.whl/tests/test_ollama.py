#!/usr/bin/env python3
"""Test script for Ollama model integration."""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from benchmarks.models.handlers.ollama_handler import OllamaHandler
from benchmarks.models.model_loader import ModelLoader


async def test_ollama_direct():
    """Test direct usage of OllamaHandler."""
    print("Testing direct OllamaHandler usage...")
    
    # Create handler with default localhost URL
    handler = OllamaHandler(verbose=True)
    
    # List available models
    print("\nListing available Ollama models:")
    models = await handler.list_models()
    
    if not models:
        print("No models found in Ollama. Please ensure Ollama is running and has models.")
        return
    
    print(f"Found {len(models)} models in Ollama:")
    for model in models:
        print(f"  - {model['name']}")
    
    # Select first model for testing
    selected_model = models[0]['id']
    
    # Test generation
    print(f"\nTesting generation with model: {selected_model}")
    prompt = "Explain what Ollama is in one paragraph."
    
    try:
        response = await handler.generate(selected_model, prompt, max_tokens=200)
        print("\nGenerated response:")
        print("-------------------")
        print(response)
        print("-------------------")
    except Exception as e:
        print(f"Error generating response: {e}")


async def test_model_loader_integration():
    """Test ModelLoader integration with Ollama."""
    print("\nTesting ModelLoader integration with Ollama...")
    
    # Create model loader
    loader = ModelLoader(verbose=True)
    
    # Register a custom Ollama model
    model_name = "test-ollama-model"
    model_config = {
        "type": "ollama",
        "model_id": "llama2",  # Adjust to a model available on your Ollama instance
        "base_url": "http://localhost:11434"  # Default Ollama URL
    }
    
    success = loader.register_custom_model(model_name, model_config)
    if not success:
        print("Failed to register Ollama model config")
        return
    
    print(f"Registered custom Ollama model: {model_name}")
    
    # Load the handler
    handler = loader.load_handler(model_name)
    if not handler:
        print("Failed to load Ollama handler")
        return
    
    print("Successfully loaded Ollama handler")
    
    # Test the handler
    prompt = "What are the advantages of using Ollama for local LLM inference?"
    
    try:
        response = await handler.generate("llama2", prompt, max_tokens=200)
        print("\nGenerated response via ModelLoader:")
        print("-----------------------------------")
        print(response)
        print("-----------------------------------")
    except Exception as e:
        print(f"Error generating response: {e}")


if __name__ == "__main__":
    # Run the tests
    async def main():
        await test_ollama_direct()
        await test_model_loader_integration()
    
    asyncio.run(main()) 