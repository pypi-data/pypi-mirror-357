"""Pytest configuration and fixtures for afcli tests"""

import pytest
import responses
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone
from airflow_client.client.exceptions import OpenApiException
import airflow_client.client


@pytest.fixture
def mock_dag_data():
    """Sample DAG data for testing"""
    return {
        "dag_id": "test_dag",
        "dag_display_name": "Test DAG",
        "is_paused": False,
        "is_stale": False,
        "last_parsed_time": "2024-01-01T00:00:00Z",
        "description": "A test DAG",
        "timetable_summary": "0 0 * * *",
        "timetable_description": "At 00:00",
        "tags": [{"name": "test", "dag_id": "test_dag"}],
        "max_active_tasks": 16,
        "max_active_runs": 16,
        "has_import_errors": False,
        "next_dagrun_logical_date": "2024-01-02T00:00:00Z",
        "owners": ["airflow"]
    }


@pytest.fixture
def mock_dag_run_data():
    """Sample DAG run data for testing"""
    return {
        "dag_run_id": "test_run_1",
        "dag_id": "test_dag",
        "state": "success",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-01-01T00:05:00Z",
        "logical_date": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_task_instance_data():
    """Sample task instance data for testing"""
    return {
        "task_id": "test_task",
        "dag_id": "test_dag",
        "dag_run_id": "test_run_1",
        "state": "success",
        "start_date": "2024-01-01T00:01:00Z",
        "end_date": "2024-01-01T00:02:00Z",
        "try_number": 1
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"


@pytest.fixture
def mock_airflow_client():
    """Mock AirflowClient without external dependencies"""
    from afcli import AirflowClient
    from unittest.mock import patch, Mock
    
    # Mock the initialization to avoid actual API calls
    with patch.object(AirflowClient, '_get_jwt_token', return_value="mock_token"):
        with patch('airflow_client.client.Configuration'):
            with patch('airflow_client.client.ApiClient'):
                with patch('airflow_client.client.api.dag_api.DAGApi'):
                    with patch('airflow_client.client.api.dag_run_api.DagRunApi'):
                        with patch('airflow_client.client.api.task_instance_api.TaskInstanceApi'):
                            client = AirflowClient("localhost:8080", "admin", "password")
                            
                            # Add mock API instances
                            client.dag_api = Mock()
                            client.dag_run_api = Mock()
                            client.task_instance_api = Mock()
                            
                            return client


@pytest.fixture
def mock_cli_client():
    """Mock client specifically for CLI command tests"""
    from unittest.mock import Mock
    
    # Create a fully mocked client for CLI tests
    client = Mock()
    
    # Add the methods we need to test
    client.list_dags = Mock()
    client.get_dag = Mock()
    client.get_dag_runs = Mock()
    client.get_task_instances = Mock()
    client.get_task_log = Mock()
    client.trigger_dag = Mock()
    client.toggle_dag_pause = Mock()
    client.clear_task_instance = Mock()
    
    return client


@pytest.fixture
def mock_dag_response(mock_dag_data):
    """Mock DAG API response"""
    mock_dag = Mock()
    mock_dag.to_dict.return_value = mock_dag_data
    
    mock_response = Mock()
    mock_response.dags = [mock_dag]
    return mock_response


@pytest.fixture
def mock_dag_run_response(mock_dag_run_data):
    """Mock DAG run API response"""
    mock_run = Mock()
    mock_run.to_dict.return_value = mock_dag_run_data
    
    mock_response = Mock()
    mock_response.dag_runs = [mock_run]
    return mock_response


@pytest.fixture
def mock_task_instance_response(mock_task_instance_data):
    """Mock task instance API response"""
    mock_task = Mock()
    mock_task.to_dict.return_value = mock_task_instance_data
    
    mock_response = Mock()
    mock_response.task_instances = [mock_task]
    return mock_response


@pytest.fixture
def mock_openapi_exception():
    """Mock OpenApiException for error testing"""
    def create_exception(status=404, reason="Not Found"):
        exc = OpenApiException(f"HTTP {status}")
        exc.status = status
        exc.reason = reason
        return exc
    return create_exception


@pytest.fixture
def responses_mock():
    """Responses mock for HTTP requests"""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_jwt_response():
    """Sample JWT token response"""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
    }


@pytest.fixture
def capsys_disabled():
    """Disable output capturing for tests that need to verify print statements"""
    import sys
    import io
    
    # Temporarily replace stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    
    yield sys.stdout, sys.stderr
    
    # Restore original streams
    sys.stdout = original_stdout
    sys.stderr = original_stderr


@pytest.fixture(autouse=True)
def mock_colorama():
    """Mock colorama to avoid issues in tests"""
    from unittest.mock import patch
    with patch('afcli.init'):
        with patch('afcli.Fore') as mock_fore:
            with patch('afcli.Style') as mock_style:
                mock_fore.RED = ""
                mock_fore.GREEN = ""
                mock_fore.YELLOW = ""
                mock_fore.CYAN = ""
                mock_fore.BLUE = ""
                mock_fore.MAGENTA = ""
                mock_fore.WHITE = ""
                mock_fore.LIGHTBLACK_EX = ""
                mock_style.RESET_ALL = ""
                yield mock_fore, mock_style