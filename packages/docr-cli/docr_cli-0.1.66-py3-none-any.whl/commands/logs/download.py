#!/usr/bin/env python3
"""Download CloudWatch logs command for downloading logs from lambda functions."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import boto3
import typer
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from utils.base_cli import BaseCLI

console = Console()


class LogsDownloadCLI(BaseCLI):
    """Download CloudWatch logs from lambda functions."""

    def __init__(self):
        """Initialize Logs Download CLI."""
        super().__init__(
            name="logs-download",
            help_text="Download CloudWatch logs from lambda functions",
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

    def _download_log_group(self, function_name: str, output_dir: Path, task_id: Optional[TaskID] = None, progress: Optional[Progress] = None) -> tuple:
        """Download logs from a single log group and return (function_name, events_count, file_path)."""
        log_group_name = self._get_log_group_name(function_name)
        logs_client = boto3.client('logs')
        
        # Create output file
        safe_function_name = function_name.replace('/', '_').replace(':', '_')
        output_file = output_dir / f"{safe_function_name}.log"
        
        events_count = 0
        
        try:
            # Get logs from the last 7 days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            # Convert to milliseconds since epoch
            start_time_ms = int(start_time.timestamp() * 1000)
            end_time_ms = int(end_time.timestamp() * 1000)
            
            with open(output_file, 'w') as f:
                # Write header
                f.write(f"# CloudWatch Logs for {log_group_name}\n")
                f.write(f"# Downloaded: {datetime.utcnow().isoformat()}Z\n")
                f.write(f"# Time range: {start_time.isoformat()}Z to {end_time.isoformat()}Z\n")
                f.write("# " + "="*80 + "\n\n")
                
                # Get log events using filter_log_events
                paginator = logs_client.get_paginator('filter_log_events')
                
                for page in paginator.paginate(
                    logGroupName=log_group_name,
                    startTime=start_time_ms,
                    endTime=end_time_ms
                ):
                    events = page.get('events', [])
                    
                    for event in events:
                        timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                        message = event['message'].rstrip()
                        
                        f.write(f"[{timestamp.isoformat()}Z] {message}\n")
                        events_count += 1
                        
                        if progress and task_id:
                            progress.update(task_id, advance=1)
                
        except logs_client.exceptions.ResourceNotFoundException:
            # Log group doesn't exist, create empty file with note
            with open(output_file, 'w') as f:
                f.write(f"# Log group {log_group_name} not found\n")
                f.write(f"# Downloaded: {datetime.utcnow().isoformat()}Z\n")
        except Exception as e:
            # Create error file
            with open(output_file, 'w') as f:
                f.write(f"# Error downloading logs from {log_group_name}\n")
                f.write(f"# Downloaded: {datetime.utcnow().isoformat()}Z\n")
                f.write(f"# Error: {str(e)}\n")
        
        return (function_name, events_count, str(output_file))

    def cli(self) -> None:
        """Download all CloudWatch logs from lambda functions.
        
        This command downloads logs from CloudWatch log groups
        associated with lambda functions defined in docr.toml.
        Logs are saved to /tmp/docr/logs/{function-name}.log
        """
        function_names = self._get_lambda_function_names()
        
        if not function_names:
            console.print("[yellow]No lambda functions found in configuration[/yellow]")
            return
        
        # Create output directory and clean existing logs
        output_dir = Path("/tmp/docr/logs")
        
        # Remove existing log files
        if output_dir.exists():
            for log_file in output_dir.glob("*.log"):
                log_file.unlink()
            console.print(f"[dim]Cleaned existing logs from {output_dir}[/dim]")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[bold]Found {len(function_names)} lambda functions:[/bold]")
        for name in function_names:
            console.print(f"  • {name}")
        
        console.print(f"\n[bold]Downloading logs to: {output_dir}[/bold]")
        console.print("[dim]Downloading logs from the last 7 days...[/dim]\n")
        
        total_events = 0
        
        # Use ThreadPoolExecutor for parallel execution
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console
        ) as progress:
            
            # Create a task for overall progress
            main_task = progress.add_task("Downloading logs...", total=len(function_names))
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all tasks
                future_to_function = {
                    executor.submit(self._download_log_group, func_name, output_dir): func_name 
                    for func_name in function_names
                }
                
                # Process completed tasks
                for future in as_completed(future_to_function):
                    function_name, events_count, file_path = future.result()
                    total_events += events_count
                    
                    # Update progress
                    progress.update(main_task, advance=1)
                    
                    # Show completion message
                    console.print(f"  ✅ {function_name}: {events_count} events → {file_path}")
        
        console.print(f"\n[bold green]✅ Download complete![/bold green]")
        console.print(f"Total log events downloaded: {total_events}")
        console.print(f"Files saved to: {output_dir}")
        
        # List all downloaded files
        log_files = list(output_dir.glob("*.log"))
        if log_files:
            console.print(f"\n[bold]Downloaded files:[/bold]")
            for log_file in sorted(log_files):
                file_size = log_file.stat().st_size
                size_str = self._format_bytes(file_size)
                console.print(f"  • {log_file.name} ({size_str})")

    def _format_bytes(self, size_bytes: int) -> str:
        """Format bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """Entry point for logs download command."""
    cli = LogsDownloadCLI()
    cli.cli()


if __name__ == "__main__":
    main()