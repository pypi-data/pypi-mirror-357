"""Initialize a new Veridock project."""
import click
import os
from pathlib import Path
from typing import Dict, Any

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

# Template for .env file
ENV_TEMPLATE = """# Server Configuration
HTTP_PORT=8088

# gRPC Server
GRPC_HOST=localhost
GRPC_PORT=50051

# HTTP Gateway
HTTP_GATEWAY_HOST=0.0.0.0
HTTP_GATEWAY_PORT=8082
"""

# Template for Makefile
MAKEFILE_TEMPLATE = """# Makefile - Project automation with Poetry
.PHONY: help run dev stop clean install update test

# Load environment variables from .env file
include .env
export $(shell sed 's/=.*//' .env)

# Project variables
PROJECT_NAME = veridock
POETRY = poetry

.DEFAULT_GOAL := help

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install all dependencies
	@echo "Installing dependencies..."
	$(POETRY) install --no-root

run:  ## Start all services
	@echo "Starting services..."
	$(POETRY) run python -m veridock.grpc_server &
	$(POETRY) run python -m veridock.http_gateway &
	caddy run --config Caddyfile

dev:  ## Start development environment
	@echo "Starting development environment..."
	$(POETRY) run python -m veridock.grpc_server --dev &
	$(POETRY) run python -m veridock.http_gateway --dev

stop:  ## Stop all services
	@pkill -f "python -m veridock" || true

clean:  ## Clean up temporary files
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name "*.py,cover" -delete

update:  ## Update dependencies
	@echo "Updating dependencies..."
	$(POETRY) update

test:  ## Run tests
	$(POETRY) run pytest -v
"""

# Template for Caddyfile
CADDYFILE_TEMPLATE = """# Caddyfile for Veridock
{
    # Enable the admin API (optional)
    admin off
}

# Main server
:{$HTTP_PORT} {
    # Enable static file server for the frontend
    root * static
    file_server
    
    # API reverse proxy
    handle_path /makefile/* {
        reverse_proxy localhost:{$HTTP_GATEWAY_PORT}
    }
    
    # Fallback for SPA routing
    handle {
        try_files {path} /index.html
    }
}
"""

def ensure_directory(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def write_file_if_not_exists(path: Path, content: str) -> None:
    """Write content to file if it doesn't exist."""
    if not path.exists():
        with open(path, 'w') as f:
            f.write(content)
        click.echo(f"Created {path}")
    else:
        click.echo(f"{path} already exists, skipping")

@click.command()
def init() -> None:
    """Initialize a new Veridock project."""
    click.echo("🚀 Initializing Veridock project...")
    
    # Create necessary directories
    directories = ["static", "scripts", "logs"]
    for dir_name in directories:
        ensure_directory(Path(dir_name))
    
    # Create configuration files
    config_files = {
        ".env": ENV_TEMPLATE,
        "Makefile": MAKEFILE_TEMPLATE,
        "Caddyfile": CADDYFILE_TEMPLATE,
    }
    
    for filename, content in config_files.items():
        write_file_if_not_exists(Path(filename), content)
    
    click.echo("✅ Veridock project initialized successfully!")
    click.echo("\nNext steps:")
    click.echo("1. Review the generated configuration files")
    click.echo("2. Run 'make install' to install dependencies")
    click.echo("3. Run 'make run' to start the server")
    click.echo("\nFor development, use 'make dev' to start in development mode")
