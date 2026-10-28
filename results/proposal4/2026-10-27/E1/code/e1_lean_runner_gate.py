"""Run anse/formal/lean_runner.py file mode on PbIgnition/Core.lean (binding repo gate) -> ../logs/lean_runner_core.json."""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path.insert(0, str(REPO))
from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402
sys.path.insert(0, str(REPO / "scripts" / "certified_numerics"))
import lean_pinned  # noqa: E402


def main() -> None:
    # pinned Lean 4.34.1 + Mathlib d13f23b7 (the main formal/ build lacks Mathlib.Tactic)
    cmd = ["/usr/bin/env", f"LEAN_PATH={lean_pinned.lean_path()}", str(lean_pinned.TOOLCHAIN_BIN / "lean"), "-DautoImplicit=false"]
    runner = LeanKernelVerifier(formal_dir=lean_pinned.PINNED, lean_cmd=cmd)
    res = runner.verify_file(REPO / "formal_cert/Programmes/PbIgnition/Core.lean", timeout_s=2400.0)
    rows = [dataclasses.asdict(r) if dataclasses.is_dataclass(r) else str(r) for r in res]
    out = Path(__file__).resolve().parent.parent / "logs" / "lean_runner_core.json"
    out.write_text(json.dumps(rows, indent=1, default=str) + "\n")
    print(json.dumps(rows, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
