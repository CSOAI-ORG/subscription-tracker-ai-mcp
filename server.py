#!/usr/bin/env python3
"""MEOK AI Labs — subscription-tracker-ai-mcp MCP Server. Track SaaS subscriptions, renewal dates, and total spend."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
import json

# In-memory store (replace with DB in production)
_store = {}

server = Server("subscription-tracker-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="add_subscription", description="Add a subscription", inputSchema={"type":"object","properties":{"name":{"type":"string"},"cost":{"type":"number"},"renewal":{"type":"string"}},"required":["name","cost"]}),
        Tool(name="get_subscriptions", description="List subscriptions", inputSchema={"type":"object","properties":{}}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "add_subscription":
        _store.setdefault("subs", []).append(args)
        return [TextContent(type="text", text=json.dumps({"status": "added"}, indent=2))]
    if name == "get_subscriptions":
        total = sum(s["cost"] for s in _store.get("subs", []))
        return [TextContent(type="text", text=json.dumps({"subscriptions": _store.get("subs", []), "monthly_total": total}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="subscription-tracker-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())