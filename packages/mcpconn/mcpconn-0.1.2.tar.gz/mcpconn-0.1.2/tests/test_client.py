import pytest
from mcpconn import MCPClient


def test_client_import():
    """Test that the MCPClient can be imported successfully."""
    assert MCPClient is not None


def test_client_initialization():
    """Test basic client initialization."""
    client = MCPClient()
    assert client is not None
    assert hasattr(client, 'connect')


def test_client_methods_exist():
    """Test that expected methods exist on the client."""
    client = MCPClient()
    expected_methods = [
        'connect',
        'disconnect',
        'query',
        'start_conversation',
        'get_conversation_history',
        'add_guardrail',
    ]
    for method in expected_methods:
        assert hasattr(client, method), f"Client should have method: {method}"


if __name__ == "__main__":
    pytest.main([__file__]) 