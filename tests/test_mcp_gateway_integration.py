#!/usr/bin/env python3
"""
Unit tests verifying MCP Cluster Routing & Gateway Integration in Antigravity v2.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from anse.guard.mcp_router import MCPRouter
from gateway import app, get_mcp_router


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT_DIR / ".antigravity" / "mcp_config.json"


@pytest.fixture
def mcp_router() -> MCPRouter:
    router = MCPRouter(CONFIG_FILE)
    return router


def test_mcp_router_initialization(mcp_router: MCPRouter) -> None:
    servers = mcp_router.list_servers()
    assert "antigravity-guard" in servers
    assert "claude-subtask-workflow" in servers
    assert "logic-planner" in servers
    assert servers["antigravity-guard"]["transport"] == "in-process"
    assert servers["claude-subtask-workflow"]["transport"] == "in-process"
    assert servers["logic-planner"]["transport"] == "stdio"


@pytest.mark.asyncio
async def test_mcp_router_in_process_tool_call(mcp_router: MCPRouter) -> None:
    res = await mcp_router.call_tool(
        server_name="antigravity-guard",
        tool_name="verify_ast_and_imports",
        arguments={"code": "import math\nval = math.sqrt(16)"},
    )
    assert res["success"] is True
    assert res["server"] == "antigravity-guard"
    assert res["result"]["valid"] is True
    assert "math" in res["result"]["detected_imports"]


@pytest.mark.asyncio
async def test_mcp_router_auto_routing(mcp_router: MCPRouter) -> None:
    res = await mcp_router.call_tool(
        server_name="auto",
        tool_name="verify_ast_and_imports",
        arguments={"code": "a = 1 + 2"},
    )
    assert res["success"] is True
    assert res["server"] == "antigravity-guard"


def test_gateway_mcp_servers_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/mcp/servers")
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    assert "antigravity-guard" in data["servers"]
    assert "claude-subtask-workflow" in data["servers"]


def test_gateway_mcp_call_endpoint() -> None:
    client = TestClient(app)
    payload = {
        "name": "verify_ast_and_imports",
        "arguments": {"code": "import sys\nver = sys.version"},
        "server": "antigravity-guard",
    }
    response = client.post("/mcp/call", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["result"]["valid"] is True
    assert "sys" in data["result"]["detected_imports"]


def test_gateway_mcp_rpc_endpoint() -> None:
    client = TestClient(app)
    rpc_payload = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {
            "name": "verify_ast_and_imports",
            "arguments": {"code": "import json"},
        },
    }
    response = client.post("/mcp/rpc/antigravity-guard", json=rpc_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 101
    assert data["result"]["valid"] is True
    assert "json" in data["result"]["detected_imports"]
