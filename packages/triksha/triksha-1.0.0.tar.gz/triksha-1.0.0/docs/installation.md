# Installation Guide for Dravik

This guide provides step-by-step instructions for installing Dravik, the advanced LLM security testing framework.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## Basic Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dravik.git
   cd dravik
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify the installation:
   ```bash
   python -m cli.dravik_cli --help
   ```

## Setting Up Email Notifications

Email notifications allow you to receive benchmark results automatically:

1. Configure email settings:
   ```bash
   python -m cli.dravik_cli settings email --action=setup
   ```

2. This will guide you through the setup process, which requires:
   - A Gmail account (recommended to use an app password)
   - Optional: Include CSV attachments with results

3. Verify your email configuration:
   ```bash
   python -m cli.dravik_cli settings email --action=status
   ```

## Setting Up Scheduled Benchmarks

To use the scheduled benchmark feature:

1. Install the additional daemon package if not already included:
   ```bash
   pip install python-daemon>=2.3.0
   ```

2. Start the scheduler service:
   ```bash
   python -m cli.dravik_cli scheduler --action=start
   ```

3. Configure a scheduled benchmark:
   ```bash
   python -m cli.dravik_cli scheduled --action=configure
   ```

4. To start the scheduler as a daemon (runs in background):
   ```bash
   python -m cli.dravik_cli scheduler --action=start-daemon
   ```

## Troubleshooting

### Common Issues

1. **ImportError for dependencies**:
   Make sure all dependencies are installed properly:
   ```bash
   pip install -r requirements.txt
   ```

2. **Scheduler service not starting**:
   Ensure the python-daemon package is installed:
   ```bash
   pip install python-daemon>=2.3.0
   ```

3. **Email notification errors**:
   - Check your Gmail account settings and ensure "less secure apps" is enabled or use an app password
   - Verify your internet connection
   - Try reconfiguring with `python -m cli.dravik_cli settings email --action=setup`

### Getting Help

If you encounter issues not covered here, please:

1. Check the detailed documentation in the `docs/` directory
2. Open an issue on the GitHub repository
3. Reach out to the maintainers for support

## Next Steps

After installation, explore these features:

- Run your first benchmark: `python -m cli.dravik_cli benchmark`
- Configure scheduled benchmarks: `python -m cli.dravik_cli scheduled --action=configure`
- Explore the dataset commands: `python -m cli.dravik_cli dataset --help` 