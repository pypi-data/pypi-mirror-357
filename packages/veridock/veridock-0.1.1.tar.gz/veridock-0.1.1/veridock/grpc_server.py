#!/usr/bin/env python3
"""gRPC server for the Makefile Command Runner."""

import logging
import os
import signal
import subprocess
import sys
from concurrent import futures

import grpc
from veridock import service_pb2
from veridock import service_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MakefileService(service_pb2_grpc.MakefileServiceServicer):
    """Implementation of the MakefileService."""

    def RunCommand(self, request, context):
        """Run a Makefile command and return the result."""
        try:
            # Build the command to run
            cmd = ["make"]
            if request.command:
                cmd.append(request.command)
            if request.args:
                cmd.extend(request.args)

            logger.info(f"Running command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=os.getcwd()
            )

            # Log the result
            logger.debug(f"Command completed with return code: {result.returncode}")
            if result.stdout:
                logger.debug(f"stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"stderr: {result.stderr}")

            # Return the response
            return service_pb2.CommandResponse(
                output=result.stdout, error=result.stderr, return_code=result.returncode
            )

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return service_pb2.CommandResponse(
                output="", error=error_msg, return_code=-1
            )


def serve(host='0.0.0.0', port=50051):
    """Start the gRPC server."""
    # Load environment variables
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Get configuration from environment variables
    server_host = os.getenv('GRPC_HOST', host)
    server_port = int(os.getenv('GRPC_PORT', str(port)))
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MakefileServiceServicer_to_server(MakefileService(), server)

    # Listen on the given port
    server_address = f"{server_host}:{server_port}"
    server.add_insecure_port(server_address)

    # Start the server
    server.start()
    logger.info(f"gRPC server started on {server_address}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {os.getenv('DEBUG', 'False')}")

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down gRPC server...")
        server.stop(0)
        logger.info("gRPC server stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep the server running
    server.wait_for_termination()


if __name__ == "__main__":
    import argparse

    # Load environment variables first to set defaults
    from dotenv import load_dotenv
    from pathlib import Path
    
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Set default port from environment or use default
    default_port = int(os.getenv('GRPC_PORT', '50051'))
    default_host = os.getenv('GRPC_HOST', '0.0.0.0')

    parser = argparse.ArgumentParser(
        description="Run the gRPC server for Makefile commands"
    )
    parser.add_argument(
        "--host", type=str, default=default_host, 
        help=f"The host to bind to (default: {default_host})"
    )
    parser.add_argument(
        "--port", type=int, default=default_port, 
        help=f"The port to listen on (default: {default_port})"
    )
    args = parser.parse_args()

    serve(host=args.host, port=args.port)
