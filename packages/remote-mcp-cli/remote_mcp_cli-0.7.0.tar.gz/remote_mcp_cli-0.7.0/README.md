# remote-mcp-cli

A simple command-line tool for interacting with **remote MCP servers** - no installation or configuration required! Just run `uvx remote-mcp-cli <server-url> <command>` from your terminal.

**remote-mcp-cli** provides a minimal CLI for remote MCP (Model Context Protocol) servers. It supports both modern Streamable HTTP transport and legacy REST endpoints for maximum compatibility.

## Quick Start

### Use with uvx (Recommended)

The easiest way to use this tool is with `uvx` - no installation needed:

```bash
# List tools from any remote MCP server
uvx remote-mcp-cli https://mcp.deepwiki.com/mcp list

# Call a tool with JSON arguments
uvx remote-mcp-cli https://mcp.deepwiki.com/mcp call read_wiki_structure '{"repoName":"openai/openai-python"}'

# Use with authentication headers
uvx remote-mcp-cli https://api.ref.tools/mcp --header "x-ref-api-key: YOURKEY" list
```

### Traditional Installation

You can also install traditionally with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install remote-mcp-cli
```

## Remote vs Local MCP Servers

**Remote MCP servers** run as web services and are the modern direction for MCP:
- **Accessible anywhere**: Just need the HTTPS URL
- **No local setup**: No configuration files or local processes
- **Auto-updating**: Server improvements are immediately available
- **Scalable**: Can handle multiple users simultaneously
- **Examples**: `https://mcp.deepwiki.com/mcp`, `https://api.ref.tools/mcp`

**Local MCP servers** run on your computer:
- **Local execution**: Run as subprocesses via stdio transport
- **Manual setup**: Require `claude_desktop_config.json` configuration
- **Manual updates**: Need to download and install updates yourself
- **Single user**: Typically only one AI application can use them at a time

This CLI is specifically designed for **remote MCP servers** that use HTTP transport rather than local servers that use stdio.

## Features

- **Modern MCP Support**: Full support for MCP Streamable HTTP transport (2025-06-18 spec)
- **Tool Schema Display**: Shows parameter names, types, and required fields when listing tools
- **Save Tool List**: `--save` writes tool details and example commands to `mcp_servers/<host>.txt`
- **Multiple Transport Support**: Automatically falls back between Streamable HTTP and legacy REST
- **Session Management**: Handles MCP session IDs for stateful servers
 - **Bearer Token Auth**: Pass tokens with `--bearer` or `MCP_TOKEN` environment variable
- **Custom Headers**: Use `--header` to send additional authentication headers

## Usage

### Basic Commands

```bash
# List available tools with their schemas
uvx remote-mcp-cli <server-url> list

# Save tool details and example commands to the mcp_servers folder
uvx remote-mcp-cli <server-url> list --save

# Call a tool with JSON arguments
uvx remote-mcp-cli <server-url> call <tool-name> <json-args>


# Get help
uvx remote-mcp-cli --help
```

### Examples

List available tools with their schemas:

```bash
uvx remote-mcp-cli https://mcp.deepwiki.com/mcp list
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
uvx remote-mcp-cli https://mcp.deepwiki.com/mcp call read_wiki_structure '{"repoName":"openai/openai-python"}'
```

### Authentication

#### Environment Variable or `--bearer`
Set the `MCP_TOKEN` environment variable or pass a token with `--bearer` for bearer authentication:

```bash
export MCP_TOKEN="your-token-here"
uvx remote-mcp-cli https://secure-mcp-server.com/mcp list

# Or pass the token directly
uvx remote-mcp-cli --bearer "your-token-here" https://secure-mcp-server.com/mcp list
```

#### Custom Headers
Use `--header` for API keys, tokens, or other authentication:

```bash
# Single custom header
uvx remote-mcp-cli https://api.ref.tools/mcp --header "x-ref-api-key: YOURKEY" list

# Options can also be placed before the server URL
remote-mcp-cli --header "x-ref-api-key: YOURKEY" https://api.ref.tools/mcp list

# Multiple custom headers
uvx remote-mcp-cli https://secure-server.com/mcp \
  --header "x-api-key: your-api-key" \
  --header "x-client-id: your-client-id" \
  list

# Authentication header (alternative to `--bearer`/`MCP_TOKEN`)
uvx remote-mcp-cli https://server.com/mcp --header "Authorization: Bearer your-token" list
```

### Supported Remote MCP Servers

This CLI works with any remote MCP server, including:
- **DeepWiki MCP Server**: `https://mcp.deepwiki.com/mcp` (Streamable HTTP)
- **Legacy MCP Servers**: Servers using `/manifest` and `/call_tool` endpoints
- **Custom MCP Servers**: Any server implementing MCP HTTP transport

### Transport Priority

The CLI automatically tries transports in this order:
1. **Streamable HTTP** (modern MCP 2025-06-18 spec)
2. **Legacy REST** (older `/manifest`, `/call_tool` endpoints)

## Development

### Building and Publishing

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
