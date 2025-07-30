"""
Ollama API handler for benchmarking.

This module handles interactions with the Ollama API for LLM benchmarking.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import backoff

OLLAMA_API_BASE = "http://localhost:11434/api"

@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientError, asyncio.TimeoutError),
    max_tries=3,
    max_time=30
)
async def test_ollama_prompt(model_name: str, prompt: str) -> str:
    """
    Send a prompt to the Ollama API and return the response.
    
    Args:
        model_name: Name of the Ollama model
        prompt: The prompt to send
        
    Returns:
        The model's response as a string
    """
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000,  # Equivalent to max_tokens
                }
            }
            
            async with session.post(
                f"{OLLAMA_API_BASE}/generate",
                json=payload,
                timeout=120  # 2-minute timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"Ollama API error: {response.status} - {error_text}")
                    return f"ERROR: Ollama API returned status {response.status}"
                
                result = await response.json()
                return result.get("response", "")
                
    except Exception as e:
        logging.exception(f"Error in Ollama API call: {str(e)}")
        return f"ERROR: {str(e)}"

async def list_ollama_models() -> List[str]:
    """
    Get a list of available Ollama models.
    
    Returns:
        List of model names
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{OLLAMA_API_BASE}/tags") as response:
                if response.status != 200:
                    logging.error(f"Ollama API error while listing models: {response.status}")
                    return []
                
                result = await response.json()
                models = [model["name"] for model in result.get("models", [])]
                return models
                
    except Exception as e:
        logging.exception(f"Error listing Ollama models: {str(e)}")
        return [] 