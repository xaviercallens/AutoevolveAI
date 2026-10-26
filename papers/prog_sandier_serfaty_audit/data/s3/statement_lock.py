#!/usr/bin/env python3
"""Write or check the sha256 lock of the P1 S3 Lean statement of the Sandier-Serfaty conjecture.

Usage:
    python3 -I statement_lock.py write   # writes ../STATEMENT_LOCK.json from the files + compile records
    python3 -I statement_lock.py check   # exit 0 iff the current files match the lock

The "statement region" is the text from `namespace ProgSandierSerfaty` up to the proved-lemma section marker;
it contains every definition the three statements depend on, so later proof additions do not change its hash,
while any edit to a definition or statement does.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
MAIN = REPO / "formal_cert/Programmes/SandierSerfatyStatement.lean"
CTRL = REPO / "formal_cert/Programmes/SandierSerfatyStatementControls.lean"
P1 = REPO / "results/programmes/2026-10-25/P1"
LOCK = P1 / "STATEMENT_LOCK.json"
COMPILE_MAIN = P1 / "s3/compile_statement.json"
COMPILE_CTRL = P1 / "s3/compile_controls.json"
START = "namespace ProgSandierSerfaty"
END = "/-! ## Proved non-degeneracy lemmas"
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}
STATEMENTS = ["SandierSerfatyStatement", "SandierSerfatyValueStatement", "SandierSerfatyOriginalStatement"]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def region(text: str) -> str:
    i, j = text.index(START), text.index(END)
    if j <= i:
        raise ValueError("statement region markers out of order")
    return text[i:j]


def axioms(output: str) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}
    for m in re.finditer(r"'([\w.]+)' depends on axioms: \[([^\]]*)\]", output):
        res[m.group(1)] = [a.strip() for a in m.group(2).split(",") if a.strip()]
    return res


def current() -> dict[str, object]:
    main_text, ctrl_text = MAIN.read_text(), CTRL.read_text()
    return {
        "main_file": str(MAIN.relative_to(REPO)),
        "main_file_sha256": sha(main_text),
        "statement_region_sha256": sha(region(main_text)),
        "controls_file": str(CTRL.relative_to(REPO)),
        "controls_file_sha256": sha(ctrl_text),
    }


def write() -> int:
    cm = json.loads(COMPILE_MAIN.read_text())
    cc = json.loads(COMPILE_CTRL.read_text())
    ax_main, ax_ctrl = axioms(str(cm["output"])), axioms(str(cc["output"]))
    proved_ok = {k: set(v) <= WHITELIST for k, v in ax_main.items()}
    controls_caught = {k: not (set(v) <= WHITELIST) for k, v in ax_ctrl.items()}
    sorry_in_main = "sorry" in re.sub(r"/-.*?-/|--[^\n]*", "", MAIN.read_text(), flags=re.S)
    lock = {
        "stage": "P1 S3 (programmes 2026-10-25)",
        "statements": STATEMENTS,
        "status": "STATED, NOT PROVED (definitions + non-degeneracy lemmas only)",
        **current(),
        "toolchain": "leanprover/lean4:v4.34.1",
        "mathlib_rev": "d13f23b723b8a846827a245b89c10fc7d3f11612",
        "compile_main": {"rc": cm["rc"], "seconds": cm["seconds"], "module": cm["module"]},
        "compile_controls": {"rc": cc["rc"], "seconds": cc["seconds"]},
        "axioms_main": ax_main,
        "axioms_main_within_whitelist": proved_ok,
        "sorry_token_in_main_code": sorry_in_main,
        "axioms_controls": ax_ctrl,
        "controls_caught": controls_caught,
        "gate_pass": bool(cm["rc"] == 0 and all(proved_ok.values()) and proved_ok and not sorry_in_main
                          and cc["rc"] == 0 and controls_caught and all(controls_caught.values())),
        "note": "Producer = verifier (same agent); parent should recompile independently. Tier A covers only the "
                "proved non-degeneracy lemmas; the statements themselves are Tier C fidelity claims "
                "(see STATEMENT_FIDELITY.md).",
    }
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    print(json.dumps({k: lock[k] for k in ("statement_region_sha256", "main_file_sha256", "gate_pass")}))
    return 0 if lock["gate_pass"] else 1


def check() -> int:
    lock = json.loads(LOCK.read_text())
    cur = current()
    diffs = {k: (lock[k], v) for k, v in cur.items() if lock.get(k) != v}
    print(json.dumps({"match": not diffs, "diffs": diffs}))
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(write() if sys.argv[1:] == ["write"] else check() if sys.argv[1:] == ["check"] else 2)
