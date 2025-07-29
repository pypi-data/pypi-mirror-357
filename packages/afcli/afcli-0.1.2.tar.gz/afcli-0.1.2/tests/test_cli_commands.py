"""Tests for CLI command functions"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from afcli import (
    cmd_list, cmd_status, cmd_pause, cmd_unpause, cmd_trigger, 
    cmd_tasks, cmd_logs, cmd_clear, main
)


class TestCmdList:
    """Test the cmd_list function"""
    
    @pytest.mark.unit
    def test_cmd_list_success(self, mock_cli_client, mock_dag_data, capsys):
        """Test successful DAG listing"""
        # Mock the client.list_dags method
        mock_cli_client.list_dags.return_value = [mock_dag_data]
        
        # Create mock args
        args = Mock()
        args.limit = 10
        args.all = False
        
        cmd_list(mock_cli_client, args)
        
        mock_cli_client.list_dags.assert_called_once_with(limit=10, only_active=True)
        
        captured = capsys.readouterr()
        assert "Available DAGs:" in captured.out
        assert "test_dag" in captured.out
        assert "Summary:" in captured.out
    
    @pytest.mark.unit
    def test_cmd_list_all_dags(self, mock_cli_client, mock_dag_data):
        """Test listing all DAGs including inactive ones"""
        mock_cli_client.list_dags.return_value = [mock_dag_data]
        
        args = Mock()
        args.limit = 10
        args.all = True
        
        cmd_list(mock_cli_client, args)
        
        mock_cli_client.list_dags.assert_called_once_with(limit=10, only_active=False)
    
    @pytest.mark.unit
    def test_cmd_list_no_dags(self, mock_cli_client, capsys):
        """Test listing when no DAGs are found"""
        mock_cli_client.list_dags.return_value = []
        
        args = Mock()
        args.limit = 10
        args.all = False
        
        cmd_list(mock_cli_client, args)
        
        captured = capsys.readouterr()
        assert "No DAGs found" in captured.out


class TestCmdStatus:
    """Test the cmd_status function"""
    
    @pytest.mark.unit
    def test_cmd_status_success(self, mock_cli_client, mock_dag_data, mock_dag_run_data, capsys):
        """Test successful DAG status display"""
        mock_cli_client.get_dag.return_value = mock_dag_data
        mock_cli_client.get_dag_runs.return_value = [mock_dag_run_data]
        
        args = Mock()
        args.dag_id = "test_dag"
        
        cmd_status(mock_cli_client, args)
        
        mock_cli_client.get_dag.assert_called_once_with("test_dag")
        mock_cli_client.get_dag_runs.assert_called_once_with("test_dag", limit=5)
        
        captured = capsys.readouterr()
        assert "DAG: test_dag" in captured.out
        assert "Recent DAG Runs:" in captured.out
    
    @pytest.mark.unit
    def test_cmd_status_no_runs(self, mock_cli_client, mock_dag_data, capsys):
        """Test DAG status with no recent runs"""
        mock_cli_client.get_dag.return_value = mock_dag_data
        mock_cli_client.get_dag_runs.return_value = []
        
        args = Mock()
        args.dag_id = "test_dag"
        
        cmd_status(mock_cli_client, args)
        
        captured = capsys.readouterr()
        assert "No recent runs found" in captured.out


class TestCmdPauseUnpause:
    """Test pause/unpause commands"""
    
    @pytest.mark.unit
    def test_cmd_pause(self, mock_cli_client, capsys):
        """Test DAG pause command"""
        mock_cli_client.toggle_dag_pause.return_value = {"is_paused": True}
        
        args = Mock()
        args.dag_id = "test_dag"
        
        cmd_pause(mock_cli_client, args)
        
        mock_cli_client.toggle_dag_pause.assert_called_once_with("test_dag", True)
        
        captured = capsys.readouterr()
        assert "DAG 'test_dag' has been paused" in captured.out
    
    @pytest.mark.unit
    def test_cmd_unpause(self, mock_cli_client, capsys):
        """Test DAG unpause command"""
        mock_cli_client.toggle_dag_pause.return_value = {"is_paused": False}
        
        args = Mock()
        args.dag_id = "test_dag"
        
        cmd_unpause(mock_cli_client, args)
        
        mock_cli_client.toggle_dag_pause.assert_called_once_with("test_dag", False)
        
        captured = capsys.readouterr()
        assert "DAG 'test_dag' has been unpaused" in captured.out


class TestCmdTrigger:
    """Test the cmd_trigger function"""
    
    @pytest.mark.unit
    def test_cmd_trigger_success(self, mock_cli_client, capsys):
        """Test successful DAG triggering"""
        mock_response = {
            "dag_run_id": "manual_123",
            "state": "queued"
        }
        mock_cli_client.trigger_dag.return_value = mock_response
        
        args = Mock()
        args.dag_id = "test_dag"
        args.config = None
        
        cmd_trigger(mock_cli_client, args)
        
        mock_cli_client.trigger_dag.assert_called_once_with("test_dag", None)
        
        captured = capsys.readouterr()
        assert "DAG 'test_dag' triggered successfully" in captured.out
        assert "Run ID: manual_123" in captured.out
    
    @pytest.mark.unit
    def test_cmd_trigger_with_config(self, mock_cli_client):
        """Test DAG triggering with configuration"""
        mock_response = {
            "dag_run_id": "manual_123",
            "state": "queued"
        }
        mock_cli_client.trigger_dag.return_value = mock_response
        
        args = Mock()
        args.dag_id = "test_dag"
        args.config = '{"key": "value", "number": 42}'
        
        cmd_trigger(mock_cli_client, args)
        
        expected_config = {"key": "value", "number": 42}
        mock_cli_client.trigger_dag.assert_called_once_with("test_dag", expected_config)
    
    @pytest.mark.unit
    def test_cmd_trigger_invalid_json(self, mock_cli_client):
        """Test DAG triggering with invalid JSON config"""
        args = Mock()
        args.dag_id = "test_dag"
        args.config = '{"invalid": json}'
        
        with pytest.raises(SystemExit):
            cmd_trigger(mock_cli_client, args)


class TestCmdTasks:
    """Test the cmd_tasks function"""
    
    @pytest.mark.unit
    def test_cmd_tasks_with_run_id(self, mock_cli_client, mock_task_instance_data, capsys):
        """Test tasks command with specific run ID"""
        mock_cli_client.get_task_instances.return_value = [mock_task_instance_data]
        
        args = Mock()
        args.dag_id = "test_dag"
        args.run_id = "test_run_1"
        
        cmd_tasks(mock_cli_client, args)
        
        mock_cli_client.get_task_instances.assert_called_once_with("test_dag", "test_run_1")
        
        captured = capsys.readouterr()
        assert "Tasks for DAG 'test_dag'" in captured.out
        assert "test_task" in captured.out
    
    @pytest.mark.unit
    def test_cmd_tasks_latest_run(self, mock_cli_client, mock_dag_run_data, mock_task_instance_data, capsys):
        """Test tasks command using latest run"""
        mock_cli_client.get_dag_runs.return_value = [mock_dag_run_data]
        mock_cli_client.get_task_instances.return_value = [mock_task_instance_data]
        
        args = Mock()
        args.dag_id = "test_dag"
        args.run_id = None
        
        cmd_tasks(mock_cli_client, args)
        
        mock_cli_client.get_dag_runs.assert_called_once_with("test_dag", limit=1)
        mock_cli_client.get_task_instances.assert_called_once_with("test_dag", "test_run_1")
        
        captured = capsys.readouterr()
        assert "Using latest run: test_run_1" in captured.out
    
    @pytest.mark.unit
    def test_cmd_tasks_no_runs(self, mock_cli_client, capsys):
        """Test tasks command when no runs exist"""
        mock_cli_client.get_dag_runs.return_value = []
        
        args = Mock()
        args.dag_id = "test_dag"
        args.run_id = None
        
        cmd_tasks(mock_cli_client, args)
        
        captured = capsys.readouterr()
        assert "No DAG runs found for 'test_dag'" in captured.out


class TestCmdLogs:
    """Test the cmd_logs function"""
    
    @pytest.mark.unit
    def test_cmd_logs_with_run_id(self, mock_cli_client, capsys):
        """Test logs command with specific run ID"""
        mock_cli_client.get_task_log.return_value = "Task log content here"
        
        args = Mock()
        args.dag_id = "test_dag"
        args.task_id = "test_task"
        args.run_id = "test_run_1"
        args.try_number = 1
        
        cmd_logs(mock_cli_client, args)
        
        mock_cli_client.get_task_log.assert_called_once_with("test_dag", "test_run_1", "test_task", 1)
        
        captured = capsys.readouterr()
        assert "Logs for task 'test_task'" in captured.out
        assert "Task log content here" in captured.out
    
    @pytest.mark.unit
    def test_cmd_logs_latest_run(self, mock_cli_client, mock_dag_run_data, capsys):
        """Test logs command using latest run"""
        mock_cli_client.get_dag_runs.return_value = [mock_dag_run_data]
        mock_cli_client.get_task_log.return_value = "Task log content"
        
        args = Mock()
        args.dag_id = "test_dag"
        args.task_id = "test_task"
        args.run_id = None
        args.try_number = 1
        
        cmd_logs(mock_cli_client, args)
        
        mock_cli_client.get_dag_runs.assert_called_once_with("test_dag", limit=1)
        
        captured = capsys.readouterr()
        assert "Using latest run: test_run_1" in captured.out


class TestCmdClear:
    """Test the cmd_clear function"""
    
    @pytest.mark.unit
    def test_cmd_clear_specific_task(self, mock_cli_client, capsys):
        """Test clearing a specific task"""
        mock_cli_client.clear_task_instance.return_value = {"cleared": True}
        
        args = Mock()
        args.dag_id = "test_dag"
        args.task_id = "test_task"
        args.run_id = "test_run_1"
        args.yes = False
        
        cmd_clear(mock_cli_client, args)
        
        mock_cli_client.clear_task_instance.assert_called_once_with("test_dag", "test_run_1", "test_task")
        
        captured = capsys.readouterr()
        assert "Cleared task 'test_task'" in captured.out
    
    @pytest.mark.unit
    def test_cmd_clear_failed_tasks_with_confirmation(self, mock_cli_client, mock_task_instance_data):
        """Test clearing all failed tasks with user confirmation"""
        # Mock failed task
        failed_task = mock_task_instance_data.copy()
        failed_task["state"] = "failed"
        
        mock_cli_client.get_dag_runs.return_value = [{"dag_run_id": "test_run_1"}]
        mock_cli_client.get_task_instances.return_value = [failed_task]
        mock_cli_client.clear_task_instance.return_value = {"cleared": True}
        
        args = Mock()
        args.dag_id = "test_dag"
        args.task_id = None
        args.run_id = None
        args.yes = True  # Skip confirmation
        
        cmd_clear(mock_cli_client, args)
        
        mock_cli_client.clear_task_instance.assert_called_once_with("test_dag", "test_run_1", "test_task")
    
    @pytest.mark.unit
    def test_cmd_clear_no_failed_tasks(self, mock_cli_client, mock_task_instance_data, capsys):
        """Test clearing when no failed tasks exist"""
        # Mock successful task
        successful_task = mock_task_instance_data.copy()
        successful_task["state"] = "success"
        
        mock_cli_client.get_dag_runs.return_value = [{"dag_run_id": "test_run_1"}]
        mock_cli_client.get_task_instances.return_value = [successful_task]
        
        args = Mock()
        args.dag_id = "test_dag"
        args.task_id = None
        args.run_id = None
        args.yes = False
        
        cmd_clear(mock_cli_client, args)
        
        captured = capsys.readouterr()
        assert "No failed tasks found" in captured.out


class TestMainFunction:
    """Test the main function and argument parsing"""
    
    @pytest.mark.integration
    @patch('afcli.AirflowClient')
    @patch('sys.argv')
    def test_main_list_command(self, mock_argv, mock_client_class):
        """Test main function with list command"""
        mock_argv.__getitem__.side_effect = lambda x: [
            'afcli', '--host', 'localhost:8080', '--user', 'admin', 
            '--password', 'secret', 'list', '--limit', '5'
        ][x]
        mock_argv.__len__.return_value = 8
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list_dags.return_value = []
        
        with patch('afcli.cmd_list') as mock_cmd_list:
            try:
                main()
            except SystemExit:
                pass  # Expected for successful completion
            
            mock_client_class.assert_called_once_with('localhost:8080', 'admin', 'secret')
            mock_cmd_list.assert_called_once()
    
    @pytest.mark.integration
    @patch('sys.argv', ['afcli'])
    def test_main_no_command(self, capsys):
        """Test main function with no command"""
        with pytest.raises(SystemExit):
            main()
    
    @pytest.mark.integration
    @patch('sys.argv', ['afcli', '--help'])
    def test_main_help(self):
        """Test main function with help"""
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Help should exit with code 0
        assert exc_info.value.code == 0