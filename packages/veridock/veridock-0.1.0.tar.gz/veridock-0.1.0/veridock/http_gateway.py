#!/usr/bin/env python3
"""HTTP Gateway for gRPC server."""

import json
import logging
import os
import sys
from concurrent import futures
from pathlib import Path

import grpc
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

from veridock import service_pb2, service_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('http_gateway.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Configuration from environment variables
GRPC_SERVER_HOST = os.getenv('GRPC_HOST', 'localhost')
GRPC_SERVER_PORT = int(os.getenv('GRPC_PORT', '50051'))
HTTP_GATEWAY_HOST = os.getenv('HTTP_GATEWAY_HOST', '0.0.0.0')
HTTP_GATEWAY_PORT = int(os.getenv('HTTP_GATEWAY_PORT', '8082'))

# Log configuration
logger.info("=== Starting HTTP Gateway ===")
logger.info(f"gRPC server configured at: {GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}")
logger.info(f"HTTP gateway will listen on: {HTTP_GATEWAY_HOST}:{HTTP_GATEWAY_PORT}")

# Debug output for environment variables
logger.debug("Environment variables:")
for key, value in dict(os.environ).items():
    if key.startswith(('GRPC_', 'HTTP_')):
        logger.debug(f"  {key}={value}")

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Keep JSON output in the order we define it

# gRPC channel to communicate with the gRPC server
channel = grpc.insecure_channel(f'{GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}')
stub = service_pb2_grpc.MakefileServiceStub(channel)

print(f"gRPC server configured at: {GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}")
print(f"HTTP gateway will listen on port: {HTTP_GATEWAY_PORT}")


@app.route('/makefile/run_command', methods=['POST', 'OPTIONS'])
@app.route('/run_command', methods=['POST'])  # Add this line to handle both paths
def run_command():
    """Handle HTTP POST request to run a Makefile command."""
    # Log the incoming request
    logger.info(f"Incoming request: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Data: {request.data}")
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        # Log incoming request
        print(f"\n=== Received request ===")
        print(f"Headers: {dict(request.headers)}")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        
        # Parse JSON request
        data = request.get_json()
        print(f"Request data: {data}")
        
        command = data.get('command', '')
        args = data.get('args', [])
        print(f"Command: {command}, Args: {args}")

        # Call gRPC service
        print("Calling gRPC service...")
        response = stub.RunCommand(
            service_pb2.CommandRequest(command=command, args=args)
        )
        print("Received response from gRPC service")

        # Prepare JSON response
        response_data = {
            'output': response.output,
            'error': response.error,
            'return_code': response.return_code
        }
        print(f"Sending response: {response_data}")
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON: {str(e)}"
        print(f"Error: {error_msg}")
        response = jsonify({
            'error': error_msg,
            'output': '',
            'return_code': -1
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 400
        
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        print(f"Error: {error_msg}")
        response = jsonify({
            'error': error_msg,
            'output': '',
            'return_code': -1
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


def serve_http(host=HTTP_GATEWAY_HOST, port=HTTP_GATEWAY_PORT, debug=False):
    """Start the HTTP server."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
        app.debug = True
    
    # Log all routes
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.endpoint}: {rule.rule} {list(rule.methods)}")
    
    # Use a simple WSGI server for development
    from werkzeug.serving import make_server
    server = make_server(host, port, app)
    logger.info(f"HTTP gateway running on http://{host}:{port}")
    logger.info("Ready to accept requests...")
    server.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HTTP Gateway for gRPC server')
    parser.add_argument('--port', type=int, default=HTTP_GATEWAY_PORT, help='Port to run the HTTP gateway on')
    parser.add_argument('--host', type=str, default=HTTP_GATEWAY_HOST, help='Host to bind the HTTP gateway to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
    args = parser.parse_args()
    
    logger.info(f"Starting HTTP gateway on {args.host}:{args.port}")
    if args.debug:
        logger.info("Debug mode enabled")
    
    serve_http(host=args.host, port=args.port, debug=args.debug)
