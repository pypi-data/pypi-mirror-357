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
    response = await client.query("Hello, world!")
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