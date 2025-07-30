"""Server management commands."""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click
from dotenv import load_dotenv

from ..utils import ProjectContext, command_success, command_error

class ServerManager:
    """Manage Veridock server processes."""
    
    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize with project directory."""
        self.ctx = ProjectContext(project_dir)
        self.processes: List[subprocess.Popen] = []
        
        # Load environment variables
        env_path = self.ctx.project_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    
    def start_grpc_server(self, dev_mode: bool = False) -> None:
        """Start the gRPC server."""
        cmd = [sys.executable, "-m", "veridock.grpc_server"]
        if dev_mode:
            cmd.append("--dev")
        self._start_process(cmd, "gRPC Server")
    
    def start_http_gateway(self, dev_mode: bool = False) -> None:
        """Start the HTTP gateway."""
        cmd = [sys.executable, "-m", "veridock.http_gateway"]
        if dev_mode:
            cmd.append("--dev")
        self._start_process(cmd, "HTTP Gateway")
    
    def start_caddy(self) -> None:
        """Start the Caddy web server."""
        cmd = ["caddy", "run", "--config", "Caddyfile"]
        self._start_process(cmd, "Caddy")
    
    def _start_process(self, cmd: List[str], name: str) -> None:
        """Start a subprocess and track it."""
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.ctx.project_dir),
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes.append(process)
            command_success(f"Started {name} (PID: {process.pid})")
            
            # Start a thread to log output
            import threading
            def log_output():
                if process.stdout:
                    for line in iter(process.stdout.readline, ''):
                        click.echo(f"[{name}] {line.strip()}")
            
            thread = threading.Thread(target=log_output, daemon=True)
            thread.start()
            
        except Exception as e:
            command_error(f"Failed to start {name}: {e}")
    
    def stop_all(self) -> None:
        """Stop all managed processes."""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                command_success(f"Stopped process {process.pid}")
            except Exception as e:
                command_error(f"Failed to stop process {process.pid}: {e}")
        self.processes = []

@click.group()
def server() -> None:
    """Manage Veridock server components."""
    pass

@server.command("start")
@click.option("--dev", is_flag=True, help="Run in development mode")
@click.option("--no-caddy", is_flag=True, help="Don't start the Caddy server")
def start_server(dev: bool, no_caddy: bool) -> None:
    """Start all server components."""
    manager = ServerManager()
    
    try:
        click.echo("🚀 Starting Veridock server...")
        manager.start_grpc_server(dev)
        manager.start_http_gateway(dev)
        
        if not no_caddy:
            manager.start_caddy()
        
        # Keep running until interrupted
        click.echo("\n🛑 Press Ctrl+C to stop the server")
        while True:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping server...")
                manager.stop_all()
                break
    
    except Exception as e:
        command_error(f"Server error: {e}")
        manager.stop_all()
        sys.exit(1)

@server.command("stop")
def stop_server() -> None:
    """Stop all running server components."""
    # This is a placeholder - in a real implementation, you would track PIDs
    click.echo("Stopping all server components...")
    # TODO: Implement proper process management
    click.echo("Note: This command needs proper process tracking to work correctly")

def register_cli(cli_group):
    """Register server commands with the main CLI group."""
    cli_group.add_command(server)
