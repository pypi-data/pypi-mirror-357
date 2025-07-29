# Contributing to mcpconn

First off, thank you for considering contributing to `mcpconn`! It's people like you that make `mcpconn` such a great tool.

We welcome contributions of all kinds, from bug reports and feature requests to code contributions and documentation improvements.

## Where to start

- **Bug reports:** If you find a bug, please open an issue in the [issue tracker](https://github.com/2796gaurav/mcpconn/issues). Please include as much information as possible, including the version of `mcpconn` you are using, the version of Python you are using, and a code sample that reproduces the bug.
- **Feature requests:** If you have an idea for a new feature, please open an issue in the [issue tracker](https://github.com/2796gaurav/mcpconn/issues). Please describe the feature in as much detail as possible, including why you think it would be a good addition to `mcpconn`.
- **Code contributions:** If you would like to contribute code to `mcpconn`, please see the "Code contributions" section below.
- **Documentation improvements:** If you would like to improve the documentation, please open a pull request with your changes.

## Code contributions

### Setting up the development environment

1.  Fork the repository on GitHub.
2.  Clone your fork locally:

    ```bash
    git clone https://github.com/YOUR_USERNAME/mcpconn.git
    ```

3.  Install the project in editable mode with the development dependencies:

    ```bash
    cd mcpconn
    pip install -e ".[dev]"
    ```

### Code style

`mcpconn` uses `black` for code formatting. Before submitting a pull request, please make sure that your code is formatted with `black`.

To format your code, run the following command:

```bash
black .
```

### Submitting a pull request

1.  Create a new branch for your feature or bug fix:

    ```bash
    git checkout -b my-new-feature
    ```

2.  Make your changes and add tests.
3.  Make sure that the tests pass and that your code is formatted with `black` and passes `mypy`'s checks.
4.  Commit your changes:

    ```bash
    git commit -am 'Add some feature'
    ```

5.  Push to the branch:

    ```bash
    git push origin my-new-feature
    ```

6.  Open a pull request on GitHub.

## Dev Guide

The `mcpconn` library is designed to be extensible, allowing you to easily add new LLM providers, transports, or guardrails.

### Project Structure

```
mcpconn/
├── __init__.py
├── client.py        # High-level mcpconn for server interaction
├── guardrails.py    # Built-in security and content filtering
├── transport.py     # Manages different connection protocols (STDIO, SSE)
├── llm/
│   ├── __init__.py
│   ├── base.py      # Base class for LLM providers
│   ├── anthropic.py # Anthropic provider
│   └── openai.py    # OpenAI provider
└── utils.py         # Utility functions
```

### Adding a new LLM Provider

1.  Create a new file in the `mcpconn/llm` directory (e.g., `my_provider.py`).
2.  Create a new class that inherits from `LLMProvider` (from `mcpconn.llm.base`).
3.  Implement the `process_request` and `process_response` methods.
4.  Add your new provider to the `LLM_PROVIDERS` dictionary in `mcpconn/llm/__init__.py`.

### Adding a new Transport

1.  Create a new class in `mcpconn/transport.py` that inherits from `BaseTransport`.
2.  Implement the `connect` and `disconnect` methods.
3.  Implement the `send` and `receive` methods to handle communication with the server.
4.  Add your new transport to the `mcpconn`'s `connect` method as a new option.

### Adding a new Guardrail

1.  Create a new function in `mcpconn/guardrails.py` that takes a string as input and returns a modified string.
2.  Add your new guardrail to the `Guardrails` class.
3.  You can then enable or disable your guardrail through the `mcpconn`.

Thank you for contributing to `mcpconn`! 