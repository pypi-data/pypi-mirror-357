# mcpconn: The Missing Connector for AI – Deep Dive, Use Cases, and Tutorial

## Introduction

**mcpconn** is a Python library that makes it easy to connect your applications to AI models using the Model Context Protocol (MCP). It wraps the lower-level `mcp` library, providing a simple, unified, and secure interface for working with multiple AI providers (like OpenAI and Anthropic) and different connection methods (STDIO, SSE, HTTP).

This guide will:
- Explain the problems with traditional MCP clients
- Show how mcpconn solves them
- Provide detailed examples and use cases
- Help you get started and extend the library for your needs

---

## The Problem: Pain Points with Traditional MCP Clients

### 1. **Complexity and Boilerplate**
- **MCP** is powerful but low-level. Setting up connections, managing conversations, and handling different providers often requires a lot of repetitive code.
- Each provider (OpenAI, Anthropic, etc.) has its own quirks and APIs.

### 2. **Lack of Security Guardrails**
- Out-of-the-box, MCP clients do not filter for PII, block dangerous content, or prevent injection attacks.
- This can be risky for production apps or public-facing bots.

### 3. **Transport Fragmentation**
- Connecting via STDIO, HTTP, or SSE often requires different code and error handling.
- Switching providers or transports is not seamless.

### 4. **Conversation Management**
- Tracking conversation history, saving/loading sessions, and managing context is manual and error-prone.

### 5. **Async Support**
- Many MCP clients are not designed for modern async Python, making them less efficient for high-throughput or real-time applications.

---

## The Solution: How mcpconn Helps

- **Unified Client**: One interface for all providers and transports.
- **Built-in Guardrails**: Automatic content filtering, PII masking, and injection detection.
- **Async by Default**: Built on `asyncio` for high performance.
- **Easy Conversation Management**: Start, save, load, and clear conversations with simple methods.
- **Extensible**: Add your own providers, transports, or guardrails.

---

## Installation

```bash
pip install mcpconn
```

---

## Quick Start Example

Connect to an Anthropic-powered local server and chat with an AI model:

```python
import asyncio
from mclpclient import mcpconn

async def main():
    # Connect to a local server using STDIO
    client = mcpconn(llm_provider="anthropic")
    await client.connect("python examples/simple_server/main.py")

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

---

## Detailed Use Cases

### 1. **Unified AI Access for Chatbots**
**Problem:** You want to build a chatbot that can switch between OpenAI and Anthropic models without rewriting your code.

**Solution:**
```python
# NOTE: OpenAI only supports remote MCP endpoints (not local/stdio/localhost). See: https://platform.openai.com/docs/guides/tools-remote-mcp
client = mcpconn(llm_provider="openai", api_key="YOUR_OPENAI_KEY")
await client.connect("https://mcp.deepwiki.com/mcp", transport="http")
# ...
client = mcpconn(llm_provider="anthropic", api_key="YOUR_ANTHROPIC_KEY")
await client.connect("https://api.anthropic.com/v1", transport="http")
```

### 2. **Security for Public-Facing Apps**
**Problem:** You need to ensure your AI never leaks PII or allows prompt injection.

**Solution:**
```python
from mcpconn.guardrails import WordMaskGuardrail, PIIGuardrail, InjectionGuardrail

client = mcpconn(llm_provider="openai", api_key="...")
client.add_guardrail(WordMaskGuardrail("mask_secret", ["secret"]))
client.add_guardrail(PIIGuardrail("pii"))
client.add_guardrail(InjectionGuardrail("injection"))
```

### 3. **Saving and Loading Conversations**
**Problem:** You want to persist conversations for later analysis or to resume chats.

**Solution:**
```python
client.save_conversation("my_convo.json")
client.load_conversation("my_convo.json")
```

### 4. **Switching Transports Easily**
**Problem:** You want to test locally with STDIO, then deploy to HTTP without changing your app logic.

**Solution:**
```python
# Local testing
await client.connect("python examples/simple_server/main.py", transport="stdio")
# Production
await client.connect("https://my-ai-server.com/api", transport="http")
```

### 5. **Async, High-Performance Apps**
**Problem:** You need to handle many concurrent AI requests efficiently.

**Solution:**
```python
import asyncio
from mclpclient import mcpconn

async def ask_ai(message):
    client = mcpconn(llm_provider="anthropic")
    await client.connect("python examples/simple_server/main.py")
    await client.start_conversation()
    response = await client.query(message)
    await client.disconnect()
    return response

async def main():
    messages = ["Hi!", "Tell me a joke.", "What's the weather?"]
    results = await asyncio.gather(*(ask_ai(msg) for msg in messages))
    print(results)

asyncio.run(main())
```

---

## Extending mcpconn

### Adding a New LLM Provider
1. Subclass `BaseProvider` (see `llm/anthropic.py` or `llm/openai.py` for reference).
2. Implement methods for starting conversations, sending messages, and managing history.
3. Register your provider in `mcpconn`.

### Adding a New Guardrail
1. Subclass `BaseGuardrail`.
2. Implement the `check()` method.
3. Add your guardrail via `client.add_guardrail()`.

---

## Project Structure

- `mcpconn/client.py`: Main client logic.
- `mcpconn/llm/`: LLM provider integrations.
- `mcpconn/guardrails.py`: Security/content guardrails.
- `mcpconn/transport.py`: Transport management.
- `examples/`: Example servers and usage scripts.
- `docs/`: Documentation source.

---

## Documentation & Support

- **Full Docs**: [https://2796gaurav.github.io/mcpconn](https://2796gaurav.github.io/mcpconn)
- **GitHub**: [https://github.com/2796gaurav/mcpconn](https://github.com/2796gaurav/mcpconn)
- **Issues/Support**: Open an issue on GitHub or email 2796gaurav@gmail.com

---

## Contributing

1. Fork the repo.
2. Create a feature branch.
3. Add your changes and tests.
4. Submit a pull request!

---

## Final Thoughts

`mcpconn` is a powerful, extensible bridge between your Python apps and the world of AI models. Whether you're building chatbots, automation tools, or research prototypes, it gives you a secure, unified, and future-proof foundation.

---

**If you found this helpful, follow me for more deep dives and tutorials on AI infrastructure!** 