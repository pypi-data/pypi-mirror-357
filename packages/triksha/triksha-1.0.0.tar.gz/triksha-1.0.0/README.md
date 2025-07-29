# Triksha - Advanced LLM Security Testing Framework

Triksha is a comprehensive framework for testing and evaluating Large Language Models (LLMs) for security vulnerabilities, including jailbreaking, prompt injection, and harmful content generation.

[![PyPI version](https://badge.fury.io/py/triksha.svg)](https://badge.fury.io/py/triksha)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Static Red Teaming**: Test models with predefined adversarial prompts to evaluate resilience to jailbreaking
- **Scheduled Red Teaming**: Schedule automated red teaming runs at specified intervals to continuously monitor model safety
- **Conversation Red Teaming**: Simulate multi-turn conversations to test for more complex vulnerabilities
- **Comprehensive Metrics**: Track success rates, response times, and vulnerability patterns
- **Email Notifications**: Get notified when benchmarks complete with detailed results
- **Custom API Models**: Test your own API endpoints with flexible configuration
- **Guardrail Testing**: Register and test custom content moderation APIs
- **Advanced Jailbreak Techniques**: DAN attacks, context hacking, role playing, deception, and encoding techniques

## Quick Start

### Installation

Install Triksha directly from PyPI:

```bash
pip install triksha
```

### Basic Usage

1. **Set up API keys** (optional, for testing API models):
   ```bash
   triksha-verify  # Check environment setup
   ```

2. **Run interactive CLI**:
   ```bash
   triksha
   ```

3. **Run specific commands**:
   ```bash
   # Download a dataset
   triksha dataset download --id microsoft/DialoGPT-medium

   # Run a benchmark
   triksha benchmark run --model gpt-3.5-turbo

   # View results
   triksha benchmark results
   ```

## Installation Options

### Standard Installation
```bash
pip install triksha
```

### Development Installation
```bash
pip install triksha[dev]
```

### With Kubernetes Support
```bash
pip install triksha[kubernetes]
```

### With Web Interface
```bash
pip install triksha[web]
```

### Full Installation (All Features)
```bash
pip install triksha[all]
```

## Requirements

- **Python**: 3.9 or higher
- **Operating System**: Cross-platform (Windows, macOS, Linux)
- **Memory**: Minimum 8GB RAM recommended for local model testing
- **Storage**: At least 5GB free space for datasets and models

### API Keys (Optional)

For testing API-based models, you'll need:
- **OpenAI API Key**: For GPT models
- **Google API Key**: For Gemini models
- **HuggingFace Token**: For downloading private models/datasets

Create a `.env` file in your working directory:
```bash
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
```

## Usage

### Command Line Interface

Triksha provides several command-line tools:

- `triksha` - Interactive CLI interface
- `triksha-cli` - Alternative interactive interface
- `triksha-dataset` - Dataset management tools
- `triksha-train` - Model training utilities
- `triksha-deps` - Dependency management
- `triksha-verify` - Environment verification

### Interactive Mode

Launch the interactive interface:
```bash
triksha
```

This provides a menu-driven interface for:
1. **Perform Red Teaming** - Run security tests against models
2. **Manage Custom Model Assets** - Add and configure custom models/guardrails
3. **Schedule Red Teaming** - Set up automated testing
4. **Manage Results** - View, export, and analyze test results
5. **User Activity Monitor** - Track usage and activities
6. **Settings** - Configure API keys and preferences

### Static Red Teaming

Test models with predefined adversarial prompts:

```bash
triksha benchmark run
```

This will guide you through:
- Selecting target models (OpenAI, Gemini, Ollama, or custom APIs)
- Choosing jailbreak techniques
- Configuring test parameters
- Running the benchmark
- Viewing results

### Scheduled Red Teaming

Set up automated testing at regular intervals:

```bash
# Configure a new scheduled benchmark
triksha scheduled --action=configure

# List all scheduled benchmarks
triksha scheduled --action=list

# Delete a scheduled benchmark
triksha scheduled --action=delete --id=<benchmark_id>
```

### Dataset Management

```bash
# Download a dataset from HuggingFace
triksha dataset download --id microsoft/DialoGPT-medium

# Format a dataset for adversarial testing
triksha dataset format --input dataset_name --type jailbreak

# View available datasets
triksha dataset view

# Export a dataset
triksha dataset export --id dataset_name --format json
```

### Custom Guardrails

Register and test custom content moderation APIs:

```bash
triksha
# Select "Manage Custom Model Assets" > "Add New Guardrail"
```

Supports complex multi-line cURL commands with automatic placeholder detection.

## Advanced Features

### Kubernetes Integration

Deploy benchmarks on Kubernetes for scalable testing:

```bash
pip install triksha[kubernetes]
```

### Conversation Red Teaming

Multi-turn conversation testing with advanced AI agents:
- Profiling phase: Analyze target model characteristics
- Strategy development: Create tailored attack strategies  
- Execution phase: Adaptive prompt generation and testing

### Email Notifications

Configure email notifications for completed benchmarks:

```bash
triksha settings email --action=setup
```

## Development

### Contributing

1. Clone the repository:
   ```bash
   git clone https://github.com/triksha-ai/triksha.git
   cd triksha
   ```

2. Install in development mode:
   ```bash
   pip install -e .[dev]
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

### Building from Source

```bash
git clone https://github.com/triksha-ai/triksha.git
cd triksha
pip install -e .
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/custom_models.md)
- [Scheduled Benchmarks](docs/scheduled_benchmarks.md)
- [Technical PRD](docs/DRAVIK_TECHNICAL_PRD.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/triksha-ai/triksha/issues)
- **Documentation**: [ReadTheDocs](https://triksha.readthedocs.io/)
- **Discussions**: [GitHub Discussions](https://github.com/triksha-ai/triksha/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Triksha in your research, please cite:

```bibtex
@software{triksha2024,
  title={Triksha: Advanced LLM Security Testing Framework},
  author={Triksha Team},
  year={2024},
  url={https://github.com/triksha-ai/triksha}
}
```
