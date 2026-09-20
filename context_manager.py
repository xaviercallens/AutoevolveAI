#!/usr/bin/env python3
"""
Context Pruner and Tool Output Offloader.
Prevents context window flooding by truncating tool outputs and isolating research artifacts.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

SCRATCHPAD_DIR = Path(".scratchpad")
SCRATCHPAD_DIR.mkdir(exist_ok=True)

MAX_INLINE_LINES = 60
HEAD_TAIL_SIZE = 25


def truncate_and_offload_context(tool_name: str, raw_output: str) -> str:
    """
    If raw_output is small, return directly.
    If large, write to .scratchpad/ and return a high-density summary pointer.
    """
    lines = raw_output.splitlines()
    if len(lines) <= MAX_INLINE_LINES:
        return raw_output

    # Hash payload to create an addressable scratchpad file
    token = hashlib.sha256(f"{tool_name}:{time.time()}".encode()).hexdigest()[:10]
    out_file = SCRATCHPAD_DIR / f"{tool_name}_{token}.log"
    out_file.write_text(raw_output, encoding="utf-8")

    head = "\n".join(lines[:HEAD_TAIL_SIZE])
    tail = "\n".join(lines[-HEAD_TAIL_SIZE:])
    total_lines = len(lines)

    return (
        f"[TOOL OUTPUT TRUNCATED - {total_lines} lines total]\n"
        f"--- HEAD (First {HEAD_TAIL_SIZE} lines) ---\n{head}\n"
        f"...\n"
        f"--- TAIL (Last {HEAD_TAIL_SIZE} lines) ---\n{tail}\n"
        f"--- END TRUNCATION ---\n"
        f"Full output stored on disk at: {out_file.resolve()}\n"
        f"Tip: Use specific line filters or grep on the scratchpad file if more detail is needed."
    )
