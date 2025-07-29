"""Frontend copy command implementation."""

import shutil
import sys
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.console_utils import console
from .utils import (
    confirm_action,
    copy_with_exclusions,
    get_exclusions,
    get_project_root,
    process_file_replacements,
    prompt_for_app_name,
)


def copy_frontend_command(app_name: str = None, force: bool = False) -> None:
    """Copy legislative review frontend to create a new frontend application."""
    # Get project root
    project_root = get_project_root()
    
    # Prompt for app name if not provided
    if not app_name:
        app_name = prompt_for_app_name()
    
    # Define paths
    source_dir = project_root / "aisolutions-docreview-serverless" / "legislative-review-frontend"
    target_parent_dir = project_root / f"aisolutions-docreview{app_name}-serverless"
    target_dir = target_parent_dir / f"{app_name}-frontend"
    
    # Check if source exists
    if not source_dir.exists():
        console.print(f"[red]Source directory not found: {source_dir}[/red]")
        sys.exit(1)
    
    # Show what will be created
    console.print(f"\nThis will create: [cyan]{target_dir.relative_to(project_root)}[/cyan]")
    
    # Check if target exists
    if target_dir.exists():
        console.print(f"\n[yellow]⚠️  Directory already exists:[/yellow] {target_dir}")
        
        if not force:
            if confirm_action("Delete existing directory and create fresh copy?"):
                console.print("[yellow]Removing existing directory...[/yellow]")
                shutil.rmtree(target_dir)
            else:
                console.print("[red]Copy cancelled.[/red]")
                sys.exit(0)
        else:
            console.print("[yellow]Force flag set. Removing existing directory...[/yellow]")
            shutil.rmtree(target_dir)
    
    # Final confirmation
    if not confirm_action("Proceed with copy?", default=True):
        console.print("[red]Copy cancelled.[/red]")
        sys.exit(0)
    
    # Create parent directory if needed
    target_parent_dir.mkdir(exist_ok=True)
    
    # Copy with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Copy files
        task = progress.add_task("Copying frontend files...", total=None)
        try:
            copy_with_exclusions(source_dir, target_dir, get_exclusions())
            progress.update(task, description="[green]Files copied successfully[/green]")
        except Exception as e:
            progress.update(task, description=f"[red]Copy failed: {e}[/red]")
            # Cleanup on failure
            if target_dir.exists():
                shutil.rmtree(target_dir)
            sys.exit(1)
        
        # Process replacements
        task = progress.add_task("Processing file replacements...", total=None)
        try:
            process_file_replacements(target_dir, app_name)
            progress.update(task, description="[green]Replacements completed[/green]")
        except Exception as e:
            progress.update(task, description=f"[red]Replacements failed: {e}[/red]")
            console.print("[yellow]Warning: Some files may not have been updated[/yellow]")
    
    # Display success and next steps
    console.print(f"\n[green]✅ Successfully created {app_name} frontend at:[/green]")
    console.print(f"   [cyan]{target_dir}[/cyan]\n")
    
    console.print("[bold]Next steps:[/bold]")
    console.print("1. cd " + str(target_dir))
    console.print("2. Update configuration files for your specific use case")
    console.print("3. Run: npm install")
    console.print("4. Run: docr setup (if not already done)")
    console.print("5. Configure your AWS resources with: sam deploy --guided")
    console.print(f"6. Deploy frontend with: docr deploy frontend --app {app_name}")
    console.print("\nFor more information, see the README.md in your new project.")