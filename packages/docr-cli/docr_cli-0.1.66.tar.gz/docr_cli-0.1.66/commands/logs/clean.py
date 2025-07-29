#!/usr/bin/env python3
"""Clean CloudWatch logs command for removing logs from lambda functions."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import boto3
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.base_cli import BaseCLI

console = Console()


class LogsCleanCLI(BaseCLI):
    """Clean CloudWatch logs from lambda functions."""

    def __init__(self):
        """Initialize Logs Clean CLI."""
        super().__init__(
            name="logs-clean",
            help_text="Clean CloudWatch logs from lambda functions",
            require_config=True
        )

    def _get_lambda_function_names(self) -> List[str]:
        """Get lambda function names from docr.toml config."""
        from utils import AppConfig
        
        try:
            config_data = AppConfig.load_config()
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return []
        
        function_names = []
        
        # Get lambda functions from applications
        if 'applications' in config_data:
            for app_name, app_config in config_data['applications'].items():
                if 'lambda_function_name' in app_config and app_config['lambda_function_name']:
                    function_names.append(app_config['lambda_function_name'])
        
        # Get lambda functions from components
        if 'components' in config_data:
            for comp_name, comp_config in config_data['components'].items():
                if 'lambda_function_name' in comp_config and comp_config['lambda_function_name']:
                    function_names.append(comp_config['lambda_function_name'])
        
        # Get OIDC authorizer function
        if 'oidc' in config_data and 'authorizer' in config_data['oidc']:
            if 'function_name' in config_data['oidc']['authorizer'] and config_data['oidc']['authorizer']['function_name']:
                function_names.append(config_data['oidc']['authorizer']['function_name'])
        
        return list(set(function_names))  # Remove duplicates

    def _get_log_group_name(self, function_name: str) -> str:
        """Convert lambda function name to CloudWatch log group name."""
        return f"/aws/lambda/{function_name}"

    def _delete_log_streams(self, log_group_name: str) -> int:
        """Delete all log streams in a log group."""
        logs_client = boto3.client('logs')
        deleted_count = 0
        
        try:
            # Get all log streams
            paginator = logs_client.get_paginator('describe_log_streams')
            
            for page in paginator.paginate(logGroupName=log_group_name):
                log_streams = page.get('logStreams', [])
                
                if not log_streams:
                    continue
                
                # Delete log streams in batches
                for stream in log_streams:
                    stream_name = stream['logStreamName']
                    try:
                        logs_client.delete_log_stream(
                            logGroupName=log_group_name,
                            logStreamName=stream_name
                        )
                        deleted_count += 1
                    except Exception as e:
                        console.print(f"  [red]Failed to delete stream {stream_name}: {str(e)}[/red]")
                        
        except logs_client.exceptions.ResourceNotFoundException:
            console.print(f"  [yellow]Log group {log_group_name} not found[/yellow]")
        except Exception as e:
            console.print(f"  [red]Error processing {log_group_name}: {str(e)}[/red]")
        
        return deleted_count

    def _clean_log_group(self, function_name: str) -> tuple:
        """Clean a single log group and return (function_name, streams_deleted)."""
        log_group_name = self._get_log_group_name(function_name)
        console.print(f"  Cleaning {log_group_name}...")
        
        deleted_count = self._delete_log_streams(log_group_name)
        return (function_name, deleted_count)

    def cli(self, yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")) -> None:
        """Clean all CloudWatch logs from lambda functions.
        
        This command deletes all log streams from CloudWatch log groups
        associated with lambda functions defined in docr.toml.
        """
        function_names = self._get_lambda_function_names()
        
        if not function_names:
            console.print("[yellow]No lambda functions found in configuration[/yellow]")
            return
        
        console.print(f"\n[bold]Found {len(function_names)} lambda functions:[/bold]")
        for name in function_names:
            console.print(f"  • {name}")
        
        # Confirm before deletion
        if not yes and not typer.confirm(f"\nAre you sure you want to delete ALL logs from these {len(function_names)} log groups?"):
            console.print("[red]Operation cancelled[/red]")
            return
        
        console.print("\n[bold]Cleaning CloudWatch logs in parallel...[/bold]")
        
        total_deleted = 0
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks
            future_to_function = {
                executor.submit(self._clean_log_group, func_name): func_name 
                for func_name in function_names
            }
            
            # Process completed tasks
            for future in as_completed(future_to_function):
                function_name, deleted_count = future.result()
                total_deleted += deleted_count
                console.print(f"  ✅ {function_name}: {deleted_count} streams deleted")
        
        console.print(f"\n[bold green]✅ Cleanup complete![/bold green]")
        console.print(f"Total log streams deleted: {total_deleted}")


def main():
    """Entry point for logs clean command."""
    cli = LogsCleanCLI()
    cli.cli()


if __name__ == "__main__":
    main()