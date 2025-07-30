"""Veridock CLI entry point."""
import click
from pathlib import Path
from typing import Optional

@click.group()
@click.version_option()
def cli():
    """Veridock - gRPC-powered server management tool."""
    pass

# Import commands to register them
from .commands import init  # noqa: F401

if __name__ == "__main__":
    cli()
