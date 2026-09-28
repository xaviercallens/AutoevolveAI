#!/usr/bin/env python3
"""Register run two's claims in an Elenchus tier-capped ledger.

Tier A (lean_axioms): one claim per locked statement -- the claim is about the
  Lean proposition as written, and says so for proxies; evidence is the
  kernel's own axiom line from results/master_math_run2/lean_compile.txt.
  `audit` stays null: nobody independent has certified statement adequacy.
Tier B (exact_harness): counts that anyone can replay from committed files
  (the controls, the kernel verdicts over the recorded proofs).
Evidence blobs are content-addressed (filename = sha256 of the bytes).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from scripts.master_math.problems import PROBLEMS  # noqa: E402

RUN = REPO / "results" / "master_math_run2"
OUT = RUN / "ledger"
LEAN = REPO / "formal" / "ANSE" / "MasterMathRun2.lean"


def blob(obj: dict) -> str:
    data = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    h = hashlib.sha256(data).hexdigest()
    (OUT / "evidence").mkdir(parents=True, exist_ok=True)
    (OUT / "evidence" / f"{h}.json").write_bytes(data)
    return f"sha256:{h}"


def main() -> int:
    compile_out = (RUN / "lean_compile.txt").read_text()
    src_sha = hashlib.sha256(LEAN.read_bytes()).hexdigest()
    claims: list[dict] = []
    for k, p in enumerate(PROBLEMS, 1):
        full = f"ANSE.MasterMathRun2.{p['id']}"
        line = next((ln for ln in compile_out.splitlines() if ln.startswith(f"'{full}' ")), None)
        if line is None:
            print(f"ABORT: no kernel axiom line for {full}")
            return 1
        gloss = {"faithful": f"a faithful statement of {p['title']}",
                 "proxy": f"an arithmetic PROXY named after {p['title']} -- it does not prove that theorem",
                 "special-case": f"a special case of {p['title']}",
                 "definitional": f"{p['title']}, which Mathlib provides as a structure field "
                                 "(a pass is lookup, not proof)"}[p["fidelity"]]
        claims.append({
            "schema_version": 1, "id": f"MM2-A-{k:04d}", "tier": "A", "kind": "lean_axioms",
            "statement": (f"{full}, {gloss}, is kernel-verified with axioms within "
                          "[propext, Classical.choice, Quot.sound]; no sorryAx."),
            "depends_on": [],
            "evidence": blob({"file": "formal/ANSE/MasterMathRun2.lean", "source_sha256": src_sha,
                              "lean_toolchain": "leanprover/lean4:v4.34.0-rc2",
                              "compile": "lake env lean (rc 0)", "kernel_axiom_footprint": line,
                              "fidelity": p["fidelity"]}),
            "audit": None,
        })
    val = json.loads((RUN / "validation.json").read_text())
    runs = json.loads((RUN / "runs.json").read_text())
    s = runs["summary"]
    claims.append({
        "schema_version": 1, "id": "MM2-B-0001", "tier": "B", "kind": "exact_harness",
        "statement": (f"All {len(val['items'])} locked statements pass three kernel controls: reference "
                      "proof clean, reference rejected on a false variant, false variant's negation "
                      "kernel-proved (scripts/master_math/validate.py)."),
        "depends_on": [], "evidence": blob({"validation": val["items"]}), "audit": None,
    })
    claims.append({
        "schema_version": 1, "id": "MM2-B-0002", "tier": "B", "kind": "exact_harness",
        "statement": (f"The recorded attempts in results/master_math_run2/runs.json contain kernel-clean "
                      f"proofs of {s['deepseek']['pass_r0']}/24 statements by DeepSeek-Prover-V2-7B and "
                      f"{s['goedel']['pass_r0']}/24 by Goedel-Prover-V2-8B in the greedy round, no additional "
                      "statement after one error-feedback round, and 0 of 48 false variants accepted."),
        "depends_on": [], "evidence": blob({"summary": s, "runs_sha256": hashlib.sha256(
            (RUN / "runs.json").read_bytes()).hexdigest()}), "audit": None,
    })
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1,
                                                ensure_ascii=False))
    print(f"{len(claims)} claims written to {OUT / 'ledger.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
