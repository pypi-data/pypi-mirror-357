#!/usr/bin/env python3
"""
Integration test script for afcli

This script tests various afcli commands against a live Airflow instance.
Requires AIRFLOW_USER and AIRFLOW_PASSWORD environment variables to be set.

Usage:
    export AIRFLOW_USER=admin
    export AIRFLOW_PASSWORD=your_password
    python test_integration.py
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Any
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class IntegrationTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_dag = None
        
        # Check required environment variables
        if not os.getenv('AIRFLOW_USER'):
            print(f"{Colors.RED}ERROR: AIRFLOW_USER environment variable not set{Colors.RESET}")
            sys.exit(1)
        if not os.getenv('AIRFLOW_PASSWORD'):
            print(f"{Colors.RED}ERROR: AIRFLOW_PASSWORD environment variable not set{Colors.RESET}")
            sys.exit(1)
    
    def run_command(self, args: List[str], expect_success: bool = True) -> Dict[str, Any]:
        """Run afcli command and return result"""
        cmd = ['uv', 'run', 'afcli/__init__.py'] + args
        print(f"{Colors.BLUE}Running: {' '.join(cmd)}{Colors.RESET}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def assert_success(self, result: Dict[str, Any], test_name: str):
        """Assert command succeeded"""
        if result['success']:
            print(f"{Colors.GREEN}✓ {test_name}{Colors.RESET}")
            self.passed += 1
        else:
            print(f"{Colors.RED}✗ {test_name}{Colors.RESET}")
            print(f"  stdout: {result['stdout']}")
            print(f"  stderr: {result['stderr']}")
            self.failed += 1
    
    def assert_failure(self, result: Dict[str, Any], test_name: str):
        """Assert command failed (for negative tests)"""
        if not result['success']:
            print(f"{Colors.GREEN}✓ {test_name} (expected failure){Colors.RESET}")
            self.passed += 1
        else:
            print(f"{Colors.RED}✗ {test_name} (expected failure but succeeded){Colors.RESET}")
            print(f"  stdout: {result['stdout']}")
            self.failed += 1
    
    def assert_contains(self, result: Dict[str, Any], text: str, test_name: str):
        """Assert output contains specific text"""
        if result['success'] and text in result['stdout']:
            print(f"{Colors.GREEN}✓ {test_name}{Colors.RESET}")
            self.passed += 1
        else:
            print(f"{Colors.RED}✗ {test_name}{Colors.RESET}")
            print(f"  Expected to contain: {text}")
            print(f"  stdout: {result['stdout']}")
            print(f"  stderr: {result['stderr']}")
            self.failed += 1
    
    def find_test_dag(self):
        """Find a DAG to use for testing"""
        result = self.run_command(['list', '--limit', '10'])
        if result['success'] and result['stdout']:
            lines = result['stdout'].split('\n')
            for line in lines:
                if '│' in line and not line.startswith('│ DAG ID') and 'DAG ID' not in line:
                    # Extract DAG ID from table format
                    parts = line.split('│')
                    if len(parts) > 1:
                        dag_id = parts[1].strip()
                        # Remove any trailing ellipsis or truncation
                        if dag_id.endswith('…'):
                            dag_id = dag_id[:-1]
                        if dag_id and dag_id != 'DAG ID' and len(dag_id) > 3:
                            self.test_dag = dag_id
                            break
        
        if not self.test_dag:
            print(f"{Colors.YELLOW}Warning: No test DAG found, some tests will be skipped{Colors.RESET}")
            # Let's try to find a known DAG name
            result = self.run_command(['list'])
            if result['success']:
                # Look for common test DAG names
                common_dags = ['example_branch_labels', 'example_bash_operator', 'tutorial']
                for dag in common_dags:
                    if dag in result['stdout']:
                        self.test_dag = dag
                        break
                
                # If still not found, try to extract from truncated names
                if not self.test_dag and 'example_b' in result['stdout']:
                    self.test_dag = 'example_branch_labels'
    
    def test_basic_commands(self):
        """Test basic commands"""
        print(f"\n{Colors.BLUE}=== Testing Basic Commands ==={Colors.RESET}")
        
        # Test help
        result = self.run_command(['--help'])
        self.assert_success(result, "Help command")
        
        # Test list command
        result = self.run_command(['list'])
        self.assert_success(result, "List DAGs")
        
        # Test list with limit
        result = self.run_command(['list', '--limit', '5'])
        self.assert_success(result, "List DAGs with limit")
        
        # Test list with --all flag
        result = self.run_command(['list', '--all'])
        self.assert_success(result, "List all DAGs")
    
    def test_dag_operations(self):
        """Test DAG-specific operations"""
        if not self.test_dag:
            print(f"{Colors.YELLOW}Skipping DAG operations - no test DAG available{Colors.RESET}")
            return
        
        print(f"\n{Colors.BLUE}=== Testing DAG Operations (using {self.test_dag}) ==={Colors.RESET}")
        
        # Test status command
        result = self.run_command(['status', self.test_dag])
        self.assert_success(result, f"Get DAG status for {self.test_dag}")
        
        # Test tasks command
        result = self.run_command(['tasks', self.test_dag])
        self.assert_success(result, f"Get tasks for {self.test_dag}")
        
        # Test pause/unpause
        result = self.run_command(['pause', self.test_dag])
        self.assert_success(result, f"Pause DAG {self.test_dag}")
        
        time.sleep(1)  # Brief pause
        
        result = self.run_command(['unpause', self.test_dag])
        self.assert_success(result, f"Unpause DAG {self.test_dag}")
    
    def test_clear_operations(self):
        """Test clear operations"""
        if not self.test_dag:
            print(f"{Colors.YELLOW}Skipping clear operations - no test DAG available{Colors.RESET}")
            return
        
        print(f"\n{Colors.BLUE}=== Testing Clear Operations ==={Colors.RESET}")
        
        # Test clear all failed tasks (should succeed even if no failed tasks)
        result = self.run_command(['clear', self.test_dag, '-y'])
        self.assert_success(result, f"Clear all failed tasks in {self.test_dag}")
        
        # Test clear specific task (may fail if task doesn't exist, but command should handle gracefully)
        result = self.run_command(['clear', self.test_dag, 'nonexistent_task', '-y'])
        # Don't assert success/failure here as it depends on DAG structure
        print(f"Clear specific task result: {result['success']}")
    
    def test_trigger_operations(self):
        """Test trigger operations"""
        if not self.test_dag:
            print(f"{Colors.YELLOW}Skipping trigger operations - no test DAG available{Colors.RESET}")
            return
        
        print(f"\n{Colors.BLUE}=== Testing Trigger Operations ==={Colors.RESET}")
        
        # Test trigger without config
        result = self.run_command(['trigger', self.test_dag])
        self.assert_success(result, f"Trigger DAG {self.test_dag}")
        
        # Test trigger with config
        config = '{"test": true, "integration_test": "yes"}'
        result = self.run_command(['trigger', self.test_dag, '--config', config])
        self.assert_success(result, f"Trigger DAG {self.test_dag} with config")
    
    def test_logs_operations(self):
        """Test logs operations"""
        if not self.test_dag:
            print(f"{Colors.YELLOW}Skipping logs operations - no test DAG available{Colors.RESET}")
            return
        
        print(f"\n{Colors.BLUE}=== Testing Logs Operations ==={Colors.RESET}")
        
        # Get tasks first to find a real task
        tasks_result = self.run_command(['tasks', self.test_dag])
        if tasks_result['success']:
            # Try to extract a task ID from the output
            lines = tasks_result['stdout'].split('\n')
            task_id = None
            for line in lines:
                if '│' in line and not line.startswith('│ Task ID'):
                    parts = line.split('│')
                    if len(parts) > 1:
                        potential_task = parts[1].strip()
                        if potential_task and potential_task != 'Task ID':
                            task_id = potential_task
                            break
            
            if task_id:
                # Test logs command
                result = self.run_command(['logs', self.test_dag, task_id])
                # Logs might fail if no runs exist, so just check if command executes
                print(f"Logs command for {task_id}: {'success' if result['success'] else 'failed (may be expected)'}")
    
    def test_error_cases(self):
        """Test error handling"""
        print(f"\n{Colors.BLUE}=== Testing Error Cases ==={Colors.RESET}")
        
        # Test invalid DAG
        result = self.run_command(['status', 'nonexistent_dag_12345'])
        self.assert_failure(result, "Status for nonexistent DAG")
        
        # Test invalid command
        result = self.run_command(['invalid_command'])
        self.assert_failure(result, "Invalid command")
    
    def test_authentication(self):
        """Test authentication scenarios"""
        print(f"\n{Colors.BLUE}=== Testing Authentication ==={Colors.RESET}")
        
        # Test with explicit credentials
        result = self.run_command([
            '--user', os.getenv('AIRFLOW_USER'),
            '--password', os.getenv('AIRFLOW_PASSWORD'),
            'list', '--limit', '1'
        ])
        self.assert_success(result, "Authentication with explicit credentials")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print(f"{Colors.BLUE}Starting afcli integration tests...{Colors.RESET}")
        print(f"Using Airflow user: {os.getenv('AIRFLOW_USER')}")
        
        # Find a test DAG
        self.find_test_dag()
        if self.test_dag:
            print(f"Using test DAG: {self.test_dag}")
        
        # Run test suites
        self.test_basic_commands()
        self.test_authentication()
        self.test_dag_operations()
        self.test_clear_operations()
        self.test_trigger_operations()
        self.test_logs_operations()
        self.test_error_cases()
        
        # Print summary
        print(f"\n{Colors.BLUE}=== Test Summary ==={Colors.RESET}")
        total = self.passed + self.failed
        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}🎉 All tests passed!{Colors.RESET}")
            return 0
        else:
            print(f"\n{Colors.RED}❌ {self.failed} test(s) failed{Colors.RESET}")
            return 1

def main():
    tester = IntegrationTester()
    return tester.run_all_tests()

if __name__ == '__main__':
    sys.exit(main())