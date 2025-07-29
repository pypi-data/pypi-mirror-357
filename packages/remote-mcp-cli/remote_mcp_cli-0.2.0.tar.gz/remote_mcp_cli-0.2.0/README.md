# remote-mcp-cli

This repository provides **remote-mcp-cli**, a minimal command line interface for
remote MCP (Model Context Protocol) servers. It supports both modern Streamable HTTP
transport and legacy REST endpoints for maximum compatibility.

## Features

- **Modern MCP Support**: Full support for MCP Streamable HTTP transport (2025-06-18 spec)
- **Tool Schema Display**: Shows parameter names, types, and required fields when listing tools
- **Multiple Transport Support**: Automatically falls back between Streamable HTTP and legacy REST
- **Session Management**: Handles MCP session IDs for stateful servers
- **Bearer Token Auth**: Support for authenticated MCP servers via `MCP_TOKEN` environment variable
- **Custom Headers**: Use `--header` to send additional authentication headers

## Installation

Use [uv](https://github.com/astral-sh/uv) to install the project in editable
mode:

```bash
uv pip install -e .
```

## Usage

After installation the `remote-mcp-cli` command is available. See its help for all
options:

```bash
remote-mcp-cli --help
```

### Examples

List available tools with their schemas:

```bash
remote-mcp-cli https://mcp.deepwiki.com/mcp list
```

Output shows tool descriptions and parameter schemas:
```
- read_wiki_structure: Get a list of documentation topics for a GitHub repository
  Parameters: *repoName(string)
  (* = required)
- ask_question: Ask any question about a GitHub repository
  Parameters: *repoName(string), *question(string)
  (* = required)
```

Call a tool (arguments are a JSON string):

```bash
remote-mcp-cli https://mcp.deepwiki.com/mcp call read_wiki_structure '{"repoName":"openai/openai-python"}'
```

The command supports the `MCP_TOKEN` environment variable for bearer tokens:

```bash
export MCP_TOKEN="your-token-here"
remote-mcp-cli https://secure-mcp-server.com/mcp list
```

### Custom Headers

Custom headers can be supplied with `--header` option. This is useful for authentication tokens, API keys, or other server-specific headers:

```bash
# Single custom header
remote-mcp-cli https://api.ref.tools/mcp --header "x-ref-api-key: YOURKEY" list

# Multiple custom headers
remote-mcp-cli https://secure-server.com/mcp \
  --header "x-api-key: your-api-key" \
  --header "x-client-id: your-client-id" \
  list

# Authentication header (alternative to MCP_TOKEN)
remote-mcp-cli https://server.com/mcp --header "Authorization: Bearer your-token" list
```

### Supported MCP Servers

This CLI works with:
- **DeepWiki MCP Server**: `https://mcp.deepwiki.com/mcp` (Streamable HTTP)
- **Legacy MCP Servers**: Servers using `/manifest` and `/call_tool` endpoints
- **Custom MCP Servers**: Any server implementing MCP Streamable HTTP transport

### Transport Priority

The CLI automatically tries transports in this order:
1. **Streamable HTTP** (`/mcp` endpoint) - Modern MCP transport
2. **Legacy REST** (`/manifest`, `/call_tool`) - Older MCP implementations

## Building and Publishing

To build and publish the package with `uv`:

```bash
uv build
uv pip install --system twine
uv twine upload dist/*
```

## MCP Protocol Support

This CLI implements:
- MCP Protocol Version: 2025-06-18
- JSON-RPC 2.0 message format
- Streamable HTTP transport with SSE support
- Session management via `Mcp-Session-Id` headers
- Proper initialization handshake
- Tool discovery and execution
