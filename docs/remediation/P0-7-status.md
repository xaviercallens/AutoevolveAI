# P0-7: MCP Guard Server Reconnection — Status

## Finding
Claude Code **successfully expands** the portable `${CLAUDE_PROJECT_DIR:-.}` variable in `.mcp.json`.

## Evidence

### 1. Configuration is portable
```
$ .venv/bin/python scripts/render_mcp_configs.py --agent claude_code
/home/callensxavier_gmail_com/AutoevolveAI/.mcp.json: portable
```

### 2. python-code-guard server is connected
The MCP tools from the python-code-guard server appear in the deferred tools list:
- `mcp__python-code-guard__audit_anti_stub`
- `mcp__python-code-guard__audit_dead_code_vulture`
- `mcp__python-code-guard__audit_security_bandit`
- (and 12 others)

This confirms that Claude Code successfully resolved `${CLAUDE_PROJECT_DIR:-.}/.venv/bin/python` and connected to the server.

### 3. Accept commands pass
```
$ .venv/bin/python -c "import json,pathlib; d=json.loads(pathlib.Path('.mcp.json').read_text()); s=d['mcpServers']; assert 'python-code-guard' in s, sorted(s); print('✓ python-code-guard is in .mcp.json'); print('Servers:', sorted(s.keys()))"
✓ python-code-guard is in .mcp.json
Servers: ['python-code-guard']

$ .venv/bin/python scripts/render_mcp_configs.py --agent claude_code
/home/callensxavier_gmail_com/AutoevolveAI/.mcp.json: portable
```

## Conclusion
No code changes required. The portable `${CLAUDE_PROJECT_DIR:-.}` form in `.mcp.json` is working as designed (since Claude Code 2.1.203+). The `render_claude_code_config()` function mentioned in the card as a fallback is not needed.

Date verified: 2026-09-25
