# Custom Guardrail Registration Feature

This document describes the custom guardrail registration feature implemented in the Dravik project, which allows users to register and test custom guardrail endpoints for AI safety and content moderation.

## Overview

The custom guardrail registration feature enables users to:
- Register custom guardrail APIs using curl commands (including multi-line commands)
- Configure success/failure detection keywords with auto-detection
- Test guardrails with sample prompts
- View and manage registered guardrails
- Delete guardrails when no longer needed

## Features

### 1. Guardrail Registration
- **Interactive CLI Interface**: Step-by-step prompts for easy registration
- **Multi-line Curl Command Support**: Properly handles complex, multi-line curl commands
- **Smart Input Handling**: Uses rich.prompt for better user experience
- **Flexible Prompt Placeholders**: Configurable placeholder for prompt injection
- **Automatic Placeholder Detection**: Smart detection and insertion of placeholders
- **Sample Response Analysis**: Automatic keyword detection from sample responses
- **Manual Keyword Configuration**: Override auto-detected keywords if needed

### 2. Guardrail Management
- **List All Guardrails**: View registered guardrails in a formatted table
- **Detailed View**: Inspect guardrail configuration, keywords, and sample responses
- **Delete Guardrails**: Remove guardrails with confirmation prompts
- **Configuration Storage**: Persistent storage in user's home directory

### 3. Guardrail Testing
- **Interactive Testing**: Test guardrails with custom prompts
- **Sample Prompt Testing**: Pre-defined test cases for common scenarios
- **Real-time Results**: Immediate feedback with confidence scores
- **Response Analysis**: Automatic classification as BLOCKED/ALLOWED

## Usage

### Accessing the Feature

1. Run the CLI: `python -m cli.main`
2. Select "Manage Custom Model Assets" (option 2)
3. Choose from:
   - "Add New Guardrail" - Register a new guardrail
   - "View Guardrails" - Manage existing guardrails

### Registering a Guardrail

1. **Guardrail Name**: Enter a unique name for your guardrail
2. **Curl Command**: Provide the complete curl command with placeholder (multi-line supported)
3. **Prompt Placeholder**: Specify where the prompt should be injected (default: `{prompt}`)
4. **Sample Responses**: Provide examples of success and failure responses
5. **Keyword Configuration**: Review and adjust auto-detected keywords
6. **Testing**: Optionally test the guardrail immediately after registration

### Example Registration

#### Simple Curl Command
```bash
curl -X POST "https://api.openai.com/v1/moderations" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "{prompt}"}'
```

#### Complex Multi-line Curl Command
```bash
curl --location 'http://10.83.33.0/fk_jarvis_aegis/v1/stream/evaluate_prompt' \
--header 'Content-Type: application/json' \
--data '{
    "input": [
        {
            "name": "list_checker",
            "required": true,
            "mandatory_accept": false,
            "parameters": {"fuzzy": "true"},
            "is_llm": false
        },
        {
            "name": "llm_guard",
            "required": true,
            "mandatory_accept": false,
            "parameters": "{}",
            "is_llm": true
        }
    ],
    "min_consensus": 2,
    "llm_payload": {
        "model": "Llama-3.1-8B",
        "messages": [
            {
                "role": "user",
                "content": "{prompt}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        "top_p": 0.9,
        "stream": false
    },
    "llm_endpoint": "http://10.83.34.18/predict"
}'
```

**Success Response Example:**
```json
{
  "id": "modr-XXXXX",
  "model": "text-moderation-007",
  "results": [
    {
      "flagged": false,
      "categories": {
        "sexual": false,
        "hate": false,
        "harassment": false
      }
    }
  ]
}
```

**Failure Response Example:**
```json
{
  "id": "modr-XXXXX",
  "model": "text-moderation-007",
  "results": [
    {
      "flagged": true,
      "categories": {
        "sexual": false,
        "hate": true,
        "harassment": false
      }
    }
  ]
}
```

**Auto-detected Keywords:**
- Success: `["flagged", "false"]`
- Failure: `["flagged", "true"]`

## Input Handling Improvements

### Multi-line Curl Command Support
The feature now properly handles complex, multi-line curl commands using `rich.prompt.Prompt.ask()`:

- **Automatic Command Cleaning**: Multi-line commands are automatically cleaned and formatted
- **Command Preview**: Shows a cleaned summary of the command for confirmation
- **Better Validation**: Improved error messages and guidance
- **Smart Placeholder Detection**: Automatically detects common patterns for placeholder insertion

### Automatic Placeholder Detection
The system can automatically detect and insert placeholders in common patterns:

- `"text": "value"` → `"text": "{prompt}"`
- `"prompt": "value"` → `"prompt": "{prompt}"`
- `"input": "value"` → `"input": "{prompt}"`
- `"query": "value"` → `"query": "{prompt}"`
- `"content": "value"` → `"content": "{prompt}"`

### Enhanced User Experience
- **Rich Formatting**: All prompts use rich formatting for better readability
- **Default Values**: Sensible defaults for sample responses
- **Inquirer Integration**: Better confirmation dialogs
- **Improved Error Handling**: Clear error messages with helpful suggestions

## Configuration Storage

Guardrail configurations are stored in:
```
~/dravik/config/guardrails/<guardrail_name>.json
```

### Configuration Format

```json
{
  "type": "custom-guardrail",
  "curl_command": "curl --location 'https://api.example.com/moderate' ...",
  "prompt_placeholder": "{prompt}",
  "success_keywords": ["safe", "approved", "clean"],
  "failure_keywords": ["unsafe", "blocked", "harmful"],
  "success_response": "{\"status\": \"safe\", \"confidence\": 0.95}",
  "failure_response": "{\"status\": \"unsafe\", \"confidence\": 0.87}",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Programmatic Usage

### Using the Guardrail Handler

```python
from benchmarks.models.handlers.guardrail_handler import GuardrailHandler

# List available guardrails
available = GuardrailHandler.list_available_guardrails()
print(f"Available guardrails: {available}")

# Load a specific guardrail
handler = GuardrailHandler("my_guardrail", verbose=True)

# Get guardrail information
info = handler.get_guardrail_info()
print(f"Guardrail info: {info}")

# Test a prompt (async)
import asyncio
result = asyncio.run(handler.generate("test", "Hello, world!"))
print(f"Result: {result}")
```

### Response Format

The guardrail handler returns JSON responses with the following structure:

```json
{
  "status": "BLOCKED|ALLOWED|ERROR",
  "confidence": 0.85,
  "explanation": "Matched 2 failure keywords: ['unsafe', 'harmful']",
  "raw_response": "...",
  "guardrail": "guardrail_name"
}
```

## Testing Features

### Interactive Testing
- **Custom Prompts**: Test with user-provided prompts
- **Sample Prompts**: Pre-defined test cases including:
  - Safe content
  - Educational queries
  - Potentially harmful content
  - Malicious intent
  - Inappropriate content

### Test Results
Each test provides:
- **Status**: BLOCKED, ALLOWED, or ERROR
- **Confidence Score**: 0.0 to 1.0
- **Explanation**: Reasoning for the decision
- **Response Time**: Latency measurement

## Implementation Details

### Files Modified/Created

1. **`cli/core.py`**:
   - Added `register_custom_guardrail()` method with improved input handling
   - Added `_view_guardrails()` method
   - Added `_test_guardrail()` method
   - Added guardrail management to custom model assets menu
   - Integrated rich.prompt for better user experience
   - Added automatic placeholder detection and insertion

2. **`benchmarks/models/handlers/guardrail_handler.py`** (new):
   - Complete guardrail execution handler
   - Response analysis and keyword matching
   - Heuristic analysis for edge cases

3. **`benchmarks/models/handlers/__init__.py`**:
   - Added GuardrailHandler import

4. **`cli/commands/delete_dataset.py`**:
   - Fixed import issues for compatibility

### Key Features

- **Robust Error Handling**: Graceful handling of API failures and malformed responses
- **Flexible Keyword Matching**: Both exact and heuristic analysis
- **Secure Execution**: Temporary file approach for safe curl execution
- **Rich UI**: Colored output and formatted tables for better user experience
- **Persistent Storage**: Configuration saved to disk for reuse
- **Multi-line Input Support**: Proper handling of complex curl commands
- **Smart Validation**: Automatic placeholder detection and insertion

## Security Considerations

- **Input Sanitization**: Prompts are properly escaped in curl commands
- **Temporary Files**: Sensitive data is handled via temporary files that are cleaned up
- **API Key Protection**: Environment variables are used for API authentication
- **Command Injection Prevention**: Proper shell escaping and validation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Authentication**: Check that API keys are properly set in environment variables
3. **Network Issues**: Verify internet connectivity and API endpoint availability
4. **Permission Errors**: Ensure write permissions to `~/dravik/config/guardrails/`
5. **Multi-line Input Issues**: The improved input handling should resolve most curl command formatting issues

### Debug Mode

Enable verbose logging by setting `verbose=True` when creating the GuardrailHandler:

```python
handler = GuardrailHandler("my_guardrail", verbose=True)
```

### Testing the Improvements

Run the test script to verify the improved functionality:

```bash
python test_improved_guardrail_input.py
```

## Recent Improvements (v2.0)

### Enhanced Input Handling
- **Multi-line Curl Support**: Now properly handles complex, multi-line curl commands
- **Rich.prompt Integration**: Better user experience with formatted prompts
- **Automatic Command Cleaning**: Commands are automatically cleaned and formatted for display
- **Smart Placeholder Detection**: Automatic detection and insertion of prompt placeholders

### Better User Experience
- **Inquirer Integration**: Better confirmation dialogs and choices
- **Default Values**: Sensible defaults for all inputs
- **Improved Validation**: Better error messages with helpful suggestions
- **Rich Formatting**: All outputs use rich formatting for better readability

### Enhanced Error Handling
- **Automatic Placeholder Insertion**: System can automatically add placeholders to common patterns
- **Better Validation Messages**: Clear, actionable error messages
- **Graceful Fallbacks**: System continues to work even when auto-detection fails

## Future Enhancements

Potential improvements for future versions:
- **Batch Testing**: Test multiple prompts simultaneously
- **Performance Metrics**: Track response times and success rates
- **Integration with Benchmarks**: Use guardrails in automated testing pipelines
- **Advanced Analytics**: Detailed reporting and trend analysis
- **Custom Response Parsers**: Support for non-JSON response formats
- **Template Library**: Pre-built templates for common guardrail APIs

## Support

For issues or questions about the custom guardrail registration feature:
1. Check the troubleshooting section above
2. Review the configuration files in `~/dravik/config/guardrails/`
3. Run the test script: `python test_improved_guardrail_input.py`
4. Enable verbose logging for detailed error information
5. Test with the original test script: `python test_guardrail_feature.py` 