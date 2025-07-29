"""Copy command module for duplicating project structures."""

from typing import Annotated

import typer

from .backend import copy_backend_command
from .frontend import copy_frontend_command

copy_app = typer.Typer(help="Copy legislative review project structure to create new applications")


@copy_app.command("backend")
def backend(
    app_name: Annotated[str, typer.Option(None, "--app-name", "-a", help="Application name (e.g., 'contracts')")] = None,
    force: Annotated[bool, typer.Option(False, "--force", "-f", help="Force overwrite if directory exists")] = False,
):
    """Copy legislative review backend to create a new backend application."""
    copy_backend_command(app_name, force)


@copy_app.command("frontend")
def frontend(
    app_name: Annotated[str, typer.Option(None, "--app-name", "-a", help="Application name (e.g., 'contracts')")] = None,
    force: Annotated[bool, typer.Option(False, "--force", "-f", help="Force overwrite if directory exists")] = False,
):
    """Copy legislative review frontend to create a new frontend application."""
    copy_frontend_command(app_name, force)