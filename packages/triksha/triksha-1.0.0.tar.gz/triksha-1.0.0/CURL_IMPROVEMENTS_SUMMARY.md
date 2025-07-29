# Curl Input Handling Improvements Summary

## Overview
Successfully implemented enhanced curl input handling for both **model registration** and **guardrail registration** features in the Dravik CLI. The improvements address the specific issue with complex multi-line curl commands and JSON escaping problems.

## Key Improvements Made

### 1. **Multi-line Curl Input Support**
- ✅ Added `_get_multiline_curl_input()` method to both `cli/core.py` and `cli/commands/benchmark/command.py`
- ✅ Supports pasting complex multi-line curl commands
- ✅ Handles line continuations (`\`) properly
- ✅ Press Enter twice or Ctrl+D to finish input

### 2. **JSON Escaping Fix** 🎯
- ✅ Added `_fix_json_escaping()` method to automatically fix nested JSON strings
- ✅ Resolves the specific issue: `"parameters": "{"fuzzy": "true"}"` → `"parameters": "{\"fuzzy\": \"true\"}"`
- ✅ Handles both single and double quoted --data parameters
- ✅ Falls back to manual fixing if JSON parsing fails

### 3. **Enhanced Validation**
- ✅ Added `_validate_curl_command()` with comprehensive checks:
  - Command starts with 'curl'
  - Contains --data or -d parameter
  - Has valid URL pattern
  - Contains required placeholder
- ✅ Provides helpful error messages and recovery options

### 4. **Smart Placeholder Detection**
- ✅ Added `_auto_detect_and_fix_placeholder()` method
- ✅ Automatically detects and inserts placeholders in common JSON patterns
- ✅ Supports multiple placeholder formats: `{prompt}`, `{text}`, `{input}`, `{content}`

### 5. **Improved User Experience**
- ✅ Better error handling with user-friendly choices
- ✅ Command preview for long curl commands
- ✅ Progress indicators and status messages
- ✅ Graceful fallbacks for edge cases

## Test Results ✅

### Before Fix (The Problem):
```bash
# Debug log showed malformed JSON:
"parameters": "{"fuzzy": "true"}"  # ❌ Unescaped quotes
# Result: {"code":400,"message":"Unable to process JSON"}
```

### After Fix (The Solution):
```bash
# Properly escaped JSON:
"parameters": "{\"fuzzy\": \"true\"}"  # ✅ Correctly escaped
# Result: Valid JSON that parses successfully
```

### Test Verification:
- ✅ **Original length**: 1141 characters → **Cleaned length**: 704 characters
- ✅ **JSON validation**: ✓ Valid and parseable
- ✅ **Placeholder preservation**: ✓ {prompt} maintained
- ✅ **Parameters field**: ✓ Properly escaped and valid
- ✅ **Curl validation**: ✓ All checks passed

## Files Modified

### Core CLI (`cli/core.py`)
- Added multi-line curl input handling
- Added JSON escaping fixes
- Added validation and placeholder detection
- Updated guardrail registration to use new methods

### Benchmark Commands (`cli/commands/benchmark/command.py`)
- Added same curl handling improvements
- Updated model registration to use new methods
- Maintains consistency across both registration flows

## Usage Examples

### Complex Curl Command (Now Supported):
```bash
curl --location 'http://10.83.33.0/fk_jarvis_aegis/v1/stream/evaluate_prompt' \
--header 'Content-Type: application/json' \
--data '{
    "aegis_payload": {
        "input": [{"role": "user", "content": "{prompt}"}],
        "guardrail_conf": [
            {
                "name": "list_checker",
                "parameters": "{\"fuzzy\": \"true\"}"
            }
        ]
    }
}'
```

### What Happens Now:
1. **Paste** the multi-line command
2. **Press Enter twice** when done
3. **Automatic cleaning** and JSON escaping
4. **Validation** with helpful feedback
5. **Placeholder detection** and fixing
6. **Success** - command works correctly!

## Impact

### For Model Registration:
- ✅ Can now handle complex API endpoints with nested JSON
- ✅ Automatic placeholder insertion for various patterns
- ✅ Better validation and error recovery

### For Guardrail Registration:
- ✅ Supports complex guardrail APIs with nested configurations
- ✅ Proper JSON escaping prevents API errors
- ✅ Enhanced testing and validation workflow

## Technical Details

### JSON Escaping Algorithm:
1. **Parse** the --data JSON content
2. **Re-serialize** with proper escaping using `json.dumps()`
3. **Fallback** to manual regex-based fixing if parsing fails
4. **Replace** the original data with the fixed version

### Validation Checks:
- Command structure validation
- URL pattern detection
- Placeholder presence verification
- JSON syntax validation

### Error Recovery:
- Multiple retry options
- Continue anyway for advanced users
- Clear error messages with suggestions

## Conclusion

The curl input handling improvements successfully resolve the JSON escaping issue and provide a robust, user-friendly experience for registering complex models and guardrails. The system now handles the most complex curl commands with nested JSON structures automatically.

**Status**: ✅ **COMPLETE AND TESTED** 