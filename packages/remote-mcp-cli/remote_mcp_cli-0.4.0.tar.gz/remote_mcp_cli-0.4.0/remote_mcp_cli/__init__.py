from __future__ import annotations
import json
import sys
import typing as _t

import click
import httpx

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
    desc = (tool.get("description") or "")[:70]

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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("server_url")
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
@click.pass_context
def cli(ctx: click.Context, server_url: str, token: str | None, header: tuple[str, ...]):
    """Minimal MCP CLI — first argument is the MCP SERVER_URL."""
    extra_headers = {}
    for h in header:
        if ":" not in h:
            raise click.BadParameter("Headers must be in 'Name: value' format")
        name, value = h.split(":", 1)
        extra_headers[name.strip()] = value.strip()

    ctx.obj = {"server": server_url, "token": token, "headers": extra_headers}


@cli.command("list")
@click.pass_obj
def list_tools(obj):
    """List available tools on the remote MCP server."""
    server = obj["server"].rstrip("/")
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
                token=obj["token"],
                request_id=1,
                extra_headers=obj.get("headers"),
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            # Get tools list
            tools_result, _ = _streamable_http_call(
                client,
                server,
                "tools/list",
                None,
                token=obj["token"],
                session_id=session_id,
                request_id=2,
                extra_headers=obj.get("headers"),
            )
            tools_list = tools_result.get("tools", []) if tools_result else []

        except Exception as e:
            # Fallback to legacy transport
            try:
                tools_list = _legacy_request(
                    client,
                    server,
                    "/manifest",
                    token=obj["token"],
                    extra_headers=obj.get("headers"),
                ).get("tools", [])
            except Exception:
                click.echo(f"Error: Could not connect to MCP server: {e}", err=True)
                sys.exit(1)

    for tool in tools_list or []:
        click.echo(_format_tool_info(tool))


@cli.command("call")
@click.argument("tool_name")
@click.argument("tool_args", default="{}")
@click.option(
    "--raw",
    is_flag=True,
    help="Only print JSON tool result (suppress wrapper metadata).",
)
@click.pass_obj
def call_tool(obj, tool_name: str, tool_args: str, raw: bool):
    """Invoke TOOL_NAME with TOOL_ARGS (a JSON string)."""
    try:
        args_json = json.loads(tool_args)
    except json.JSONDecodeError as exc:
        click.echo(f"\u2717 Invalid JSON for tool_args: {exc}", err=True)
        sys.exit(1)

    server = obj["server"].rstrip("/")
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
                token=obj["token"],
                request_id=1,
                extra_headers=obj.get("headers"),
            )
            session_id = init_headers.get("Mcp-Session-Id") or init_headers.get("mcp-session-id")

            # Call the tool
            resp, _ = _streamable_http_call(
                client,
                server,
                "tools/call",
                {"name": tool_name, "arguments": args_json},
                token=obj["token"],
                session_id=session_id,
                request_id=2,
                extra_headers=obj.get("headers"),
            )

        except Exception as e:
            # Fallback to legacy transport
            try:
                payload = {"name": tool_name, "arguments": args_json}
                resp = _legacy_request(
                    client,
                    server,
                    "/call_tool",
                    token=obj["token"],
                    payload=payload,
                    extra_headers=obj.get("headers"),
                )
            except Exception:
                click.echo(f"Error: Could not call tool: {e}", err=True)
                sys.exit(1)

    click.echo(json.dumps(resp if raw else {"result": resp}, indent=2))


def _reorder_args(args: list[str]) -> list[str]:
    """Move the server URL to the beginning of the argument list.

    ``click`` expects options before positional arguments, but users may place
    options before **or** after the server URL. This helper finds the first
    argument that is neither an option nor a known command and treats it as the
    server URL. All options are kept in their original order.
    """

    if not args:
        return args

    commands = {"list", "call"}
    server_url: str | None = None
    opts: list[str] = []
    rest: list[str] = []
    expect_val: str | None = None

    for arg in args:
        if expect_val:
            opts.append(arg)
            expect_val = None
            continue

        if arg in ("--token", "--header"):
            opts.append(arg)
            expect_val = arg
            continue

        if arg.startswith("--token=") or arg.startswith("--header=") or arg in ("-h", "--help"):
            opts.append(arg)
            continue

        if not arg.startswith("-") and server_url is None and arg not in commands:
            server_url = arg
            continue

        rest.append(arg)

    if server_url is None:
        return args

    return opts + [server_url] + rest


def main(argv: _t.Sequence[str] | None = None) -> None:
    """Entry point that allows flexible option placement."""

    if argv is None:
        argv = sys.argv[1:]

    reordered = _reorder_args(list(argv))
    cli.main(args=reordered, prog_name="remote-mcp-cli")


if __name__ == "__main__":
    main()
