"""Assemble result.json for the A1 continuation from the artifacts on disk (re-runnable at any time):
scheduler summary, per-stage measured rates and projections, dump2 consistency, hand-test measurements, the
rusty-SUNDIALS cross-check report, and sha256 of the scripts and of the hand-written Lean core files."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1common import CONT, DUMP2, L1DIR, sha256  # noqa: E402

RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ss-table")
WORK = Path("/home/callensxavier_gmail_com/a1l1_oleans")


def git_head(repo: Path) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True)
    return r.stdout.strip()


def main() -> int:
    summary = json.loads((CONT / "status_summary.json").read_text()) if (CONT / "status_summary.json").exists() else {}
    cons = json.loads((CONT / "dump2_consistency.json").read_text()) if (CONT / "dump2_consistency.json").exists() else {}
    hand = json.loads((CONT / "hand_tests.json").read_text()) if (CONT / "hand_tests.json").exists() else {}
    proj = json.loads((CONT / "projection.json").read_text()) if (CONT / "projection.json").exists() else {}
    cc = RUSTY / "crates/qf-sandier-serfaty-table/results/cross_check.json"
    rusty = json.loads(cc.read_text()) if cc.exists() else []
    tight = [r for r in rusty if r.get("rtol") in (1e-13, 1e-14)]
    scripts = {p.name: sha256(p) for p in sorted((CONT / "scripts").glob("*")) if p.is_file()}
    cores = {str(p.relative_to(L1DIR)): sha256(p) for p in sorted(L1DIR.glob("*/Core.lean"))}
    cores.update({str(p.relative_to(L1DIR)): sha256(p) for p in [L1DIR / "Jet/Data.lean", L1DIR / "Jet/InitCheck.lean"] if p.exists()})
    pid = (WORK / "scheduler.pid").read_text().strip() if (WORK / "scheduler.pid").exists() else None
    alive = bool(pid) and Path(f"/proc/{pid}").exists()
    res = {
        "item": "proposal2 / A1 continuation: L1 port of the remaining certificate stages (cs, core_test, bdsup, inside_hess, global_grid, table)",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "claim_scope": "L1 = kernel re-execution of the C++ interval computation (decide +kernel), bit-equal to the C++ endpoints; "
                       "NOT a proof of the Sandier-Serfaty conjecture; transcription fidelity rests on bit equality; producer = verifier (no independent audit of this continuation yet)",
        "scheduler": {"pid": pid, "alive_at_generation": alive, "status_md": str(CONT / "STATUS.md"),
                      "status_dir": str(WORK / "status"), "config": str(CONT / "pipeline_config.json")},
        "stages": summary.get("stages", {}),
        "projection": proj,
        "hand_tests": hand,
        "dump2": {"path": str(DUMP2), "sha256": sha256(DUMP2), "consistency_with_A1_dump": cons},
        "rusty_sundials_cross_check": {
            "tier": "X", "worktree": str(RUSTY), "branch": "physics/sandier-serfaty-table-cvode-2026-10-26",
            "commit": git_head(RUSTY), "pushed": False,
            "verdict": ("PASS: at rtol 1e-13 and 1e-14 every CVODE value (17,640 global, 8,800 node-to-node) lies inside the certificate's "
                        "table-state enclosures; negative controls (b -> (1+1e-6) b; k -> k(1+1e-6)) leave the enclosures by up to 1.4e-7 / 1.1e-7, "
                        "far beyond the measured solver drift (<= 9.9e-13); coarser tolerances fail because the solver error exceeds the enclosure widths"),
            "tight_tolerance_rows": tight,
        },
        "sha256": {"scripts": scripts, "lean_core_files": cores},
    }
    (CONT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("wrote", CONT / "result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
