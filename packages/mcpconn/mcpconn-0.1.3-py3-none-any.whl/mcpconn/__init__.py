"""Open MCP Protocol - Simplified MCP client package."""

from .client import MCPClient
from .llm.anthropic import AnthropicProvider
from .llm.openai import OpenAIProvider
from .utils import setup_logging

__version__ = "0.1.2"
__all__ = ["MCPClient", "AnthropicProvider", "OpenAIProvider"]

# By default, only warnings and errors are shown. Set LOGLEVEL env var or call setup_logging(level=logging.INFO) to enable more verbose logs.
setup_logging()
