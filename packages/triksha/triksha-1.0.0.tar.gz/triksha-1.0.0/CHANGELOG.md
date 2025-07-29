# Changelog

All notable changes to the Triksha project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Triksha framework
- Static red teaming with predefined adversarial prompts
- Scheduled red teaming with automated testing at intervals
- Conversation red teaming with multi-turn AI agents
- Support for OpenAI, Gemini, Ollama, and custom API models
- Custom guardrail testing and content moderation API support
- Email notification system for benchmark completion
- Interactive CLI interface with menu-driven navigation
- Dataset management tools for downloading and formatting datasets
- Comprehensive benchmark metrics and reporting
- Kubernetes integration for scalable testing
- Advanced jailbreak techniques (DAN, context hacking, role playing, etc.)
- User activity monitoring and logging
- Configuration templates and settings management
- Cross-platform support (Windows, macOS, Linux)
- PyPI package distribution with proper entry points

### Features
- Command-line tools: `triksha`, `triksha-cli`, `triksha-dataset`, `triksha-train`
- Support for multiple model testing environments
- Flexible API key configuration via .env files
- Automated dependency checking and environment verification
- Export capabilities for benchmark results and datasets
- Template-based configuration system
- Comprehensive error handling and logging

### Documentation
- Complete README with installation and usage instructions
- Technical documentation for API reference
- Quick start guide for new users
- Scheduled benchmarks documentation
- Custom models integration guide

### Dependencies
- Python 3.9+ support
- Core dependencies: requests, pandas, numpy, transformers
- Optional dependencies for Kubernetes, web interface, and development

## [0.9.0] - 2024-01-XX (Pre-release)

### Added
- Core framework development
- Basic CLI functionality
- Initial model testing capabilities

---

## Release Notes

### v1.0.0 Release Notes

This is the initial stable release of Triksha, a comprehensive LLM security testing framework. The package is now available on PyPI and can be installed with `pip install triksha`.

**Key Highlights:**
- Full-featured CLI interface for interactive red teaming
- Support for major LLM providers (OpenAI, Google, Ollama)
- Advanced conversation-based testing with AI agents
- Automated scheduling and email notifications
- Extensible architecture for custom models and guardrails

**Installation:**
```bash
pip install triksha
```

**Quick Start:**
```bash
triksha-verify  # Check environment
triksha         # Launch interactive CLI
```

For detailed documentation and examples, see the [README](README.md) and [documentation](docs/). 