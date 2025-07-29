"""Shared utilities for copy commands."""

import os
import re
import shutil
from pathlib import Path
from typing import List, Set

from utils.console_utils import console
from utils.path_config import PathConfig


def validate_app_name(app_name: str) -> bool:
    """Validate application name format."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', app_name))


def get_exclusions() -> Set[str]:
    """Get the set of directories and patterns to exclude from copying."""
    return {
        '.venv', 'node_modules', '.git', '.aws-sam', 'dist', '__pycache__',
        '.pytest_cache', '.env.json', 'samconfig.toml', '*.log', '*.pyc',
        '.DS_Store', '*.swp', '*.swo', '.env', 'package-lock.json',
        '.tsbuildinfo', '*.egg-info', 'build'
    }


def get_backend_job_exclusions() -> Set[str]:
    """Get legislative-review-specific job directories to exclude."""
    return {
        'process', 'sync_federal', 'sync_federal_regulations', 
        'sync_maryland', 'monitor'
    }


def get_backend_test_exclusions() -> Set[str]:
    """Get legislative-review-specific test directories to exclude."""
    return {
        'sync_maryland', 'process', 'sync_federal'
    }


def should_exclude(path: Path, exclusions: Set[str], root_path: Path) -> bool:
    """Check if a path should be excluded from copying."""
    # Check exact name matches
    if path.name in exclusions:
        return True
    
    # Check pattern matches
    for pattern in exclusions:
        if '*' in pattern and path.match(pattern):
            return True
    
    # Check job-specific exclusions for backend
    if 'app/jobs' in str(path.relative_to(root_path)):
        if path.name in get_backend_job_exclusions():
            return True
    
    # Check test-specific exclusions for backend
    if 'tests/unit/jobs' in str(path.relative_to(root_path)):
        if path.name in get_backend_test_exclusions():
            return True
    
    return False


def copy_with_exclusions(src: Path, dst: Path, exclusions: Set[str]) -> None:
    """Copy directory tree while excluding specified patterns."""
    def ignore_patterns(directory, contents):
        """Function for shutil.copytree to ignore specific patterns."""
        ignored = []
        dir_path = Path(directory)
        
        for item in contents:
            item_path = dir_path / item
            if should_exclude(item_path, exclusions, src):
                ignored.append(item)
        
        return ignored
    
    shutil.copytree(src, dst, ignore=ignore_patterns)


def replace_in_file(file_path: Path, replacements: dict) -> None:
    """Replace strings in a file."""
    try:
        content = file_path.read_text()
        for old, new in replacements.items():
            content = content.replace(old, new)
        file_path.write_text(content)
    except Exception:
        # Skip binary files or files that can't be read
        pass


def process_file_replacements(root_path: Path, app_name: str) -> None:
    """Process string replacements in all text files."""
    replacements = {
        'legislative-review': app_name,
        'Legislative Review': ' '.join(word.capitalize() for word in app_name.split('-')),
        'LEGISLATIVE_REVIEW': app_name.upper().replace('-', '_'),
        'legislative_review': app_name.replace('-', '_')
    }
    
    # File extensions to process
    text_extensions = {
        '.py', '.yaml', '.yml', '.json', '.toml', '.md', '.txt', '.sh',
        '.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.env', '.example'
    }
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in text_extensions:
            replace_in_file(file_path, replacements)


def get_project_root() -> Path:
    """Get the project root directory."""
    config = PathConfig()
    return config.project_root


def prompt_for_app_name(default: str = None) -> str:
    """Prompt user for application name."""
    if default:
        prompt = f"Enter the new application name [{default}]: "
    else:
        prompt = "Enter the new application name (e.g., 'contracts'): "
    
    app_name = console.input(prompt).strip()
    if not app_name and default:
        app_name = default
    
    while not validate_app_name(app_name):
        console.print("[red]Invalid app name. Use lowercase letters, numbers, and hyphens only.[/red]")
        app_name = console.input(prompt).strip()
    
    return app_name


def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt for yes/no confirmation."""
    default_str = "Y/n" if default else "y/N"
    response = console.input(f"{message} [{default_str}] ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']