"""Veridock CLI entry point."""

import click

from .commands import init  # noqa: F401
from .commands import service  # noqa: F401
from .commands import server  # noqa: F401


@click.group()
@click.version_option()
def cli() -> None:
    """Veridock - gRPC-powered server management tool."""
    pass


# Register command groups
service.register_cli(cli)
server.register_cli(cli)

if __name__ == "__main__":
    cli()
