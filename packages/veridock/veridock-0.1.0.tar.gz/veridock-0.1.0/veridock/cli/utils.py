"""Utility functions for the Veridock CLI."""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

import click

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

class ProjectContext:
    """Project context and configuration."""
    
    def __init__(self, project_dir: Path = None):
        """Initialize with project directory."""
        self.project_dir = project_dir or Path.cwd()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration."""
        # TODO: Load from pyproject.toml or config file
        return {}
    
    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)
    
    def write_template(
        self,
        template_name: str,
        output_path: Path,
        context: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> bool:
        """Write a template file."""
        if output_path.exists() and not force:
            click.echo(f"{output_path} already exists, skipping")
            return False
            
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            click.echo(f"Template {template_name} not found", err=True)
            return False
            
        content = template_path.read_text()
        if context:
            content = content.format(**context)
            
        output_path.write_text(content)
        click.echo(f"Created {output_path}")
        return True

def get_project_context() -> ProjectContext:
    """Get or create project context."""
    # TODO: Detect if we're in a project directory
    return ProjectContext()

def command_success(message: str) -> None:
    """Display success message."""
    click.echo(click.style(f"✓ {message}", fg="green"))

def command_error(message: str) -> None:
    """Display error message."""
    click.echo(click.style(f"✗ {message}", fg="red"), err=True)
