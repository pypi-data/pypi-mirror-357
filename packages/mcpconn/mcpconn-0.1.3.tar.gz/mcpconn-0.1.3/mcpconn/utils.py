"""Utility functions for MCP client."""

import os
import asyncio
from pathlib import Path
from urllib.parse import urlparse


def load_env_vars(env_file=None):
    """Load environment variables from file."""
    if env_file and os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value


def validate_server_path(server_path):
    """Validate server path exists."""
    return os.path.exists(server_path) or os.path.exists(server_path.split()[0])


def get_server_command(server_path):
    """Parse server command and arguments."""
    parts = server_path.split()
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    # Handle Python scripts
    if command.endswith(".py"):
        return "python", [command] + args

    return command, args


def is_valid_url(url):
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


async def run_with_timeout(coro, timeout):
    """Run coroutine with timeout."""
    return await asyncio.wait_for(coro, timeout=timeout)


def format_tool_for_llm(tool):
    """Format MCP tool for LLM consumption."""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


def setup_logging(level: int = None, json_format: bool = True):
    """
    Set up structured logging for the mcpconn package.
    Args:
        level (int): Logging level (default: logging.WARNING). Set LOGLEVEL env var or call setup_logging(level=logging.INFO) to enable more verbose logs.
        json_format (bool): Use JSON formatter if True, else key-value pairs.
    """
    import logging
    import sys
    level = level or int(os.environ.get("LOGLEVEL", logging.WARNING))
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter()
        except ImportError:
            formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(extra)s"
            )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(extra)s"
        )
    handler.setFormatter(formatter)
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers[0] = handler

    # Suppress noisy logs from common HTTP/AI libraries
    for noisy_logger in [
        "httpx", "openai", "anthropic", "urllib3", "requests"
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
