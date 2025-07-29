# mcp-agent-client

**⚠️ Legacy MCP Client - Consider using py-agent ecosystem instead**

![PyPI](https://img.shields.io/pypi/v/mcp-agent-client)
![Python](https://img.shields.io/pypi/pyversions/mcp-agent-client)

## 📢 Migration Notice

This package has been superseded by the **py-agent ecosystem**. For new projects, please use:

- **py-agent-core** - Core MCP functionality
- **py-agent-client** - Modern client implementation
- **py-agent-server** - Server implementation
- **py-agent-tool** - Additional tools

## 🎯 What is mcp-agent-client?

The original MCP (Model Context Protocol) client implementation. This package provides basic functionality for connecting to MCP servers but is now considered legacy.

## 🚀 Quick Start

```bash
pip install mcp-agent-client
```

```python
from mcp_agent_client import MCPClient

# Basic usage (legacy)
client = MCPClient()
client.connect("localhost:8080")
```

## ⬆️ Migration Guide

### Old (mcp-agent-client):
```python
from mcp_agent_client import MCPClient
client = MCPClient()
```

### New (py-agent-client):
```python
from py_agent_client import MCPClient
client = MCPClient()
# Enhanced features and better performance
```

## 🔄 Recommended Migration

1. **Install new ecosystem:**
   ```bash
   pip install py-agent-client
   ```

2. **Update imports:**
   ```python
   # Old
   from mcp_agent_client import MCPClient
   
   # New
   from py_agent_client import MCPClient
   ```

3. **Enjoy enhanced features:**
   - Better error handling
   - Improved performance
   - More comprehensive tooling
   - Active development

## 🚧 Support Status

- ⚠️ **Legacy support only**
- 🚫 **No new features**
- ✅ **Critical bug fixes only**
- 📈 **Migrate to py-agent-client recommended**

## 📦 py-agent Ecosystem

For new projects, use the modern ecosystem:

```bash
pip install py-agent-core py-agent-client py-agent-server py-agent-tool
```

## 📄 License

Apache License 2.0

## 🤝 Migration Support

Need help migrating? Check out the **py-agent-client** documentation or open an issue.

---

**Built with ❤️ by fmonfasanidev**

**✨ Upgrade to py-agent ecosystem for the best experience! ✨**