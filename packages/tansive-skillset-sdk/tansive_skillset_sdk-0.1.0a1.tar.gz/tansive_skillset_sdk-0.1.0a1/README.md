# Tansive Python SDK

The official Python SkillSet SDK for Tansive - Open Platform for Secure AI Agents.

## Installation

```bash
pip install tansive
```

## Quick Start

```python
from tansive.skillset_sdk import TansiveClient

# Initialize the client with a Unix domain socket path
client = TansiveClient("/tmp/tangent.sock")

# Invoke a skill
result = client.invoke_skill(
    session_id="session-123",
    invocation_id="invoke-456",
    skill_name="example.echo",
    args={"message": "Hello from Tansive!"}
)

print(result.output)

# Retrieve tools
tools = client.get_tools(session_id="session-123")
print(tools)

# Fetch context
context = client.get_context(
    session_id="session-123",
    invocation_id="invoke-456",
    name="model-config"
)
print(context)
```

## Documentation

For detailed documentation, visit [docs.tansive.io](https://docs.tansive.io).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
