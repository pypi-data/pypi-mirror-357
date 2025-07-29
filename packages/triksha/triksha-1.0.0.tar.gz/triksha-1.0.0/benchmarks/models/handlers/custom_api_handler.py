import os
import re
import json
import asyncio
import aiohttp
import subprocess
import shlex
import tempfile
import glob
from typing import Dict, Any, List, Optional, Union
import logging
import time
import uuid

from ..base_handler import ModelHandler

# Configure logger
logger = logging.getLogger(__name__)


class CustomAPIHandler(ModelHandler):
    """Handler for custom API endpoints or curl commands."""

    def __init__(
        self,
        name: str,
        curl_command: Optional[str] = None,
        prompt_placeholder: str = '{prompt}',
        endpoint_url: Optional[str] = None,
        http_method: str = 'POST',
        headers: Optional[Dict[str, str]] = None,
        json_path: Optional[str] = None,
        sample_response: Optional[str] = None,
        verbose: bool = False
    ):
        """Initialize the custom API handler
        
        Args:
            name: Name of the model
            curl_command: Full curl command with prompt placeholder 
            prompt_placeholder: String to replace with the actual prompt in curl command
            endpoint_url: URL for direct HTTP requests (alternative to curl)
            http_method: HTTP method for direct requests
            headers: HTTP headers for direct requests
            json_path: JSONPath expression to extract text from response
            sample_response: Sample response from the API for validation
            verbose: Whether to output verbose logs
        """
        self.name = name
        self.curl_command = curl_command
        self.prompt_placeholder = prompt_placeholder
        self.endpoint_url = endpoint_url
        self.http_method = http_method
        self.headers = headers or {}
        self.json_path = json_path
        self.sample_response = sample_response
        self.verbose = verbose
        
        # Configure logging
        self.logger = logging.getLogger(f"CustomAPIHandler:{name}")
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(log_level)
        
        # Log initialization
        if verbose:
            self.logger.debug(f"Initialized CustomAPIHandler for {name}")
            if curl_command:
                self.logger.debug(f"Using curl command with placeholder: {prompt_placeholder}")
            else:
                self.logger.debug(f"Using direct HTTP: {http_method} {endpoint_url}")
            if sample_response:
                self.logger.debug("Sample response provided for validation")
            if json_path:
                self.logger.debug(f"Using JSON path: {json_path}")
                
        # Store the original curl command for reference
        self._original_curl = curl_command
        
        # Validate that we have either endpoint_url or curl_command
        if not endpoint_url and not curl_command:
            raise ValueError("Either endpoint_url or curl_command must be provided")
            
        if self.verbose:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            logger.addHandler(handler)
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models.
        
        Returns:
            List containing only this custom model
        """
        return [{
            "id": self.name,
            "name": self.name,
            "provider": "custom-api"
        }]
    
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate a response from the custom API.
        
        Args:
            model_id: The model ID (ignored for custom APIs)
            prompt: The prompt to send to the API
            **kwargs: Additional arguments
            
        Returns:
            The generated text
        """
        try:
            timeout = kwargs.pop('timeout', 60)
            if self.curl_command:
                response_data = await self._generate_with_curl(prompt, **kwargs)
            else:
                response_data = await self._generate_with_http(prompt, **kwargs)
                
            # Store the raw response for later reference
            self.last_raw_response = response_data
            
            # Process the response to extract the text
            extracted_value = self._process_response(response_data)
            
            # Store the extracted value with its path
            if hasattr(self, 'json_path') and self.json_path:
                self.last_extracted_value = {
                    "value": extracted_value,
                    "path": self.json_path
                }
            else:
                self.last_extracted_value = {
                    "value": extracted_value,
                    "path": "auto-detected"
                }
                
            return extracted_value
            
        except Exception as e:
            if self.verbose:
                logger.error(f"Error in generate: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _generate_with_curl(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate using the provided curl command.
        
        Args:
            prompt: The prompt to generate a response for
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional parameters
            
        Returns:
            The generated text response
        """
        tmp_file = None
        try:
            # Clean up the curl command - handle multiline commands, unnecessary whitespace
            curl_cmd = self.curl_command.strip()
            
            # Replace newlines and multiple spaces with single spaces
            curl_cmd = re.sub(r'\s+', ' ', curl_cmd)
            
            # Process parameters to avoid duplicates
            # Don't pass max_tokens and temperature via kwargs if they're already in the parameters
            processed_kwargs = {k: v for k, v in kwargs.items() 
                               if k not in ['max_tokens', 'temperature', 'prompt']}
            
            # ALWAYS use a temp file approach for the payload to completely sandbox the prompt
            # This avoids issues with shell interpretation of spaces, quotes, etc.
            tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            
            # Check if the command is using a data payload (-d or --data flag)
            # Fixed regex pattern that properly handles quoted JSON payloads
            data_pattern = r'(?:-d|--data)\s+([\'"])(.*?)\1'
            data_match = re.search(data_pattern, curl_cmd, re.DOTALL)
            
            if data_match:
                # Extract the data payload
                quote_char = data_match.group(1)
                data_content = data_match.group(2)
                
                if self.prompt_placeholder in data_content:
                    try:
                        # Try parsing as JSON first
                        try:
                            # If it's valid JSON, parse and replace the placeholder
                            json_data = json.loads(data_content)
                            # Recursively replace placeholder in the JSON structure
                            self._replace_in_json(json_data, self.prompt_placeholder, prompt)
                            # Write the updated JSON to the temp file
                            json.dump(json_data, tmp_file, ensure_ascii=False)
                        except json.JSONDecodeError:
                            # Not valid JSON, do a simple string replacement
                            data_content_updated = data_content.replace(self.prompt_placeholder, 
                                                                       json.dumps(prompt)[1:-1])  # Escape for JSON
                            tmp_file.write(data_content_updated)
                    except Exception as e:
                        if self.verbose:
                            logger.error(f"Error processing payload: {str(e)}")
                        # Fallback: just do a simple replacement
                        data_content_updated = data_content.replace(self.prompt_placeholder, prompt)
                        tmp_file.write(data_content_updated)
                else:
                    # No placeholder in data, but still write it to file
                    # Replace other parameters like max_tokens and temperature
                    processed_data = data_content
                    if "{max_tokens}" in processed_data:
                        processed_data = processed_data.replace("{max_tokens}", str(max_tokens))
                    if "{temperature}" in processed_data:
                        processed_data = processed_data.replace("{temperature}", str(temperature))
                    tmp_file.write(processed_data)
                
                # Flush and close the file
                tmp_file.flush()
                
                # Replace the data section with reference to the temporary file
                # Find the complete data argument in the original command
                original_data_arg = data_match.group(0)  # The entire matched string
                curl_cmd = curl_cmd.replace(original_data_arg, f"-d @{tmp_file.name}")
            else:
                # No data payload, but the prompt might be in a URL or other part
                # Create a simple text file with the prompt
                tmp_file.write(prompt)
                tmp_file.flush()
                
                # Replace the placeholder with the file path, properly quoted
                if self.prompt_placeholder in curl_cmd:
                    # Use cat to read the file content and pipe it to curl
                    # This ensures the prompt is treated as a single string
                    file_reference = f"$(cat {tmp_file.name})"
                    curl_cmd = curl_cmd.replace(self.prompt_placeholder, shlex.quote(file_reference))
            
            # Replace other common placeholders if present
            if "{max_tokens}" in curl_cmd:
                curl_cmd = curl_cmd.replace("{max_tokens}", str(max_tokens))
                
            if "{temperature}" in curl_cmd:
                curl_cmd = curl_cmd.replace("{temperature}", str(temperature))
            
            # Replace any additional parameters that might be in the command
            for key, value in processed_kwargs.items():
                placeholder = "{" + key + "}"
                if placeholder in curl_cmd:
                    if isinstance(value, str):
                        curl_cmd = curl_cmd.replace(placeholder, shlex.quote(value))
                    else:
                        curl_cmd = curl_cmd.replace(placeholder, str(value))
            
            if self.verbose:
                logger.debug(f"Executing curl command with temp file: {curl_cmd}")
            
            # Run the curl command with explicit timeout to prevent hanging
            try:
                process = await asyncio.create_subprocess_shell(
                    curl_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Set a timeout for the curl command
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120.0)
                except asyncio.TimeoutError:
                    # Kill the process if it times out
                    try:
                        process.kill()
                    except:
                        pass
                    raise ValueError("Curl command timed out after 120 seconds")
            
                if process.returncode != 0:
                    error_message = stderr.decode('utf-8', errors='replace')
                    if self.verbose:
                        logger.error(f"Curl command failed with code {process.returncode}: {error_message}")
                    raise ValueError(f"Curl command failed (exit code {process.returncode}): {error_message}")
            
                # Parse the response
                response_text = stdout.decode('utf-8', errors='replace')
                
                # Try to parse as JSON first
                try:
                    response_json = json.loads(response_text)
                    return self._process_response(response_json)
                except json.JSONDecodeError as json_err:
                    # If not valid JSON, try to handle common issues
                    if self.verbose:
                        logger.debug(f"JSON parse error: {str(json_err)}")
                        logger.debug(f"First 500 chars of response: {response_text[:500]}")
                    
                    # Check if response might be wrapped in additional output
                    # Try to extract JSON from the response using regex
                    json_pattern = r'({.*}|\[.*\])'
                    json_matches = re.findall(json_pattern, response_text)
                    if json_matches:
                        for potential_json in json_matches:
                            try:
                                data = json.loads(potential_json)
                                return self._process_response(data)
                            except:
                                continue
                    
                    # If not JSON, return raw response (with some cleanup)
                    return response_text.strip()
            except Exception as curl_error:
                raise ValueError(f"Error executing curl command: {str(curl_error)}")
                
        except Exception as e:
            if self.verbose:
                logger.error(f"Error in _generate_with_curl: {str(e)}")
            return f"Error: {str(e)}"
        finally:
            # Clean up any temporary files
            if tmp_file and os.path.exists(tmp_file.name):
                try:
                    os.unlink(tmp_file.name)
                except Exception as cleanup_error:
                    if self.verbose:
                        logger.warning(f"Error cleaning up temporary file: {str(cleanup_error)}")
            
            # Clean up any other temporary files we might have created
            try:
                for filename in glob.glob('/tmp/curl_prompt_*.json'):
                    if os.path.exists(filename):
                        os.unlink(filename)
            except Exception as cleanup_error:
                if self.verbose:
                    logger.warning(f"Error cleaning up temporary files: {str(cleanup_error)}")
    
    def _replace_in_json(self, obj, placeholder, replacement):
        """Recursively replace placeholder in JSON structure.
        
        Args:
            obj: JSON object (dict, list, or primitive)
            placeholder: String to replace
            replacement: Replacement string
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    self._replace_in_json(value, placeholder, replacement)
                elif isinstance(value, str) and placeholder in value:
                    obj[key] = value.replace(placeholder, replacement)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    self._replace_in_json(item, placeholder, replacement)
                elif isinstance(item, str) and placeholder in item:
                    obj[i] = item.replace(placeholder, replacement)
    
    async def _generate_with_http(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate using direct HTTP request.
        
        Args:
            prompt: The prompt to generate a response for
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional parameters
            
        Returns:
            The generated text response
        """
        if not self.endpoint_url:
            raise ValueError("endpoint_url is required for HTTP generation")
        
        try:
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add other parameters if provided
            for key, value in kwargs.items():
                if key not in ["prompt", "max_tokens", "temperature"]:
                    payload[key] = value
            
            if self.verbose:
                logger.debug(f"Making HTTP request to {self.endpoint_url}")
                logger.debug(f"Headers: {self.headers}")
                logger.debug(f"Payload: {payload}")
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                method = getattr(session, self.http_method.lower())
                
                async with method(
                    self.endpoint_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        if self.verbose:
                            logger.error(f"HTTP request failed: {response.status} - {error_text}")
                        raise ValueError(f"HTTP request failed: {response.status} - {error_text}")
                    
                    # Handle response based on content type
                    content_type = response.headers.get("Content-Type", "")
                    
                    if "application/json" in content_type:
                        data = await response.json()
                        return self._process_response(data)
                    else:
                        # Return raw text for non-JSON responses
                        return await response.text()
                        
        except Exception as e:
            if self.verbose:
                logger.error(f"Error in _generate_with_http: {str(e)}")
            raise
    
    def _process_response(self, response_data: Union[Dict, List, Any]) -> str:
        """Process the API response and extract the generated text.
        
        Args:
            response_data: The parsed API response
            
        Returns:
            The extracted generated text
        """
        # If a json_path is provided, use it to extract the response
        if self.json_path:
            try:
                extracted_value = self._extract_from_json_path(response_data, self.json_path)
                if extracted_value is not None:
                    # Return the extracted value, converting to string if needed
                    if not isinstance(extracted_value, str):
                        return str(extracted_value)
                    return extracted_value
                    
                if self.verbose:
                    logger.warning(f"No data found at path: {self.json_path}")
                    logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
            except Exception as e:
                if self.verbose:
                    logger.error(f"Error extracting from path '{self.json_path}': {str(e)}")
        
        # Fall back to automatic extraction methods
        # 1. OpenAI format
        try:
            # Standard OpenAI chat completion format
            if isinstance(response_data, dict) and "choices" in response_data:
                choices = response_data["choices"]
                if isinstance(choices, list) and len(choices) > 0:
                    choice = choices[0]
                    # Chat completion format
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    # Completion format
                    elif "text" in choice:
                        return choice["text"]
                    # Handle content-only
                    elif "content" in choice:
                        return choice["content"]
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error extracting OpenAI format: {str(e)}")
        
        # 2. Gemini (Google AI) format
        try:
            # Handle Gemini format (candidates with parts)
            if isinstance(response_data, dict) and "candidates" in response_data:
                candidates = response_data["candidates"]
                if isinstance(candidates, list) and len(candidates) > 0:
                    candidate = candidates[0]
                    # New Gemini format with parts
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if isinstance(parts, list) and len(parts) > 0:
                            # Handle text or multimodal
                            if "text" in parts[0]:
                                return parts[0]["text"]
                    # Direct content field
                    elif "content" in candidate:
                        return candidate["content"]
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error extracting Gemini format: {str(e)}")
        
        # 3. Anthropic format
        try:
            # Handle Anthropic Claude format
            if isinstance(response_data, dict):
                # New Claude 3 format
                if "content" in response_data and isinstance(response_data["content"], list):
                    content_parts = response_data["content"]
                    text_parts = []
                    for part in content_parts:
                        if part.get("type") == "text" and "text" in part:
                            text_parts.append(part["text"])
                    if text_parts:
                        return "\n".join(text_parts)
                
                # Older Claude format
                if "completion" in response_data:
                    return response_data["completion"]
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error extracting Anthropic format: {str(e)}")

        # 4. Meta Llama 3 format
        try:
            # Handle Meta Llama 3 format
            if isinstance(response_data, dict):
                # Safety-v8-Meta-Llama-3 format - direct response field
                if "response" in response_data:
                    response_val = response_data["response"]
                    if isinstance(response_val, str) and response_val.strip():
                        return response_val
                    
                # Meta Llama 3 standard format - generation field
                if "generation" in response_data:
                    return response_data["generation"]
                
                # Llama3 format with generations array
                if "generations" in response_data and isinstance(response_data["generations"], list):
                    generations = response_data["generations"]
                    if len(generations) > 0:
                        # Usually the first generation contains the primary output
                        gen = generations[0]
                        if isinstance(gen, dict) and "text" in gen:
                            return gen["text"]
                
                # Some Meta Llama endpoints return content directly
                if "content" in response_data and isinstance(response_data["content"], str):
                    return response_data["content"]
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error extracting Meta Llama 3 format: {str(e)}")

        # 5. Raw text field with common names
        try:
            common_fields = ["text", "content", "output", "result", "response", "data", "generated_text", "message"]
            for field in common_fields:
                if isinstance(response_data, dict) and field in response_data:
                    content = response_data[field]
                    if isinstance(content, str):
                        return content
                    # Handle nested content
                    elif isinstance(content, dict) and "text" in content:
                        return content["text"]
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error extracting from common fields: {str(e)}")
        
        # If we got a string directly, just return it
        if isinstance(response_data, str):
            return response_data
            
        # If we reach here and didn't extract anything, return formatted JSON
        if self.verbose:
            logger.warning("Could not extract text from response. Returning formatted JSON.")
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
            
        try:
            return json.dumps(response_data, indent=2)
        except:
            # Last resort: convert to string
            return str(response_data)
    
    def _extract_from_json_path(self, data: Union[Dict, List, Any], path: str) -> Any:
        """Extract a value from a nested data structure using a JSON path string.
        
        Args:
            data: The data structure to extract from
            path: A JSON path like "choices[0].message.content"
            
        Returns:
            The extracted value, or None if not found
        """
        # Handle empty path
        if not path:
            return data
            
        # Split path into components
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]  # Remove empty parts
        
        current = data
        for part in parts:
            # Handle array indices
            if part.isdigit():
                idx = int(part)
                if isinstance(current, list) and 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            # Handle object keys
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
        
    async def test_prompt(self, model_id: str, prompt: str, streaming: bool = False, timeout: int = 30) -> Dict:
        """Test the API endpoint with a short prompt to validate configuration.
        
        Args:
            model_id: Identifier for the model
            prompt: Test prompt to validate API connection
            streaming: Whether to use streaming (ignored for testing)
            timeout: Maximum time to wait for response in seconds
            
        Returns:
            Dictionary with test results
        """
        try:
            # If sample response is provided, use it instead of making an actual API call
            if hasattr(self, 'sample_response') and self.sample_response:
                self.logger.info("Using provided sample response for validation")
                start_time = time.time()
                
                try:
                    import json
                    sample_json = json.loads(self.sample_response)
                    
                    # Use the configured json_path to extract the value if available
                    extracted_field = None
                    if hasattr(self, 'json_path') and self.json_path:
                        extracted_value = self._extract_from_json_path(sample_json, self.json_path)
                        
                        if extracted_value is not None:
                            # Convert to string if it's not already
                            if not isinstance(extracted_value, str):
                                extracted_value = str(extracted_value)
                                
                            # Store the extracted field info
                            extracted_field = {
                                "path": self.json_path,
                                "value": extracted_value
                            }
                                
                            response_time = time.time() - start_time
                            return {
                                "success": True,
                                "response": extracted_value,
                                "response_time": response_time,
                                "model": model_id,
                                "provider": "custom-api",
                                "is_sample": True,
                                "extracted_field": extracted_field
                            }
                    
                    # Fallback if json_path didn't work: try common patterns
                    for field in ["result", "response", "text", "content", "output", "message"]:
                        if field in sample_json and isinstance(sample_json[field], (str, bool, int, float)):
                            extracted_field = {
                                "path": field,
                                "value": str(sample_json[field])
                            }
                            return {
                                "success": True,
                                "response": str(sample_json[field]),
                                "response_time": time.time() - start_time,
                                "model": model_id,
                                "provider": "custom-api",
                                "is_sample": True,
                                "extracted_field": extracted_field
                            }
                    
                    # Return the whole sample as string if we couldn't extract anything
                    return {
                        "success": True,
                        "response": f"Sample response validated, but could not extract specific field. Raw JSON: {str(sample_json)[:100]}...",
                        "response_time": time.time() - start_time,
                        "model": model_id,
                        "provider": "custom-api",
                        "is_sample": True,
                        "raw_response": sample_json
                    }
                    
                except Exception as sample_error:
                    self.logger.warning(f"Error processing sample response: {str(sample_error)}")
                    # Continue with actual API test if sample fails
            
            # Make an actual API call
            start_time = time.time()
            
            # Clear previous values
            if hasattr(self, 'last_raw_response'):
                delattr(self, 'last_raw_response')
            if hasattr(self, 'last_extracted_value'):
                delattr(self, 'last_extracted_value')
                
            # Use a single character as the test prompt to minimize potential issues
            test_prompt = "x"
            
            try:
                # Log what we're doing
                if self.verbose:
                    self.logger.info(f"Testing API connection with minimal test prompt: '{test_prompt}'")
                
                # Use a very short timeout for the test
                test_timeout = min(timeout, 20)  # Cap at 20 seconds max for testing
                
                response = await asyncio.wait_for(
                    self.generate(model_id, test_prompt, max_tokens=5, temperature=0.7, timeout=test_timeout),
                    timeout=test_timeout
                )
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": f"Timeout error: API did not respond within {test_timeout} seconds",
                    "model": model_id,
                    "provider": "custom-api"
                }
            except Exception as gen_error:
                error_msg = str(gen_error)
                
                # Check for common curl errors and provide more helpful messages
                if "Could not resolve host" in error_msg:
                    detailed_error = (
                        "The curl command is treating the prompt as separate URLs. "
                        "This is often caused by unquoted spaces in the command. "
                        "Please ensure your curl command has the prompt placeholder properly enclosed in quotes "
                        "within the JSON payload: {'prompt': '{prompt}'}"
                    )
                    return {
                        "success": False,
                        "error": f"Curl command error: {error_msg[:200]}...",
                        "model": model_id,
                        "provider": "custom-api",
                        "details": detailed_error
                    }
                elif "syntax error" in error_msg.lower() or "unexpected" in error_msg.lower():
                    detailed_error = (
                        "There appears to be a syntax error in your curl command. "
                        "This is often caused by mismatched quotes or braces. "
                        "Please check your curl command carefully."
                    )
                    return {
                        "success": False,
                        "error": f"Curl command syntax error: {error_msg[:200]}...",
                        "model": model_id,
                        "provider": "custom-api",
                        "details": detailed_error
                    }
                elif "curl command failed" in error_msg.lower():
                    # Curl command error - provide more specific guidance
                    return {
                        "success": False,
                        "error": f"Curl command error: {error_msg[:200]}...",
                        "model": model_id,
                        "provider": "custom-api",
                        "details": "Check that your curl command is valid and that the API endpoint is accessible."
                    }
                else:
                    # General error
                    return {
                        "success": False,
                        "error": f"Generation error: {error_msg[:200]}...",
                        "model": model_id,
                        "provider": "custom-api"
                    }
            
            # Check for empty response
            if not response:
                return {
                    "success": False,
                    "error": "Empty response from API",
                    "model": model_id,
                    "provider": "custom-api"
                }
                
            # Check if response contains an error message
            if isinstance(response, str) and response.startswith("Error:"):
                return {
                    "success": False,
                    "error": response,
                    "model": model_id,
                    "provider": "custom-api"
                }
                
            if isinstance(response, dict) and "error" in response:
                return {
                    "success": False,
                    "error": str(response["error"]),
                    "model": model_id,
                    "provider": "custom-api"
                }
                
            # Success case - Include extracted field info if available
            response_time = time.time() - start_time
            result = {
                "success": True,
                "response": response,
                "response_time": response_time,
                "model": model_id,
                "provider": "custom-api"
            }
            
            # Add the extracted field information if available
            if hasattr(self, 'last_extracted_value'):
                result["extracted_field"] = self.last_extracted_value
                
            # Add the raw response if available
            if hasattr(self, 'last_raw_response'):
                result["raw_response"] = self.last_raw_response
                
            return result
            
        except Exception as e:
            # Log the full exception for debugging
            if self.verbose:
                import logging
                logging.error(f"Error testing custom API: {str(e)}")
                import traceback
                traceback.print_exc()
                
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "model": model_id,
                "provider": "custom-api"
            } 