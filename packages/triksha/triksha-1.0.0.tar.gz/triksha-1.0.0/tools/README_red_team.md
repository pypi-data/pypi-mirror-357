# Red Teaming Tools

This directory contains advanced tools for LLM red teaming, leveraging Markov-based techniques for dynamic adversarial prompt generation.

## Overview

These tools allow you to:

1. Generate synthetic adversarial datasets using static and dynamic Markov-based techniques
2. Evaluate models on these datasets to measure their resilience to jailbreak attempts
3. Integrate with various models (OpenAI, Gemini, Ollama) for comprehensive red teaming

## Prerequisites

- Python 3.8+
- Required packages: `rich`, `requests`, `openai`, `google-generativeai` (optional)
- API keys for commercial models (if used)

## Red Teaming Conversation Tool

The main red teaming interface is available through `benchmark/conversation_red_teaming.py`. This tool provides an interactive UI for running red teaming conversations between models.

```bash
python -m benchmark.conversation_red_teaming
```

### Features:

- **Three-Phase Red Teaming**: Uses an advisor model to profile the target and develop strategies, then a red team model to execute attacks
- **Multiple Attack Vectors**: DAN, Likert, Crescendo, Jailbreak, RolePlaying, and Markov-based variants
- **Multi-Model Support**: Works with OpenAI, Gemini, Ollama, and HuggingFace models
- **Memory**: Remembers recently used models for convenience

### Usage Instructions:

1. Select Red Team and Advisor models (can use local HuggingFace models or API-based models)
2. Select a target model to test (OpenAI, Ollama, or Gemini)
3. Choose an attack vector and number of conversation turns
4. Observe the automated red teaming session and results

## Synthetic Dataset Generation

Generate diverse synthetic red teaming datasets using static templates and dynamic Markov-based techniques.

```bash
# List available techniques
python tools/generate_red_team_dataset.py --list-techniques

# Generate a dataset with 100 samples using all techniques
python tools/generate_red_team_dataset.py --output datasets/red_team_synthetic.jsonl --num-samples 100

# Generate dataset with specific techniques and custom format
python tools/generate_red_team_dataset.py --output datasets/red_team_dan.json --format json \
  --techniques DAN RolePlaying --num-samples 50
```

### Options:

- `--output, -o`: Path to save the dataset (default: datasets/red_team_synthetic.jsonl)
- `--num-samples, -n`: Number of samples to generate (default: 1000)
- `--techniques, -t`: Space-separated list of techniques to use (default: all)
- `--format, -f`: Output format: jsonl, json, or csv (default: jsonl)
- `--no-markov`: Disable Markov-based generation (use standard only)
- `--no-metadata`: Exclude metadata from dataset
- `--seed`: Random seed for reproducibility
- `--list-techniques`: List available techniques and exit

## Model Evaluation

Evaluate models on red teaming datasets to measure their resilience.

```bash
# Evaluate OpenAI model
python tools/evaluate_red_team_dataset.py --dataset datasets/red_team_synthetic.jsonl \
  --model-type openai --model-id gpt-3.5-turbo

# Evaluate local Ollama model with custom settings
python tools/evaluate_red_team_dataset.py --dataset datasets/red_team_synthetic.jsonl \
  --model-type ollama --model-id llama2:7b --max-samples 50 --concurrency 4

# Evaluate Gemini model with custom output path
python tools/evaluate_red_team_dataset.py --dataset datasets/red_team_synthetic.jsonl \
  --model-type gemini --model-id gemini-pro --output results/gemini_eval.json
```

### Options:

- `--dataset, -d`: Path to the red teaming dataset (required)
- `--model-type, -m`: Type of model to evaluate: openai, gemini, ollama (required)
- `--model-id, -i`: Model ID (e.g., gpt-3.5-turbo, llama2:7b) (required)
- `--output, -o`: Path to save evaluation results (default: results/red_team_eval_results.json)
- `--max-samples, -n`: Maximum number of samples to evaluate (default: all)
- `--api-base`: Custom API base URL (for Ollama)
- `--temperature, -t`: Temperature for model responses (default: 0.0)
- `--max-tokens`: Maximum tokens to generate for each response (default: 256)
- `--concurrency, -c`: Number of concurrent requests (default: 1)

## Available Jailbreak Techniques

The system supports multiple jailbreak techniques including:

- **DAN**: "Do Anything Now" techniques to bypass restrictions
- **Likert**: Exploiting self-evaluation mechanisms
- **Crescendo**: Gradually escalating harmful requests
- **Deception**: Using deceptive framing and fictional scenarios
- **TokenManipulation**: Breaking up trigger words with special characters
- **ContextHacking**: Using fake system prompts and context manipulation
- **RolePlaying**: Character exploitation and roleplay scenarios
- **FunctionCalling**: Parameter manipulation using function-call format
- **Multilingual**: Using other languages to hide intent

### Markov-Based Variants:

- **Markov-DAN**: Dynamic DAN templates using Markov chains
- **Markov-Crescendo**: Dynamic escalation patterns using Markov chains
- **Markov-Mixed**: Combines multiple techniques with Markov-based generation

## Example Workflow

A typical red teaming workflow might look like:

1. Generate a synthetic dataset:
   ```bash
   python tools/generate_red_team_dataset.py -o datasets/synthetic_jailbreaks.jsonl -n 200
   ```

2. Evaluate a model on the dataset:
   ```bash
   python tools/evaluate_red_team_dataset.py -d datasets/synthetic_jailbreaks.jsonl -m openai -i gpt-4
   ```

3. Analyze results to identify vulnerabilities and improve model robustness.

## Extending the Tools

You can extend these tools by:

- Adding new jailbreak techniques in `benchmarks/templates/`
- Creating custom Markov models in `benchmarks/templates/markov_jailbreak_generator.py`
- Adding support for additional model types in the evaluation tool

## Responsible Use

These tools are provided for legitimate research, evaluation, and improvement of AI safety measures. Always use them responsibly and in accordance with applicable terms of service for any third-party models. 