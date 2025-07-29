"""Tests for AirflowClient class"""

import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
from airflow_client.client.exceptions import OpenApiException
import requests

from afcli import AirflowClient


class TestAirflowClientInit:
    """Test AirflowClient initialization"""
    
    @pytest.mark.unit
    @patch('afcli.airflow_client.client.Configuration')
    @patch('afcli.airflow_client.client.ApiClient')
    @patch('afcli.dag_api.DAGApi')
    @patch('afcli.dag_run_api.DagRunApi')
    @patch('afcli.task_instance_api.TaskInstanceApi')
    def test_init_without_credentials(self, mock_task_api, mock_dag_run_api, mock_dag_api, 
                                    mock_api_client, mock_config):
        """Test initialization without credentials"""
        client = AirflowClient("localhost:8080")
        
        assert client.host == "localhost:8080"
        assert client.base_url == "http://localhost:8080"
        assert client.auth_url == "http://localhost:8080/auth/token"
        
        # Configuration should be called with no access token
        mock_config.assert_called_once_with(
            host="http://localhost:8080",
            access_token=None
        )
    
    @pytest.mark.unit
    @patch('afcli.airflow_client.client.Configuration')
    @patch('afcli.airflow_client.client.ApiClient')
    @patch('afcli.dag_api.DAGApi')
    @patch('afcli.dag_run_api.DagRunApi')
    @patch('afcli.task_instance_api.TaskInstanceApi')
    @patch.object(AirflowClient, '_get_jwt_token')
    def test_init_with_credentials(self, mock_get_token, mock_task_api, mock_dag_run_api, 
                                 mock_dag_api, mock_api_client, mock_config):
        """Test initialization with credentials"""
        mock_get_token.return_value = "test_token"
        
        client = AirflowClient("localhost:8080", "admin", "password")
        
        mock_get_token.assert_called_once_with("admin", "password")
        mock_config.assert_called_once_with(
            host="http://localhost:8080",
            access_token="test_token"
        )


class TestAirflowClientAuth:
    """Test authentication methods"""
    
    @pytest.mark.unit
    def test_get_jwt_token_success(self, responses_mock, sample_jwt_response):
        """Test successful JWT token retrieval"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json=sample_jwt_response,
            status=200
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            token = client._get_jwt_token("admin", "password")
            
            assert token == sample_jwt_response["access_token"]
    
    @pytest.mark.unit
    def test_get_jwt_token_http_error(self, responses_mock):
        """Test JWT token retrieval with HTTP error"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json={"error": "Invalid credentials"},
            status=401
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "wrong_password")
    
    @pytest.mark.unit
    def test_get_jwt_token_no_access_token(self, responses_mock):
        """Test JWT token retrieval when response has no access_token"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json={"message": "success"},  # No access_token field
            status=200
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")


class TestAirflowClientDagMethods:
    """Test DAG-related methods"""
    
    @pytest.mark.unit
    def test_list_dags_success(self, mock_airflow_client, mock_dag_response):
        """Test successful DAG listing"""
        mock_airflow_client.dag_api.get_dags.return_value = mock_dag_response
        
        result = mock_airflow_client.list_dags(limit=10, only_active=True)
        
        mock_airflow_client.dag_api.get_dags.assert_called_once_with(limit=10, paused=False)
        assert len(result) == 1
        assert result[0]["dag_id"] == "test_dag"
    
    @pytest.mark.unit
    def test_list_dags_all_dags(self, mock_airflow_client, mock_dag_response):
        """Test listing all DAGs (including paused)"""
        mock_airflow_client.dag_api.get_dags.return_value = mock_dag_response
        
        result = mock_airflow_client.list_dags(limit=10, only_active=False)
        
        mock_airflow_client.dag_api.get_dags.assert_called_once_with(limit=10, paused=None)
    
    @pytest.mark.unit
    def test_list_dags_empty_response(self, mock_airflow_client):
        """Test DAG listing with empty response"""
        mock_response = Mock()
        mock_response.dags = None
        mock_airflow_client.dag_api.get_dags.return_value = mock_response
        
        result = mock_airflow_client.list_dags()
        
        assert result == []
    
    @pytest.mark.unit
    def test_list_dags_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test DAG listing with API error"""
        mock_airflow_client.dag_api.get_dags.side_effect = mock_openapi_exception(404)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.list_dags()
    
    @pytest.mark.unit
    def test_get_dag_success(self, mock_airflow_client, mock_dag_data):
        """Test successful DAG retrieval"""
        mock_dag = Mock()
        mock_dag.to_dict.return_value = mock_dag_data
        mock_airflow_client.dag_api.get_dag.return_value = mock_dag
        
        result = mock_airflow_client.get_dag("test_dag")
        
        mock_airflow_client.dag_api.get_dag.assert_called_once_with("test_dag")
        assert result["dag_id"] == "test_dag"
    
    @pytest.mark.unit
    def test_toggle_dag_pause(self, mock_airflow_client):
        """Test DAG pause toggle"""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"is_paused": True}
        mock_airflow_client.dag_api.patch_dag.return_value = mock_response
        
        with patch('afcli.airflow_client.client.DAGPatchBody') as mock_patch_body:
            result = mock_airflow_client.toggle_dag_pause("test_dag", True)
            
            mock_patch_body.assert_called_once_with(is_paused=True)
            assert result["is_paused"] is True


class TestAirflowClientDagRunMethods:
    """Test DAG run-related methods"""
    
    @pytest.mark.unit
    def test_get_dag_runs_success(self, mock_airflow_client, mock_dag_run_response):
        """Test successful DAG runs retrieval"""
        mock_airflow_client.dag_run_api.get_dag_runs.return_value = mock_dag_run_response
        
        result = mock_airflow_client.get_dag_runs("test_dag", limit=5)
        
        mock_airflow_client.dag_run_api.get_dag_runs.assert_called_once_with("test_dag", limit=5)
        assert len(result) == 1
        assert result[0]["dag_run_id"] == "test_run_1"
    
    @pytest.mark.unit
    def test_trigger_dag_success(self, mock_airflow_client):
        """Test successful DAG triggering"""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"dag_run_id": "new_run", "state": "queued"}
        mock_airflow_client.dag_run_api.post_dag_run.return_value = mock_response
        
        with patch('afcli.airflow_client.client.TriggerDAGRunPostBody') as mock_trigger_body:
            result = mock_airflow_client.trigger_dag("test_dag", {"key": "value"})
            
            mock_trigger_body.assert_called_once()
            assert result["dag_run_id"] == "new_run"
    
    @pytest.mark.unit
    def test_trigger_dag_with_custom_date(self, mock_airflow_client):
        """Test DAG triggering with custom logical date"""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"dag_run_id": "new_run", "state": "queued"}
        mock_airflow_client.dag_run_api.post_dag_run.return_value = mock_response
        
        with patch('afcli.airflow_client.client.TriggerDAGRunPostBody') as mock_trigger_body:
            custom_date = "2024-01-01T00:00:00Z"
            result = mock_airflow_client.trigger_dag(
                "test_dag", 
                config={"key": "value"}, 
                logical_date=custom_date,
                dag_run_id="custom_run"
            )
            
            mock_trigger_body.assert_called_once_with(
                logical_date=custom_date,
                conf={"key": "value"},
                dag_run_id="custom_run"
            )


class TestAirflowClientTaskMethods:
    """Test task-related methods"""
    
    @pytest.mark.unit
    def test_get_task_instances_success(self, mock_airflow_client, mock_task_instance_response):
        """Test successful task instances retrieval"""
        mock_airflow_client.task_instance_api.get_task_instances.return_value = mock_task_instance_response
        
        result = mock_airflow_client.get_task_instances("test_dag", "test_run_1")
        
        mock_airflow_client.task_instance_api.get_task_instances.assert_called_once_with(
            "test_dag", "test_run_1"
        )
        assert len(result) == 1
        assert result[0]["task_id"] == "test_task"
    
    @pytest.mark.unit
    def test_get_task_log_success(self, mock_airflow_client):
        """Test successful task log retrieval"""
        mock_response = Mock()
        mock_response.content = "Task log content"
        mock_airflow_client.task_instance_api.get_log.return_value = mock_response
        
        result = mock_airflow_client.get_task_log("test_dag", "test_run_1", "test_task", 1)
        
        mock_airflow_client.task_instance_api.get_log.assert_called_once_with(
            "test_dag", "test_run_1", "test_task", 1
        )
        assert result == "Task log content"
    
    @pytest.mark.unit
    def test_get_task_log_no_content_attr(self, mock_airflow_client):
        """Test task log retrieval when response has no content attribute"""
        mock_response = Mock()
        del mock_response.content  # Remove content attribute
        mock_airflow_client.task_instance_api.get_log.return_value = mock_response
        
        result = mock_airflow_client.get_task_log("test_dag", "test_run_1", "test_task", 1)
        
        assert result == str(mock_response)
    
    @pytest.mark.unit
    def test_clear_task_instance_success(self, mock_airflow_client):
        """Test successful task instance clearing"""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"task_instances_cleared": ["test_task"]}
        mock_airflow_client.dag_api.post_clear_task_instances.return_value = mock_response
        
        with patch('afcli.airflow_client.client.ClearTaskInstancesBody') as mock_clear_body:
            result = mock_airflow_client.clear_task_instance("test_dag", "test_run_1", "test_task")
            
            mock_clear_body.assert_called_once_with(
                dry_run=False,
                task_ids=["test_task"],
                only_failed=True,
                only_running=False,
                include_subdags=True,
                include_parentdag=True,
                reset_dag_runs=False
            )
            assert result["task_instances_cleared"] == ["test_task"]


class TestAirflowClientErrorHandling:
    """Test error handling in AirflowClient"""
    
    @pytest.mark.unit
    def test_handle_api_error_401(self, mock_airflow_client, mock_openapi_exception):
        """Test handling 401 authentication error"""
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(
                mock_openapi_exception(401, "Unauthorized"), 
                "test operation"
            )
    
    @pytest.mark.unit
    def test_handle_api_error_404(self, mock_airflow_client, mock_openapi_exception):
        """Test handling 404 not found error"""
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(
                mock_openapi_exception(404, "Not Found"), 
                "test operation"
            )
    
    @pytest.mark.unit
    def test_handle_api_error_403(self, mock_airflow_client, mock_openapi_exception):
        """Test handling 403 forbidden error"""
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(
                mock_openapi_exception(403, "Forbidden"), 
                "test operation"
            )
    
    @pytest.mark.unit
    def test_handle_api_error_generic(self, mock_airflow_client, mock_openapi_exception):
        """Test handling generic API error"""
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(
                mock_openapi_exception(500, "Internal Server Error"), 
                "test operation"
            )