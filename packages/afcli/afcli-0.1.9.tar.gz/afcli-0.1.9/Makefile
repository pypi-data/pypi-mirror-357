# Makefile for AFCLI development and testing

.PHONY: help install test test-unit test-integration test-cov lint clean check-all

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install package with test dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run code linting (if available)"
	@echo "  clean         - Clean up generated files"
	@echo "  check-all     - Run all checks (tests, lint, coverage)"

# Install package with test dependencies
install:
	uv pip install -e ".[test]"

# Run all tests
test:
	uv run pytest

# Run unit tests only
test-unit:
	uv run pytest -m unit

# Run integration tests only
test-integration:
	uv run pytest -m integration

# Run tests with coverage
test-cov:
	uv run pytest --cov=afcli --cov-report=term-missing --cov-report=html

# Run code linting (placeholder for future linting setup)
lint:
	@echo "Linting not configured yet. Consider adding ruff, black, or pylint."

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Run all checks
check-all: test-cov lint
	@echo "All checks completed!"

# Quick development test cycle
dev-test:
	uv run pytest -x -v tests/

# Test with output
test-verbose:
	uv run pytest -v -s

# Test specific file
test-file:
	@read -p "Enter test file (e.g., test_utils.py): " file; \
	uv run pytest tests/$$file -v

# Test specific function
test-func:
	@read -p "Enter test function (e.g., test_format_datetime_valid_iso_string): " func; \
	uv run pytest -k $$func -v