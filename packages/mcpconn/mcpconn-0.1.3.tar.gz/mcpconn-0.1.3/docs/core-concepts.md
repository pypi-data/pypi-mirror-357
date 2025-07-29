# Core Concepts

This page explains the key concepts behind `mcpconn` and the protocol it is built upon.

## The Model Context Protocol (MCP)

At its heart, `mcpconn` is designed to simplify interactions with servers that use the **Model Context Protocol (MCP)**. MCP is a standardized protocol that creates a common ground for different AI models (like those from Anthropic or OpenAI) and the applications that use them.

Think of it as a universal adapter for AI. Instead of writing custom code to handle the specific API of each AI provider, you can connect to an MCP-compliant server that handles those details for you.

The key benefits of this approach are:

*   **Provider Agnostic**: You can switch between different AI providers with minimal code changes, often just by changing a parameter in the client.
*   **Standardized Tool Use**: MCP defines a standard way for AI models to request the use of external tools (like a weather API, a calculator, or a database). Your application can expose these tools to the AI in a consistent way.
*   **Simplified Communication**: The protocol handles the complexities of streaming responses, managing conversation history, and handling different data formats.

## How `mcpconn` Helps

While MCP provides the standard, `mcpconn` provides the convenience. It acts as a high-level client library that abstracts away the low-level details of the protocol.

Instead of manually constructing MCP messages, you can use the intuitive methods on the `mcpconn`:

*   `client.connect()`: Handles establishing the connection over different transports (like STDIO or HTTP).
*   `client.query()`: Sends a message to the AI and automatically handles the back-and-forth of tool usage.
*   `client.start_conversation()`: Manages session IDs and history.

By using `mcpconn`, you can focus on building your application's logic instead of worrying about the intricacies of AI integration. 