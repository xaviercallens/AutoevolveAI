"""Write the H4 night-lane preregistration (hashes computed from the files on disk)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
LANE = ROOT / "results/openai_math/hypotheses/night_2026-10-07/H4"
CODE = [
    "scripts/openai_math/hypotheses/night/h4_v2.py",
    "tests/openai_math/test_night_h4.py",
    "results/openai_math/hypotheses/night_2026-10-07/H4/design/sdi_probe.py",
    "results/openai_math/hypotheses/night_2026-10-07/H4/design/smoke.py",
    "results/openai_math/hypotheses/night_2026-10-07/H4/design/debug_vdp.py",
    "results/openai_math/hypotheses/night_2026-10-07/H4/design/write_prereg.py",
    "scripts/openai_math/hypotheses/h4_lienard.py",
    "scripts/openai_math/hypotheses/program.md",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


polish = json.loads((LANE / "design/smoke_sdi_strength_deg6_A.json").read_text())
prereg = json.loads((LANE / "design/prereg_body.json").read_text())
prereg["written_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
prereg["code_sha256"] = {c: sha(ROOT / c) for c in CODE}
prereg["design_artifacts_sha256"] = {
    p.name: sha(p) for p in sorted((LANE / "design").glob("*.json")) if p.name != "prereg_body.json"}
prereg["primary_family"]["c_high_from_polish_file"] = polish["best"]["c_high"]
(LANE / "preregistration.json").write_text(json.dumps(prereg, indent=2) + "\n")
print(json.dumps(prereg["code_sha256"], indent=1))
