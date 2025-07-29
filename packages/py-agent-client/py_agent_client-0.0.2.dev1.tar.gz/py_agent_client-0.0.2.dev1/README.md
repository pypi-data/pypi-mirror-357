# 🚀 py-agent-client

**Build powerful MCP client applications with the Intelligent Agents Platform**

[![PyPI](https://img.shields.io/pypi/v/py-agent-client)](https://pypi.org/project/py-agent-client/)
[![Python](https://img.shields.io/pypi/pyversions/py-agent-client)](https://pypi.org/project/py-agent-client/)
[![Downloads](https://img.shields.io/pypi/dm/py-agent-client)](https://pypi.org/project/py-agent-client/)
[![License](https://img.shields.io/pypi/l/py-agent-client)](https://pypi.org/project/py-agent-client/)

## 🎯 What is py-agent-client?

**py-agent-client** is the flagship client library for the **Intelligent Agents Platform (IAP)**. It enables developers to build applications that interact seamlessly with **Model Context Protocol (MCP)** servers, making AI agent development intuitive and powerful.

✨ **Key Features:**
- 🔌 **Universal MCP Support** - Connect to any MCP-compliant server
- ⚡ **High Performance** - Optimized for speed and reliability
- 🛠️ **Rich Tooling** - Comprehensive tool discovery and execution
- 🐍 **Pythonic Design** - Clean, intuitive API
- 🔒 **Enterprise Ready** - Built for production environments

## 🚀 Quick Start

### Installation
```bash
pip install py-agent-client
```

### Your First MCP Client
```python
from py_agent_client import MCPClient

async def main():
    # Connect to an MCP server
    client = MCPClient()
    await client.connect("ws://localhost:8080")
    
    # Discover available tools
    tools = await client.list_tools()
    print(f"Found {len(tools)} tools available")
    
    # Execute a tool
    result = await client.call_tool("file_reader", {
        "path": "document.txt"
    })
    print(f"Result: {result}")

import asyncio
asyncio.run(main())
```

## 🏗️ Intelligent Agents Platform Ecosystem

**py-agent-client** is part of the comprehensive **IAP ecosystem**:

```
🏗️ py-agent-core       - Foundation & shared utilities
├── py-agent-client    - ✅ Client applications (You are here)
├── py-agent-server    - 🚧 MCP server development
├── py-agent-tool      - 🚧 Development & debugging tools
└── py-agent-resources - 🚧 Templates & examples
```

## 🔧 Features & Examples

### Tool Discovery
```python
# List all available tools
tools = await client.list_tools()

# Get detailed tool information
tool_info = await client.get_tool_info("web_scraper")
print(f"Parameters: {tool_info.parameters}")
```

### Tool Execution
```python
# Execute tools with parameters
result = await client.call_tool("calculator", {
    "operation": "multiply",
    "a": 15,
    "b": 7
})

# Handle errors gracefully
try:
    data = await client.call_tool("api_caller", {
        "url": "https://api.example.com/data"
    })
except MCPToolError as e:
    print(f"Tool execution failed: {e}")
```

### Advanced Connection Management
```python
from py_agent_client import ConnectionConfig

# Custom configuration
config = ConnectionConfig(
    url="wss://secure-server.com:8443",
    timeout=30,
    retry_attempts=5,
    headers={"Authorization": "Bearer token123"}
)

client = MCPClient(config)
await client.connect()
```

### Real-time Events
```python
# Listen for server events
@client.on("tool_added")
async def on_new_tool(tool_info):
    print(f"New tool available: {tool_info.name}")

@client.on("connection_lost")
async def on_disconnect():
    await client.reconnect()
```

## 📊 Monitoring & Performance

### Built-in Metrics
```python
# Get performance statistics
stats = client.get_stats()
print(f"Tools called: {stats.tools_called}")
print(f"Average response time: {stats.avg_response_time}ms")
print(f"Success rate: {stats.success_rate}%")
```

### Custom Logging
```python
import logging

# Enable debug logging
logging.getLogger("py_agent_client").setLevel(logging.DEBUG)
```

## 🔧 Configuration

### Environment Variables
```bash
export IAP_SERVER_URL="ws://localhost:8080"
export IAP_TIMEOUT=30
export IAP_API_KEY="your_api_key"
```

### Configuration File
```python
# config.py
IAP_CONFIG = {
    "server_url": "ws://localhost:8080",
    "timeout": 30,
    "retry_attempts": 3,
    "tools": {
        "enabled": ["file_ops", "web_scraper", "calculator"]
    }
}
```

## 🚧 Ecosystem Status

| Package | Status | Description |
|---------|--------|-------------|
| **py-agent-client** | ✅ **Available Now** | Full-featured MCP client |
| py-agent-core | 🚧 In Development | Foundation & shared utilities |
| py-agent-server | 🚧 In Development | Build MCP servers |
| py-agent-tool | 🚧 In Development | Development & debugging tools |
| py-agent-resources | 🚧 In Development | Templates & examples |

## 📚 Resources

- 📖 **[Documentation](https://github.com/fmonfasani/intelligent-agents-platform/wiki)**
- 🎯 **[Examples](https://github.com/fmonfasani/intelligent-agents-platform/tree/main/examples)**
- 🐛 **[Issues](https://github.com/fmonfasani/intelligent-agents-platform/issues)**
- 💬 **[Discussions](https://github.com/fmonfasani/intelligent-agents-platform/discussions)**

## 🤝 Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/fmonfasani/intelligent-agents-platform) for contribution guidelines.

### Development Setup
```bash
git clone https://github.com/fmonfasani/intelligent-agents-platform
cd intelligent-agents-platform
pip install -e .[dev,test]
pytest tests/
```

## 📄 License

Licensed under the **MIT License** - see [LICENSE](https://github.com/fmonfasani/intelligent-agents-platform/blob/main/LICENSE) for details.

---

<div align="center">

**🚀 Start building intelligent agents today!**

[![GitHub](https://img.shields.io/badge/GitHub-⭐%20Star-yellow?style=for-the-badge&logo=github)](https://github.com/fmonfasani/intelligent-agents-platform)
[![PyPI](https://img.shields.io/badge/PyPI-📦%20Install-blue?style=for-the-badge&logo=python)](https://pypi.org/project/py-agent-client/)

**Built with ❤️ by [Federico Monfasani](https://github.com/fmonfasani)**

*Part of the Intelligent Agents Platform*

</div>