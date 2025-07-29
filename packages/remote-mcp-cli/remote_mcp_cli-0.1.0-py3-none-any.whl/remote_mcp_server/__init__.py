from __future__ import annotations
import json
import sys
import typing as _t

import click
import httpx

DEFAULT_TIMEOUT = 30.0  # seconds


def _request(
    server: str,
    path: str,
    *,
    token: str | None = None,
    payload: dict | None = None,
) -> _t.Any:
    """One-shot helper around httpx for GET/POST JSON-RPC."""
    url = server.rstrip("/") + path
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        if payload is None:
            res = client.get(url, headers=headers)
        else:
            res = client.post(url, json=payload, headers=headers)
        res.raise_for_status()
        # If the server is streaming SSE, gather events then decode once done.
        if res.headers.get("content-type", "").startswith("text/event-stream"):
            data = "".join(line.decode() for line in res.iter_bytes())
            return data
        return res.json()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("server_url")
@click.option(
    "--token",
    envvar="MCP_TOKEN",
    help="Bearer token (or set MCP_TOKEN env var)",
)
@click.pass_context
def cli(ctx: click.Context, server_url: str, token: str | None):
    """Minimal MCP CLI — first argument is the MCP SERVER_URL."""
    ctx.obj = {"server": server_url, "token": token}


@cli.command("list")
@click.pass_obj
def list_tools(obj):
    """List available tools on the remote MCP server."""
    out = _request(obj["server"], "/manifest", token=obj["token"])
    for tool in out.get("tools", []):
        desc = (tool.get("description") or "")[:70]
        click.echo(f"- {tool['name']}: {desc}")


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

    payload = {"name": tool_name, "arguments": args_json}
    resp = _request(obj["server"], "/call_tool", token=obj["token"], payload=payload)
    click.echo(json.dumps(resp if raw else {"result": resp}, indent=2))


if __name__ == "__main__":
    cli()
