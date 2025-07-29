# Getting Started

This guide will help you get up and running with `mcpconn`.

## Installation

To install `mcpconn`, run the following command in your terminal:

```bash
pip install mcpconn
```

This will install the core library and its dependencies.

## Quick Start

Here's a simple example of how to use `mcpconn` to connect to an MCP server and interact with an AI model:

```python
import asyncio
from mcpconn import MCPClient

async def main():
    # Set your OpenAI API key in the environment before running
    # export OPENAI_API_KEY="your-key-here"

    # Connect to a remote MCP server using OpenAI and streamable_http transport
    # NOTE: OpenAI only supports remote MCP endpoints (not local/stdio/localhost). See: https://platform.openai.com/docs/guides/tools-remote-mcp
    client = MCPClient(llm_provider="openai")
    await client.connect("https://mcp.deepwiki.com/mcp", transport="streamable_http")

    # Send a message and get a response
    response = await client.query("give me list of tools provided")
    print(f"AI: {response}")

    # Disconnect from the server
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

_Note: Set your OpenAI API key in the environment before running the example (e.g., `export OPENAI_API_KEY="your-key-here"`)._

**Warning:** OpenAI provider only supports remote MCP endpoints. Local/STDIO/localhost servers are not supported. See: https://platform.openai.com/docs/guides/tools-remote-mcp

_This is the easiest way to get started: just connect to a remote MCP server using OpenAI and streamable_http transport._

_Note: For Python scripts, do **not** include the 'python' prefix in the connection string; it is added automatically by mcpconn._

For more detailed examples, please refer to the `examples` directory in the [project repository](https://github.com/2796gaurav/mcpconn). 

---

## Example Servers for Local Testing

The `examples/simple_server/` directory contains sample MCP server implementations (stdio, HTTP, SSE) for local testing and development. These are not production servers, but are useful for experimenting with the client examples.

- `weather_stdio.py`: Stdio-based weather server
- `streamable_http_server.py`: HTTP server for weather tools
- `sse_mcp_example_server.py`: SSE server for weather tools

To run a server for local testing:

```bash
python examples/simple_server/weather_stdio.py
# or
python examples/simple_server/streamable_http_server.py --port 8123
# or
python examples/simple_server/sse_mcp_example_server.py --port 8080
```

Then connect with a client, e.g.:

```bash
python examples/simple_client/simple_client.py /path/to/server
```

See the `examples/simple_client/README.md` for more details on client usage and options. 

---

## Client Usage Examples

### Switching Models and Providers

You can easily switch between Anthropic and OpenAI providers, and specify models:

```bash
# Use Anthropic (default)
python examples/simple_client/simple_client.py http://localhost:8000

# Use OpenAI (remote MCP only)
python examples/simple_client/simple_client.py https://mcp.deepwiki.com/mcp --provider openai

# Use a specific model
python examples/simple_client/simple_client.py http://localhost:8000 --model claude-3-5-sonnet-20241022
```

_Note: OpenAI only supports remote MCP endpoints (not local/stdio/localhost)._

### Using Conversation IDs and History

For advanced conversation management, use the conversation client:

```bash
# Auto-generate conversation IDs
python examples/simple_client/simple_client_with_conversation_id.py /path/to/server --auto-generate

# Start with a specific conversation ID
python examples/simple_client/simple_client_with_conversation_id.py /path/to/server --conversation-id "my-convo-123"
```

**In the client, use:**
- `new` — Start a new conversation
- `history` — Show conversation history
- `exit` — Quit the client

### Switching Transports

Choose the transport that matches your server:

```bash
# Use stdio (local server)
python examples/simple_client/simple_client.py /path/to/server --transport stdio

# Use SSE
python examples/simple_client/simple_client.py http://localhost:8000 --transport sse

# Use streamable HTTP
python examples/simple_client/simple_client.py http://localhost:8000 --transport streamable_http
```

### Guardrails (Content Safety)

For content filtering and safety, use the guardrails client:

```bash
# Enable all guardrails
python examples/simple_client/simple_client_with_guardrails.py /path/to/server --enable-all

# Enable specific guardrails
python examples/simple_client/simple_client_with_guardrails.py /path/to/server --enable-word-mask --enable-pii
```

See the [Using Guardrails](guardrails.md) page for more details and advanced usage.

---

For more detailed examples and advanced usage, see the `examples/simple_client/README.md` in the project repository. 