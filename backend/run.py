#!/usr/bin/env python3
"""
Start the Plasma Physics API server.

Usage:
    python run.py
    python run.py --port 8080
    python run.py --host 0.0.0.0 --port 8000 --reload
"""

import argparse
import uvicorn
from config import settings


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description='Start the Plasma Physics API')
    parser.add_argument(
        '--host',
        type=str,
        default=settings.api_host,
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=settings.api_port,
        help='Port to bind to (default: 8000)'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        default=settings.debug,
        help='Enable auto-reload on code changes'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['critical', 'error', 'warning', 'info', 'debug'],
        help='Log level (default: info)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print("=" * 80)
    print(f"Host: {args.host}:{args.port}")
    print(f"Docs: http://{args.host}:{args.port}/docs")
    print(f"Fuseki: {settings.fuseki_endpoint}")
    print(f"Reload: {args.reload}")
    print("=" * 80)
    print()

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
