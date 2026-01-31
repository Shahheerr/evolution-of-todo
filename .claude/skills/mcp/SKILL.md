---
name: MCP (Model Context Protocol)
description: Complete reference for implementing MCP servers and clients using the official Python SDK
---

# MCP (Model Context Protocol)

MCP is an open protocol developed by Anthropic that enables AI models to securely access external tools, data sources, and services. It provides a standardized way to connect AI assistants to the world.

## Package Information

- **Package Name**: `mcp`
- **PyPI**: https://pypi.org/project/mcp/
- **GitHub**: https://github.com/modelcontextprotocol/python-sdk
- **Documentation**: https://modelcontextprotocol.io/

## Installation

```bash
# Using pip
pip install mcp

# Using uv
uv add mcp
```

## Core Concepts

### 1. MCP Server
An MCP server exposes **tools**, **resources**, and **prompts** to AI clients.

### 2. MCP Client
An MCP client connects to MCP servers and uses their capabilities.

### 3. Transports
MCP supports multiple transport mechanisms:
- **stdio**: Communication via stdin/stdout (for local processes)
- **SSE (Server-Sent Events)**: HTTP-based streaming
- **Streamable HTTP**: HTTP with bidirectional streaming

### 4. Primitives
- **Tools**: Functions the AI can call (e.g., `search_database`, `send_email`)
- **Resources**: Data the AI can read (e.g., files, database records)
- **Prompts**: Pre-defined prompt templates

## File Structure Reference

See the following files for detailed implementation:

- `server/` - Server implementation patterns
  - `basic-server.md` - Creating a basic MCP server
  - `tools.md` - Defining and implementing tools
  - `resources.md` - Exposing resources
  - `prompts.md` - Creating prompt templates
  - `transports.md` - Transport configuration

- `client/` - Client implementation patterns
  - `basic-client.md` - Creating an MCP client
  - `connecting.md` - Connecting to servers

- `examples/` - Complete working examples
  - `database-server.md` - Database access server
  - `filesystem-server.md` - File system access server

- `reference/` - API reference
  - `decorators.md` - All MCP decorators
  - `types.md` - Type definitions
  - `errors.md` - Error handling
