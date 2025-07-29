# Real Jailbreak Generator

This tool implements a real, working jailbreak generator that creates and tests prompts that attempt to bypass AI safety mechanisms. Unlike mock implementations, this version makes real API calls to language models and generates prompts on the fly using various jailbreak techniques.

⚠️ **WARNING: For Ethical Research Purposes Only** ⚠️

This tool is provided strictly for educational, research, and defensive testing purposes. It should only be used responsibly and ethically to understand and improve AI safety mechanisms. Misuse of this tool is strictly prohibited.

## Features

- **Real-time Jailbreak Generation**: Creates actual jailbreak prompts using various techniques
- **Direct Model Interaction**: Makes real API calls to test prompts against models
- **Multiple Techniques**: Implements several jailbreak techniques (DAN, Context Hacking, Role Playing, etc.)
- **Response Analysis**: Automatically evaluates model responses to determine jailbreak success
- **Detailed Reporting**: Produces comprehensive reports of jailbreak attempts and results

## Prerequisites

Before running the real jailbreak generator, ensure you have:

1. Python 3.8 or higher
2. Required Python packages:
   ```
   pip install requests
   ```

3. Ollama running locally with models installed (or API keys for other providers)

## Usage

The basic usage of the real jailbreak generator is:

```bash
python real_jailbreak_test.py --target-model "ollama:gemma3:1b" --goal "data exfiltration" --iterations 1 --technique DAN
```

### Command-line Arguments

- `--target-model`: Target model for jailbreak testing (default: "gemma3:1b")
  - Format for Ollama models: "ollama:gemma3:1b" (or simply "gemma3:1b")

- `--goal`: The goal for the jailbreak prompt (default: "data exfiltration")
  - Examples: "bypassing content filters", "generating harmful content", etc.

- `--iterations`: Number of refinement iterations (default: 2)
  - Higher values attempt more jailbreak variations

- `--technique`: Specific technique to use (optional)
  - Options: "DAN", "CONTEXT_HACKING", "ROLE_PLAYING", "DECEPTION", "ENCODING"
  - If omitted, techniques are selected randomly

- `--output`: Output file to save results (default: "real_jailbreak_results_<timestamp>.json")

## Implementation Details

### Jailbreak Techniques

1. **DAN (Do Anything Now)**: Uses the "Do Anything Now" persona to bypass restrictions
2. **Context Hacking**: Manipulates the context window with false system messages
3. **Role Playing**: Exploits role-playing scenarios to encourage harmful outputs
4. **Deception**: Uses deceptive framing (fiction writing, academic research, etc.)
5. **Encoding**: Hides harmful requests using base64 encoding or other transformations

### Evaluation Mechanism

The tool evaluates jailbreak success using:

- **Refusal Detection**: Checks for refusal patterns in responses
- **Compliance Detection**: Identifies signs that the model is complying with harmful requests
- **Success Scoring**: Calculates a score based on refusal patterns and compliance indicators

## Examples

### Testing with the DAN technique:

```bash
python real_jailbreak_test.py --target-model "ollama:gemma3:1b" --goal "data exfiltration" --technique DAN
```

### Testing with Context Hacking:

```bash
python real_jailbreak_test.py --target-model "ollama:gemma3:1b" --goal "bypassing content filters" --technique CONTEXT_HACKING
```

### Multiple iterations with random techniques:

```bash
python real_jailbreak_test.py --target-model "ollama:gemma3:1b" --goal "social engineering attacks" --iterations 5
```

## Understanding Results

The results JSON file contains:

- **id**: Unique identifier for the jailbreak attempt
- **goal**: The objective of the jailbreak
- **target_model**: The model tested against
- **generation_time**: How long the generation took
- **iterations**: Number of iterations completed
- **attempts**: Details of each jailbreak attempt
- **best_jailbreak**: The most successful jailbreak found
- **success**: Whether the jailbreak was successful
- **score**: The success score (0.0-1.0)

## Responsible Use

This tool should only be used:

- For legitimate research on AI safety
- To test and improve safety mechanisms
- In controlled, private environments
- With informed consent of model providers when applicable

Unauthorized or malicious use is strictly prohibited.

## Future Improvements

- Support for more LLM providers (OpenAI, Anthropic, Google, etc.)
- Additional jailbreak techniques
- More sophisticated response analysis
- Multi-step jailbreaking attempts
- Reinforcement learning for technique optimization

## Contributing

Contributions for improving this tool for research purposes are welcome. Please ensure all contributions adhere to responsible AI research practices.

## Disclaimer

This tool is provided as-is without any warranty. The authors are not responsible for any misuse or consequences arising from the use of this tool. 