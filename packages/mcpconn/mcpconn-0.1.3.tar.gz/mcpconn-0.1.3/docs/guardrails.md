# Using Guardrails

`mcpconn` comes with a powerful, built-in guardrail system to help you secure your application and moderate content. Guardrails can inspect tool results automatically, and you can also manually apply them to user input or LLM output if desired.

## How it Works

The `mcpconn` client has a `GuardrailManager` that can hold multiple guardrails. You can add any of the built-in guardrails or even create your own.

When you call `client.query()`, the following happens:
1. The user's message is sent directly to the LLM (**no guardrails are applied automatically to user input**).
2. If the LLM calls a tool, the tool's result is checked against all registered guardrails before being returned to the user (**guardrails are automatically applied to tool results**).
3. The LLM's direct output (text) is **not** automatically checked by guardrails. If you want to filter or mask LLM output, you must do so manually after receiving the response.

## Basic Example: Manually Applying Guardrails to LLM Output

```python
import asyncio
from mcpconn import MCPClient
from mcpconn.guardrails import PIIGuardrail, WordMaskGuardrail

async def main():
    client = MCPClient(llm_provider="anthropic")
    client.add_guardrail(PIIGuardrail(name="pii_detector"))
    client.add_guardrail(WordMaskGuardrail(name="word_mask", words_to_mask=["secret"], replacement="[CENSORED]"))

    await client.connect("examples/simple_server/weather_stdio.py", transport="stdio") # add your stdio server

    user_input = "what is the weather alert in texas."
    # Send to LLM (no guardrails applied automatically)
    response = await client.query(user_input)

    # If you want to apply guardrails to the LLM output, do it manually:
    guardrail_results = await client.guardrails.check_all(response)
    for result in guardrail_results:
        if not result.passed and result.masked_content:
            response = result.masked_content

    print("Sanitized response:", response)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Guardrails

### `PIIGuardrail`
Detects and masks common Personally Identifiable Information (PII).
- **Finds**: Email addresses, phone numbers, SSNs, and credit card numbers.
- **Action**: Replaces found PII with `[REDACTED]`.

### `WordMaskGuardrail`
Masks a custom list of words or phrases.
- **Configuration**:
  - `words_to_mask`: A list of strings to find.
  - `replacement`: The string to replace them with.
- **Action**: Replaces found words with the replacement string.

### `ResponseBlockGuardrail`
Blocks a response entirely if it contains certain words and replaces it with a standardized message. This is most useful for moderating AI output.
- **Configuration**:
  - `blocked_words`: A list of strings that will trigger the block.
  - `standardized_response`: The message to return instead.
- **Action**: If a blocked word is found, the original response is discarded and the standardized response is returned.

### `InjectionGuardrail`
Detects common patterns associated with injection attacks.
- **Finds**: Cross-Site Scripting (XSS), SQL injection, shell injection, and path traversal patterns.
- **Action**: Fails the check if a potential attack is detected. Does not mask content by default, as the entire input should likely be rejected.

## Where Are Guardrails Enforced?

Guardrails in `mcpconn` are enforced **on the client side**. This means:
- You can add, configure, and manage guardrails in your client code.
- The server (including remote MCP servers like OpenAI or Anthropic endpoints) does **not** enforce guardrails or content filtering by default.
- Guardrails are **automatically applied only to tool results**. LLM output and user input are not filtered unless you do so manually.

### OpenAI and Remote MCP Servers

When using a remote MCP server (such as OpenAI via `https://mcp.deepwiki.com/mcp`), guardrails in your client will only filter tool results (if any). **They do not filter or block the LLM's direct output.**

**Warning:** OpenAI provider only supports remote MCP endpoints. Local/STDIO/localhost servers are not supported. See: https://platform.openai.com/docs/guides/tools-remote-mcp

If you want to apply guardrails to the LLM's output, you can manually check the response after calling `client.query()`:

```python
response = await client.query(user_input)
# Manually check LLM output with guardrails
results = await client.guardrails.check_all(response)
for result in results:
    if not result.passed and result.masked_content:
        response = result.masked_content
print(response)
```

This approach allows you to enforce guardrails on any LLM output, regardless of provider or transport.

_This design allows each client to choose its own safety and filtering policies, rather than relying on the server to enforce them._

---

## Advanced Example: Guardrails with Tool Results and Chat Loop

See `examples/simple_client/simple_client_with_guardrails.py` in the repository for a more advanced example that demonstrates enabling and testing all guardrail types, including a chat loop and tool result filtering. 