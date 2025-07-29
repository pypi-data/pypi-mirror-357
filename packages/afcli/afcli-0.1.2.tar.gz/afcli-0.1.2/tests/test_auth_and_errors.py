"""Tests for authentication and error handling"""

import pytest
import responses
import requests
from unittest.mock import Mock, patch, MagicMock
from airflow_client.client.exceptions import OpenApiException

from afcli import AirflowClient


class TestAuthentication:
    """Test authentication mechanisms"""
    
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
            
            assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
            
            # Verify the request was made correctly
            assert len(responses_mock.calls) == 1
            request = responses_mock.calls[0].request
            assert request.headers["Content-Type"] == "application/json"
            request_body = request.body.decode() if isinstance(request.body, bytes) else request.body
            assert '"username": "admin"' in request_body
            assert '"password": "password"' in request_body
    
    @pytest.mark.unit
    def test_get_jwt_token_http_401_error(self, responses_mock, capsys):
        """Test JWT token retrieval with 401 error"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json={"detail": "Invalid credentials"},
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
            
            captured = capsys.readouterr()
            assert "Authentication failed" in captured.out
    
    @pytest.mark.unit
    def test_get_jwt_token_http_500_error(self, responses_mock, capsys):
        """Test JWT token retrieval with 500 server error"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json={"error": "Internal server error"},
            status=500
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")
            
            captured = capsys.readouterr()
            assert "Authentication failed" in captured.out
    
    @pytest.mark.unit
    def test_get_jwt_token_connection_error(self, responses_mock, capsys):
        """Test JWT token retrieval with connection error"""
        # Don't add any response to simulate connection error
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'), \
             patch('requests.post', side_effect=requests.ConnectionError("Connection failed")):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")
            
            captured = capsys.readouterr()
            assert "Failed to authenticate" in captured.out
    
    @pytest.mark.unit
    def test_get_jwt_token_missing_access_token(self, responses_mock, capsys):
        """Test JWT token retrieval when response doesn't contain access_token"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            json={"message": "Login successful"},  # Missing access_token
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
            
            captured = capsys.readouterr()
            assert "No access token in response" in captured.out
    
    @pytest.mark.unit
    def test_get_jwt_token_invalid_json(self, responses_mock, capsys):
        """Test JWT token retrieval with invalid JSON response"""
        responses_mock.add(
            responses.POST,
            "http://localhost:8080/auth/token",
            body="Invalid JSON response",
            status=200,
            content_type="text/plain"
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")
            
            captured = capsys.readouterr()
            assert "Failed to authenticate" in captured.out


class TestErrorHandling:
    """Test error handling throughout the application"""
    
    @pytest.mark.unit
    def test_handle_api_error_401_unauthorized(self, mock_airflow_client, capsys):
        """Test handling 401 Unauthorized error"""
        exception = OpenApiException("401 Unauthorized")
        exception.status = 401
        exception.reason = "Unauthorized"
        
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(exception, "test operation")
        
        captured = capsys.readouterr()
        assert "Authentication failed. Please check your credentials." in captured.out
    
    @pytest.mark.unit
    def test_handle_api_error_404_not_found(self, mock_airflow_client, capsys):
        """Test handling 404 Not Found error"""
        exception = OpenApiException("404 Not Found")
        exception.status = 404
        exception.reason = "Not Found"
        
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(exception, "get DAG details")
        
        captured = capsys.readouterr()
        assert "Resource not found for operation: get DAG details" in captured.out
    
    @pytest.mark.unit
    def test_handle_api_error_403_forbidden(self, mock_airflow_client, capsys):
        """Test handling 403 Forbidden error"""
        exception = OpenApiException("403 Forbidden")
        exception.status = 403
        exception.reason = "Forbidden"
        
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(exception, "modify DAG")
        
        captured = capsys.readouterr()
        assert "Access forbidden for operation: modify DAG" in captured.out
    
    @pytest.mark.unit
    def test_handle_api_error_500_server_error(self, mock_airflow_client, capsys):
        """Test handling 500 Internal Server Error"""
        exception = OpenApiException("500 Internal Server Error")
        exception.status = 500
        exception.reason = "Internal Server Error"
        
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(exception, "list DAGs")
        
        captured = capsys.readouterr()
        assert "API Error (500): Internal Server Error" in captured.out
    
    @pytest.mark.unit
    def test_handle_api_error_unknown_status(self, mock_airflow_client, capsys):
        """Test handling unknown API error status"""
        exception = OpenApiException("422 Unprocessable Entity")
        exception.status = 422
        exception.reason = "Unprocessable Entity"
        
        with pytest.raises(SystemExit):
            mock_airflow_client._handle_api_error(exception, "process request")
        
        captured = capsys.readouterr()
        assert "API Error (422): Unprocessable Entity" in captured.out


class TestClientMethodErrorHandling:
    """Test error handling in specific client methods"""
    
    @pytest.mark.unit
    def test_list_dags_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test list_dags method with API error"""
        mock_airflow_client.dag_api.get_dags.side_effect = mock_openapi_exception(500)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.list_dags()
    
    @pytest.mark.unit
    def test_get_dag_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test get_dag method with API error"""
        mock_airflow_client.dag_api.get_dag.side_effect = mock_openapi_exception(404)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.get_dag("nonexistent_dag")
    
    @pytest.mark.unit
    def test_get_dag_runs_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test get_dag_runs method with API error"""
        mock_airflow_client.dag_run_api.get_dag_runs.side_effect = mock_openapi_exception(403)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.get_dag_runs("test_dag")
    
    @pytest.mark.unit
    def test_toggle_dag_pause_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test toggle_dag_pause method with API error"""
        with patch('afcli.airflow_client.client.DAGPatchBody'), \
             patch.object(mock_airflow_client.dag_api, 'patch_dag', 
                         side_effect=mock_openapi_exception(401)):
            
            with pytest.raises(SystemExit):
                mock_airflow_client.toggle_dag_pause("test_dag", True)
    
    @pytest.mark.unit
    def test_trigger_dag_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test trigger_dag method with API error"""
        with patch('afcli.airflow_client.client.TriggerDAGRunPostBody'), \
             patch.object(mock_airflow_client.dag_run_api, 'post_dag_run', 
                         side_effect=mock_openapi_exception(400)):
            
            with pytest.raises(SystemExit):
                mock_airflow_client.trigger_dag("test_dag")
    
    @pytest.mark.unit
    def test_get_task_instances_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test get_task_instances method with API error"""
        mock_airflow_client.task_instance_api.get_task_instances.side_effect = mock_openapi_exception(404)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.get_task_instances("test_dag", "test_run")
    
    @pytest.mark.unit
    def test_get_task_log_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test get_task_log method with API error"""
        mock_airflow_client.task_instance_api.get_log.side_effect = mock_openapi_exception(404)
        
        with pytest.raises(SystemExit):
            mock_airflow_client.get_task_log("test_dag", "test_run", "test_task")
    
    @pytest.mark.unit
    def test_clear_task_instance_api_error(self, mock_airflow_client, mock_openapi_exception):
        """Test clear_task_instance method with API error"""
        with patch('afcli.airflow_client.client.ClearTaskInstancesBody'), \
             patch.object(mock_airflow_client.dag_api, 'post_clear_task_instances', 
                         side_effect=mock_openapi_exception(403)):
            
            with pytest.raises(SystemExit):
                mock_airflow_client.clear_task_instance("test_dag", "test_run", "test_task")


class TestNetworkErrorHandling:
    """Test handling of network-related errors"""
    
    @pytest.mark.unit
    def test_authentication_network_timeout(self, responses_mock, capsys):
        """Test authentication with network timeout"""
        import socket
        
        def request_callback(request):
            raise socket.timeout("Request timed out")
        
        responses_mock.add_callback(
            responses.POST,
            "http://localhost:8080/auth/token",
            callback=request_callback
        )
        
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'):
            
            client = AirflowClient("localhost:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")
            
            captured = capsys.readouterr()
            assert "Failed to authenticate" in captured.out
    
    @pytest.mark.unit
    def test_authentication_dns_error(self, capsys):
        """Test authentication with DNS resolution error"""
        with patch('afcli.airflow_client.client.Configuration'), \
             patch('afcli.airflow_client.client.ApiClient'), \
             patch('afcli.dag_api.DAGApi'), \
             patch('afcli.dag_run_api.DagRunApi'), \
             patch('afcli.task_instance_api.TaskInstanceApi'), \
             patch('requests.post', side_effect=requests.exceptions.ConnectionError("Name resolution failed")):
            
            client = AirflowClient("invalid-host:8080")
            
            with pytest.raises(SystemExit):
                client._get_jwt_token("admin", "password")
            
            captured = capsys.readouterr()
            assert "Failed to authenticate" in captured.out