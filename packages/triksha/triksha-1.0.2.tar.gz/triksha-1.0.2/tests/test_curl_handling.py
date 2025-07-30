#!/usr/bin/env python3
"""Test script for improved curl command handling in CustomAPIHandler."""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from benchmarks.models.handlers.custom_api_handler import CustomAPIHandler


async def test_curl_format_handling():
    """Test various curl command formats."""
    print("\n=== Testing Curl Command Format Handling ===")
    
    # Test cases with different curl command formats
    test_cases = [
        {
            "name": "Single-line curl command",
            "curl_cmd": 'curl --location "http://example.com/api" --header "Content-Type: application/json" --data \'{"prompt": "{prompt}", "max_tokens": 100}\'',
            "expected_placeholder": "{prompt}"
        },
        {
            "name": "Multi-line curl command with backslashes",
            "curl_cmd": '''curl --location "http://example.com/api" \\
            --header "Content-Type: application/json" \\
            --data '{
                "prompt": "{prompt}",
                "max_tokens": 100
            }'
            ''',
            "expected_placeholder": "{prompt}"
        },
        {
            "name": "Curl command with quoted prompt placeholder",
            "curl_cmd": 'curl "http://example.com/api" -H "Content-Type: application/json" -d \'{"prompt": "{prompt}", "params": {"temperature": 0.7}}\'',
            "expected_placeholder": "{prompt}"
        },
        {
            "name": "Curl command with newlines in JSON",
            "curl_cmd": '''curl http://example.com/api -H "Content-Type: application/json" -d '{
  "prompt": "{prompt}",
  "tokens": 1000,
  "stream": false
}'
            ''',
            "expected_placeholder": "{prompt}"
        },
        {
            "name": "Curl command with custom placeholder",
            "curl_cmd": 'curl http://example.com/api -d \'{"text": "USER_PROMPT_HERE", "options": {"max_tokens": 500}}\'',
            "expected_placeholder": "USER_PROMPT_HERE"
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. Testing: {test_case['name']}")
        print("-" * 50)
        
        # Create handler with the test curl command
        handler = CustomAPIHandler(
            name=f"test-curl-{i}",
            curl_command=test_case["curl_cmd"],
            prompt_placeholder=test_case["expected_placeholder"],
            verbose=True
        )
        
        # Test the internal _generate_with_curl method by mocking it
        # This is a basic verification that the command is properly formatted
        try:
            # We need to patch the communicate method to avoid actually running curl
            original_create_subprocess = asyncio.create_subprocess_shell
            
            async def mock_create_subprocess_shell(cmd, stdout=None, stderr=None):
                class MockProcess:
                    def __init__(self):
                        self.returncode = 0
                    
                    async def communicate(self):
                        # Return a mock JSON response
                        return (
                            b'{"choices":[{"message":{"content":"This is a test response"}}]}', 
                            b''
                        )
                
                print(f"Formatted curl command:\n{cmd}")
                # Verify the command contains the placeholder or has been replaced
                prompt_value = "This is a test prompt"
                if prompt_value in cmd:
                    print("✓ Command contains the test prompt (placeholder was properly replaced)")
                else:
                    print("⚠ Command doesn't contain the test prompt")
                    
                return MockProcess()
            
            # Replace the create_subprocess_shell function temporarily
            asyncio.create_subprocess_shell = mock_create_subprocess_shell
            
            # Now call the internal method with a test prompt
            try:
                # We're not really interested in the return value here,
                # just that the command is formatted correctly
                await handler._generate_with_curl("This is a test prompt", 100, 0.7)
                print("✓ Command processed successfully")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
            
            # Restore the original function
            asyncio.create_subprocess_shell = original_create_subprocess
            
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
    
    print("\n=== Curl Command Format Tests Complete ===")


async def test_response_processing():
    """Test processing of different API response formats."""
    print("\n=== Testing Response Format Processing ===")
    
    # Define various response format tests
    response_formats = [
        {
            "name": "OpenAI Chat Completion",
            "data": {
                "choices": [
                    {"message": {"content": "This is a test response from OpenAI"}}
                ]
            },
            "expected": "This is a test response from OpenAI"
        },
        {
            "name": "OpenAI Completion",
            "data": {
                "choices": [
                    {"text": "This is a test completion response"}
                ]
            },
            "expected": "This is a test completion response"
        },
        {
            "name": "Gemini Response",
            "data": {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "This is a test response from Gemini"}
                            ]
                        }
                    }
                ]
            },
            "expected": "This is a test response from Gemini"
        },
        {
            "name": "Anthropic Claude 3 Response",
            "data": {
                "content": [
                    {"type": "text", "text": "This is a test response from Claude"}
                ]
            },
            "expected": "This is a test response from Claude"
        },
        {
            "name": "Simple JSON Response",
            "data": {
                "response": "This is a simple response"
            },
            "expected": "This is a simple response"
        },
        {
            "name": "Custom JSON Path",
            "data": {
                "nested": {
                    "deeply": {
                        "result": "This is a deeply nested result"
                    }
                }
            },
            "json_path": "nested.deeply.result",
            "expected": "This is a deeply nested result"
        },
    ]
    
    # Create a handler to test response processing
    handler = CustomAPIHandler(
        name="test-response-processor",
        curl_command="echo 'test'",  # Not used in this test
        verbose=True
    )
    
    # Test each response format
    for i, test_case in enumerate(response_formats):
        print(f"\n{i+1}. Testing: {test_case['name']}")
        print("-" * 50)
        
        # Set JSON path if specified in the test case
        if "json_path" in test_case:
            handler.json_path = test_case["json_path"]
        else:
            handler.json_path = None
            
        # Process the response
        result = handler._process_response(test_case["data"])
        
        # Check if the result matches the expected output
        if result == test_case["expected"]:
            print(f"✓ Success: Got expected result: {result}")
        else:
            print(f"✗ Failure: Expected '{test_case['expected']}', got '{result}'")
    
    print("\n=== Response Format Tests Complete ===")


async def main():
    """Run all tests."""
    try:
        await test_curl_format_handling()
        await test_response_processing()
        print("\n✓ All tests completed")
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 