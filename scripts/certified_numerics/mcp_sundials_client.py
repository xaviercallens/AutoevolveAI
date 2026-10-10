#!/usr/bin/env python3
"""Minimal stdio JSON-RPC client for the rusty-SUNDIALS MCP server (sundials-mcp), used as an untrusted cross-check.

Usage:
    python3 scripts/certified_numerics/mcp_sundials_client.py list
    python3 scripts/certified_numerics/mcp_sundials_client.py call <tool> '<json arguments>'
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BIN = Path("/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/rust_audit_target/release/sundials-mcp")


class Client:
    def __init__(self) -> None:
        self.p = subprocess.Popen([str(BIN)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self.n = 0
        self.request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "p2-crosscheck", "version": "0"}})
        self.notify("notifications/initialized", {})

    def notify(self, method: str, params: dict) -> None:
        assert self.p.stdin is not None
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params}) + "\n")
        self.p.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        assert self.p.stdin is not None and self.p.stdout is not None
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}) + "\n")
        self.p.stdin.flush()
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("server closed: " + (self.p.stderr.read() if self.p.stderr else ""))
            msg = json.loads(line)
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(json.dumps(msg["error"]))
                return msg["result"]

    def close(self) -> None:
        self.p.terminate()


def main() -> int:
    c = Client()
    try:
        if sys.argv[1] == "list":
            res = c.request("tools/list", {})
            for t in res.get("tools", []):
                print(t["name"], "|", t.get("description", "")[:160])
                print("   schema:", json.dumps(t.get("inputSchema", {}))[:600])
        elif sys.argv[1] == "call":
            res = c.request("tools/call", {"name": sys.argv[2], "arguments": json.loads(sys.argv[3])})
            print(json.dumps(res)[:4000])
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
