from __future__ import annotations

import argparse
import sys

from reachkit.integrations.stdio_server import run_stdio_server


def handle_serve_stdio(args: argparse.Namespace) -> int:
    run_stdio_server(sys.stdin, sys.stdout)
    return 0


def add_serve_parser(subparsers) -> None:
    serve_parser = subparsers.add_parser("serve", help="Run an integration server.")
    serve_subparsers = serve_parser.add_subparsers(dest="serve_mode", required=True)
    stdio_parser = serve_subparsers.add_parser("stdio", help="Run newline-delimited JSON over stdio.")
    stdio_parser.set_defaults(handler=handle_serve_stdio)
