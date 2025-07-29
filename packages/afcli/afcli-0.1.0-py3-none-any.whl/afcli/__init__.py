#!/usr/bin/env python3
"""
Airflow CLI wrapper - A command-line utility for interacting with Airflow REST API
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)


class AirflowClient:
    """Client for interacting with Airflow REST API"""
    
    def __init__(self, host: str = "localhost:8080", username: Optional[str] = None, password: Optional[str] = None):
        self.host = host
        self.base_url = f"http://{host}/api/v2"
        self.session = requests.Session()
        self.token = None
        
        # Authenticate and get token if credentials provided
        if username and password:
            self._authenticate(username, password)
    
    def _authenticate(self, username: str, password: str):
        """Authenticate with Airflow and get a JWT token"""
        auth_url = f"http://{self.host}/auth/token"
        try:
            response = self.session.post(
                auth_url,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Extract token from response
            token_data = response.json()
            if 'access_token' in token_data:
                self.token = token_data['access_token']
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                print(f"{Fore.RED}No access token in response{Style.RESET_ALL}")
                sys.exit(1)
                
        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}Authentication failed: {e}{Style.RESET_ALL}")
            if e.response:
                print(f"{Fore.RED}Response: {e.response.text}{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Failed to authenticate: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request to the Airflow API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"{Fore.RED}Authentication failed. Please check your credentials.{Style.RESET_ALL}")
            elif e.response.status_code == 404:
                print(f"{Fore.RED}Resource not found: {endpoint}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}HTTP Error: {e}{Style.RESET_ALL}")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}Failed to connect to Airflow at {self.base_url}{Style.RESET_ALL}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Request failed: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def list_dags(self, limit: int = 100, only_active: bool = True) -> List[Dict[str, Any]]:
        """List all DAGs"""
        params = {"limit": limit, "only_active": only_active}
        response = self._request("GET", "/dags", params=params)
        return response.json().get("dags", [])
    
    def get_dag(self, dag_id: str) -> Dict[str, Any]:
        """Get DAG details"""
        response = self._request("GET", f"/dags/{dag_id}")
        return response.json()
    
    def get_dag_runs(self, dag_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Get DAG runs"""
        response = self._request("GET", f"/dags/{dag_id}/dagRuns", params={"limit": limit})
        return response.json().get("dag_runs", [])
    
    def toggle_dag_pause(self, dag_id: str, is_paused: bool) -> Dict[str, Any]:
        """Toggle DAG pause state"""
        response = self._request("PATCH", f"/dags/{dag_id}", json={"is_paused": is_paused})
        return response.json()
    
    def trigger_dag(self, dag_id: str, config: Optional[Dict[str, Any]] = None, 
                    logical_date: Optional[str] = None, dag_run_id: Optional[str] = None) -> Dict[str, Any]:
        """Trigger a DAG run"""
        # If no logical_date provided, use current time
        if logical_date is None:
            logical_date = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        data = {
            "logical_date": logical_date,
            "conf": config or {}
        }
        
        # Add optional dag_run_id if provided
        if dag_run_id:
            data["dag_run_id"] = dag_run_id
            
        response = self._request("POST", f"/dags/{dag_id}/dagRuns", json=data)
        return response.json()
    
    def get_task_instances(self, dag_id: str, dag_run_id: str) -> List[Dict[str, Any]]:
        """Get task instances for a DAG run"""
        response = self._request("GET", f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances")
        return response.json().get("task_instances", [])
    
    def get_task_log(self, dag_id: str, dag_run_id: str, task_id: str, task_try_number: int = 1) -> str:
        """Get task log"""
        response = self._request(
            "GET", 
            f"/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{task_try_number}"
        )
        return response.text
    
    def clear_task_instance(self, dag_id: str, dag_run_id: str, task_id: str) -> Dict[str, Any]:
        """Clear a task instance"""
        data = {
            "dry_run": False,
            "task_ids": [task_id],
            "only_failed": True,
            "only_running": False,
            "include_subdags": True,
            "include_parentdag": True,
            "reset_dag_runs": False
        }
        response = self._request(
            "POST",
            f"/dags/{dag_id}/clearTaskInstances",
            json=data
        )
        return response.json()


def format_datetime(dt_str: Optional[str]) -> str:
    """Format datetime string for display"""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def get_status_color(state: str) -> str:
    """Get color for task/dag state"""
    state_colors = {
        "success": Fore.GREEN,
        "failed": Fore.RED,
        "running": Fore.YELLOW,
        "queued": Fore.CYAN,
        "scheduled": Fore.BLUE,
        "skipped": Fore.MAGENTA,
        "up_for_retry": Fore.YELLOW,
        "up_for_reschedule": Fore.YELLOW,
        "deferred": Fore.CYAN,
        "removed": Fore.LIGHTBLACK_EX,
        "restarting": Fore.YELLOW
    }
    return state_colors.get(state.lower(), Fore.WHITE)


def cmd_list(client: AirflowClient, args):
    """List all DAGs"""
    dags = client.list_dags(limit=args.limit, only_active=not args.all)
    
    if not dags:
        print(f"{Fore.YELLOW}No DAGs found{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Available DAGs:{Style.RESET_ALL}")
    
    headers = ["DAG ID", "Is Paused", "Schedule", "Tags", "Next Run", "Import Errors"]
    rows = []
    
    for dag in sorted(dags, key=lambda x: x['dag_id']):
        # Color code based on status
        if dag.get('has_import_errors', False):
            dag_id_display = f"{Fore.RED}{dag['dag_id']}{Style.RESET_ALL}"
        elif dag.get('is_paused', True):
            dag_id_display = f"{Fore.YELLOW}{dag['dag_id']}{Style.RESET_ALL}"
        else:
            dag_id_display = f"{Fore.GREEN}{dag['dag_id']}{Style.RESET_ALL}"
        
        # Get schedule info
        schedule = dag.get('timetable_summary') or dag.get('timetable_description', 'None')
        
        # Extract tag names from tag objects
        tags = dag.get('tags', [])
        tag_names = [tag['name'] if isinstance(tag, dict) else str(tag) for tag in tags]
        
        rows.append([
            dag_id_display,
            f"{Fore.RED if dag.get('is_paused', True) else Fore.GREEN}{'Paused' if dag.get('is_paused', True) else 'Active'}{Style.RESET_ALL}",
            schedule,
            ', '.join(tag_names) or 'None',
            format_datetime(dag.get('next_dagrun_run_after')),
            f"{Fore.RED}Yes{Style.RESET_ALL}" if dag.get('has_import_errors', False) else "No"
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Summary
    total_count = len(dags)
    paused_count = sum(1 for dag in dags if dag.get('is_paused', True))
    active_count = total_count - paused_count
    error_count = sum(1 for dag in dags if dag.get('has_import_errors', False))
    
    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  Total DAGs: {total_count}")
    print(f"  Active: {active_count}")
    print(f"  Paused: {paused_count}")
    if error_count > 0:
        print(f"  {Fore.RED}Import Errors: {error_count}{Style.RESET_ALL}")


def cmd_status(client: AirflowClient, args):
    """View DAG status"""
    dag = client.get_dag(args.dag_id)
    dag_runs = client.get_dag_runs(args.dag_id, limit=5)
    
    print(f"\n{Fore.CYAN}DAG: {dag['dag_id']}{Style.RESET_ALL}")
    if dag.get('dag_display_name') and dag['dag_display_name'] != dag['dag_id']:
        print(f"Display Name: {dag['dag_display_name']}")
    print(f"Description: {dag.get('description', 'N/A')}")
    print(f"Is Paused: {Fore.RED if dag.get('is_paused', True) else Fore.GREEN}{'Yes' if dag.get('is_paused', True) else 'No'}{Style.RESET_ALL}")
    print(f"Schedule: {dag.get('timetable_summary') or dag.get('timetable_description', 'N/A')}")
    # Extract tag names from tag objects
    tags = dag.get('tags', [])
    tag_names = [tag['name'] if isinstance(tag, dict) else str(tag) for tag in tags]
    print(f"Tags: {', '.join(tag_names) or 'None'}")
    print(f"Max Active Tasks: {dag.get('max_active_tasks', 'N/A')}")
    print(f"Max Active Runs: {dag.get('max_active_runs', 'N/A')}")
    if dag.get('has_import_errors', False):
        print(f"{Fore.RED}Import Errors: Yes{Style.RESET_ALL}")
    print(f"Next Run: {format_datetime(dag.get('next_dagrun_run_after'))}")
    
    if dag_runs:
        print(f"\n{Fore.CYAN}Recent DAG Runs:{Style.RESET_ALL}")
        headers = ["Run ID", "State", "Start Date", "End Date"]
        rows = []
        for run in dag_runs:
            state = run.get('state', 'unknown')
            color = get_status_color(state)
            rows.append([
                run['dag_run_id'],
                f"{color}{state}{Style.RESET_ALL}",
                format_datetime(run.get('start_date')),
                format_datetime(run.get('end_date'))
            ])
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print(f"\n{Fore.YELLOW}No recent runs found{Style.RESET_ALL}")


def cmd_pause(client: AirflowClient, args):
    """Pause a DAG"""
    result = client.toggle_dag_pause(args.dag_id, True)
    print(f"{Fore.GREEN}DAG '{args.dag_id}' has been paused{Style.RESET_ALL}")


def cmd_unpause(client: AirflowClient, args):
    """Unpause a DAG"""
    result = client.toggle_dag_pause(args.dag_id, False)
    print(f"{Fore.GREEN}DAG '{args.dag_id}' has been unpaused{Style.RESET_ALL}")


def cmd_trigger(client: AirflowClient, args):
    """Trigger a DAG run"""
    config = None
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Invalid JSON config: {args.config}{Style.RESET_ALL}")
            sys.exit(1)
    
    result = client.trigger_dag(args.dag_id, config)
    print(f"{Fore.GREEN}DAG '{args.dag_id}' triggered successfully{Style.RESET_ALL}")
    print(f"Run ID: {result['dag_run_id']}")
    print(f"State: {result['state']}")


def cmd_tasks(client: AirflowClient, args):
    """View tasks in a DAG and their statuses"""
    # Get the latest DAG run if run_id not specified
    if not args.run_id:
        dag_runs = client.get_dag_runs(args.dag_id, limit=1)
        if not dag_runs:
            print(f"{Fore.YELLOW}No DAG runs found for '{args.dag_id}'{Style.RESET_ALL}")
            return
        dag_run_id = dag_runs[0]['dag_run_id']
        print(f"Using latest run: {dag_run_id}")
    else:
        dag_run_id = args.run_id
    
    tasks = client.get_task_instances(args.dag_id, dag_run_id)
    
    if not tasks:
        print(f"{Fore.YELLOW}No tasks found{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Tasks for DAG '{args.dag_id}' (Run: {dag_run_id}):{Style.RESET_ALL}")
    
    headers = ["Task ID", "State", "Start Date", "End Date", "Duration", "Try Number"]
    rows = []
    
    for task in sorted(tasks, key=lambda x: x.get('start_date') or ''):
        state = task.get('state', 'unknown')
        color = get_status_color(state)
        
        # Calculate duration
        duration = "N/A"
        if task.get('start_date') and task.get('end_date'):
            try:
                start = datetime.fromisoformat(task['start_date'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(task['end_date'].replace('Z', '+00:00'))
                duration = str(end - start).split('.')[0]  # Remove microseconds
            except:
                pass
        
        rows.append([
            task['task_id'],
            f"{color}{state}{Style.RESET_ALL}",
            format_datetime(task.get('start_date')),
            format_datetime(task.get('end_date')),
            duration,
            task.get('try_number', 1)
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Summary
    state_counts = {}
    for task in tasks:
        state = task.get('state', 'unknown')
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    for state, count in state_counts.items():
        color = get_status_color(state)
        print(f"  {color}{state}: {count}{Style.RESET_ALL}")


def cmd_logs(client: AirflowClient, args):
    """View task logs"""
    # Get the latest DAG run if run_id not specified
    if not args.run_id:
        dag_runs = client.get_dag_runs(args.dag_id, limit=1)
        if not dag_runs:
            print(f"{Fore.YELLOW}No DAG runs found for '{args.dag_id}'{Style.RESET_ALL}")
            return
        dag_run_id = dag_runs[0]['dag_run_id']
        print(f"Using latest run: {dag_run_id}")
    else:
        dag_run_id = args.run_id
    
    try:
        logs = client.get_task_log(args.dag_id, dag_run_id, args.task_id, args.try_number)
        print(f"\n{Fore.CYAN}Logs for task '{args.task_id}' (Try: {args.try_number}):{Style.RESET_ALL}")
        print("-" * 80)
        
        # Try to parse as JSON and format nicely
        try:
            log_data = json.loads(logs)
            if isinstance(log_data, dict) and 'content' in log_data:
                for entry in log_data['content']:
                    if 'timestamp' in entry and 'event' in entry:
                        timestamp = entry['timestamp'][:19].replace('T', ' ')
                        level = entry.get('level', 'info').upper()
                        logger = entry.get('logger', '')
                        event = entry['event']
                        
                        # Color code by level
                        if level == 'ERROR':
                            level_color = Fore.RED
                        elif level == 'WARNING':
                            level_color = Fore.YELLOW
                        elif level == 'INFO':
                            level_color = Fore.CYAN
                        else:
                            level_color = Fore.WHITE
                        
                        print(f"{timestamp} {level_color}[{level}]{Style.RESET_ALL} {logger}: {event}")
                    elif 'event' in entry:
                        # Simple event without timestamp
                        print(entry['event'])
            else:
                # Not the expected format, print as is
                print(logs)
        except json.JSONDecodeError:
            # Not JSON, print as plain text
            print(logs)
            
        print("-" * 80)
    except Exception as e:
        print(f"{Fore.RED}Failed to retrieve logs: {e}{Style.RESET_ALL}")


def cmd_clear(client: AirflowClient, args):
    """Clear failed tasks in a DAG"""
    # Get the latest DAG run if run_id not specified
    if not args.run_id:
        dag_runs = client.get_dag_runs(args.dag_id, limit=1)
        if not dag_runs:
            print(f"{Fore.YELLOW}No DAG runs found for '{args.dag_id}'{Style.RESET_ALL}")
            return
        dag_run_id = dag_runs[0]['dag_run_id']
        print(f"Using latest run: {dag_run_id}")
    else:
        dag_run_id = args.run_id
    
    if args.task_id:
        # Clear specific task
        result = client.clear_task_instance(args.dag_id, dag_run_id, args.task_id)
        print(f"{Fore.GREEN}Cleared task '{args.task_id}'{Style.RESET_ALL}")
    else:
        # Clear all failed tasks
        tasks = client.get_task_instances(args.dag_id, dag_run_id)
        failed_tasks = [t for t in tasks if t.get('state') == 'failed']
        
        if not failed_tasks:
            print(f"{Fore.YELLOW}No failed tasks found{Style.RESET_ALL}")
            return
        
        print(f"Found {len(failed_tasks)} failed tasks:")
        for task in failed_tasks:
            print(f"  - {task['task_id']}")
        
        if not args.yes:
            response = input(f"\n{Fore.YELLOW}Clear all failed tasks? [y/N]: {Style.RESET_ALL}")
            if response.lower() != 'y':
                print("Cancelled")
                return
        
        for task in failed_tasks:
            result = client.clear_task_instance(args.dag_id, dag_run_id, task['task_id'])
            print(f"{Fore.GREEN}Cleared task '{task['task_id']}'{Style.RESET_ALL}")


def main():
    examples = """
Examples:
  # Set credentials via environment variables
  export AIRFLOW_USER=admin AIRFLOW_PASSWORD=secret

  # List all DAGs
  afcli list

  # Get DAG status and recent runs
  afcli status my_dag

  # View tasks and their status in a DAG run
  afcli tasks my_dag

  # Trigger a DAG with configuration
  afcli trigger my_dag --config '{"date": "2024-01-01", "env": "prod"}'

  # View logs for a specific task
  afcli logs my_dag task_name

  # Pause/unpause DAGs
  afcli pause my_dag
  afcli unpause my_dag

  # Clear failed tasks
  afcli clear my_dag

  # Use with different Airflow instance
  afcli --host airflow.company.com:8080 --user admin --password secret list

Useful LLM Context Commands:
  afcli list --limit 20                    # See available DAGs
  afcli status <dag_id>                     # Get DAG details and recent runs
  afcli tasks <dag_id>                      # See task execution status
  afcli logs <dag_id> <task_id>            # Debug task failures
"""

    parser = argparse.ArgumentParser(
        description="Airflow CLI wrapper - A command-line utility for interacting with Airflow REST API",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument("--host", 
                        default=os.environ.get("AIRFLOW_HOST", "localhost:8080"), 
                        help="Airflow host (default: localhost:8080, env: AIRFLOW_HOST)")
    parser.add_argument("--user", 
                        default=os.environ.get("AIRFLOW_USER"), 
                        help="Username for API authentication (env: AIRFLOW_USER)")
    parser.add_argument("--password", 
                        default=os.environ.get("AIRFLOW_PASSWORD"), 
                        help="Password for API authentication (env: AIRFLOW_PASSWORD)")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all DAGs")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of DAGs to display (default: 100)")
    list_parser.add_argument("--all", action="store_true", help="Show all DAGs including inactive ones")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="View DAG status")
    status_parser.add_argument("dag_id", help="DAG ID")
    
    # Pause command
    pause_parser = subparsers.add_parser("pause", help="Pause a DAG")
    pause_parser.add_argument("dag_id", help="DAG ID")
    
    # Unpause command
    unpause_parser = subparsers.add_parser("unpause", help="Unpause a DAG")
    unpause_parser.add_argument("dag_id", help="DAG ID")
    
    # Trigger command
    trigger_parser = subparsers.add_parser("trigger", help="Trigger a DAG run")
    trigger_parser.add_argument("dag_id", help="DAG ID")
    trigger_parser.add_argument("--config", help="JSON configuration for the DAG run")
    
    # Tasks command
    tasks_parser = subparsers.add_parser("tasks", help="View tasks in a DAG and their statuses")
    tasks_parser.add_argument("dag_id", help="DAG ID")
    tasks_parser.add_argument("--run-id", help="DAG run ID (default: latest)")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View task logs")
    logs_parser.add_argument("dag_id", help="DAG ID")
    logs_parser.add_argument("task_id", help="Task ID")
    logs_parser.add_argument("--run-id", help="DAG run ID (default: latest)")
    logs_parser.add_argument("--try-number", type=int, default=1, help="Task try number (default: 1)")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear failed tasks")
    clear_parser.add_argument("dag_id", help="DAG ID")
    clear_parser.add_argument("--task-id", help="Specific task ID to clear (default: all failed tasks)")
    clear_parser.add_argument("--run-id", help="DAG run ID (default: latest)")
    clear_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create client
    client = AirflowClient(args.host, args.user, args.password)
    
    # Execute command
    commands = {
        "list": cmd_list,
        "status": cmd_status,
        "pause": cmd_pause,
        "unpause": cmd_unpause,
        "trigger": cmd_trigger,
        "tasks": cmd_tasks,
        "logs": cmd_logs,
        "clear": cmd_clear
    }
    
    command_func = commands.get(args.command)
    if command_func:
        command_func(client, args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()