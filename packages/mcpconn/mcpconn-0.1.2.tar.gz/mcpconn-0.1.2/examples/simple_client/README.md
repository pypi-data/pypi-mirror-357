# Simple MCP Client

Basic example showing how to use the `mcpconn` package as an MCP client.

## Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
# or
export OPENAI_API_KEY="your-key-here"

# Run the client
python simple_client.py /path/to/server
```

> **Note:** For Python scripts, do **not** include the 'python' prefix in the server path. The client will automatically use `python` to run `.py` files.

## Usage Examples

### STDIO Transport (Local Server)
```bash
# Connect to local stdio server
python simple_client.py /path/to/your/server

# With specific model
python simple_client.py /path/to/server --model claude-3-5-sonnet-20241022
```

### HTTP Transport (Remote Server)
```bash
# Connect to HTTP server (auto-detects transport)
python simple_client.py http://localhost:8000

# Explicitly specify transport
python simple_client.py http://localhost:8000 --transport streamable_http
python simple_client.py http://localhost:8000 --transport sse
```

### Different LLM Providers
```bash
# Use Anthropic (default for example)
python simple_client.py http://localhost:8000

## ⚠️ OpenAI Provider Limitation
**OpenAI only supports remote MCP endpoints (not local/stdio/localhost).**
See: https://platform.openai.com/docs/guides/tools-remote-mcp

# Use OpenAI (remote MCP only)
python simple_client.py https://mcp.deepwiki.com/mcp --provider openai

# Use specific OpenAI model (remote MCP only)
python simple_client.py https://mcp.deepwiki.com/mcp --provider openai --model gpt-4.1
```

## Conversation Management

For conversation ID and history management, use `simple_client_with_conversation_id.py`:

```bash
# Basic conversation with auto-generated IDs
python simple_client_with_conversation_id.py /path/to/server --auto-generate

# Start with specific conversation ID
python simple_client_with_conversation_id.py /path/to/server --conversation-id "my-conversation-123"

# Use different provider with conversation management (OpenAI remote MCP only)
python simple_client_with_conversation_id.py https://mcp.deepwiki.com/mcp --provider openai --auto-generate
```

### Conversation Commands
Once connected, you can use these commands:
- `new` - Start a new conversation
- `history` - Show conversation history
- `exit` - Quit the client

## Content Safety with Guardrails

For content filtering and safety features, use `simple_client_with_guardrails.py`:

```bash
# Enable all guardrails
python simple_client_with_guardrails.py /path/to/server --enable-all

# Enable specific guardrails
python simple_client_with_guardrails.py /path/to/server --enable-word-mask --enable-pii

# Use with different provider (OpenAI remote MCP only)
python simple_client_with_guardrails.py https://mcp.deepwiki.com/mcp --provider openai --enable-all
```

### Available Guardrails
- **Word Masking**: Masks sensitive words like "password", "secret", "confidential"
- **PII Detection**: Detects and handles personally identifiable information
- **Injection Detection**: Detects injection attempts like XSS scripts
- **Response Blocking**: Blocks responses containing harmful content

### Guardrail Commands
Once connected, you can use these commands:
- `test` - Run predefined guardrail tests
- `status` - Show current guardrail status
- `exit` - Quit the client

## Command Line Options

### Basic Client
```bash
python simple_client.py [SERVER] [OPTIONS]

Arguments:
  server                  Server path (stdio) or URL (HTTP)

Options:
  --provider {anthropic,openai}  LLM provider (default: anthropic)
  --model MODEL                   Model name
  --transport {stdio,sse,streamable_http}  Transport type
  -h, --help                      Show help
```

### Conversation Client
```bash
python simple_client_with_conversation_id.py [SERVER] [OPTIONS]

Arguments:
  server                  Server path (stdio) or URL (HTTP)

Options:
  --provider {anthropic,openai}  LLM provider (default: anthropic)
  --model MODEL                   Model name
  --transport {stdio,sse,streamable_http}  Transport type
  --conversation-id ID            Start with specific conversation ID
  --auto-generate                 Auto-generate conversation IDs for each message
  -h, --help                      Show help
```

### Guardrails Client
```bash
python simple_client_with_guardrails.py [SERVER] [OPTIONS]

Arguments:
  server                  Server path (stdio) or URL (HTTP)

Options:
  --provider {anthropic,openai}  LLM provider (default: anthropic)
  --model MODEL                   Model name
  --transport {stdio,sse,streamable_http}  Transport type
  --enable-word-mask              Enable word masking guardrail
  --enable-pii                    Enable PII detection guardrail
  --enable-injection              Enable injection detection guardrail
  --enable-response-block         Enable response blocking guardrail
  --enable-all                    Enable all guardrails
  -h, --help                      Show help
```

## How It Works

The client uses the `mclpclient.mcpconn` class:

```python
from mclpclient import mcpconn

# Create client
client = mcpconn(
    llm_provider="anthropic",  # or "openai"
    model="claude-3-5-sonnet-20241022",  # optional
    timeout=30.0,
    ssl_verify=False
)

# Connect to server
await client.connect("http://localhost:8000", transport="streamable_http")

# Send query
response = await client.query("Hello!")

# Disconnect
await client.disconnect()
```

### With Conversation Management
```python
# Create client with conversation support
client = mcpconn(
    llm_provider="anthropic",
    conversation_id="my-conversation",  # optional
    auto_generate_ids=True,  # generate unique IDs for each message
    ssl_verify=False
)

# Start new conversation
conv_id = client.start_conversation()

# Send messages (maintains context)
response1 = await client.query("Hello!")
response2 = await client.query("What did I just say?")

# Get conversation history
history = client.get_conversation_history()
```

### With Guardrails
```python
from mcpconn.guardrails import WordMaskGuardrail, PIIGuardrail

# Create client
client = mcpconn(llm_provider="anthropic", ssl_verify=False)

# Add guardrails
word_guardrail = WordMaskGuardrail(
    name="sensitive_words",
    words_to_mask=["password", "secret"],
    replacement="[REDACTED]"
)
client.add_guardrail(word_guardrail)

pii_guardrail = PIIGuardrail(name="pii_detection")
client.add_guardrail(pii_guardrail)

# Send query (will be processed through guardrails)
response = await client.query("My password is 123456 and email is john@example.com")
```

## Supported Protocols

- **stdio**: For local MCP servers
- **sse**: Server-Sent Events over HTTP
- **streamable_http**: Streamable HTTP (default for HTTP URLs)

## Supported LLMs

- **Anthropic**: Claude models (default)
- **OpenAI**: GPT models

## Environment Variables

Set your API key before running:

```bash
# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For OpenAI  
export OPENAI_API_KEY="your-openai-api-key"
``` 