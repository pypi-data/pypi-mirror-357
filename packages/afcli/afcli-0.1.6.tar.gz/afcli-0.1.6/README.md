# Airflow CLI Wrapper

[![Test](https://github.com/ouachitalabs/af/actions/workflows/test.yml/badge.svg)](https://github.com/ouachitalabs/af/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/afcli.svg)](https://badge.fury.io/py/afcli)
[![Python versions](https://img.shields.io/pypi/pyversions/afcli.svg)](https://pypi.org/project/afcli/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)](https://github.com/ouachitalabs/af)

A command-line utility for interacting with the Airflow REST API.

## Installation

```bash
uv tool install afcli
```

Or with `pip`:
```bash
pip install afcli
```

## Configuration

### Environment Variables

You can set authentication credentials using environment variables:

```bash
export AIRFLOW_HOST="airflow.example.com:8080"  # Default: localhost:8080
export AIRFLOW_USER="admin"
export AIRFLOW_PASSWORD="your-password"
```

### Command Line Arguments

Command line arguments override environment variables:

```bash
afcli --host airflow.example.com:8080 --user admin --password secret list
```

## Usage

### Basic Usage

By default, the tool connects to `localhost:8080`:

```bash
# Using environment variables
afcli list

# Using command line arguments
afcli --user admin --password secret status my_dag
```

### Available Commands

#### List DAGs
```bash
afcli list
afcli list --limit 10  # Show only 10 DAGs
afcli list --all       # Include inactive DAGs
```

#### View DAG Status
```bash
afcli status <dag_id>
```
Shows DAG configuration and recent runs with color-coded states.

#### Pause/Unpause DAG
```bash
afcli pause <dag_id>
afcli unpause <dag_id>
```

#### Trigger DAG
```bash
afcli trigger <dag_id>
afcli trigger <dag_id> --config '{"key": "value"}'
```

#### View Tasks and Their Status
```bash
afcli tasks <dag_id>
afcli tasks <dag_id> --run-id <specific_run_id>
```
Shows all tasks with color-coded states:
- 🟢 Green: Success
- 🔴 Red: Failed
- 🟡 Yellow: Running/Retry
- 🔵 Blue: Scheduled
- 🟣 Purple: Skipped

#### View Task Logs
```bash
afcli logs <dag_id> <task_id>
afcli logs <dag_id> <task_id> --run-id <specific_run_id> --try-number 2
```

#### Clear Failed Tasks
```bash
# Clear all failed tasks in the latest run
afcli clear <dag_id>

# Clear a specific task
afcli clear <dag_id> --task-id <task_id>

# Skip confirmation prompt
afcli clear <dag_id> -y
```

## Examples

```bash
# Set credentials via environment
export AIRFLOW_USER=admin
export AIRFLOW_PASSWORD=secret

# List all DAGs
afcli list

# Check status of example_dag
afcli status example_dag

# Trigger example_dag with configuration
afcli trigger example_dag --config '{"date": "2024-01-01"}'

# View all tasks in the latest run
afcli tasks example_dag

# View logs for a specific task
afcli logs example_dag process_data

# Clear all failed tasks
afcli clear example_dag
```

## Authentication

The tool uses JWT (JSON Web Token) authentication. It automatically obtains a token using the provided credentials and includes it in all API requests.

## Development

### Installation for Development

```bash
# Install with test dependencies
uv pip install -e ".[test]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=afcli --cov-report=html

# Run specific test categories
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only

# Use Makefile commands
make test              # All tests
make test-cov          # With coverage report
make test-unit         # Unit tests only
```
