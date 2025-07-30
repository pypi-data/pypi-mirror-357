from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class ModelHandler(ABC):
    """Base class for all model handlers.
    
    A model handler is responsible for interfacing with a specific model or API
    to generate responses from prompts.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the model handler.
        
        Args:
            verbose: Whether to output verbose logging information
        """
        self.verbose = verbose
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models from this provider.
        
        Returns:
            List of dictionaries containing model information with keys:
            - id: Unique identifier for the model
            - name: Human-readable name of the model
            - provider: Provider name (e.g., "openai", "gemini", etc.)
        """
        pass
    
    @abstractmethod
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate a response from the given prompt using the specified model.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to generate a response for
            **kwargs: Additional parameters for generation (e.g., max_tokens, temperature)
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    async def test_prompt(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """Test a prompt against the model and return detailed information.
        
        This is similar to generate() but includes additional metadata about the generation.
        
        Args:
            model_id: ID of the model to use
            prompt: The prompt to test
            
        Returns:
            Dictionary containing:
            - success: Whether the generation was successful
            - response: The generated text (if successful)
            - error: Error message (if unsuccessful)
            - metadata: Additional metadata about the generation (e.g., tokens used)
        """
        pass 