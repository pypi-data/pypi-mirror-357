# Quick Start Guide

This guide helps you get started quickly with Dravik, the advanced LLM security testing framework.

## Initial Setup

If you haven't installed Dravik yet, see the [Installation Guide](installation.md).

## Running Your First Security Benchmark

1. **Run a static red teaming benchmark**:
   ```bash
   python -m cli.dravik_cli benchmark
   ```

2. This will guide you through an interactive menu where you can:
   - Select target models to test
   - Choose the number of prompts to use
   - Select attack techniques
   - Configure other benchmark parameters

3. After the benchmark completes, you'll see a results summary with:
   - Success rates by model and technique
   - Average response times
   - Most successful attack vectors

## Setting Up Email Notifications

To receive benchmark results via email:

```bash
python -m cli.dravik_cli settings email --action=setup
```

This will prompt you for:
- Your Gmail address
- App password (recommended) or account password
- Whether to include CSV result files

## Setting Up Scheduled Benchmarks

1. **Start the scheduler service**:
   ```bash
   python -m cli.dravik_cli scheduler --action=start
   ```

2. **Configure a scheduled benchmark**:
   ```bash
   python -m cli.dravik_cli scheduled --action=configure
   ```

3. Follow the prompts to configure:
   - Models to test
   - Number of prompts
   - Attack techniques
   - Schedule type (once, daily, weekly, monthly, custom)
   - Start date and time
   - Recurrence pattern (if applicable)

4. **List your scheduled benchmarks**:
   ```bash
   python -m cli.dravik_cli scheduled --action=list
   ```

## Viewing Benchmark Results

1. **View all benchmark results**:
   ```bash
   python -m cli.dravik_cli benchmark
   ```
   
2. Then select the "View Results" option from the menu.

3. **Export benchmark results**:
   ```bash
   python -m cli.dravik_cli benchmark
   ```
   
4. Then select the "Export Results" option from the menu.

## Conversation Red Teaming

For more advanced security testing, try conversation red teaming:

1. Start a conversation red team test via the benchmark menu:
   ```bash
   python -m cli.dravik_cli benchmark
   ```
   
2. Select "Conversation Red Teaming" from the menu.

3. Configure:
   - Target model to test
   - Number of conversation turns
   - Attack vectors and techniques

## Common Commands

- **Help**: `python -m cli.dravik_cli --help`
- **Benchmark status**: `python -m cli.dravik_cli benchmark`
- **Scheduler status**: `python -m cli.dravik_cli scheduler --action=status`
- **Email setup**: `python -m cli.dravik_cli settings email --action=setup`
- **Email status**: `python -m cli.dravik_cli settings email --action=status`

## Next Steps

- Read the [Scheduled Benchmarks documentation](scheduled_benchmarks.md)
- Explore [Custom Models configuration](custom_models.md)
- Learn about different benchmark types in [Benchmark Types](benchmarks.md) 