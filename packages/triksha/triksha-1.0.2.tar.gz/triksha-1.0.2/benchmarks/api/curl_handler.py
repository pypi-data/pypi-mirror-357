"""Handler for custom curl-based API interactions"""
import os
import json
import asyncio
import time
import subprocess
import shlex
from typing import List, Dict, Any, Optional

class CurlHandler:
    """Handler for custom curl-based API interactions"""
    
    def __init__(self, 
                 curl_command: str,
                 prompt_placeholder: str = "{prompt}",
                 response_format: str = "openai",
                 json_path: Optional[str] = None,
                 model_name: str = "custom-api-model",
                 verbose: bool = False):
        """Initialize curl-based model handler
        
        Args:
            curl_command: Curl command with placeholder for the prompt
            prompt_placeholder: The placeholder text to replace with the actual prompt
            response_format: Format of the response (openai, simple, custom)
            json_path: JSON path for custom response format (e.g., 'response.result.content')
            model_name: Name to identify this model
            verbose: Whether to output verbose logs
        """
        self.curl_command = curl_command
        self.prompt_placeholder = prompt_placeholder
        self.response_format = response_format
        self.json_path = json_path
        self.model_name = model_name
        self.verbose = verbose
        
        if self.verbose:
            print(f"Initialized curl handler with model name: {model_name}")
            print(f"Curl command: {curl_command}")
            print(f"Prompt placeholder: {prompt_placeholder}")
            print(f"Response format: {response_format}")
            if json_path:
                print(f"JSON path: {json_path}")
    
    @staticmethod
    async def list_models() -> List[str]:
        """List available models - always returns a single model for curl handler
        
        Returns:
            List containing the single model name
        """
        return ["custom-api-model"]
    
    def _extract_response_text(self, json_data: Any) -> str:
        """Extract response text from JSON data based on configured format
        
        Args:
            json_data: Parsed JSON data from the API response
            
        Returns:
            Extracted response text
        """
        try:
            if self.response_format == "openai":
                # OpenAI format: {"choices": [{"message": {"content": "response"}}]}
                return json_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            elif self.response_format == "simple":
                # Simple format: {"text": "response"}
                return json_data.get("text", str(json_data))
            
            elif self.response_format == "custom" and self.json_path:
                # Custom format with JSON path
                parts = self.json_path.split(".")
                value = json_data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        if self.verbose:
                            print(f"Could not find '{part}' in JSON path")
                        return str(json_data)
                return str(value)
            
            else:
                # Fallback: convert the entire response to string
                return str(json_data)
                
        except Exception as e:
            if self.verbose:
                print(f"Error extracting response text: {str(e)}")
            return str(json_data)
    
    async def test_prompt(self, prompt: str) -> Dict[str, Any]:
        """Test a prompt using the custom curl command
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Dictionary with response information
        """
        try:
            start_time = time.time()
            
            # Replace the placeholder with the prompt
            escaped_prompt = prompt.replace('"', '\\"').replace("'", "\\'")
            cmd = self.curl_command.replace(self.prompt_placeholder, escaped_prompt)
            
            if self.verbose:
                print(f"Executing curl command for prompt: '{prompt[:50]}...'")
            
            # Execute the curl command
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            elapsed_time = time.time() - start_time
            
            if process.returncode != 0:
                # Command failed
                error_message = stderr.decode().strip() or "Unknown error executing curl command"
                
                if self.verbose:
                    print(f"Curl command failed: {error_message}")
                
                return {
                    "success": False,
                    "error": f"Curl error: {error_message}",
                    "model": self.model_name,
                    "provider": "custom-api",
                    "version": "curl",
                    "response_time": elapsed_time
                }
            
            # Parse the JSON response
            try:
                response_data = json.loads(stdout.decode().strip())
                response_text = self._extract_response_text(response_data)
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model_name,
                    "provider": "custom-api",
                    "version": "curl",
                    "response_time": elapsed_time
                }
                
            except json.JSONDecodeError:
                # If the output is not valid JSON, return it as is
                raw_output = stdout.decode().strip()
                
                if self.verbose:
                    print(f"Received non-JSON response: {raw_output[:100]}...")
                
                return {
                    "success": True,
                    "response": raw_output,
                    "model": self.model_name,
                    "provider": "custom-api",
                    "version": "curl",
                    "response_time": elapsed_time
                }
                
        except Exception as e:
            if self.verbose:
                print(f"Error in curl test_prompt: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name,
                "provider": "custom-api",
                "version": "curl",
                "response_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def generate(self, prompt: str) -> str:
        """Generate a response using the custom curl command
        
        This is a simpler interface that just returns the text.
        
        Args:
            prompt: The prompt to process
            
        Returns:
            Generated text response
        """
        result = await self.test_prompt(prompt)
        return result.get("response", f"Error: {result.get('error', 'Unknown error')}") 