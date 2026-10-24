#!/usr/bin/env python3
"""Top-level AutoevolveAI entry point for the 1-Hour Project HiveMind PR, Roadmap, Experimentation & Discussion Orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
HIVEMIND_SRC = ROOT_DIR / "sub_projects" / "hivemind" / "HiveMind" / "src"

for path_entry in (ROOT_DIR, HIVEMIND_SRC):
    if str(path_entry) not in sys.path:
        sys.path.insert(0, str(path_entry))

from hivemind.cli.community_orchestrator import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
