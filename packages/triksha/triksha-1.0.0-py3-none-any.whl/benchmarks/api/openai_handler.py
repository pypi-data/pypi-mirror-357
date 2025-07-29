import os
from typing import Dict, Any, List
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from ..utils.reporting import detect_refusal
from utils.env_loader import get_api_key

class OpenAIHandler:
    """Handler for OpenAI API interactions using the latest v1.0+ client"""
    # Updated available models list
    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
    
    def __init__(self, model_name: str = None, verbose: bool = False):
        self.verbose = verbose
        self.api_key = get_api_key("openai", verbose=verbose)
        self.model_name = model_name or "gpt-4"  # Default model
        self.provider = "OpenAI"  # Store provider information
        self.model_version = self._get_model_version(self.model_name)
        
        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key, timeout=15.0)
                if self.verbose:
                    print(f"OpenAI API key configured (length: {len(self.api_key)})")
                    print(f"Using OpenAI model: {self.model_name} (Version: {self.model_version})")
            except Exception as e:
                self.client = None
                print(f"\n[ERROR] Failed to initialize OpenAI client: {str(e)}")
        else:
            self.client = None
            print("\n[WARNING] OpenAI API key not found. Please add your API key to the .env file.")
            print(f"Current working directory: {os.getcwd()}")
            print("To add your key, create or edit the .env file in the project root directory.")
            print("Example: OPENAI_API_KEY=sk-your-key-here")
            print("Once added, restart the benchmark process.")
    
    def _get_model_version(self, model_name: str) -> str:
        """Extract version information from model name"""
        # Extract version from model name (gpt-3.5-turbo -> 3.5)
        if "gpt-" in model_name:
            parts = model_name.split('-')
            if len(parts) > 1:
                for part in parts:
                    if '.' in part:
                        return part
        return "unknown"

    @staticmethod
    @retry(
        wait=wait_random_exponential(min=0.5, max=5),
        stop=stop_after_attempt(3)
    )
    async def list_available_models(api_key: str = None) -> List[str]:
        """List available OpenAI models with robust error handling and retries"""
        if not api_key:
            api_key = get_api_key("openai")
            
        if not api_key:
            print("\n[WARNING] No OpenAI API key found. Using default model list.")
            return OpenAIHandler.AVAILABLE_MODELS
            
        try:
            print("Attempting to fetch OpenAI models...")
            client = AsyncOpenAI(api_key=api_key, timeout=10.0)  # Add explicit timeout
            models = await client.models.list()
            
            # Filter for chat models
            chat_models = [
                model.id for model in models.data 
                if model.id.startswith(("gpt-3", "gpt-4"))
            ]
            
            if not chat_models:
                print("\n[WARNING] No chat models found in API response. Using default models.")
                return OpenAIHandler.AVAILABLE_MODELS
                
            print(f"Successfully fetched {len(chat_models)} OpenAI models.")
            return sorted(chat_models)
        except Exception as e:
            print(f"\n[ERROR] Failed to fetch OpenAI models: {str(e)}")
            print("Using default model list instead.")
            return OpenAIHandler.AVAILABLE_MODELS

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Test prompt against OpenAI API"""
        try:
            if not self.api_key or not self.client:
                return {
                    "success": False, 
                    "error": "No API key configured", 
                    "model": self.model_name,
                    "provider": self.provider,
                    "version": self.model_version
                }
                
            # Clean model name if it has a provider prefix
            model_name = self.model_name
            if ":" in model_name:
                model_name = model_name.split(":", 1)[1]
                
            # Validate model name
            if not model_name.startswith("gpt-"):
                return {
                    "success": False,
                    "error": f"Invalid model name format: {model_name}. Should start with 'gpt-'",
                    "model": model_name,
                    "provider": self.provider,
                    "version": self.model_version
                }

            # Using correct async API with specified model
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            return {
                "success": not detect_refusal(content),
                "response": content,
                "model": model_name,
                "provider": self.provider,
                "version": self.model_version
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "model": self.model_name,
                "provider": self.provider,
                "version": self.model_version
            }
