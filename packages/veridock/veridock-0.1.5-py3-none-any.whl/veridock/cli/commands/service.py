"""Service management commands."""
import click
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils import ProjectContext, command_success, command_error

SERVICE_TEMPLATES = {
    "ftp": {
        "description": "FTP server service",
        "dependencies": ["pyftpdlib"],
        "config": {
            "FTP_PORT": 2121,
            "FTP_USER": "user",
            "FTP_PASSWORD": "password",
            "FTP_DIRECTORY": "./ftp_share"
        }
    },
    "webdav": {
        "description": "WebDAV server service",
        "dependencies": ["wsgidav", "cheroot"],
        "config": {
            "WEBDAV_PORT": 8000,
            "WEBDAV_USER": "user",
            "WEBDAV_PASSWORD": "password",
            "WEBDAV_DIRECTORY": "./webdav_share"
        }
    },
    "ssh": {
        "description": "SSH server service",
        "dependencies": ["paramiko"],
        "config": {
            "SSH_PORT": 2222,
            "SSH_USERNAME": "user",
            "SSH_PASSWORD": "password",
            "SSH_HOST_KEYS_DIR": "./ssh_keys"
        }
    }
}

@click.group()
def service() -> None:
    """Manage Veridock services."""
    pass

@service.command("list")
def list_services() -> None:
    """List available services."""
    click.echo("Available services:")
    for name, info in SERVICE_TEMPLATES.items():
        click.echo(f"  {name}: {info['description']}")

@service.command("add")
@click.argument("service_name")
@click.option("--force", is_flag=True, help="Overwrite existing files")
def add_service(service_name: str, force: bool) -> None:
    """Add a new service to the project."""
    ctx = ProjectContext()
    
    if service_name not in SERVICE_TEMPLATES:
        command_error(f"Unknown service: {service_name}")
        click.echo("Available services: " + ", ".join(SERVICE_TEMPLATES.keys()))
        return
    
    service_info = SERVICE_TEMPLATES[service_name]
    
    # Add service dependencies to pyproject.toml
    # TODO: Implement dependency management
    
    # Create service directory
    service_dir = ctx.project_dir / "services" / service_name
    ctx.ensure_directory(service_dir)
    
    # Add service configuration to .env
    env_path = ctx.project_dir / ".env"
    if env_path.exists():
        with open(env_path, "a") as f:
            f.write(f"\n# {service_name.upper()} Configuration\n")
            for key, value in service_info["config"].items():
                f.write(f"{key}={value}\n")
    
    # Create service implementation
    service_file = service_dir / f"{service_name}_service.py"
    if not service_file.exists() or force:
        service_class = service_name.capitalize()
        description = service_info['description']
        
        template = f'''# {service_class} Service Implementation
from pathlib import Path
import os
from typing import Dict, Any

class {service_class}Service:
    """{description} implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup()
    
    def _setup(self) -> None:
        """Set up the service."""
        # TODO: Implement service setup
        pass
    
    def start(self) -> None:
        """Start the service."""
        # TODO: Implement service start
        print(f"Starting {service_name} service...")
    
    def stop(self) -> None:
        """Stop the service."""
        # TODO: Implement service stop
        print(f"Stopping {service_name} service...")
'''
        service_file.write_text(template)
        command_success(f"Created service implementation at {service_file}")
    
    command_success(f"Added {service_name} service to the project")

# Register the service command group
def register_cli(cli_group):
    """Register service commands with the main CLI group."""
    cli_group.add_command(service)
