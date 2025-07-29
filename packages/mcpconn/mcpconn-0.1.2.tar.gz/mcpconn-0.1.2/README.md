# mcpconn: The Missing Connector for AI

**mcpconn** is a Python library that provides a simple and efficient way to connect your applications to AI models using the Model Context Protocol (MCP). It acts as a wrapper around the `mcp` library, offering a streamlined client interface for seamless integration with various AI providers and transport protocols.

[![PyPI version](https://badge.fury.io/py/mcpconn.svg)](https://badge.fury.io/py/mcpconn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/Documentation-blue.svg)](https://2796gaurav.github.io/mcpconn)
[![Tests](https://github.com/2796gaurav/mcpconn/workflows/Python%20Tests/badge.svg)](https://github.com/2796gaurav/mcpconn/actions)

## Table of Contents

- [mcpconn: The Missing Connector for AI](#mcpconn-the-missing-connector-for-ai)
  - [✨ Features](#-features)
  - [🚀 Getting Started](#-getting-started)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
  - [📚 Documentation](#-documentation)
  - [🗺️ Roadmap](#️-roadmap)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [⚠️ Disclaimer](#️-disclaimer)
  - [Code of Conduct](#code-of-conduct)
  - [🛡️ Security](#️-security)
  - [🌟 Showcase](#-showcase)
  - [💬 Support](#-support)

## ✨ Features

- **Simplified Client Interface**: A high-level `MCPClient` for easy interaction with MCP servers.
- **Multi-provider Support**: Out-of-the-box support for Anthropic and OpenAI models. **Note:** OpenAI only supports remote MCP endpoints (not local/stdio/localhost). See: https://platform.openai.com/docs/guides/tools-remote-mcp
- **Flexible Transports**: Connect to servers using STDIO, SSE, or Streamable HTTP. **OpenAI only supports remote MCP endpoints.**
- **Built-in Guardrails**: Protect your application with content filtering, PII masking, and injection detection.
- **Conversation Management**: Easily manage conversation history, context, and persistence.
- **Asynchronous by Design**: Built with `asyncio` for high-performance, non-blocking I/O.
- **Extensible**: Easily add new LLM providers, transports, or guardrails.

## 🚀 Getting Started

### Installation

```bash
pip install mcpconn
```

### Quick Start

Here's a simple example of how to use `mcpconn` to connect to an MCP server and interact with an AI model:

```python
import asyncio
from mcpconn import MCPClient

async def main():
    # Connect to a local server using STDIO (Anthropic only)
    client = MCPClient(llm_provider="anthropic")
    await client.connect("python examples/simple_server/weather_stdio.py")

    # ---
    # OpenAI usage example (remote MCP only):
    # client = MCPClient(llm_provider="openai")
    # await client.connect("https://mcp.deepwiki.com/mcp", transport="streamable_http")
    # ---

    # Note: OpenAI does NOT support local/stdio/localhost servers. See: https://platform.openai.com/docs/guides/tools-remote-mcp

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

## 📚 Documentation

For full details on all features and the complete API reference, please visit our **[documentation site](https://2796gaurav.github.io/mcpconn)**.

The documentation is automatically generated from the `main` branch and includes:

- A full **Getting Started** guide.
- In-depth **tutorials and examples**.
- The complete **API Reference**.

## 🗺️ Roadmap

- [ ] Add support for more LLM providers.
- [ ] Implement a more comprehensive test suite.
- [ ] Add more examples and tutorials.
- [ ] Improve documentation and type hinting.

## 🤝 Contributing 

Contributions are welcome! If you'd like to contribute to `mcpconn`, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and add tests.
4.  Ensure that the tests pass.
5.  Submit a pull request with a clear description of your changes.

## 📄 License

`mcpconn` is licensed under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This project is under active development and may undergo significant changes.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for everyone. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🛡️ Security

If you discover a security vulnerability, please report it to us by emailing [2796gaurav@gmail.com](mailto:2796gaurav@gmail.com). We will address all reports promptly.

## 🌟 Showcase

Have you built something cool with `mcpconn`? Written an article or created a video? We'd love to see it! Please open a pull request to add your project to this list.

## 💬 Support

If you have questions or need help, please open an issue in the [issue tracker](https://github.com/2796gaurav/mcpconn/issues). 