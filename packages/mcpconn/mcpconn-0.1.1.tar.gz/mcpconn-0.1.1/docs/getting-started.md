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
    # Connect to a local server using STDIO
    client = MCPClient(llm_provider="anthropic")
    await client.connect("python examples/simple_server/weather_stdio.py")

    # Start a conversation
    conversation_id = client.start_conversation()
    print(f"Started conversation: {conversation_id}")

    # Send a message and get a response
    response = await client.query("Hello, world!")
    print(f"AI: {response}")

    # Disconnect from the server
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

This example demonstrates the basic workflow:

1.  **Import `mcpconn`**: The main entry point for interacting with the library.
2.  **Instantiate the client**: Create an instance of `mcpconn`, specifying the desired LLM provider.
3.  **Connect to a server**: Use `await client.connect()` to establish a connection.
4.  **Interact with the AI**: Use methods like `start_conversation()` and `query()` to have a conversation.
5.  **Disconnect**: Cleanly close the connection with `await client.disconnect()`.

For more detailed examples, please refer to the `examples` directory in the [project repository](https://github.com/2796gaurav/mcpconn). 