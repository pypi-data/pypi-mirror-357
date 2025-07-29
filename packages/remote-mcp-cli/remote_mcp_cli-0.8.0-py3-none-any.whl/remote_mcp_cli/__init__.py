from __future__ import annotations
import asyncio
import json
import sys
import os
from pathlib import Path
from urllib.parse import urlparse
import typing as _t

import click
import httpx

from .config import (
    load_config, normalize_server_config, is_remote_server,
    is_mcp_remote_proxy, extract_env_headers, validate_env_vars
)
from .stdio import detect_server_url, list_tools_stdio, call_tool_stdio

DEFAULT_TIMEOUT = 30.0  # seconds


# ---------------------------------------------------------------------------
# Transport helpers
# ---------------------------------------------------------------------------


def _streamable_http_call(
    client: httpx.Client,
    server_url: str,
    method: str,
    params: dict | None,
    *,
    token: str | None,
    session_id: str | None = None,
    request_id: int = 1,
    extra_headers: dict[str, str] | None = None,
) -> tuple[_t.Any, dict]:
    """Send a JSON-RPC request using Streamable HTTP transport.

    Returns (result, headers) tuple.
    """
    headers: dict[str, str] = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    if extra_headers:
        headers.update(extra_headers)

    req_body = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params is not None:
        req_body["params"] = params

    # Use shorter timeout for faster responses
    res = client.post(server_url, headers=headers, json=req_body, timeout=10.0)
    res.raise_for_status()

    content_type = res.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = res.json()
    elif content_type.startswith("text/event-stream"):
        # Parse SSE stream more efficiently - stop as soon as we get our response
        payload = None
        for raw in res.iter_text():
            for line in raw.split('\n'):
                line = line.strip()
                if line.startswith("data: "):
                    data_content = line[6:]  # Remove "data: " prefix
                    if data_content and data_content != "ping":
                        try:
                            parsed = json.loads(data_content)
                            # Check if this is our response (matching request ID)
                            if parsed.get("id") == request_id:
                                payload = parsed
                                break
                        except json.JSONDecodeError:
                            continue
            if payload:
                break

        if not payload:
            raise RuntimeError("No matching response found in SSE stream")
    else:
        raise RuntimeError(f"Unexpected Content-Type: {content_type}")

    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "Unknown JSON-RPC error"))
    return payload.get("result"), res.headers


def _legacy_request(
    client: httpx.Client,
    server: str,
    path: str,
    *,
    token: str | None = None,
    payload: dict | None = None,
    extra_headers: dict[str, str] | None = None,
) -> _t.Any:
    """Fallback to the pre-2024 HTTP+SSE MCP transport (``/manifest`` etc.)."""
    url = server.rstrip("/") + path
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    if payload is None:
        res = client.get(url, headers=headers)
    else:
        res = client.post(url, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()


def _format_tool_info(tool: dict) -> str:
    """Format tool information including schema details."""
    name = tool.get("name", "unknown")
    desc = tool.get("description") or ""

    # Extract schema information
    schema = tool.get("inputSchema", {})
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    result = f"- {name}: {desc}"

    if properties:
        params = []
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type", "any")
            is_required = prop_name in required
            param_str = f"{prop_name}({prop_type})"
            if is_required:
                param_str = f"*{param_str}"
            params.append(param_str)

        if params:
            result += f"\n  Parameters: {', '.join(params)}"
            result += "\n  (* = required)"

    return result


def _example_args(schema: dict) -> str:
    """Create a JSON string with placeholder arguments for a tool."""
    props = schema.get("properties", {})
    result: dict[str, _t.Any] = {}
    for name, info in props.items():
        typ = info.get("type")
        if typ == "string":
            result[name] = "VALUE"
        elif typ in ("integer", "number"):
            result[name] = 0
        elif typ == "boolean":
            result[name] = False
        elif typ == "array":
            result[name] = []
        elif typ == "object":
            result[name] = {}
        else:
            result[name] = "VALUE"
    return json.dumps(result)


def _example_command(
    tool: dict,
    server: str,
    token: str | None,
    headers: dict[str, str] | None,
) -> str:
    """Return an example CLI command for calling the given tool - legacy format."""
    name = tool.get("name", "tool")
    opts: list[str] = []
    if token:
        opts.append(f"--bearer \"{token}\"")
    if headers:
        for k, v in headers.items():
            opts.append(f"--header \"{k}: {v}\"")
    options = " ".join(opts)
    args = _example_args(tool.get("inputSchema", {}))
    if options:
        options = " " + options
    return f"uvx remote-mcp-cli {server}{options} call {name} '{args}'"


def _example_simplified_command(tool: dict, server_name: str) -> str:
    """Return an example CLI command using the simplified interface."""
    name = tool.get("name", "tool")
    args = _example_args(tool.get("inputSchema", {}))
    return f"uvx remote-mcp-cli call {server_name} {name} '{args}'"


def _save_tool_info(
    tools: list[dict],
    server: str,
    token: str | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    """Save tool information to a text file under ``mcp_servers`` folder."""
    host = urlparse(server).netloc or server
    file_name = host.replace(":", "_") + ".txt"
    out_dir = Path("mcp_servers")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / file_name

    blocks: list[str] = []
    for t in tools:
        info = _format_tool_info(t)
        example = _example_command(t, server, token, headers)
        blocks.append(info + "\n  Example: " + example)

    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    return str(path)


def _example_stdio_command(tool: dict, server_name: str) -> str:
    """Return an example CLI command for calling a stdio tool."""
    name = tool.get("name", "tool")
    args = _example_args(tool.get("inputSchema", {}))
    return f"uvx remote-mcp-cli call {server_name} {name} '{args}'"


class ToolEntry:
    """Represents a tool entry for consolidated output."""
    def __init__(
        self,
        tool: dict,
        server_name: str,
        server_url: str | None = None,
        is_stdio: bool = False,
        token: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.tool = tool
        self.server_name = server_name
        self.server_url = server_url
        self.is_stdio = is_stdio
        self.token = token
        self.headers = headers

    def format_for_output(self) -> str:
        """Format this tool entry for the consolidated output file."""
        info = _format_tool_info(self.tool)
        # Use simplified interface for all examples
        example = _example_simplified_command(self.tool, self.server_name)
        return info + "\n  Example: " + example


def _save_consolidated_tools(tool_entries: list[ToolEntry]) -> str:
    """Save all tool information to consolidated mcp_tools.txt file."""
    path = Path("mcp_tools.txt")

    # Group tools by server
    servers: dict[str, list[ToolEntry]] = {}
    for entry in tool_entries:
        if entry.server_name not in servers:
            servers[entry.server_name] = []
        servers[entry.server_name].append(entry)

    # Format output
    sections: list[str] = []
    for server_name, entries in servers.items():
        if not entries:
            continue

        # Determine server type for header
        first_entry = entries[0]
        if first_entry.is_stdio:
            server_header = f"### Server: {server_name}  (local npx, stdio)"
        else:
            server_header = f"### Server: {server_name}  ({first_entry.server_url})"

        # Format all tools for this server
        tool_lines = [entry.format_for_output() for entry in entries]

        section = server_header + "\n" + "\n\n".join(tool_lines)
        sections.append(section)

    # Write consolidated file
    content = "\n\n".join(sections) + "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """Remote MCP CLI - Connect to MCP servers locally and remotely."""
    pass


@cli.command("init")
@click.option(
    "--configpath",
    help="Path to MCP config file (defaults to .cursor/mcp.json or mcp.json)",
)
@click.option(
    "--spawn-timeout",
    type=float,
    default=15.0,
    help="Timeout in seconds for spawning local servers (default: 15)",
)
def import_tools(configpath: str | None, spawn_timeout: float):
    """Initialize tools from all servers in MCP config and save to mcp_tools.txt."""
    try:
        config = load_config(configpath)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    servers = config["mcpServers"]
    tool_entries: list[ToolEntry] = []
    success_count = 0
    failed_servers: list[str] = []

    for server_name, server_config in servers.items():
        try:
            normalized = normalize_server_config(server_name, server_config)

            if is_remote_server(normalized):
                # Remote server path
                success = _process_remote_server(
                    server_name, normalized, tool_entries
                )
            else:
                # Spawn path (stdio or mcp-remote proxy)
                success = asyncio.run(_process_spawned_server(
                    server_name, normalized, tool_entries, spawn_timeout
                ))

            if success:
                success_count += 1
            else:
                failed_servers.append(server_name)

        except Exception as e:
            click.echo(f"Failed to process server '{server_name}': {e}", err=True)
            failed_servers.append(server_name)

    # Save consolidated output
    if tool_entries:
        output_file = _save_consolidated_tools(tool_entries)
        total_tools = len(tool_entries)
        click.echo(f"✓ Processed {success_count} servers successfully")
        if failed_servers:
            click.echo(f"✗ Failed servers: {', '.join(failed_servers)}")
        click.echo(f"→ {output_file} written with {total_tools} tools total")
    else:
        click.echo("No tools found from any server", err=True)
        sys.exit(1)


@cli.command("list")
@click.argument("server_name")
@click.option(
    "--configpath",
    help="Path to MCP config file (defaults to .cursor/mcp.json or mcp.json)",
)
def list_server_tools(server_name: str, configpath: str | None):
    """List tools for SERVER_NAME from config (simplified interface)."""
    try:
        config = load_config(configpath)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    servers = config["mcpServers"]
    if server_name not in servers:
        click.echo(f"Error: Server '{server_name}' not found in config", err=True)
        available = list(servers.keys())
        click.echo(f"Available servers: {', '.join(available)}", err=True)
        sys.exit(1)

    server_config = normalize_server_config(server_name, servers[server_name])

    try:
        if is_remote_server(server_config):
            # Remote server
            _list_remote_tools(server_name, server_config)
        else:
            # Spawned server
            asyncio.run(_list_spawned_tools(server_name, server_config))
    except Exception as e:
        click.echo(f"Error listing tools for '{server_name}': {e}", err=True)
        sys.exit(1)


@cli.command("call")
@click.argument("server_name")
@click.argument("tool_name")
@click.argument("tool_args", default="{}")
@click.option(
    "--configpath",
    help="Path to MCP config file (defaults to .cursor/mcp.json or mcp.json)",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Only print JSON tool result (suppress wrapper metadata).",
)
def call_server_tool(server_name: str, tool_name: str, tool_args: str, configpath: str | None, raw: bool):
    """Call TOOL_NAME on SERVER_NAME with TOOL_ARGS (simplified interface)."""
    try:
        args_json = json.loads(tool_args)
    except json.JSONDecodeError as exc:
        click.echo(f"\u2717 Invalid JSON for tool_args: {exc}", err=True)
        sys.exit(1)

    try:
        config = load_config(configpath)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    servers = config["mcpServers"]
    if server_name not in servers:
        click.echo(f"Error: Server '{server_name}' not found in config", err=True)
        available = list(servers.keys())
        click.echo(f"Available servers: {', '.join(available)}", err=True)
        sys.exit(1)

    server_config = normalize_server_config(server_name, servers[server_name])

    try:
        if is_remote_server(server_config):
            # Remote server
            result = _call_remote_tool(server_name, server_config, tool_name, args_json)
        else:
            # Spawned server
            result = asyncio.run(_call_spawned_tool(server_name, server_config, tool_name, args_json))

        click.echo(json.dumps(result if raw else {"result": result}, indent=2))
    except Exception as e:
        click.echo(f"Error calling tool '{tool_name}' on '{server_name}': {e}", err=True)
        sys.exit(1)


def _list_remote_tools(server_name: str, server_config: dict):
    """List tools from a remote server."""
    server_url = server_config.get("serverUrl") or server_config.get("url", "")
    headers = server_config.get("headers", {})

    # Extract token from headers if present
    token = None
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        tools_list = None

        # Try Streamable HTTP transport first
        try:
            init_result, init_headers = _streamable_http_call(
                client,
                server_url,
                "initialize",
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "remote-mcp-cli",
                        "version": "0.1.1"
                    }
                },
                token=token,
                request_id=1,
                extra_headers=headers,
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            tools_result, _ = _streamable_http_call(
                client,
                server_url,
                "tools/list",
                None,
                token=token,
                session_id=session_id,
                request_id=2,
                extra_headers=headers,
            )
            tools_list = tools_result.get("tools", []) if tools_result else []

        except Exception:
            # Fallback to legacy transport
            tools_list = _legacy_request(
                client,
                server_url,
                "/manifest",
                token=token,
                extra_headers=headers,
            ).get("tools", [])

    for tool in tools_list or []:
        info = _format_tool_info(tool)
        click.echo(info)


async def _list_spawned_tools(server_name: str, server_config: dict):
    """List tools from a spawned server."""
    command = server_config.get("command", "")
    args = server_config.get("args", [])
    env_config = server_config.get("env", {})

    # Validate environment variables
    env = validate_env_vars(env_config)

    tools = await list_tools_stdio(command, args, env)
    for tool in tools:
        info = _format_tool_info(tool)
        click.echo(info)


def _call_remote_tool(server_name: str, server_config: dict, tool_name: str, tool_args: dict):
    """Call a tool on a remote server."""
    server_url = server_config.get("serverUrl") or server_config.get("url", "")
    headers = server_config.get("headers", {})

    # Extract token from headers if present
    token = None
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        # Try Streamable HTTP transport first
        try:
            init_result, init_headers = _streamable_http_call(
                client,
                server_url,
                "initialize",
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "remote-mcp-cli",
                        "version": "0.1.1"
                    }
                },
                token=token,
                request_id=1,
                extra_headers=headers,
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            result, _ = _streamable_http_call(
                client,
                server_url,
                "tools/call",
                {"name": tool_name, "arguments": tool_args},
                token=token,
                session_id=session_id,
                request_id=2,
                extra_headers=headers,
            )
            return result

        except Exception:
            # Fallback to legacy transport
            payload = {"name": tool_name, "arguments": tool_args}
            return _legacy_request(
                client,
                server_url,
                "/call_tool",
                token=token,
                payload=payload,
                extra_headers=headers,
            )


async def _call_spawned_tool(server_name: str, server_config: dict, tool_name: str, tool_args: dict):
    """Call a tool on a spawned server."""
    command = server_config.get("command", "")
    args = server_config.get("args", [])
    env_config = server_config.get("env", {})

    # Validate environment variables
    env = validate_env_vars(env_config)

    return await call_tool_stdio(command, args, tool_name, tool_args, env)


def _process_remote_server(
    server_name: str,
    server_config: dict,
    tool_entries: list[ToolEntry]
) -> bool:
    """Process a remote MCP server and add its tools to tool_entries."""
    server_url = server_config.get("serverUrl") or server_config.get("url", "")
    headers = server_config.get("headers", {})

    # Extract token from headers if present
    token = None
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            tools_list = None

            # Try Streamable HTTP transport first
            try:
                init_result, init_headers = _streamable_http_call(
                    client,
                    server_url,
                    "initialize",
                    {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "remote-mcp-cli",
                            "version": "0.1.1"
                        }
                    },
                    token=token,
                    request_id=1,
                    extra_headers=headers,
                )
                session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

                tools_result, _ = _streamable_http_call(
                    client,
                    server_url,
                    "tools/list",
                    None,
                    token=token,
                    session_id=session_id,
                    request_id=2,
                    extra_headers=headers,
                )
                tools_list = tools_result.get("tools", []) if tools_result else []

            except Exception:
                # Fallback to legacy transport
                tools_list = _legacy_request(
                    client,
                    server_url,
                    "/manifest",
                    token=token,
                    extra_headers=headers,
                ).get("tools", [])

        # Add tools to entries
        for tool in tools_list or []:
            entry = ToolEntry(
                tool=tool,
                server_name=server_name,
                server_url=server_url,
                is_stdio=False,
                token=token,
                headers=headers,
            )
            tool_entries.append(entry)

        return True

    except Exception as e:
        click.echo(f"Remote server '{server_name}' failed: {e}", err=True)
        return False


async def _process_spawned_server(
    server_name: str,
    server_config: dict,
    tool_entries: list[ToolEntry],
    spawn_timeout: float,
) -> bool:
    """Process a spawned MCP server and add its tools to tool_entries."""
    command = server_config.get("command", "")
    args = server_config.get("args", [])
    env_config = server_config.get("env", {})

    if not command:
        click.echo(f"Server '{server_name}' missing 'command' field", err=True)
        return False

    try:
        # Validate environment variables are set
        env = validate_env_vars(env_config)

        # Check if this is an mcp-remote proxy
        if is_mcp_remote_proxy(server_config):
            # Try URL detection first for mcp-remote
            detected_url = await detect_server_url(command, args, env, spawn_timeout)
            if detected_url:
                # Treat as remote server
                proxy_config = {
                    "serverUrl": detected_url,
                    "headers": extract_env_headers(env),
                }
                return _process_remote_server(server_name, proxy_config, tool_entries)

        # For regular stdio servers or mcp-remote fallback
        # Try URL detection first
        detected_url = await detect_server_url(command, args, env, spawn_timeout)
        if detected_url:
            # Server exposes HTTP interface
            proxy_config = {
                "serverUrl": detected_url,
                "headers": extract_env_headers(env),
            }
            return _process_remote_server(server_name, proxy_config, tool_entries)
        else:
            # Fall back to stdio mode
            tools_list = await list_tools_stdio(command, args, env)

            # Add tools to entries
            for tool in tools_list:
                entry = ToolEntry(
                    tool=tool,
                    server_name=server_name,
                    is_stdio=True,
                )
                tool_entries.append(entry)

            return True

    except ValueError as e:
        click.echo(f"Server '{server_name}' environment error: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"Spawned server '{server_name}' failed: {e}", err=True)
        return False


@cli.group()
def direct():
    """Direct URL-based access to remote MCP servers (no config needed)."""
    pass


@direct.command("list")
@click.option(
    "--url",
    required=True,
    help="MCP server URL",
)
@click.option(
    "--bearer",
    "token",
    envvar="MCP_TOKEN",
    help="Authorization bearer token (or set MCP_TOKEN env var)",
)
@click.option(
    "--header",
    multiple=True,
    help="Custom header in 'Name: value' format. Can be passed multiple times.",
)
def direct_list_tools(url: str, token: str | None, header: tuple[str, ...]):
    """List available tools on the remote MCP server."""
    extra_headers = {}
    for h in header:
        if ":" not in h:
            raise click.BadParameter("Headers must be in 'Name: value' format")
        name, value = h.split(":", 1)
        extra_headers[name.strip()] = value.strip()

    server = url.rstrip("/")
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        tools_list = None

        # Try Streamable HTTP transport first (much faster than SSE)
        try:
            # Initialize session
            init_result, init_headers = _streamable_http_call(
                client,
                server,
                "initialize",
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "remote-mcp-cli",
                        "version": "0.1.1"
                    }
                },
                token=token,
                request_id=1,
                extra_headers=extra_headers,
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            # Get tools list
            tools_result, _ = _streamable_http_call(
                client,
                server,
                "tools/list",
                None,
                token=token,
                session_id=session_id,
                request_id=2,
                extra_headers=extra_headers,
            )
            tools_list = tools_result.get("tools", []) if tools_result else []

        except Exception as e:
            # Fallback to legacy transport
            try:
                tools_list = _legacy_request(
                    client,
                    server,
                    "/manifest",
                    token=token,
                    extra_headers=extra_headers,
                ).get("tools", [])
            except Exception:
                click.echo(f"Error: Could not connect to MCP server: {e}", err=True)
                sys.exit(1)

    for tool in tools_list or []:
        info = _format_tool_info(tool)
        click.echo(info)


@direct.command("call")
@click.option(
    "--url",
    required=True,
    help="MCP server URL",
)
@click.option(
    "--bearer",
    "token",
    envvar="MCP_TOKEN",
    help="Authorization bearer token (or set MCP_TOKEN env var)",
)
@click.option(
    "--header",
    multiple=True,
    help="Custom header in 'Name: value' format. Can be passed multiple times.",
)
@click.argument("tool_name")
@click.argument("tool_args", default="{}")
@click.option(
    "--raw",
    is_flag=True,
    help="Only print JSON tool result (suppress wrapper metadata).",
)
def direct_call_tool(url: str, token: str | None, header: tuple[str, ...], tool_name: str, tool_args: str, raw: bool):
    """Invoke TOOL_NAME with TOOL_ARGS (a JSON string) on remote server."""
    try:
        args_json = json.loads(tool_args)
    except json.JSONDecodeError as exc:
        click.echo(f"\u2717 Invalid JSON for tool_args: {exc}", err=True)
        sys.exit(1)

    extra_headers = {}
    for h in header:
        if ":" not in h:
            raise click.BadParameter("Headers must be in 'Name: value' format")
        name, value = h.split(":", 1)
        extra_headers[name.strip()] = value.strip()

    server = url.rstrip("/")
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = None

        # Try Streamable HTTP transport first
        try:
            # Initialize session
            init_result, init_headers = _streamable_http_call(
                client,
                server,
                "initialize",
                {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "remote-mcp-cli",
                        "version": "0.1.1"
                    }
                },
                token=token,
                request_id=1,
                extra_headers=extra_headers,
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            # Call the tool
            resp, _ = _streamable_http_call(
                client,
                server,
                "tools/call",
                {"name": tool_name, "arguments": args_json},
                token=token,
                session_id=session_id,
                request_id=2,
                extra_headers=extra_headers,
            )

        except Exception as e:
            # Fallback to legacy transport
            try:
                payload = {"name": tool_name, "arguments": args_json}
                resp = _legacy_request(
                    client,
                    server,
                    "/call_tool",
                    token=token,
                    payload=payload,
                    extra_headers=extra_headers,
                )
            except Exception:
                click.echo(f"Error: Could not call tool: {e}", err=True)
                sys.exit(1)

    click.echo(json.dumps(resp if raw else {"result": resp}, indent=2))


def main(argv: _t.Sequence[str] | None = None) -> None:
    """Entry point for the remote-mcp-cli."""
    if argv is None:
        argv = sys.argv[1:]

    cli.main(args=list(argv), prog_name="remote-mcp-cli")


if __name__ == "__main__":
    main()
