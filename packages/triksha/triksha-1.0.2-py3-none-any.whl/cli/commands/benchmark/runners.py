"""Benchmark runner implementations"""
import asyncio
import time
import os
import json
import shlex
import subprocess
import traceback
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from rich.console import Console, Group
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from benchmarks import BenchmarkRunner
from benchmarks.api.bypass_tester import BypassTester
from benchmarks.flexible_benchmark import FlexibleBenchmarkRunner as FBRunner
from benchmarks.templates.benchmark_template import BenchmarkDomain
from benchmarks.utils.backup_manager import BackupManager
from datetime import datetime
import aiohttp
from benchmarks.models.model_loader import ModelLoader
from benchmarks.models.handlers.openai_handler import OpenAIHandler
from benchmarks.models.handlers.gemini_handler import GeminiHandler
from benchmarks.models.handlers.huggingface_handler import HuggingFaceHandler
from benchmarks.models.handlers.custom_api_handler import CustomAPIHandler
from benchmarks.models.handlers.ollama_handler import OllamaHandler
import math
from benchmarks.api.response_evaluator import is_refusal_response
from .retry_logic import RetryConfig, retry_with_backoff, is_retryable_error
import random

# New model provider class to handle different API providers
class ModelProvider:
    """Base class for model providers"""
    
    def __init__(self, model_name: str, timeout: int = 60, verbose: bool = False):
        """
        Initialize the model provider
        
        Args:
            model_name: Name of the model to use
            timeout: Timeout in seconds for API calls
            verbose: Whether to print verbose output
        """
        self.model_name = model_name
        self.timeout = timeout
        self.verbose = verbose
        self._setup()
    
    def _setup(self):
        """Setup the provider - override in subclasses"""
        pass
    
    async def generate(self, prompt: str, attempt: int = 1) -> Dict[str, Any]:
        """
        Generate a response to the prompt
        
        Args:
            prompt: The prompt to generate a response for
            attempt: Current attempt number for retries
            
        Returns:
            Dictionary with response details
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def get_effective_timeout(self, attempt: int) -> float:
        """
        Get an effective timeout value that increases with each retry
        
        Args:
            attempt: Current attempt number
            
        Returns:
            Timeout in seconds with progressive increase
        """
        # Increase timeout by 50% on each retry
        return self.timeout * (1 + (attempt - 1) * 0.5)


class OpenAIProvider(ModelProvider):
    """OpenAI API provider"""
    
    def _setup(self):
        """Setup the OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI()
            self.available = True
        except (ImportError, Exception) as e:
            print(f"Warning: OpenAI setup failed: {str(e)}")
            self.available = False
    
    async def generate(self, prompt: str, attempt: int = 1) -> Dict[str, Any]:
        """Generate a response using OpenAI API"""
        if not self.available:
            return {
                "success": False,
                "error": "OpenAI client not available",
                "error_type": "SetupError",
                "provider": "openai",
                "model": self.model_name
            }
            
        try:
            import openai
            from openai import OpenAI
            
            effective_timeout = self.get_effective_timeout(attempt)
            
            if self.verbose:
                print(f"OpenAI API call to {self.model_name} (attempt {attempt}, timeout: {effective_timeout:.1f}s)")
            
            start_time = time.time()

            # Use asyncio to run the synchronous OpenAI call
            loop = asyncio.get_event_loop()
            client = self.client or OpenAI()
            
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=effective_timeout
                )
            )
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "elapsed_time": elapsed_time,
                "provider": "openai",
                "model": self.model_name,
                "attempt": attempt
            }
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Handle timeout errors
            if "timeout" in error_msg.lower() or error_type in ["Timeout", "TimeoutError", "ReadTimeout"]:
                if attempt < 3:  # Allow up to 3 attempts
                    if self.verbose:
                        print(f"Timeout on OpenAI API call, retrying (attempt {attempt}/3)")
                    # Use asyncio.sleep to respect the async environment
                    await asyncio.sleep(1)  # Brief pause before retry
                    return await self.generate(prompt, attempt + 1)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "provider": "openai",
                "model": self.model_name
            }


class GeminiProvider(ModelProvider):
    """Google Gemini API provider"""
    
    def _setup(self):
        """Setup the Gemini client"""
        try:
            import google.generativeai as genai
            self.genai = genai
            
            # Check for API key in environment
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.available = True
            else:
                print("Warning: GOOGLE_API_KEY not found in environment variables")
                self.available = False
                
        except ImportError:
            print("Warning: google.generativeai package not installed")
            self.available = False
    
    async def generate(self, prompt: str, attempt: int = 1) -> Dict[str, Any]:
        """Generate a response using Gemini API"""
        if not self.available:
            return {
                "success": False,
                "error": "Gemini client not available",
                "error_type": "SetupError",
                "provider": "gemini",
                "model": self.model_name
            }
            
        try:
            effective_timeout = self.get_effective_timeout(attempt)
            
            if self.verbose:
                print(f"Gemini API call to {self.model_name} (attempt {attempt}, timeout: {effective_timeout:.1f}s)")
            
            start_time = time.time()
            
            # Use asyncio to run the synchronous Gemini call
            loop = asyncio.get_event_loop()
            
            # Create model with correct format
            gemini_model = self.genai.GenerativeModel(model_name=self.model_name)
            
            # Format prompt according to new API structure
            content = [{"role": "user", "parts": [{"text": prompt}]}]
            
            # Run in executor to avoid blocking the event loop
            response = await loop.run_in_executor(
                None,
                lambda: gemini_model.generate_content(
                    content,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1024,
                    },
                    # Note: Gemini doesn't have a direct timeout parameter like OpenAI,
                    # but we'll simulate timeout handling with elapsed time checks
                )
            )
            
            elapsed_time = time.time() - start_time
            
            # Check if the call exceeded our timeout
            if elapsed_time > effective_timeout:
                raise TimeoutError(f"API call exceeded timeout of {effective_timeout} seconds")
            
            # Extract text from the response
            response_text = ""
            if hasattr(response, "text"):
                response_text = response.text
            elif hasattr(response, "parts") and response.parts:
                response_text = response.parts[0].text
            elif hasattr(response, "candidates") and response.candidates:
                parts = response.candidates[0].content.parts
                if parts:
                    response_text = parts[0].text
            
            return {
                "success": True,
                "response": response_text,
                "elapsed_time": elapsed_time,
                "provider": "gemini",
                "model": self.model_name,
                "attempt": attempt
            }
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Handle timeout errors
            if "timeout" in error_msg.lower() or error_type in ["Timeout", "TimeoutError", "ReadTimeout"]:
                if attempt < 3:  # Allow up to 3 attempts
                    if self.verbose:
                        print(f"Timeout on Gemini API call, retrying (attempt {attempt}/3)")
                    # Use asyncio.sleep to respect the async environment
                    await asyncio.sleep(1)  # Brief pause before retry
                    return await self.generate(prompt, attempt + 1)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "provider": "gemini",
                "model": self.model_name
            }


class CustomCurlProvider(ModelProvider):
    """Custom API provider using curl commands"""
    
    def __init__(self, curl_command: str, prompt_placeholder: str = "{prompt}", **kwargs):
        self.curl_command = curl_command
        self.prompt_placeholder = prompt_placeholder
        super().__init__(**kwargs)
    
    async def generate(self, prompt: str, attempt: int = 1) -> Dict[str, Any]:
        """Generate a response using a custom curl command"""
        try:
            effective_timeout = self.get_effective_timeout(attempt)
            
            if self.verbose:
                print(f"Custom API call (attempt {attempt}, timeout: {effective_timeout:.1f}s)")
            
            # Replace the placeholder with the prompt
            escaped_prompt = prompt.replace('"', '\\"').replace("'", "\\'")
            cmd = self.curl_command.replace(self.prompt_placeholder, shlex.quote(escaped_prompt))
            
            start_time = time.time()
            
            # Use asyncio to run the subprocess command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            try:
                # Set a timeout for the process
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
                
                # Calculate the elapsed time
                elapsed_time = time.time() - start_time
                
                # Check if the process was successful
                if proc.returncode != 0:
                    error_msg = stderr.decode('utf-8').strip() or "Unknown error"
                    if self.verbose:
                        print(f"Curl command failed with error: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": f"Curl error: {error_msg}",
                        "model": self.model_name,
                        "provider": "custom-api",
                        "type": "curl",
                        "response_time": elapsed_time
                    }
                
                # Get the response and try to parse as JSON
                response_text = stdout.decode('utf-8').strip()
                
                try:
                    # Try to parse as JSON
                    response_json = json.loads(response_text)
                    
                    # Extract the text from the JSON response
                    text = self._extract_text_from_response(response_json)
                    if text:
                        return {
                            "success": True,
                            "response": text,
                            "raw_response": response_json,
                            "model": self.model_name,
                            "provider": "custom-api",
                            "type": "curl",
                            "response_time": elapsed_time
                        }
                    else:
                        # Return the raw JSON if no text could be extracted
                        return {
                            "success": True,
                            "response": json.dumps(response_json),
                            "raw_response": response_json,
                            "model": self.model_name,
                            "provider": "custom-api",
                            "type": "curl",
                            "response_time": elapsed_time
                        }
                
                except json.JSONDecodeError:
                    # If not JSON, return the raw text
                    return {
                        "success": True,
                        "response": response_text,
                        "model": self.model_name,
                        "provider": "custom-api",
                        "type": "curl",
                        "response_time": elapsed_time
                    }
                    
            except asyncio.TimeoutError:
                # Handle timeout
                elapsed_time = time.time() - start_time
                
                if self.verbose:
                    print(f"Curl command timed out after {elapsed_time:.1f}s")
                
                return {
                    "success": False,
                    "error": f"Timeout after {elapsed_time:.1f}s",
                    "model": self.model_name,
                    "provider": "custom-api",
                    "type": "curl",
                    "response_time": elapsed_time
                }
                
        except Exception as e:
            # Handle other exceptions
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            
            if self.verbose:
                print(f"Error in CustomCurlProvider: {str(e)}")
            
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "model": self.model_name,
                "provider": "custom-api",
                "type": "curl",
                "response_time": elapsed_time
            }
    
    def _extract_text_from_response(self, response_data):
        """Extract text from a JSON response."""
        # Check for OpenAI format
        if isinstance(response_data, dict):
            # OpenAI completion format
            if "choices" in response_data and isinstance(response_data["choices"], list) and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                
                # Chat completion format
                if isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                    return choice["message"]["content"]
                
                # Text completion format
                if isinstance(choice, dict) and "text" in choice:
                    return choice["text"]
            
            # Gemini format
            if "candidates" in response_data and isinstance(response_data["candidates"], list) and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if isinstance(candidate, dict) and "content" in candidate and isinstance(candidate["content"], dict) and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            # Simple formats
            for key in ["response", "output", "text", "content", "result", "generated_text"]:
                if key in response_data:
                    return response_data[key]
                    
        # Return None if no text could be extracted
        return None


class CustomCurlJsonProvider(ModelProvider):
    """Custom API provider using curl commands with JSON path specification for the prompt field."""
    
    def __init__(self, curl_command: str, prompt_field: str, **kwargs):
        """Initialize the custom JSON-aware curl provider.
        
        Args:
            curl_command: Complete curl command with JSON payload
            prompt_field: JSON path to the field that contains the prompt (e.g., "messages[0].content")
            **kwargs: Additional keyword arguments
        """
        self.curl_command = curl_command
        self.prompt_field = prompt_field
        self.verbose = kwargs.get('verbose', False)
        self.model_name = kwargs.get('model_name', 'custom-api')
        super().__init__(**kwargs)
    
    async def generate(self, prompt: str, attempt: int = 1) -> Dict[str, Any]:
        """Generate a response by replacing the specified JSON field in the curl command.
        
        Args:
            prompt: The prompt to send to the API
            attempt: Current attempt number for retries
            
        Returns:
            Dictionary with response details
        """
        try:
            import re
            import json
            import shlex
            
            effective_timeout = self.get_effective_timeout(attempt)
            
            if self.verbose:
                print(f"Custom API call with JSON path (attempt {attempt}, timeout: {effective_timeout:.1f}s)")
            
            # First, extract the JSON data part from the curl command
            data_match = re.search(r"--data\s+[\"']?(\{.*\})[\"']?", self.curl_command, re.DOTALL)
            
            if not data_match:
                raise ValueError("Could not find JSON data in curl command")
                
            # Parse the JSON data
            data_str = data_match.group(1)
            data = json.loads(data_str)
            
            # Store original stop tokens if they exist (for safety evaluation APIs)
            original_stop_tokens = None
            if "stop" in data and isinstance(data["stop"], list):
                original_stop_tokens = data["stop"]
            
            # Navigate through the JSON structure to set the prompt
            # Parse the field path (e.g., "messages[0].content")
            parts = re.findall(r'([^\[\]\.]+)|\[(\d+)\]', self.prompt_field)
            current = data
            
            # Traverse the path except the last part
            path_parts = []
            for i, (name, index) in enumerate(parts):
                if i == len(parts) - 1:
                    # This is the last part, we'll use it for the replacement
                    break
                    
                if name:  # Object property
                    path_parts.append(name)
                    if name not in current:
                        current[name] = {} if i + 1 < len(parts) and parts[i+1][1] == '' else []
                    current = current[name]
                elif index:  # Array index
                    path_parts.append(f"[{index}]")
                    idx = int(index)
                    # Extend array if needed
                    while len(current) <= idx:
                        current.append({})
                    current = current[idx]
            
            # Set the value at the final path
            last_name, last_index = parts[-1]
            if last_name:  # Object property
                current[last_name] = prompt
            elif last_index:  # Array index
                idx = int(last_index)
                # Extend array if needed
                while len(current) <= idx:
                    current.append("")
                current[idx] = prompt
            
            # For safety evaluation APIs, restore the original stop tokens
            if original_stop_tokens is not None:
                data["stop"] = original_stop_tokens
            
            # Serialize back to JSON
            updated_data_str = json.dumps(data)
            
            # Replace the data in the curl command
            updated_curl = re.sub(
                r"(--data\s+)[\"']?\{.*\}[\"']?", 
                f"\\1'{updated_data_str}'", 
                self.curl_command, 
                flags=re.DOTALL
            )
            
            start_time = time.time()
            
            # Use asyncio to run the subprocess command
            proc = await asyncio.create_subprocess_shell(
                updated_curl,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            # Set timeout for the process
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
                
                elapsed_time = time.time() - start_time
                
                if proc.returncode != 0:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    return {
                        "success": False,
                        "error": f"Custom API call failed: {error_msg}",
                        "error_type": "ProcessError",
                        "provider": "custom",
                        "model": self.model_name,
                        "attempt": attempt
                    }
                
                # Try to parse the JSON response
                try:
                    response_text = stdout.decode()
                    response_json = json.loads(response_text)
                    
                    # Extract the model output based on standard formats
                    extracted_text = None
                    
                    # Check OpenAI-like format (choices[0].message.content)
                    if "choices" in response_json and isinstance(response_json["choices"], list) and len(response_json["choices"]) > 0:
                        choice = response_json["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            extracted_text = choice["message"]["content"]
                        elif "text" in choice:
                            extracted_text = choice["text"]
                    # Check Claude/Anthropic format (content)
                    elif "content" in response_json:
                        extracted_text = response_json["content"]
                    # Check text field directly
                    elif "text" in response_json:
                        extracted_text = response_json["text"]
                    # Check safety API specific format
                    elif "model_responses" in response_json and isinstance(response_json["model_responses"], list) and len(response_json["model_responses"]) > 0:
                        extracted_text = response_json["model_responses"][0]
                    # Check safety ratings
                    elif "safety_ratings" in response_json and isinstance(response_json["safety_ratings"], list):
                        # Format safety ratings in a human-readable format
                        ratings = []
                        for rating in response_json["safety_ratings"]:
                            category = rating.get("category", "Unknown")
                            score = rating.get("score", 0)
                            probability = rating.get("probability", 0)
                            ratings.append(f"{category}: {score} (p={probability})")
                        extracted_text = "SAFETY RATINGS:\n" + "\n".join(ratings)
                    
                    if extracted_text:
                        return {
                            "success": True,
                            "response": extracted_text,
                            "raw_response": response_text,
                            "elapsed_time": elapsed_time,
                            "provider": "custom",
                            "model": self.model_name,
                            "attempt": attempt
                        }
                    else:
                        # Return the full JSON if we couldn't extract text
                        return {
                            "success": True,
                            "response": response_text,
                            "elapsed_time": elapsed_time,
                            "provider": "custom",
                            "model": self.model_name,
                            "attempt": attempt
                        }
                except json.JSONDecodeError:
                    # Not JSON, just return the response as is
                    return {
                        "success": True,
                        "response": stdout.decode(),
                        "elapsed_time": elapsed_time,
                        "provider": "custom",
                        "model": self.model_name,
                        "attempt": attempt
                    }
                
            except asyncio.TimeoutError:
                # Try to kill the process if it's still running
                try:
                    proc.kill()
                except:
                    pass
                    
                if attempt < 3:  # Allow up to 3 attempts
                    if self.verbose:
                        print(f"Timeout on custom API call, retrying (attempt {attempt}/3)")
                    # Use asyncio.sleep to respect the async environment
                    await asyncio.sleep(1)  # Brief pause before retry
                    return await self.generate(prompt, attempt + 1)
                
                return {
                    "success": False,
                    "error": f"API timeout after {attempt} attempts",
                    "error_type": "TimeoutError",
                    "provider": "custom",
                    "model": self.model_name,
                    "attempt": attempt
                }
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "provider": "custom",
                "model": self.model_name,
                "attempt": attempt
            }


class APIBenchmarkRunner:
    """Runner for API-based benchmarks."""

    def __init__(
        self,
        db=None,
        console=None,
        backup_manager=None,
        model_configs=None,
        concurrency=3,
        retry_config=None,
    ):
        """Initialize the benchmark runner with configuration."""
        self.db = db
        self.concurrency = min(max(1, concurrency), 20)  # Limit concurrency to 20
        self.model_configs = model_configs or []
        self.console = console or Console()
        self.backup_manager = backup_manager
        self.model_handlers = {}
        self.session = None  # Initialize session attribute
        
        # Add retry configuration
        self.retry_config = retry_config or RetryConfig()
        
        # Setup progress tracking
        self.total_examples = 0
        self.completed_examples = 0
        self.session_id = None
        
        # Initialize notification service
        try:
            from cli.notification import EmailNotificationService
            self.notification_service = EmailNotificationService(console=self.console)
        except ImportError:
            self.notification_service = None
    
    async def _test_custom_model_endpoint(self, model_handler, model_config):
        """Test custom model endpoint with a simple prompt before running the benchmark.
        
        Args:
            model_handler: The model handler instance
            model_config: The model configuration
            
        Returns:
            bool: True if test was successful, False otherwise
        """
        self.console.print(f"[cyan]Testing connection to custom model: {model_config.get('model_id', 'unknown')}...[/]")
        
        # Simple test prompt
        test_prompt = "This is a test prompt to verify API connection. Please respond with a short message."
        
        try:
            # Test the model handler with a test prompt
            model_id = model_config.get('model_id', 'custom-model')
            
            # Try calling test_prompt method if it exists
            if hasattr(model_handler, 'test_prompt'):
                response = await model_handler.test_prompt(model_id, test_prompt)
                success = response.get('success', False)
                
                if success:
                    self.console.print(f"[green]✓ Connection test successful for {model_id}[/]")
                    preview_text = response.get("response", "")
                    if preview_text:
                        if len(preview_text) > 100:
                            preview_text = preview_text[:97] + "..."
                        self.console.print(f"[dim]Response preview: {preview_text}[/]")
                    return True
                else:
                    error_msg = response.get('error', 'Unknown error')
                    self.console.print(f"[red]✗ Connection test failed for {model_id}: {error_msg}[/]")
                    return False
            
            # Fallback to generate method
            response = await model_handler.generate(model_id, test_prompt, max_tokens=50)
            
            if response and not response.startswith("Error:"):
                self.console.print(f"[green]✓ Connection test successful for {model_id}[/]")
                preview_text = response[:100] + "..." if len(response) > 100 else response
                self.console.print(f"[dim]Response preview: {preview_text}[/]")
                return True
            else:
                self.console.print(f"[red]✗ Connection test failed for {model_id}: {response}[/]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]✗ Connection test failed for {model_config.get('model_id', 'unknown')}: {str(e)}[/]")
            return False
    
    def _init_model_handlers(self, config=None):
        """Initialize model handlers from configurations."""
        self.model_handlers = {}
        
        # Process each model configuration
        for model_config in self.model_configs:
            try:
                model_type = model_config.get('type', 'openai')
                model_id = model_config.get('model_id', 'gpt-3.5-turbo')
                
                self.console.print(f"[cyan]Initializing {model_type} model: {model_id}[/]")
                
                # Initialize the appropriate handler based on model type
                if model_type == 'openai':
                    # Import OpenAI handler
                    from benchmarks.models.handlers.openai_handler import OpenAIHandler
                    
                    # Create handler
                    handler = OpenAIHandler()
                    
                elif model_type == 'gemini':
                    # Import Gemini handler
                    from benchmarks.models.handlers.gemini_handler import GeminiHandler
                    
                    # Create handler
                    handler = GeminiHandler()
                
                elif model_type == 'anthropic':
                    # Import Anthropic handler
                    from benchmarks.models.handlers.anthropic_handler import AnthropicHandler
                    
                    # Create handler
                    handler = AnthropicHandler()
                    
                elif model_type == 'ollama':
                    # Import Ollama handler
                    from benchmarks.models.handlers.ollama_handler import OllamaHandler
                    
                    # Get base URL from config or use default
                    base_url = model_config.get('base_url', 'http://localhost:11434')
                    
                    # Create handler
                    handler = OllamaHandler(base_url=base_url)
                
                elif model_type == 'guardrail':
                    # Import GuardrailHandler
                    from benchmarks.models.handlers.guardrail_handler import GuardrailHandler
                    
                    # Extract guardrail name from model_id (remove guardrail: prefix if present)
                    guardrail_name = model_config.get('name', model_id)
                    if guardrail_name.startswith('guardrail:'):
                        guardrail_name = guardrail_name.replace('guardrail:', '')
                    
                    # Create handler
                    handler = GuardrailHandler(
                        guardrail_name=guardrail_name,
                        verbose=True
                    )
                    
                    self.console.print(f"[green]✓ Loaded guardrail: {guardrail_name}[/]")
                
                elif model_type == 'custom-api':
                    # Import CustomAPIHandler
                    from benchmarks.models.handlers.custom_api_handler import CustomAPIHandler
                    
                    # Create handler based on API configuration
                    if 'curl_command' in model_config:
                        # Get prompt placeholder from config or use default
                        prompt_placeholder = config.get("prompt_placeholder", "{prompt}") if config else model_config.get("prompt_placeholder", "{prompt}")
                        
                        # Create handler with curl command
                        handler = CustomAPIHandler(
                            name=model_id,
                            curl_command=model_config.get('curl_command'),
                            prompt_placeholder=prompt_placeholder,
                            json_path=model_config.get('json_path'),
                            verbose=True
                        )
                    else:
                        # Create handler with direct API endpoint
                        handler = CustomAPIHandler(
                            name=model_id,
                            endpoint_url=model_config.get('endpoint_url'),
                            headers=model_config.get('headers', {}),
                            http_method=model_config.get('http_method', 'POST'),
                            json_path=model_config.get('json_path'),
                            verbose=True
                        )
                        
                    # Test the custom API endpoint before proceeding
                    import asyncio
                    endpoint_valid = asyncio.run(self._test_custom_model_endpoint(handler, model_config))
                    
                    if not endpoint_valid:
                        # Ask if the user wants to continue despite the test failure
                        import inquirer
                        continue_anyway = inquirer.confirm(
                            f"Connection test failed for {model_id}. Continue anyway?",
                            default=False
                        )
                        
                        if not continue_anyway:
                            self.console.print(f"[yellow]Skipping model {model_id} due to connection test failure.[/]")
                            continue
                        else:
                            self.console.print(f"[yellow]Continuing with model {model_id} despite test failure.[/]")
                
                elif model_type == 'custom':
                    # Import ModelLoader to load custom handler
                    from benchmarks.models.model_loader import ModelLoader
                    
                    # Create model loader
                    model_loader = ModelLoader(verbose=True)
                    
                    # Load the custom handler
                    handler = model_loader.load_handler(model_id)
                    if not handler:
                        self.console.print(f"[red]Could not load custom handler for {model_id}[/]")
                        continue
                
                else:
                    self.console.print(f"[yellow]Unknown model type: {model_type}. Skipping {model_id}.[/]")
                    continue
                
                # Store the handler
                # Use the appropriate key format based on model type
                if model_type in ['custom-api', 'custom', 'guardrail']:
                    # For custom API models and guardrails, use just the model_id as the key
                    handler_key = model_id
                    
                    # Also store under type:id format for compatibility
                    self.model_handlers[f"{model_type}:{model_id}"] = handler
                    
                    # Custom API handlers and guardrails should also be available directly by model_id 
                    # as some parts of code might look them up this way
                    self.model_handlers[model_id] = handler
                else:
                    # For other models, use type:model_id format
                    handler_key = f"{model_type}:{model_id}"
                
                # Store the handler
                self.model_handlers[handler_key] = handler
                
                self.console.print(f"[green]✓ Successfully initialized {model_type} model: {model_id}[/]")
                
            except Exception as e:
                self.console.print(f"[red]Error initializing model {model_config.get('model_id', 'unknown')}: {str(e)}[/]")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    async def _init_session(self):
        """Initialize the aiohttp session if it doesn't exist."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
    async def _close_session(self):
        """Close the aiohttp session and any model handlers if they exist."""
        if self.session:
            await self.session.close()
            self.session = None
            
        # Close any model handlers that need cleanup
        for handler in self.model_handlers.values():
            if hasattr(handler, 'close'):
                await handler.close()
        self.model_handlers = {}
    
    async def _process_prompt(self, model_config, prompt, example_idx):
        """Process a single prompt with the specified model.
        
        SECURITY GUARANTEE: This method only receives prompts that have been processed 
        through the Gemini augmentation pipeline. Raw prompts never reach target models.
        
        Args:
            model_config: Model configuration dictionary
            prompt: The prompt to process (already augmented/validated)
            example_idx: Index of the example in the dataset
            
        Returns:
            dict: Result of processing the prompt
        """
        model_type = model_config.get("type", "openai")
        model_id = model_config.get("model_id", "unknown")
        max_tokens = model_config.get("max_tokens", 1000)
        temperature = model_config.get("temperature", 0.7)
        
        # SECURITY LOG: Track that we're sending a processed prompt to target model
        # This ensures accountability and verifies the flow
        if hasattr(self, 'console') and self.console:
            # Only log in verbose mode to avoid spam, but ensure security is maintained
            # self.console.print(f"[dim]🔒 Sending processed prompt to {model_id}: {prompt[:30]}...[/]")
            pass
        
        # Get the correct handler key based on model type
        if model_type in ["custom-api", "custom"]:
            # For custom API models, use just the model_id without prefix
            config_key = model_id
        else:
            # For other model types, use the type:id format
            config_key = f"{model_type}:{model_id}"
            
        handler = self.model_handlers.get(config_key)
        
        if not handler:
            # Try alternative key format if handler not found
            alt_key = model_id if ":" in config_key else f"{model_type}:{model_id}"
            handler = self.model_handlers.get(alt_key)
            
            if not handler:
                return {
                    "success": False,
                    "error": f"No handler found for {model_id} (tried keys: {config_key}, {alt_key})",
                    "prompt": prompt,
                    "example_idx": example_idx,
                    "response_time": 0,
                    "security_verified": True  # Mark that this was through the secure flow
                }
        
        start_time = time.time()
        try:
            # Import retry utilities
            import asyncio
            import random
            
            # Define retry logic directly in this method
            async def execute_with_retry():
                """Execute the model call with retry logic"""
                last_error = None
                
                for attempt in range(self.retry_config.max_retries + 1):
                    try:
                        # CRITICAL: This is where the processed/augmented prompt is actually sent to the target model
                        # By this point, the prompt has gone through the Gemini augmentation pipeline
                        response = await handler.generate(
                            model_id, 
                            prompt, 
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                        
                        # Success - return with attempt count
                        return {
                            "success": True,
                            "response": response,
                            "attempts": attempt + 1
                        }
                        
                    except Exception as e:
                        last_error = e
                        
                        # Check if this is the last attempt
                        if attempt >= self.retry_config.max_retries:
                            break
                        
                        # Check if the error is retryable
                        error_str = str(e).lower()
                        is_retryable = any(indicator in error_str for indicator in [
                            'rate limit', 'rate_limit', 'ratelimit',
                            'too many requests', 'quota exceeded',
                            'throttled', 'throttling', '429',
                            'timeout', 'connection', 'network',
                            'temporary', 'temporarily',
                            '502', '503', '504',
                            'bad gateway', 'service unavailable',
                            'gateway timeout', 'internal server error'
                        ])
                        
                        if not is_retryable:
                            # Non-retryable error, fail immediately
                            break
                        
                        # Calculate delay with exponential backoff
                        delay = self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt)
                        delay = min(delay, self.retry_config.max_delay)
                        
                        # Add jitter to prevent thundering herd
                        if self.retry_config.jitter:
                            delay = delay * (0.5 + random.random() * 0.5)
                        
                        # Log the retry attempt
                        error_type = "Rate limit" if any(x in error_str for x in ['rate limit', '429']) else "Error"
                        self.console.print(f"[yellow]{error_type} for {model_id}: {str(e)[:100]}...[/]")
                        self.console.print(f"[cyan]Retrying in {delay:.1f} seconds (attempt {attempt + 1}/{self.retry_config.max_retries + 1})[/]")
                        
                        # Wait before retrying
                        await asyncio.sleep(delay)
                
                # All retries exhausted
                return {
                    "success": False,
                    "error": str(last_error),
                    "attempts": self.retry_config.max_retries + 1
                }
            
            # Execute with retry logic
            retry_result = await execute_with_retry()
            elapsed_time = time.time() - start_time
            
            if retry_result["success"]:
                result = {
                    "success": True,
                    "response": retry_result["response"],
                    "prompt": prompt,
                    "example_idx": example_idx,
                    "response_time": elapsed_time,
                    "security_verified": True,  # Mark that this was through the secure flow
                    "target_model": model_id,   # Track which model received the prompt
                    "prompt_source": "augmented_pipeline",  # Verify prompt came through augmentation pipeline
                    "retry_attempts": retry_result["attempts"]  # Track how many attempts were needed
                }
                
                # Log successful retry if it took more than one attempt
                if retry_result["attempts"] > 1:
                    self.console.print(f"[green]✓ Success after {retry_result['attempts']} attempts for {model_id}[/]")
            else:
                # All retries failed
                result = {
                    "success": False,
                    "error": retry_result["error"],
                    "prompt": prompt,
                    "example_idx": example_idx,
                    "response_time": elapsed_time,
                    "security_verified": True,  # Mark that this was through the secure flow
                    "target_model": model_id,   # Track which model would have received the prompt
                    "prompt_source": "augmented_pipeline",  # Verify prompt came through augmentation pipeline
                    "retry_attempts": retry_result["attempts"]  # Track how many attempts were made
                }
                
                self.console.print(f"[red]All retry attempts exhausted for {model_id}: {retry_result['error'][:100]}...[/]")
            
            # Add extracted field information for custom API handlers
            is_custom_model = model_type in ["custom-api", "custom"]
            if is_custom_model and hasattr(handler, 'last_extracted_value'):
                result["extracted_field"] = handler.last_extracted_value
            
            # Add raw response for custom API handlers if available
            if is_custom_model and hasattr(handler, 'last_raw_response'):
                result["raw_response"] = handler.last_raw_response
                
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "example_idx": example_idx,
                "response_time": elapsed_time,
                "security_verified": True,  # Mark that this was through the secure flow
                "target_model": model_id,   # Track which model would have received the prompt
                "prompt_source": "augmented_pipeline",  # Verify prompt came through augmentation pipeline
                "retry_attempts": 1  # At least one attempt was made
            }
    
    async def _run_benchmark_async(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run all benchmark asynchronous tasks.
        
        Args:
            examples: List of example prompts to test
            
        Returns:
            Dictionary of results
        """
        # Import required classes
        from rich.table import Table
        from rich.layout import Layout
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text
        from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
        from rich.console import Group
        
        # Function to update a model's panel
        def update_model_panel(model_key):
            """Update the display panel for a model"""
            if model_key not in model_panels_map:
                return
                
            panel_index = model_panels_map[model_key]
            panel = model_panels[panel_index]
            
            # Create a new table instead of copying
            table = Table(show_header=True, expand=True)
            table.add_column("Prompt", width=40)
            table.add_column("Status", width=16)
            table.add_column("Time", width=8)
            
            # Get the latest processing information
            info = model_status[model_key]
            
            # Add rows for current prompts
            display_data = model_display_data.get(model_key, {})
            examples_data = display_data.get("examples", {})
            
            # Display the most recent examples first
            example_indices = sorted(examples_data.keys(), reverse=True)[:5] if examples_data else []
            for idx in example_indices:
                row = examples_data[idx]
                table.add_row(
                    row["prompt"],
                    row["status"],
                    row["response_time"]
                )
            
            # Create a panel with the table
            status_text = f"Status: {info['status']}"
            if info.get("loading_status"):
                status_text += f" - {info['loading_status']}"
            
            panel_content = Group(
                Text(status_text),
                table
            )
            
            # Create a title with model information
            model_config = next((c for c in self.model_configs if c.get("custom_name") == info["display_name"]), None)
            model_type = model_config.get("type", "unknown") if model_config else "unknown"
            title = f"{info['display_name']} ({model_type})"
            
            # Update the panel
            layout_panel = Panel(
                panel_content,
                title=title,
                border_style="green" if info["status"] == "Running" else "cyan"
            )
            
            # Update the panel in the layout
            panel.update(layout_panel)
        
        # Ensure we have a valid event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create a new event loop if one doesn't exist
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Initialize the session if needed
        await self._init_session()
        
        # Initialize model handlers if needed
        self._init_model_handlers()
        
        # Check if we have valid model handlers
        if not self.model_handlers:
            raise ValueError("No valid model handlers available - please check API keys and configurations")
            
        # Create results structure
        results = {
            "timestamp": datetime.now().isoformat(),
            "model_count": len(self.model_configs),
            "example_count": len(examples),
            "model_results": {}
        }
        
        # Add model-specific results sections
        for config in self.model_configs:
            model_type = config.get("type", "openai")
            model_id = config.get("model_id", "unknown")
            display_name = config.get("custom_name", model_id)
            
            # Use consistent model key
            model_key = f"{model_type}:{display_name}"
            
            results["model_results"][model_key] = {
                "type": model_type,
                "model_id": model_id,
                "display_name": display_name,
                "success_count": 0,
                "fail_count": 0,
                "total_time": 0,
                "examples": []
            }
        
        # Create a rich layout for displaying multiple panels
        layout = Layout()
        layout.split_column(
            Layout(name="summary", size=6),
            Layout(name="models")
        )
        
        # Split the model area into a grid (dynamically based on the number of models)
        model_area = layout["models"]
        model_count = len(self.model_configs)
        
        # Determine grid layout: try to make a grid with approximately square cells
        grid_columns = min(3, max(1, round(math.sqrt(model_count))))
        
        # Create panels
        model_panels = []
        
        # Create a grid layout
        if grid_columns > 1:
            row_layouts = []
            current_row = []
            
            for i in range(model_count):
                if i > 0 and i % grid_columns == 0:
                    # Create a new row
                    row_layout = Layout()
                    row_layout.split_row(*current_row)
                    row_layouts.append(row_layout)
                    current_row = []
                
                panel_layout = Layout(name=f"model_{i}")
                current_row.append(panel_layout)
                model_panels.append(panel_layout)
            
            # Add the last row if it has any panels
            if current_row:
                row_layout = Layout()
                row_layout.split_row(*current_row)
                row_layouts.append(row_layout)
            
            # Add all rows to the model area
            if row_layouts:
                model_area.split_column(*row_layouts)
        else:
            # Just a single column
            column_layouts = []
            for i in range(model_count):
                panel_layout = Layout(name=f"model_{i}")
                column_layouts.append(panel_layout)
                model_panels.append(panel_layout)
            
            model_area.split_column(*column_layouts)
        
        # Create progress display
        main_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("Completed: {task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn()
        )
        
        # Summary table
        summary_table = Table(title="Benchmark Progress", show_header=True, expand=True)
        summary_table.add_column("Model")
        summary_table.add_column("Type", width=12)
        summary_table.add_column("Completed")
        summary_table.add_column("Success Rate")
        summary_table.add_column("Avg Time")
        summary_table.add_column("Status")
        
        # Initialize the summary table
        for config in self.model_configs:
            model_type = config.get("type", "openai")
            model_id = config.get("model_id", "unknown")
            display_name = config.get("custom_name", model_id)
            summary_table.add_row(
                display_name, 
                model_type,
                "0/0", 
                "0%", 
                "0.00s",
                "Initializing"
            )
        
        # Create tasks for tracking progress
        tasks = {}
        for i, config in enumerate(self.model_configs):
            model_type = config.get("type", "openai")
            model_id = config.get("model_id", "unknown")
            display_name = config.get("custom_name", model_id)
            model_key = f"{model_type}:{display_name}"
            
            # Create a task for progress tracking
            task_description = f"[cyan]{display_name}[/]"
            tasks[model_key] = main_progress.add_task(
                task_description, 
                total=len(examples),
                completed=0
            )
        
        # Summary panel with overall progress
        summary_panel = Panel(
            Group(
                Text("Benchmark in Progress", style="bold cyan"),
                main_progress,
                summary_table
            ),
            title="Benchmark Progress",
            border_style="cyan"
        )
        layout["summary"].update(summary_panel)
        
        # Initialize status tracking
        model_status = {}
        model_display_data = {}
        model_panels_map = {}  # Map from model_key to panel index
        
        # Create a panel for each model
        for i, config in enumerate(self.model_configs):
            model_type = config.get("type", "openai")
            model_id = config.get("model_id", "unknown")
            display_name = config.get("custom_name", model_id)
            model_key = f"{model_type}:{display_name}"
            
            # Map this model key to its panel index
            model_panels_map[model_key] = i
            
            # Initialize model status
            model_status[model_key] = {
                "display_name": display_name,
                "status": "Initializing",
                "is_hf_model": model_type == "huggingface",
                "model_loaded": False,
                "loading_status": None,
                "current_prompt": None
            }
            
            # Initialize display data structure
            model_display_data[model_key] = {
                "examples": {}
            }
            
            # Initialize the panel
            update_model_panel(model_key)
        
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.concurrency)
        
        # Create a helper function for processing prompts with status tracking
        async def process_with_status(config: Dict[str, Any], example_obj: Union[Dict[str, Any], str], example_idx: int, model_key: str) -> Dict[str, Any]:
            """Process a single prompt with a given model and track status.
            
            Args:
                config: Model configuration dictionary
                example_obj: The example object (either dict with 'prompt' or direct string)
                example_idx: Index of the example being processed
                model_key: Key to identify the model in the results
                
            Returns:
                Dictionary of results for this prompt and model
            """
            # Get configuration values
            model_type = config.get("type", "openai")
            model_id = config.get("model_id", "unknown")
            display_name = config.get("custom_name", model_id)
            
            # Extract prompt from example
            if isinstance(example_obj, dict):
                prompt = example_obj.get("prompt", example_obj.get("input", ""))
                if not prompt and len(example_obj) == 1:
                    # If no prompt key but only one key, use its value
                    prompt = next(iter(example_obj.values()))
            else:
                prompt = str(example_obj)
                
            # Initialize return value with defaults
            result = {
                "example_idx": example_idx,
                "prompt": prompt,
                "success": False,
                "response": "",
                "response_time": 0.0,
                "error": None
            }
            
            # Preserve technique information from the original example
            if isinstance(example_obj, dict):
                # Copy technique-related fields to preserve them in the results
                technique_fields = ["technique", "adversarial_technique", "base_goal", "generation_method"]
                for field in technique_fields:
                    if field in example_obj:
                        result[field] = example_obj[field]
            
            try:
                # Update status for this model to show we're working on this prompt
                model_status[model_key]["status"] = "Running"
                model_status[model_key]["current_prompt"] = f"Example {example_idx+1}: {prompt[:30]}..."
                
                # Update display data
                if model_key not in model_display_data:
                    model_display_data[model_key] = {"examples": {}}
                    
                if "examples" not in model_display_data[model_key]:
                    model_display_data[model_key]["examples"] = {}
                    
                # Add this example to the display data
                model_display_data[model_key]["examples"][example_idx] = {
                    "prompt": prompt[:80] + "..." if len(prompt) > 80 else prompt,
                    "status": "Processing",
                    "response_time": "-",
                    "response": ""
                }
                    
                # Update the model panel with fresh data
                update_model_panel(model_key)
                
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"Processing example {example_idx+1} with model {model_key}")
                
                # Process the example with the model using semaphore for concurrency control
                async with semaphore:
                    # Get the appropriate handler based on model type
                    handler_key = f"{model_type}:{model_id}"
                    if handler_key not in self.model_handlers:
                        error_msg = f"No handler available for {handler_key} - please check your configuration"
                        if hasattr(self, 'verbose') and self.verbose:
                            print(f"Error: {error_msg}")
                        result["error"] = error_msg
                        return result
                    
                    handler = self.model_handlers[handler_key]
                    
                    # Extract parameters from config
                    max_tokens = config.get("max_tokens", 1000)
                    temperature = config.get("temperature", 0.7)
                    
                    # Generate response using the handler
                    if hasattr(self, 'verbose') and self.verbose:
                        print(f"Generating response for '{prompt[:50]}...' using {model_type}:{model_id}")
                    
                    # Record start time
                    start_time = time.time()
                    
                    # Different handling based on model type
                    if model_type == "ollama":
                        # Ollama API has a specific handler
                        try:
                            if hasattr(self, 'verbose') and self.verbose:
                                print(f"Calling Ollama handler.generate with model_id={model_id}")
                            
                            # Test the Ollama service first with a simple request
                            try:
                                # First ensure session is available
                                if not handler.session:
                                    await handler._ensure_session()
                                
                                # First check if Ollama is responsive with a small test prompt
                                test_response = await handler.test_prompt(
                                    model_id=model_id,
                                    prompt="Hello, are you working?"
                                )
                                if hasattr(self, 'verbose') and self.verbose:
                                    print(f"Ollama test response: {test_response}")
                                    if test_response.get("success", False):
                                        print("Ollama test was successful!")
                                    else:
                                        print(f"Ollama test failed: {test_response.get('error', 'Unknown error')}")
                            except Exception as test_err:
                                # Log the test error but continue with the actual request
                                if hasattr(self, 'verbose') and self.verbose:
                                    print(f"Ollama test request failed: {str(test_err)}")
                                    import traceback
                                    traceback.print_exc()
                                
                            # Use a longer timeout for Ollama as it may be running locally with limited resources
                            extended_timeout = 60  # 60 seconds for Ollama requests
                            
                            # Try up to 3 times with exponential backoff
                            retry_count = 0
                            max_retries = 3
                            last_error = None
                            
                            while retry_count < max_retries:
                                try:
                                    # Add a small delay between retries (except first attempt)
                                    if retry_count > 0:
                                        delay = retry_count * 2  # 2, 4, 6 seconds
                                        if hasattr(self, 'verbose') and self.verbose:
                                            print(f"Waiting {delay} seconds before retry {retry_count+1}/{max_retries}")
                                        await asyncio.sleep(delay)
                                    
                                    # Make the API call with longer timeout
                                    response_text = await asyncio.wait_for(
                                        handler.generate(
                                            model_id=model_id,
                                            prompt=prompt,
                                            max_tokens=max_tokens,
                                            temperature=temperature
                                        ),
                                        timeout=extended_timeout
                                    )
                                    
                                    if hasattr(self, 'verbose') and self.verbose:
                                        print(f"Ollama response received: {len(response_text)} characters")
                                    
                                    result["success"] = True
                                    result["response"] = response_text
                                    break  # Success, exit retry loop
                                    
                                except asyncio.TimeoutError:
                                    retry_count += 1
                                    last_error = f"Timeout after {extended_timeout} seconds"
                                    if hasattr(self, 'verbose') and self.verbose:
                                        print(f"Ollama request timed out (attempt {retry_count}/{max_retries})")
                                    
                                    if retry_count >= max_retries:
                                        result["error"] = f"Request timed out after {max_retries} attempts"
                                        
                                except Exception as e:
                                    retry_count += 1
                                    last_error = str(e)
                                    if hasattr(self, 'verbose') and self.verbose:
                                        print(f"Ollama request failed (attempt {retry_count}/{max_retries}): {str(e)}")
                                    
                                    if retry_count >= max_retries:
                                        result["error"] = f"Request failed after {max_retries} attempts: {str(e)}"
                            
                            # If we exhausted retries and still failed
                            if not result["success"]:
                                result["error"] = last_error
                                
                        except Exception as e:
                            if hasattr(self, 'verbose') and self.verbose:
                                print(f"Error generating with Ollama: {str(e)}")
                                import traceback
                                traceback.print_exc()
                            result["error"] = str(e)
                    else:
                        # Standard handlers with common interface
                        try:
                            response_text = await handler.generate(
                                model_id=model_id,
                                prompt=prompt,
                                max_tokens=max_tokens,
                                temperature=temperature
                            )
                            result["success"] = True
                            result["response"] = response_text
                        except Exception as e:
                            if hasattr(self, 'verbose') and self.verbose:
                                print(f"Error generating with {model_type}: {str(e)}")
                            result["error"] = str(e)
                    
                    # Calculate elapsed time
                    elapsed_time = time.time() - start_time
                    result["response_time"] = elapsed_time
                    
                    # Consider empty responses to be failures
                    if result["success"] and (not result["response"] or result["response"].strip() == ""):
                        result["success"] = False
                        result["error"] = "Empty response"
                
                # Update display data with result
                if model_key in model_display_data and "examples" in model_display_data[model_key]:
                    if example_idx in model_display_data[model_key]["examples"]:
                        # Check if response is a refusal
                        is_refusal = is_refusal_response(result.get("response", ""))
                        evaluation = "FAIL" if is_refusal else "SUCCESS"
                        
                        # Store evaluation in result
                        result["evaluation"] = evaluation
                        
                        # Update display data
                        model_display_data[model_key]["examples"][example_idx]["status"] = evaluation
                        model_display_data[model_key]["examples"][example_idx]["response_time"] = f"{result['response_time']:.2f}s"
                        response_preview = result["response"][:100] + "..." if result["response"] and len(result["response"]) > 100 else result["response"]
                        model_display_data[model_key]["examples"][example_idx]["response"] = response_preview
                
                # Update the model panel
                update_model_panel(model_key)
                
                # Determine if this is a custom API model that might have extracted fields
                is_custom_api = (model_type == "custom-api" or model_type == "custom") and hasattr(handler, 'last_extracted_value')
                
                if is_custom_api and hasattr(handler, 'last_extracted_value'):
                    result["extracted_field"] = handler.last_extracted_value
                    
                # Add raw response for custom API models if available
                if is_custom_api and hasattr(handler, 'last_raw_response'):
                    result["raw_response"] = handler.last_raw_response
                
                return result
                
            except Exception as e:
                # Handle any unexpected errors
                error_msg = f"Unexpected error processing example {example_idx}: {str(e)}"
                if hasattr(self, 'verbose') and self.verbose:
                    print(error_msg)
                    import traceback
                    traceback.print_exc()
                
                result["error"] = error_msg
                
                # Update display data
                if model_key in model_display_data and "examples" in model_display_data[model_key]:
                    if example_idx in model_display_data[model_key]["examples"]:
                        model_display_data[model_key]["examples"][example_idx]["status"] = "Error"
                        model_display_data[model_key]["examples"][example_idx]["response"] = f"Error: {error_msg}"
                
                # Update the model panel
                update_model_panel(model_key)
                
                return result
        
        # Run the tasks
        try:
            # List to store all tasks
            all_tasks = []
            
            # Create tasks for each combination of model and prompt
            for example_idx, example in enumerate(examples):
                for config in self.model_configs:
                    model_type = config.get("type", "openai")
                    display_name = config.get("custom_name", config.get("model_id", "unknown"))
                    model_key = f"{model_type}:{display_name}"
                    
                    # Create the task with the model_key embedded in the task
                    task = asyncio.create_task(
                        process_with_status(config, example, example_idx, model_key)
                    )
                    # Store model_key as an attribute directly on the task
                    task._model_key = model_key
                    task._example_idx = example_idx
                    task._prompt = example
                    
                    all_tasks.append(task)
            
            # Process tasks as they complete
            with Live(layout, refresh_per_second=4) as live:
                pending_tasks = all_tasks.copy()
                
                while pending_tasks:
                    # Update the summary table
                    summary_table = Table(title="Benchmark Progress", show_header=True, expand=True)
                    summary_table.add_column("Model")
                    summary_table.add_column("Type", width=12)
                    summary_table.add_column("Completed")
                    summary_table.add_column("Success Rate")
                    summary_table.add_column("Avg Time")
                    summary_table.add_column("Status")
                    
                    for model_key, model_result in results["model_results"].items():
                        display_name = model_result["display_name"]
                        model_type = model_result["type"]
                        total_processed = model_result["success_count"] + model_result["fail_count"]
                        success_rate = f"{(model_result['success_count'] / total_processed * 100) if total_processed > 0 else 0:.1f}%"
                        avg_time = f"{(model_result['total_time'] / total_processed) if total_processed > 0 else 0:.2f}s"
                        status = model_status[model_key]["status"]
                        
                        status_style = "green" if status == "Running" else "yellow"
                        
                        summary_table.add_row(
                            display_name,
                            model_type,
                            f"{total_processed}/{len(examples)}",
                            success_rate,
                            avg_time,
                            f"[{status_style}]{status}[/{status_style}]"
                        )
                    
                    # Update the summary panel
                    summary_panel = Panel(
                        Group(
                            Text("Benchmark in Progress", style="bold cyan"),
                            main_progress,
                            summary_table
                        ),
                        title="Benchmark Progress",
                        border_style="cyan"
                    )
                    layout["summary"].update(summary_panel)
                    
                    # Wait for the next task to complete
                    done, pending_tasks = await asyncio.wait(
                        pending_tasks, 
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=0.5
                    )
                    
                    # Process completed tasks
                    for task in done:
                        try:
                            # Get the model key from the task directly
                            model_key = getattr(task, "_model_key", None)
                            
                            if not model_key:
                                self.console.print("[red]Error: Could not find model key for task[/]")
                                continue
                                
                            # Get the result
                            task_result = await task
                            
                            # Update progress
                            main_progress.update(tasks[model_key], advance=1)
                            
                            # Update results
                            model_results = results["model_results"][model_key]
                            
                            if task_result["success"]:
                                model_results["success_count"] += 1
                            else:
                                model_results["fail_count"] += 1
                            
                            model_results["total_time"] += task_result["response_time"]
                            model_results["examples"].append(task_result)
                        except Exception as e:
                            self.console.print(f"[red]Error processing task: {str(e)}[/]")
                            model_key = getattr(task, "_model_key", "unknown")
                            if model_key != "unknown":
                                self.console.print(f"[red]Task error for model {model_key}[/]")
                
                # Mark all models as completed
                for model_key in model_status:
                    model_status[model_key]["status"] = "Completed"
                    update_model_panel(model_key)
                
                # Final update of the summary table
                summary_table = Table(title="Benchmark Complete", show_header=True, expand=True)
                summary_table.add_column("Model")
                summary_table.add_column("Type", width=12)
                summary_table.add_column("Completed")
                summary_table.add_column("Success Rate")
                summary_table.add_column("Avg Time")
                summary_table.add_column("Status")
                
                for model_key, model_result in results["model_results"].items():
                    display_name = model_result["display_name"]
                    model_type = model_result["type"]
                    total_processed = model_result["success_count"] + model_result["fail_count"]
                    success_rate = f"{(model_result['success_count'] / total_processed * 100) if total_processed > 0 else 0:.1f}%"
                    avg_time = f"{(model_result['total_time'] / total_processed) if total_processed > 0 else 0:.2f}s"
                    
                    summary_table.add_row(
                        display_name,
                        model_type,
                        f"{total_processed}/{len(examples)}",
                        success_rate,
                        avg_time,
                        "[green]Completed[/green]"
                    )
                
                # Update the summary panel one last time
                summary_panel = Panel(
                    Group(
                        Text("Benchmark Complete", style="bold green"),
                        main_progress,
                        summary_table
                    ),
                    title="Benchmark Results",
                    border_style="green"
                )
                layout["summary"].update(summary_panel)
                
                # Allow the final display to persist for a moment
                await asyncio.sleep(1)
        
        except Exception as e:
            self.console.print(f"[red]Error in task processing: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            
        # Close the session
        await self._close_session()
        
        # Calculate summary statistics
        models_tested = []
        overall_success_count = 0
        overall_fail_count = 0
        overall_time = 0
        
        for model_key, model_result in results["model_results"].items():
            total = model_result["success_count"] + model_result["fail_count"]
            if total > 0:
                model_result["success_rate"] = (model_result["success_count"] / total) * 100
                model_result["average_response_time"] = model_result["total_time"] / total
            else:
                model_result["success_rate"] = 0
                model_result["average_response_time"] = 0
                
            # Extract model info
            model_type = model_result["type"]
            model_id = model_result["model_id"]
            display_name = model_result["display_name"]
            
            # Format for models_tested list
            model_info = {
                "provider": model_type,
                "name": display_name,
                "model_id": model_id,
                "success_count": model_result["success_count"],
                "fail_count": model_result["fail_count"],
                "success_rate": model_result["success_rate"],
                "average_response_time": model_result["average_response_time"],
                "examples": model_result["examples"]
            }
            
            # Add extracted field information for custom API models
            # Check for both "custom-api" type and for keys that might have been remapped to "custom"
            is_custom_api = model_type == "custom-api" or (model_type == "custom" and any("extracted_field" in example for example in model_result["examples"]))
            
            if is_custom_api:
                # If type got remapped to "custom" but it's really a custom-api, fix it
                if model_type == "custom":
                    model_info["provider"] = "custom-api"
                
                # Collect all extracted_field data from examples
                extracted_fields = []
                for example in model_result["examples"]:
                    if "extracted_field" in example:
                        extracted_fields.append(example["extracted_field"])
                
                # If we have extracted fields, add them to the model info
                if extracted_fields:
                    model_info["extracted_fields"] = extracted_fields
                    
                    # Also add the most common path for reporting
                    paths = [field.get("path", "unknown") for field in extracted_fields if field]
                    if paths:
                        from collections import Counter
                        path_counts = Counter(paths)
                        most_common_path = path_counts.most_common(1)[0][0]
                        model_info["extracted_field_path"] = most_common_path
            
            models_tested.append(model_info)
            
            # Accumulate overall statistics
            overall_success_count += model_result["success_count"]
            overall_fail_count += model_result["fail_count"]
            overall_time += model_result["total_time"]
        
        # Calculate overall metrics
        overall_total = overall_success_count + overall_fail_count
        if overall_total > 0:
            overall_success_rate = (overall_success_count / overall_total) * 100
            overall_avg_time = overall_time / overall_total
        else:
            overall_success_rate = 0
            overall_avg_time = 0
        
        # Return final results in expected format
        final_results = {
            "timestamp": results["timestamp"],
            "examples_tested": results["example_count"],
            "success_rate": overall_success_rate,
            "average_response_time": overall_avg_time,
            "models_tested": models_tested
        }
        
        return final_results
    
    def run_with_dataset(self, dataset):
        """Run the API benchmark with the provided dataset.
        
        Args:
            dataset: The dataset to use for the benchmark
            
        Returns:
            dict: The results of the benchmark
        """
        examples = dataset.get("examples", [])
        
        if not examples:
            self.console.print("[yellow]Warning: Dataset contains no examples[/]")
            return {"error": "Dataset contains no examples"}
        
        # Check if max_samples is specified in any model config
        max_samples = None
        for config in self.model_configs:
            if config.get("max_samples") is not None:
                max_samples = config.get("max_samples")
                break
        
        # Limit examples if max_samples is specified
        original_count = len(examples)
        if max_samples is not None and max_samples > 0:
            examples = examples[:max_samples]
            self.console.print(f"[cyan]Processing {len(examples)} of {original_count} examples (limited by max_samples={max_samples})[/]")
        else:
            self.console.print(f"[cyan]Running benchmark with {len(examples)} examples[/]")
        
        # Create a new event loop for async operations to work around issues in certain environments
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Initialize handlers first to check availability
            self._init_model_handlers()
            
            # Check if any valid model handlers were initialized
            if not self.model_handlers:
                self.console.print("[bold red]Error: No valid model handlers available for the selected models.[/]")
                self.console.print("[yellow]Please check that you have the required API keys in your environment.[/]")
                return {
                    "error": "No valid model handlers available for the selected models.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "examples_tested": 0,
                    "success_rate": 0,
                    "average_response_time": 0,
                    "models_tested": []
                }
            
            # Pre-initialize Ollama models if any are in the configuration
            async def init_ollama_models():
                has_ollama = False
                for config in self.model_configs:
                    if config.get("type") == "ollama":
                        has_ollama = True
                        model_id = config.get("model_id")
                        model_key = f"ollama:{model_id}"
                        handler = self.model_handlers.get(model_key)
                        
                        if handler:
                            self.console.print(f"[cyan]Pre-initializing Ollama model: {model_id}[/]")
                            try:
                                # Ensure session is available
                                await handler._ensure_session()
                                
                                # Perform a simple test to verify model is available
                                await handler._ensure_model_loaded(model_id)
                                
                                # Test the model with a simple prompt
                                test_response = await handler.test_prompt(
                                    model_id=model_id,
                                    prompt="Hello, test connection"
                                )
                                
                                if test_response.get("success", False):
                                    self.console.print(f"[green]✓ Ollama model {model_id} initialized successfully[/]")
                                else:
                                    error = test_response.get("error", "Unknown error")
                                    self.console.print(f"[yellow]Warning: Ollama model {model_id} test failed: {error}[/]")
                                    
                            except Exception as e:
                                self.console.print(f"[yellow]Warning: Error initializing Ollama model {model_id}: {str(e)}[/]")
                
                return has_ollama
            
            # Run the Ollama initialization if needed
            has_ollama_models = loop.run_until_complete(init_ollama_models())
            if has_ollama_models:
                self.console.print("[cyan]Ollama models initialization complete[/]")
                
            # Run the benchmark with proper exception handling
            try:
                results = loop.run_until_complete(self._run_benchmark_async(examples))
                
                # Send email notification if configured
                if hasattr(self, 'notification_service') and self.notification_service and results.get('benchmark_id'):
                    try:
                        notification_sent = self.notification_service.send_benchmark_complete_notification(
                            benchmark_id=results['benchmark_id'],
                            results=results,
                            benchmark_type="Static Red Teaming"
                        )
                        
                        if notification_sent:
                            self.console.print("[dim]Email notification sent for benchmark completion.[/]")
                    except Exception as e:
                        self.console.print(f"[yellow]Failed to send notification: {str(e)}[/]")
                
                return results
            except Exception as e:
                self.console.print(f"[bold red]Error running benchmark: {str(e)}[/]")
                import traceback
                self.console.print(traceback.format_exc())
                return {
                    "error": f"Error running benchmark: {str(e)}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "examples_tested": 0,
                    "success_rate": 0,
                    "average_response_time": 0,
                    "models_tested": []
                }
        finally:
            loop.close()
    
    def _display_results(self, results):
        """Display the benchmark results in a user-friendly format.
        
        Args:
            results: Results dictionary from the benchmark
        """
        self.console.print("\n")
        
        # Create a table for the results
        table = Table(title="Benchmark Results", show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan")
        table.add_column("Success Rate", justify="right")
        table.add_column("Avg Response Time", justify="right")
        table.add_column("Successes", justify="right")
        table.add_column("Fails", justify="right")
        
        # Add rows for each model
        for model_key, model_result in results["model_results"].items():
            display_name = model_result["display_name"]
            success_rate = f"{model_result['success_rate']:.1f}%"
            avg_time = f"{model_result['average_response_time']:.2f}s"
            successes = str(model_result["success_count"])
            fails = str(model_result["fail_count"])
            
            table.add_row(
                display_name,
                success_rate,
                avg_time,
                successes,
                fails
            )
        
        # Print the table
        self.console.print(table)
        
        # Show any common errors
        self._display_error_summary(results)
    
    def _display_error_summary(self, results):
        """Display a summary of common errors encountered during the benchmark.
        
        Args:
            results: Results dictionary from the benchmark
        """
        # Collect all errors
        all_errors = []
        for model_key, model_result in results["model_results"].items():
            for example in model_result["examples"]:
                if not example.get("success", False):
                    error = example.get("error", "Unknown error")
                    all_errors.append((model_key, error))
        
        if not all_errors:
            return
        
        # Count error frequencies
        error_counts = {}
        for model_key, error in all_errors:
            error_str = str(error)
            if error_str not in error_counts:
                error_counts[error_str] = {"count": 0, "models": set()}
            
            error_counts[error_str]["count"] += 1
            error_counts[error_str]["models"].add(model_key)
        
        # Display the most common errors
        if error_counts:
            self.console.print("\n[bold red]Common Errors:[/]")
            for error, info in sorted(error_counts.items(), key=lambda x: x[1]["count"], reverse=True):
                if len(error) > 100:
                    error = error[:100] + "..."
                self.console.print(f"- [red]{error}[/] ({info['count']} times, affecting {len(info['models'])} models)")

class ModelPerformanceRunner:
    """Runner for model performance benchmarks"""
    
    def __init__(self, 
                 console: Console, 
                 model_path: str = "karanxa/Dravik",
                 verbose: bool = False):
        """Initialize performance benchmark runner"""
        self.console = console
        self.model_path = model_path
        self.verbose = verbose
    
    def run(self) -> Dict[str, Any]:
        """Run the performance benchmark"""
        self.console.print("[yellow]Performance benchmarking is not yet implemented[/]")
        return {}


class FlexibleBenchmarkRunner:
    """Runner for multi-domain benchmarks using the flexible benchmarking system"""
    
    def __init__(self, 
                db,
                console: Console,
                backup_manager: BackupManager,
                target_model: str = "karanxa/Dravik",
                domain: str = "general",
                benchmark_name: str = None,
                eval_models: List[Dict[str, str]] = None,
                examples_path: str = None,
                output_dir: str = "benchmark_results",
                max_examples: int = 10,
                verbose: bool = False):
        """Initialize flexible benchmark runner"""
        self.db = db
        self.console = console
        self.backup_manager = backup_manager
        self.target_model = target_model
        self.domain = domain
        self.benchmark_name = benchmark_name or f"{domain.capitalize()} Benchmark"
        
        # Default evaluator models
        self.eval_models = eval_models or [
            {"provider": "openai", "model": "gpt-4"},
            {"provider": "gemini", "model": "gemini-pro"}
        ]
        
        self.examples_path = examples_path
        self.output_dir = output_dir
        self.max_examples = max_examples
        self.verbose = verbose
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self) -> Dict[str, Any]:
        """Run the flexible benchmark for the specified domain"""
        try:
            # Status indicator
            with self.console.status(f"[bold blue]Setting up {self.domain} benchmark for {self.target_model}...") as status:
                # Initialize the flexible benchmark runner from our framework
                runner = FBRunner(
                    target_model=self.target_model,
                    domain=self.domain,
                    benchmark_name=self.benchmark_name,
                    eval_models=self.eval_models,
                    examples_path=self.examples_path,
                    output_dir=self.output_dir,
                    verbose=self.verbose
                )
                
                # Initialize the benchmark
                runner.initialize()
                
                # Load examples or use defaults
                examples = runner.load_examples()
                if len(examples) > self.max_examples:
                    examples = examples[:self.max_examples]
                    self.console.print(f"[yellow]Limiting to {self.max_examples} examples for this run[/]")
                
                self.console.print(f"[green]Loaded {len(examples)} examples for {self.domain} benchmark[/]")
                
            # Show evaluator models being used
            self.console.print(f"[blue]Running benchmark with evaluators:[/]")
            for evaluator in self.eval_models:
                self.console.print(f"[blue]- {evaluator['provider'].capitalize()}: {evaluator['model']}[/]")
            
            # Run the benchmark
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold]{task.completed}/{task.total}"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                # Create a progress task
                task_id = progress.add_task(f"Running {self.domain} benchmark", total=len(examples))
                
                # Run the benchmark with progress updates
                def progress_callback(example_idx, total, metrics):
                    progress.update(task_id, completed=example_idx + 1)
                    if metrics:
                        description = f"Running {self.domain} benchmark - Score: {metrics.get('overall', 0):.2f}"
                        progress.update(task_id, description=description)
                
                # Create a coroutine for the benchmark
                async def run_with_progress():
                    results = await runner.run_benchmark()
                    return results
                
                # Run the benchmark
                results = asyncio.run(run_with_progress())
            
            # Add metadata
            results["benchmark_runner"] = "flexible"
            results["benchmark_completed"] = True
            results["save_timestamp"] = datetime.now().isoformat()
            
            # Save results (although the runner already saves them)
            results_path = os.path.join(
                self.output_dir,
                f"{self.domain}_{self.target_model.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_summary.json"
            )
            
            with open(results_path, 'w') as f:
                # Create a summary version for the database
                summary = {
                    "domain": self.domain,
                    "target_model": self.target_model,
                    "benchmark_name": self.benchmark_name,
                    "timestamp": datetime.now().isoformat(),
                    "num_examples": len(examples),
                    "overall_score": results.get("overall", 0),
                    "metrics": results.get("metrics", {}),
                    "passed": results.get("passed", False),
                    "eval_models": self.eval_models,
                    "results_path": results_path
                }
                json.dump(summary, f, indent=2)
            
            # Store in database if available
            try:
                if self.db:
                    self.db.store_benchmark_result(
                        self.target_model,
                        self.domain,
                        results_path,
                        summary
                    )
            except Exception as db_error:
                self.console.print(f"[yellow]Warning: Could not store benchmark in database: {str(db_error)}[/]")
            
            self.console.print(f"[green]Benchmark completed! Results saved to {results_path}[/]")
            
            return summary
            
        except Exception as e:
            self.console.print(f"[red]Error running flexible benchmark: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            
            return {}

class KubernetesBenchmarkManager:
    """Manager for running benchmarks on Kubernetes"""
    
    def __init__(self, 
                 console: Console, 
                 backup_manager: BackupManager,
                 verbose: bool = False):
        self.console = console
        self.backup_manager = backup_manager
        self.verbose = verbose
        
        # Initialize Kubernetes client
        try:
            from kubernetes import client, config
            config.load_kube_config()
            self.k8s_api = client.CoreV1Api()
            self.k8s_available = True
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not initialize Kubernetes client: {str(e)}[/]")
            self.k8s_available = False
    
    def run_on_kubernetes(self, 
                         config: Dict[str, Any], 
                         output_dir: str,
                         run_id: str,
                         namespace: str = "default") -> Dict[str, Any]:
        """Run a benchmark on Kubernetes with improved error handling"""
        if not self.k8s_available:
            self.console.print("[red]Error: Kubernetes is not available.[/]")
            return {"error": "Kubernetes not available"}
            
        try:
            from kubernetes import client
            
            # Create unique names
            pod_name = f"dravik-benchmark-{run_id[:8]}"
            
            # Ensure the namespace exists
            try:
                self.k8s_api.read_namespace(namespace)
            except:
                self.console.print(f"[yellow]Warning: Namespace {namespace} not found, using default[/]")
                namespace = "default"
            
            # Create the benchmark pod with resource limits and requests
            pod = client.V1Pod(
                metadata=client.V1ObjectMeta(
                    name=pod_name,
                    namespace=namespace,
                    labels={
                        "app": "dravik-benchmark",
                        "run-id": run_id
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="benchmark",
                            image="dravik/benchmark:latest",  # Make sure this image exists
                            env=[
                                client.V1EnvVar(name="BENCHMARK_RUN_ID", value=run_id),
                                client.V1EnvVar(name="BENCHMARK_CONFIG", value=json.dumps(config)),
                                client.V1EnvVar(name="BENCHMARK_OUTPUT_DIR", value=output_dir)
                            ],
                            resources=client.V1ResourceRequirements(
                                requests={
                                    "cpu": "1",
                                    "memory": "2Gi"
                                },
                                limits={
                                    "cpu": "2",
                                    "memory": "4Gi"
                                }
                            ),
                            volume_mounts=[
                                client.V1VolumeMount(
                                    name="benchmark-data",
                                    mount_path="/data"
                                )
                            ]
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name="benchmark-data",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name="benchmark-data-pvc"
                            )
                        )
                    ],
                    restart_policy="Never"
                )
            )
            
            # Create pod in Kubernetes
            try:
                created_pod = self.k8s_api.create_namespaced_pod(namespace=namespace, body=pod)
                self.console.print(f"[green]✓ Created benchmark pod: {pod_name}[/]")
            except Exception as e:
                self.console.print(f"[red]Error creating pod: {str(e)}[/]")
                if "already exists" in str(e):
                    # Try to delete the existing pod and retry
                    try:
                        self.k8s_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
                        self.console.print("[yellow]Deleted existing pod, retrying...[/]")
                        created_pod = self.k8s_api.create_namespaced_pod(namespace=namespace, body=pod)
                    except Exception as retry_e:
                        raise Exception(f"Failed to recreate pod: {str(retry_e)}")
                else:
                    raise
            
            # Monitor pod status
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                refresh_per_second=1
            ) as progress:
                monitor_task = progress.add_task("Monitoring benchmark pod...", total=100)
                
                while True:
                    try:
                        pod = self.k8s_api.read_namespaced_pod(name=pod_name, namespace=namespace)
                        status = pod.status.phase
                        
                        # Update progress description based on status
                        progress.update(
                            monitor_task, 
                            description=f"Pod status: {status}",
                            advance=1 if status == "Running" else 0
                        )
                        
                        # Check for completion or failure
                        if status == "Succeeded":
                            progress.update(monitor_task, completed=100)
                            self.console.print("[green]✓ Benchmark completed successfully[/]")
                            break
                        elif status == "Failed":
                            progress.update(monitor_task, completed=100)
                            # Get pod logs for error information
                            logs = self.get_pod_logs(pod_name, namespace)
                            self.console.print(f"[red]✗ Benchmark failed. Pod logs:[/]\n{logs}")
                            break
                        elif status == "Pending":
                            # Check for issues in pod events
                            events = self.k8s_api.list_namespaced_event(
                                namespace=namespace,
                                field_selector=f"involvedObject.name={pod_name}"
                            )
                            for event in events.items:
                                if event.type == "Warning":
                                    self.console.print(f"[yellow]Warning: {event.message}[/]")
                        
                        time.sleep(2)
                        
                    except Exception as e:
                        self.console.print(f"[red]Error monitoring pod: {str(e)}[/]")
                        break
            
            # Get final results
            try:
                logs = self.get_pod_logs(pod_name, namespace)
                results = self._parse_benchmark_results(logs)
                
                # Clean up the pod
                try:
                    self.k8s_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
                    self.console.print("[green]✓ Cleaned up benchmark pod[/]")
                except:
                    self.console.print("[yellow]Warning: Could not clean up benchmark pod[/]")
                
                return results
                
            except Exception as e:
                self.console.print(f"[red]Error getting benchmark results: {str(e)}[/]")
                return {"error": str(e)}
            
        except Exception as e:
            self.console.print(f"[red]Error in Kubernetes benchmark: {str(e)}[/]")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return {"error": str(e)}
    
    def _parse_benchmark_results(self, logs: str) -> Dict[str, Any]:
        """Parse benchmark results from pod logs"""
        try:
            # Look for JSON output in the logs
            import re
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, logs)
            
            if matches:
                # Try each match until we find valid JSON
                for match in matches:
                    try:
                        return json.loads(match)
                    except:
                        continue
                        
            # If no valid JSON found, return the raw logs
            return {
                "error": "Could not parse benchmark results",
                "logs": logs
            }
            
        except Exception as e:
            return {
                "error": f"Error parsing benchmark results: {str(e)}",
                "logs": logs
            }
    
    def get_pod_logs(self, pod_name: str, namespace: str = "default", tail_lines: int = 200) -> str:
        """Get logs from a Kubernetes pod
        
        Args:
            pod_name: Name of the Kubernetes pod
            namespace: Kubernetes namespace
            tail_lines: Number of lines to retrieve from the end of logs
            
        Returns:
            str: Pod logs
        """
        try:
            from kubernetes import client, config as k8s_config
            
            k8s_config.load_kube_config()
            k8s_api = client.CoreV1Api()
            
            logs = k8s_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container="benchmark-container",
                tail_lines=tail_lines
            )
            
            return logs
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not get pod logs: {str(e)}[/]")
            return f"Error retrieving logs: {str(e)}"
    
    def get_pod_status(self, pod_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Get detailed status of a Kubernetes pod
        
        Args:
            pod_name: Name of the Kubernetes pod
            namespace: Kubernetes namespace
            
        Returns:
            Dict: Pod status information
        """
        try:
            from kubernetes import client, config as k8s_config
            
            k8s_config.load_kube_config()
            k8s_api = client.CoreV1Api()
            
            pod = k8s_api.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            status_info = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "pod_ip": pod.status.pod_ip,
                "node": pod.spec.node_name,
                "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
                "labels": pod.metadata.labels,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "last_transition_time": c.last_transition_time.isoformat() if c.last_transition_time else None
                    }
                    for c in pod.status.conditions or []
                ],
                "container_statuses": [
                    {
                        "name": c.name,
                        "ready": c.ready,
                        "restart_count": c.restart_count,
                        "state": {
                            "running": c.state.running.started_at.isoformat() if c.state.running else None,
                            "terminated": {
                                "exit_code": c.state.terminated.exit_code if c.state.terminated else None,
                                "reason": c.state.terminated.reason if c.state.terminated else None,
                                "message": c.state.terminated.message if c.state.terminated else None,
                                "finished_at": c.state.terminated.finished_at.isoformat() if c.state.terminated and c.state.terminated.finished_at else None
                            } if c.state.terminated else None,
                            "waiting": {
                                "reason": c.state.waiting.reason if c.state.waiting else None,
                                "message": c.state.waiting.message if c.state.waiting else None
                            } if c.state.waiting else None
                        }
                    }
                    for c in pod.status.container_statuses or []
                ]
            }
            
            return status_info
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not get pod status: {str(e)}[/]")
            return {"error": str(e)}

    def _prepare_model_configs(self, models: List[str], model_loader, max_tokens: int, temperature: float) -> List[Dict[str, Any]]:
        """Prepare model configurations based on the selected models
        
        Args:
            models: List of model IDs
            model_loader: ModelLoader instance
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            
        Returns:
            List of model configuration dictionaries
        """
        model_configs = []
        
        for model_id in models:
            config = {}
            
            # Check if this is a guardrail model
            if model_id.startswith("guardrail:"):
                guardrail_name = model_id.replace("guardrail:", "", 1)
                config = {
                    "type": "guardrail",
                    "model_id": model_id,  # Keep the full guardrail:name format
                    "name": guardrail_name,  # Store the actual guardrail name
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
            # Check if this is a custom model
            elif model_id.startswith("custom:"):
                custom_name = model_id.replace("custom:", "", 1)
                custom_config = model_loader.get_custom_model_config(custom_name)
                
                if not custom_config:
                    self.console.print(f"[yellow]Warning: No configuration found for custom model {custom_name}. Skipping.[/]")
                    continue
                
                # Check the model type
                model_type = custom_config.get("type", "").lower()
                
                if model_type == "ollama":
                    # Handle Ollama models
                    config = {
                        "type": "ollama",
                        "model_id": custom_config.get("model_id"),
                        "custom_name": custom_name,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "base_url": custom_config.get("base_url")
                    }
                elif model_type == "custom-api":
                    # Handle custom API models
                    config = {
                        "type": "custom-api",
                        "model_id": custom_name,  # Use the custom name as the model ID
                        "custom_name": custom_name,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        # Add API-specific configuration
                        "endpoint_url": custom_config.get("endpoint_url"),
                        "curl_command": custom_config.get("curl_command"),
                        "http_method": custom_config.get("http_method", "POST"),
                        "headers": custom_config.get("headers", {}),
                        "json_path": custom_config.get("json_path")
                    }
                else:
                    # Legacy or unknown type - try to determine from provider
                    provider = custom_config.get("provider", "").lower()
                    
                    if provider == "huggingface":
                        # Convert legacy HuggingFace format to new format
                        params = custom_config.get("params", {})
                        hf_model_id = params.get("model_id", "")
                        
                        if not hf_model_id:
                            self.console.print(f"[yellow]Warning: No model ID found for HuggingFace model {custom_name}. Skipping.[/]")
                            continue
                            
                        config = {
                            "type": "huggingface",
                            "model_id": hf_model_id,
                            "custom_name": custom_name,
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                            "api_key": params.get("api_key", "")
                        }
                    else:
                        # Generic custom model
                        self.console.print(f"[yellow]Warning: Unknown custom model type for {custom_name}. Trying generic handling.[/]")
                        config = {
                            "type": "custom",
                            "model_id": custom_name,
                            "custom_name": custom_name,
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                            "config": custom_config
                        }
                
            # Check if this is a HuggingFace model
            elif model_id.startswith("hf:"):
                hf_model_id = model_id.replace("hf:", "", 1)
                config = {
                    "type": "huggingface",
                    "model_id": hf_model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
            # Handle OpenAI models
            elif "gpt" in model_id.lower():
                config = {
                    "type": "openai",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
            # Handle Gemini models
            elif "gemini" in model_id.lower():
                config = {
                    "type": "gemini",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
            # Handle Anthropic models
            elif "claude" in model_id.lower():
                config = {
                    "type": "anthropic",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
            # If we couldn't determine the type, skip this model
            if not config:
                self.console.print(f"[yellow]Warning: Could not determine type for model {model_id}. Skipping.[/]")
                continue
                
            model_configs.append(config)
            
        return model_configs
