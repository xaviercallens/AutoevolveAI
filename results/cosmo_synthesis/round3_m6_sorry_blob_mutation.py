#!/usr/bin/env python3
"""Round-3 response: re-run of the round-3 formal referee's mutation control M6 (script copied from
/tmp/r3f/ledger_sorry_blob_mutation.py; only the output locations changed) on COPIES of the ledgers.
Question: does the Elenchus ledger gate notice a Tier A `lean_axioms` row whose
OWN evidence blob reports `sorryAx` in the axiom list?  The gate source only
hashes blobs (LEDGER_EVIDENCE_MISMATCH) and never parses `lean_axioms` content,
so the prediction is rc 0.  This is the sharpest form of the "digest binds
bytes, not claims" limitation the paper already discloses; run it to make the
consequence concrete.  Originals are untouched."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run")
GATE = Path("/home/callensxavier_gmail_com/.claude/jobs/4d188676/tmp/elenchus_survey/SocrateAI-Scientific-Elenchus/tools/ledger.py")
OUT = Path("/tmp/r3resp/m6")
REPORT = WT / "results/cosmo_synthesis/round3_m6_mutation.json"
RUNS = {
    "desi_dr2_bao": "DR2-A-0002",
    "eboss_vs_desi": "EVD-A-0005",
    "bao_bbn_h0": "BBNH0-A-0002",
}


def gate(ledger: Path, evdir: Path) -> tuple[int, str]:
    p = subprocess.run(["python3", str(GATE), "--evidence-dir", str(evdir), str(ledger)], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    report = {}
    for run, rid in RUNS.items():
        src = WT / "results" / run / "ledger"
        dst = OUT / run
        shutil.copytree(src, dst)
        led = json.loads((dst / "ledger.json").read_text())
        row = next(c for c in led["claims"] if c["id"] == rid)
        old_digest = row["evidence"].split(":", 1)[1]
        blob_path = dst / "evidence" / (old_digest + ".json")
        raw = blob_path.read_text()
        # insert sorryAx into the axiom list of the theorem this row is about
        # (the blob text may already contain the words "no sorryAx" in a gloss;
        # only the axiom list itself is mutated)
        mutated = raw.replace("[propext, Classical.choice, Quot.sound]", "[propext, sorryAx, Classical.choice, Quot.sound]")
        if mutated == raw:
            mutated = raw.replace('"propext"', '"sorryAx", "propext"', 1)
        assert mutated != raw, blob_path
        new_digest = hashlib.sha256(mutated.encode()).hexdigest()
        (dst / "evidence" / (new_digest + ".json")).write_text(mutated)
        row["evidence"] = "sha256:" + new_digest
        (dst / "ledger.json").write_text(json.dumps(led, indent=1))
        rc_before, out_before = gate(src / "ledger.json", src / "evidence")
        rc_after, out_after = gate(dst / "ledger.json", dst / "evidence")
        report[run] = {
            "row": rid,
            "blob_before": old_digest[:12],
            "blob_after_with_sorryAx": new_digest[:12],
            "rc_original": rc_before,
            "rc_mutated": rc_after,
            "findings_mutated": out_after.splitlines()[-3:],
            "sorryAx_in_mutated_blob": "sorryAx" in mutated,
            "gate_detected": rc_after != rc_before or "sorry" in out_after.lower(),
        }
        print(run, rid, "rc original", rc_before, "-> mutated", rc_after, "detected:", report[run]["gate_detected"])
    (OUT / "m6_report.json").write_text(json.dumps(report, indent=1))
    REPORT.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
