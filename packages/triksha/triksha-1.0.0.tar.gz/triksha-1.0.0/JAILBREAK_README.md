# Jailbreak Generator

This tool generates and tests jailbreak prompts against language models. It uses a multi-agent approach to create sophisticated prompts that attempt to bypass AI safety mechanisms.

⚠️ **IMPORTANT: For Educational and Research Purposes Only** ⚠️

This tool is provided for educational, research, and defensive testing purposes only. It should be used responsibly and ethically to understand and improve AI safety mechanisms.

## Prerequisites

Before running the jailbreak generator, ensure you have the following prerequisites:

1. Python 3.8 or higher
2. Required Python packages (install with `pip install -r requirements.txt`):
   - requests
   - openai (for OpenAI models)
   - anthropic (for Claude models)
   - google-generativeai (for Gemini models)

3. Access to at least one of the following:
   - Ollama running locally with models
   - OpenAI API key
   - Anthropic API key
   - Google AI API key

## Environment Setup

Set up your environment variables based on the models you want to test:

```bash
# For OpenAI models
export OPENAI_API_KEY="your-api-key"

# For Anthropic models
export ANTHROPIC_API_KEY="your-api-key"

# For Google AI (Gemini) models
export GOOGLE_API_KEY="your-api-key"

# For Ollama (default is localhost:11434)
export OLLAMA_HOST="http://localhost:11434"
```

## Usage

The basic usage of the jailbreak generator is as follows:

```bash
python jailbreak_test.py --target-model "gemma3:1b" --goal "data exfiltration" --iterations 2
```

### Command-line Arguments

- `--target-model`: Target model for jailbreak generation and testing (default: "gemma3:1b")
  - Format for OpenAI models: "openai:gpt-4"
  - Format for Anthropic models: "anthropic:claude-3-opus"
  - Format for Gemini models: "gemini:gemini-pro"
  - Format for Ollama models: "ollama:gemma3:1b" or simply "gemma3:1b"

- `--goal`: The goal for the jailbreak prompt (default: "data exfiltration")
  - Examples: "harmful content generation", "security bypass", "code injection"

- `--iterations`: Number of iterations for refining the jailbreak (default: 2)
  - Higher values may produce better results but take longer

- `--output`: Output file to save results (default: jailbreak_results_<timestamp>.json)

## How It Works

The jailbreak generator uses a multi-agent system to create sophisticated jailbreak prompts:

1. **Strategy Agent**: Develops an attack strategy based on the target model and goal
2. **Content Agent**: Generates the core content of the jailbreak prompt
3. **Evasion Agent**: Applies various evasion techniques to bypass safety filters
4. **Evaluation Agent**: Tests the jailbreak against the target model and evaluates its effectiveness

The system iteratively refines the jailbreak through multiple iterations, improving it based on feedback from the evaluation.

## Examples

### Testing against Ollama with Gemma 3 1B:

```bash
python jailbreak_test.py --target-model "gemma3:1b" --goal "data exfiltration" --iterations 2
```

### Testing against OpenAI's GPT-4:

```bash
export OPENAI_API_KEY="your-api-key"
python jailbreak_test.py --target-model "openai:gpt-4" --goal "data exfiltration" --iterations 3
```

### Testing against Anthropic's Claude:

```bash
export ANTHROPIC_API_KEY="your-api-key"
python jailbreak_test.py --target-model "anthropic:claude-3-sonnet" --goal "security bypass" --iterations 2
```

## Analyzing Results

After running the jailbreak generator, you can analyze the results to understand:

1. The effectiveness of different jailbreak techniques
2. Model vulnerabilities and areas for improvement
3. How safety mechanisms respond to various attack strategies

Results are saved in JSON format and can be further processed for detailed analysis.

## Responsible Use Guidelines

- Always use this tool for legitimate research and educational purposes
- Do not deploy generated jailbreaks against production systems
- Report any significant findings to the respective model providers
- Be transparent about your research methodology and goals

## Troubleshooting

If you encounter issues:

1. Ensure all required environment variables are set
2. Verify that the target model is accessible (Ollama running, API keys valid)
3. Check logs for detailed error messages
4. Ensure all dependencies are installed 