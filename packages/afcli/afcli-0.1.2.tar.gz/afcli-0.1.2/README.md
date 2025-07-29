# Airflow CLI Wrapper

[![Test](https://github.com/ouachitalabs/af/actions/workflows/test.yml/badge.svg)](https://github.com/ouachitalabs/af/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/afcli.svg)](https://badge.fury.io/py/afcli)
[![Python versions](https://img.shields.io/pypi/pyversions/afcli.svg)](https://pypi.org/project/afcli/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)](https://github.com/ouachitalabs/af)

A command-line utility for interacting with the Airflow REST API.

## Installation

```bash
pip install -r requirements.txt
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
python af.py --host airflow.example.com:8080 --user admin --password secret list
```

## Usage

### Basic Usage

By default, the tool connects to `localhost:8080`:

```bash
# Using environment variables
python af.py list

# Using command line arguments
python af.py --user admin --password secret status my_dag
```

### Available Commands

#### List DAGs
```bash
python af.py list
python af.py list --limit 10  # Show only 10 DAGs
python af.py list --all       # Include inactive DAGs
```

#### View DAG Status
```bash
python af.py status <dag_id>
```
Shows DAG configuration and recent runs with color-coded states.

#### Pause/Unpause DAG
```bash
python af.py pause <dag_id>
python af.py unpause <dag_id>
```

#### Trigger DAG
```bash
python af.py trigger <dag_id>
python af.py trigger <dag_id> --config '{"key": "value"}'
```

#### View Tasks and Their Status
```bash
python af.py tasks <dag_id>
python af.py tasks <dag_id> --run-id <specific_run_id>
```
Shows all tasks with color-coded states:
- 🟢 Green: Success
- 🔴 Red: Failed
- 🟡 Yellow: Running/Retry
- 🔵 Blue: Scheduled
- 🟣 Purple: Skipped

#### View Task Logs
```bash
python af.py logs <dag_id> <task_id>
python af.py logs <dag_id> <task_id> --run-id <specific_run_id> --try-number 2
```

#### Clear Failed Tasks
```bash
# Clear all failed tasks in the latest run
python af.py clear <dag_id>

# Clear a specific task
python af.py clear <dag_id> --task-id <task_id>

# Skip confirmation prompt
python af.py clear <dag_id> -y
```

## Examples

```bash
# Set credentials via environment
export AIRFLOW_USER=admin
export AIRFLOW_PASSWORD=secret

# List all DAGs
python af.py list

# Check status of example_dag
python af.py status example_dag

# Trigger example_dag with configuration
python af.py trigger example_dag --config '{"date": "2024-01-01"}'

# View all tasks in the latest run
python af.py tasks example_dag

# View logs for a specific task
python af.py logs example_dag process_data

# Clear all failed tasks
python af.py clear example_dag
```

## Authentication

The tool uses JWT (JSON Web Token) authentication. It automatically obtains a token using the provided credentials and includes it in all API requests.

## Development

### Installation for Development

```bash
# Install with test dependencies
uv pip install -e ".[test]"
```

### Releasing

```bash
# Create a new release (replace 0.2.0 with desired version)
./scripts/release.sh 0.2.0
```

This will:
1. Create and push a git tag
2. Guide you to create a GitHub release
3. Automatically trigger CI/CD to publish to PyPI

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

### Test Suite

- **81 comprehensive tests** covering all functionality
- **88% code coverage** with detailed reporting
- **No external dependencies** - all API calls mocked
- **Fast execution** - full suite runs in <1 second

Test categories:
- Unit tests for AirflowClient class methods
- Integration tests for CLI commands  
- Authentication and error handling tests
- Utility function tests

See `tests/README.md` for detailed testing documentation.