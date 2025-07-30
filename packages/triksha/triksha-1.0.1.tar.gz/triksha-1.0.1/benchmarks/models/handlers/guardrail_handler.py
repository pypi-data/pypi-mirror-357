import os
import re
import json
import asyncio
import aiohttp
import subprocess
import shlex
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from pathlib import Path
import time
import uuid

from ..base_handler import ModelHandler

# Configure logger
logger = logging.getLogger(__name__)


class GuardrailHandler(ModelHandler):
    """Handler for executing custom guardrails."""

    def __init__(
        self,
        guardrail_name: str,
        verbose: bool = False
    ):
        """Initialize the guardrail handler
        
        Args:
            guardrail_name: Name of the registered guardrail to load
            verbose: Whether to output verbose logs
        """
        self.guardrail_name = guardrail_name
        self.verbose = verbose
        self.config = None
        
        # Configure logging
        self.logger = logging.getLogger(f"GuardrailHandler:{guardrail_name}")
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(log_level)
        
        # Load guardrail configuration
        self._load_guardrail_config()
        
        if verbose:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            logger.addHandler(handler)
    
    def _load_guardrail_config(self):
        """Load the guardrail configuration from disk"""
        try:
            config_dir = Path.home() / "dravik" / "config" / "guardrails"
            config_file = config_dir / f"{self.guardrail_name}.json"
            
            if not config_file.exists():
                raise FileNotFoundError(f"Guardrail configuration not found: {self.guardrail_name}")
                
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                
            if self.verbose:
                self.logger.debug(f"Loaded guardrail config for {self.guardrail_name}")
                
        except Exception as e:
            raise ValueError(f"Failed to load guardrail {self.guardrail_name}: {str(e)}")
    
    async def list_models(self) -> List[Dict[str, str]]:
        """List available models.
        
        Returns:
            List containing only this guardrail
        """
        return [{
            "id": self.guardrail_name,
            "name": self.guardrail_name,
            "provider": "guardrail"
        }]
    
    async def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Execute the guardrail against the given prompt.
        
        Args:
            model_id: The model ID (ignored for guardrails)
            prompt: The prompt to test against the guardrail
            **kwargs: Additional arguments
            
        Returns:
            The guardrail response indicating pass/fail status
        """
        try:
            timeout = kwargs.pop('timeout', 60)
            
            # Execute the guardrail
            response_data = await self._execute_guardrail(prompt, **kwargs)
            
            # Store the raw response for later reference
            self.last_raw_response = response_data
            
            # Analyze the response to determine pass/fail
            is_blocked, confidence, explanation = self._analyze_response(response_data)
            
            # Format the result
            result = {
                "status": "BLOCKED" if is_blocked else "ALLOWED",
                "confidence": confidence,
                "explanation": explanation,
                "raw_response": response_data,
                "guardrail": self.guardrail_name
            }
            
            # Store the analyzed result
            self.last_analysis = result
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            if self.verbose:
                logger.error(f"Error in guardrail execution: {str(e)}")
            return json.dumps({
                "status": "ERROR",
                "error": str(e),
                "guardrail": self.guardrail_name
            }, indent=2)
    
    async def _execute_guardrail(self, prompt: str, **kwargs) -> str:
        """Execute the guardrail using the stored curl command.
        
        Args:
            prompt: The prompt to test
            **kwargs: Additional parameters
            
        Returns:
            The raw response from the guardrail API
        """
        tmp_file = None
        try:
            # Get the curl command and placeholder from config
            curl_cmd = self.config.get('curl_command', '').strip()
            prompt_placeholder = self.config.get('prompt_placeholder', '{prompt}')
            
            if not curl_cmd:
                raise ValueError("No curl command found in guardrail configuration")
            
            # Clean up the curl command
            curl_cmd = re.sub(r'\s+', ' ', curl_cmd)
            
            # Use temp file approach for the payload
            tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            
            # Check if the command is using a data payload
            # Fixed regex pattern that properly handles quoted JSON payloads
            data_pattern = r'(?:-d|--data)\s+([\'"])(.*?)\1'
            data_match = re.search(data_pattern, curl_cmd, re.DOTALL)
            
            if data_match:
                quote_char = data_match.group(1)
                data_content = data_match.group(2)
                
                if prompt_placeholder in data_content:
                    try:
                        # Try parsing as JSON and replace the placeholder
                        json_data = json.loads(data_content)
                        self._replace_in_json(json_data, prompt_placeholder, prompt)
                        json.dump(json_data, tmp_file, ensure_ascii=False)
                    except json.JSONDecodeError:
                        # Not valid JSON, do a simple string replacement
                        data_content_updated = data_content.replace(prompt_placeholder, 
                                                                   json.dumps(prompt)[1:-1])
                        tmp_file.write(data_content_updated)
                    
                    tmp_file.close()
                    
                    # Replace the data part in the curl command with the temp file
                    original_data_arg = data_match.group(0)  # The entire matched string
                    curl_cmd = curl_cmd.replace(original_data_arg, f'-d @{tmp_file.name}')
                else:
                    tmp_file.close()
            else:
                # Try simple placeholder replacement in the entire command
                curl_cmd = curl_cmd.replace(prompt_placeholder, shlex.quote(prompt))
                tmp_file.close()
            
            if self.verbose:
                self.logger.debug(f"Executing guardrail command: {curl_cmd}")
            
            # Execute the curl command
            process = await asyncio.create_subprocess_shell(
                curl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise RuntimeError(f"Curl command failed with return code {process.returncode}: {error_msg}")
            
            response = stdout.decode('utf-8')
            
            if self.verbose:
                self.logger.debug(f"Guardrail response: {response[:200]}...")
            
            return response
            
        except Exception as e:
            if self.verbose:
                self.logger.error(f"Error executing guardrail: {str(e)}")
            raise
        finally:
            # Clean up temp file
            if tmp_file and os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)
    
    def _replace_in_json(self, obj, placeholder, replacement):
        """Recursively replace placeholder in JSON object."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and placeholder in value:
                    obj[key] = value.replace(placeholder, replacement)
                elif isinstance(value, (dict, list)):
                    self._replace_in_json(value, placeholder, replacement)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and placeholder in item:
                    obj[i] = item.replace(placeholder, replacement)
                elif isinstance(item, (dict, list)):
                    self._replace_in_json(item, placeholder, replacement)
    
    def _analyze_response(self, response_data: str) -> Tuple[bool, float, str]:
        """Analyze the guardrail response to determine if content should be blocked.
        
        Args:
            response_data: Raw response from the guardrail API
            
        Returns:
            Tuple of (is_blocked, confidence, explanation)
        """
        try:
            # Get keywords from config
            success_keywords = self.config.get('success_keywords', [])
            failure_keywords = self.config.get('failure_keywords', [])
            
            # Try to parse as JSON first
            try:
                response_json = json.loads(response_data)
                response_text = json.dumps(response_json).lower()
            except json.JSONDecodeError:
                response_text = response_data.lower()
            
            # Count keyword matches
            success_matches = sum(1 for keyword in success_keywords if keyword.lower() in response_text)
            failure_matches = sum(1 for keyword in failure_keywords if keyword.lower() in response_text)
            
            total_keywords = len(success_keywords) + len(failure_keywords)
            
            if total_keywords == 0:
                # No keywords defined, try to analyze the response content
                return self._heuristic_analysis(response_data)
            
            # Determine result based on keyword matches
            if success_matches > failure_matches:
                confidence = (success_matches / len(success_keywords)) if success_keywords else 0.5
                explanation = f"Matched {success_matches} success keywords: {[k for k in success_keywords if k.lower() in response_text]}"
                return False, confidence, explanation
            elif failure_matches > success_matches:
                confidence = (failure_matches / len(failure_keywords)) if failure_keywords else 0.5
                explanation = f"Matched {failure_matches} failure keywords: {[k for k in failure_keywords if k.lower() in response_text]}"
                return True, confidence, explanation
            else:
                # Tie or no matches - use heuristic analysis
                return self._heuristic_analysis(response_data)
                
        except Exception as e:
            if self.verbose:
                self.logger.error(f"Error analyzing response: {str(e)}")
            return False, 0.0, f"Analysis error: {str(e)}"
    
    def _heuristic_analysis(self, response_data: str) -> Tuple[bool, float, str]:
        """Perform heuristic analysis when keyword matching is inconclusive.
        
        Args:
            response_data: Raw response from the guardrail API
            
        Returns:
            Tuple of (is_blocked, confidence, explanation)
        """
        response_lower = response_data.lower()
        
        # Common patterns that suggest blocking
        block_patterns = [
            'blocked', 'denied', 'rejected', 'violation', 'inappropriate',
            'harmful', 'unsafe', 'prohibited', 'not allowed', 'error'
        ]
        
        # Common patterns that suggest allowing
        allow_patterns = [
            'allowed', 'approved', 'safe', 'ok', 'acceptable', 'passed',
            'clean', 'compliant', 'success'
        ]
        
        block_score = sum(1 for pattern in block_patterns if pattern in response_lower)
        allow_score = sum(1 for pattern in allow_patterns if pattern in response_lower)
        
        if block_score > allow_score:
            confidence = min(0.8, block_score / len(block_patterns))
            return True, confidence, f"Heuristic analysis suggests blocking (score: {block_score} vs {allow_score})"
        elif allow_score > block_score:
            confidence = min(0.8, allow_score / len(allow_patterns))
            return False, confidence, f"Heuristic analysis suggests allowing (score: {allow_score} vs {block_score})"
        else:
            return False, 0.3, "Heuristic analysis inconclusive, defaulting to allow"
    
    def get_guardrail_info(self) -> Dict[str, Any]:
        """Get information about the loaded guardrail.
        
        Returns:
            Dictionary with guardrail configuration details
        """
        if not self.config:
            return {"error": "No guardrail configuration loaded"}
        
        return {
            "name": self.guardrail_name,
            "type": self.config.get("type", "unknown"),
            "created_at": self.config.get("created_at", "unknown"),
            "success_keywords": self.config.get("success_keywords", []),
            "failure_keywords": self.config.get("failure_keywords", []),
            "prompt_placeholder": self.config.get("prompt_placeholder", "{prompt}"),
            "has_curl_command": bool(self.config.get("curl_command")),
        }
    
    @classmethod
    def list_available_guardrails(cls) -> List[str]:
        """List all available registered guardrails.
        
        Returns:
            List of guardrail names
        """
        try:
            config_dir = Path.home() / "dravik" / "config" / "guardrails"
            if not config_dir.exists():
                return []
            
            guardrail_files = list(config_dir.glob("*.json"))
            return [f.stem for f in guardrail_files]
            
        except Exception:
            return []
    
    async def test_prompt(self, model_id: str, prompt: str, streaming: bool = False, timeout: int = 30) -> Dict:
        """Test a prompt against the guardrail.
        
        Args:
            model_id: The model ID (ignored)
            prompt: The prompt to test
            streaming: Whether to use streaming (ignored for guardrails)
            timeout: Timeout for the request
            
        Returns:
            Test result dictionary
        """
        try:
            start_time = time.time()
            result = await self.generate(model_id, prompt, timeout=timeout)
            end_time = time.time()
            
            return {
                "success": True,
                "response": result,
                "latency": end_time - start_time,
                "model": self.guardrail_name,
                "prompt": prompt,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.guardrail_name,
                "prompt": prompt,
                "timestamp": time.time()
            } 