# Scheduled Red Teaming Benchmarks

This feature allows you to schedule static red teaming benchmarks to run automatically at specified times. You can schedule one-time or recurring benchmarks to ensure continuous monitoring of model safety.

## Getting Started

### Scheduler Auto-Start

The scheduler daemon now starts automatically by default when you use the CLI. This ensures that your scheduled benchmarks will run even when you're not actively using the application.

You can configure the auto-start behavior:

```bash
# Enable auto-start (default)
python -m cli.dravik_cli scheduler --action=config-autostart --enable=true

# Disable auto-start
python -m cli.dravik_cli scheduler --action=config-autostart --enable=false
```

### Scheduler Management

If needed, you can manually control the scheduler service:

```bash
# Start the scheduler manually if auto-start is disabled
python -m cli.dravik_cli scheduler --action=start

# Check the scheduler status
python -m cli.dravik_cli scheduler --action=status

# Stop the scheduler
python -m cli.dravik_cli scheduler --action=stop
```

To install the scheduler as a system service (to run at system startup):

```bash
# Install as a system service (Linux/macOS)
python -m cli.dravik_cli scheduler --action=install-service
```

### Configuring a Scheduled Benchmark

You can configure a scheduled benchmark using the CLI:

```bash
# Configure through interactive interface
python -m cli.dravik_cli scheduled --action=configure
```

This will guide you through a series of prompts to:
1. Select models to benchmark
2. Configure benchmark parameters (number of prompts, techniques)
3. Set up the schedule (one-time or recurring)

### Managing Scheduled Benchmarks

To list all scheduled benchmarks:

```bash
python -m cli.dravik_cli scheduled --action=list
```

To delete a scheduled benchmark:

```bash
# Delete through interactive interface
python -m cli.dravik_cli scheduled --action=delete

# Or delete by ID
python -m cli.dravik_cli scheduled --action=delete --id=<task_id>
```

## Schedule Types

When configuring a scheduled benchmark, you can choose from several schedule types:

- **Run once**: Run the benchmark once at a specific date and time
- **Run daily**: Run the benchmark every day at the specified time
- **Run weekly**: Run the benchmark every week on the same day and time
- **Run monthly**: Run the benchmark every month on the same day and time
- **Custom interval**: Run the benchmark at a custom interval (minutes, hours, or days)

## Email Notifications

If you have configured email notifications (using `python -m cli.dravik_cli settings email --action=setup`), you will receive email notifications when scheduled benchmarks complete. 

These notifications include:
- Benchmark summary (success rate, average response time)
- CSV attachment with detailed results (if enabled)

## Logging

Logs for the scheduler service are stored in:
- `~/dravik/logs/scheduler.log` - General scheduler logs
- `~/dravik/logs/scheduler_service.log` - Service-specific logs

## Task Storage

Scheduled tasks are stored in JSON format at:
- `~/dravik/scheduler/tasks.json` - Task definitions
- `~/dravik/scheduler/<task_id>_params.json` - Benchmark parameters for each task

## Implementation Details

The scheduled benchmark functionality is implemented using:

1. **Scheduler**: A background process that checks for due tasks and runs them automatically
2. **Task Management**: Functions to create, list, and delete scheduled benchmark tasks
3. **Execution**: Runs benchmarks using the same underlying code as manual benchmarks

The scheduler runs in a separate process and persists tasks to disk, so they survive between restarts of the application or scheduler service. 