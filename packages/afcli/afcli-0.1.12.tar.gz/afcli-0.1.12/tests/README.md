# AFCLI Test Suite

This directory contains a comprehensive test suite for the AFCLI (Airflow CLI wrapper) tool.

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual functions and methods in isolation
- Use mocks to avoid external dependencies
- Fast execution, suitable for development

### Integration Tests (`@pytest.mark.integration`)
- Test interactions between components
- May involve the full CLI argument parsing
- Test end-to-end workflows

## Running Tests

### Install Test Dependencies
```bash
uv pip install -e ".[test]"
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests with coverage
pytest --cov=afcli --cov-report=html
```

### Run Specific Test Files
```bash
# Test utility functions
pytest tests/test_utils.py

# Test AirflowClient class
pytest tests/test_airflow_client.py

# Test CLI commands
pytest tests/test_cli_commands.py

# Test authentication and errors
pytest tests/test_auth_and_errors.py
```

### Run Specific Tests
```bash
# Run a specific test function
pytest tests/test_utils.py::TestFormatDatetime::test_format_datetime_valid_iso_string

# Run a specific test class
pytest tests/test_airflow_client.py::TestAirflowClientInit
```

## Test Coverage

The test suite aims for >90% code coverage across all modules, including the AirflowClient class, CLI commands, utility functions, and authentication/error handling.

## Testing Approach

The test suite uses comprehensive fixtures and mocking strategies to ensure:
- All external API calls are properly mocked
- Tests run without requiring a live Airflow instance
- Output is captured and verified
- Tests are deterministic and fast

## Continuous Integration

Tests are designed to run in CI environments:

- No external dependencies required
- All network calls are mocked
- Deterministic test results
- Fast execution (< 30 seconds)

## Adding New Tests

When adding new functionality to AFCLI:

1. **Add unit tests** for new functions/methods
2. **Add integration tests** for new CLI commands
3. **Update fixtures** if new data structures are used
4. **Test error cases** for new error conditions
5. **Update coverage** requirements if needed

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Descriptive names indicating what is being tested

### Example Test Structure

```python
class TestNewFeature:
    """Test the new feature functionality"""
    
    @pytest.mark.unit
    def test_new_feature_success(self, mock_client):
        """Test successful execution of new feature"""
        # Arrange
        mock_client.new_method.return_value = expected_result
        
        # Act
        result = new_feature_function(mock_client, args)
        
        # Assert
        assert result == expected_result
        mock_client.new_method.assert_called_once_with(expected_args)
    
    @pytest.mark.unit
    def test_new_feature_error_handling(self, mock_client, mock_openapi_exception):
        """Test error handling in new feature"""
        # Arrange
        mock_client.new_method.side_effect = mock_openapi_exception(404)
        
        # Act & Assert
        with pytest.raises(SystemExit):
            new_feature_function(mock_client, args)
```

## Debugging Tests

### Verbose Output
```bash
pytest -v
```

### Print Statements
```bash
pytest -s
```

### Stop on First Failure
```bash
pytest -x
```

### Debug Mode
```bash
pytest --pdb
```

### Run Last Failed Tests
```bash
pytest --lf
```

## Performance

The test suite is optimized for speed:

- Unit tests: ~10 seconds
- Integration tests: ~5 seconds
- Full suite with coverage: ~20 seconds

For development, run unit tests frequently and full suite before commits.