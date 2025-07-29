# Using Guardrails

`mcpconn` comes with a powerful, built-in guardrail system to help you secure your application and moderate content. Guardrails can inspect both user input before it's sent to the AI and the AI's response before it's sent to the user.

## How it Works

The `mcpconn` has a `GuardrailManager` that can hold multiple guardrails. You can add any of the built-in guardrails or even create your own.

When you call `client.query()`, the following happens:
1. The user's message is checked against all registered guardrails.
2. If a guardrail detects an issue and provides masked content (e.g., `[REDACTED]`), the message is sanitized before being sent to the AI.
3. After the AI responds, its message is also checked against all guardrails.
4. If the response is flagged, it can be masked or blocked entirely before being returned to your application.

## Example Usage

Here is a complete example of how to add and use multiple guardrails.

```python
import asyncio
from mclpclient import mcpconn
from mcpconn.guardrails import PIIGuardrail, WordMaskGuardrail, InjectionGuardrail

async def main():
    # NOTE: OpenAI only supports remote MCP endpoints (not local/stdio/localhost). See: https://platform.openai.com/docs/guides/tools-remote-mcp
    client = mcpconn(llm_provider="openai")
    
    # Add a guardrail to detect and mask PII
    client.add_guardrail(PIIGuardrail(name="pii_detector"))

    # Add a guardrail to block specific sensitive words
    client.add_guardrail(WordMaskGuardrail(
        name="word_mask",
        words_to_mask=["secret", "confidential"],
        replacement="[CENSORED]"
    ))

    # Add a guardrail to detect common injection attacks
    client.add_guardrail(InjectionGuardrail(name="injection_detector"))

    # This message contains PII and a masked word
    user_message = "Hi, my name is John Doe and my email is john.doe@example.com. This is a secret."
    print(f"Original message: {user_message}")

    # The client will automatically apply the guardrails
    # NOTE: For this example, we aren't connecting to a real server
    # We are demonstrating the guardrail check on the input message
    
    guardrail_results = await client.guardrails.check_all(user_message)
    
    final_message = user_message
    for result in guardrail_results:
        if not result.passed:
            print(f"Guardrail '{result.message}' failed.")
            if result.masked_content:
                final_message = result.masked_content

    print(f"Sanitized message: {final_message}")


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
- This is a feature: guardrails are designed to empower each client to control its own content filtering and safety, rather than enforcing a global policy on the server.

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