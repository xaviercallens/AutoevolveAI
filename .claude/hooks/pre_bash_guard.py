#!/usr/bin/env python3
"""PreToolUse guard for Bash: blocks history-destroying git commands and hook bypasses."""

import json
import re
import sys

BLOCKED = [
    (r"git\s+push\b.*(--force\b|--force-with-lease\b|\s-f\b)", "force push"),
    (r"git\s+reset\s+--hard", "git reset --hard"),
    (r"git\s+clean\s+-\w*f", "git clean -f"),
    (r"--no-verify\b", "hook bypass (--no-verify)"),
    (r"\brm\s+-\w*r\w*f?\s+/(\s|$)", "rm -rf /"),
]


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    for pattern, label in BLOCKED:
        if re.search(pattern, command):
            print(f"Blocked by .claude/hooks/pre_bash_guard.py: {label}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
