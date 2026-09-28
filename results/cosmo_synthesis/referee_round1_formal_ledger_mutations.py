"""Referee round 1 (formal lens): my own mutation controls on the Elenchus ledger gate.

Copies each real ledger to /tmp, applies one mutation per case, runs ledger.py with the real
evidence dir, and records the exit code and the finding codes. Nothing under results/*/ledger is
touched. Expected: every mutation raises at least one block finding (rc 1), and the unmodified
copy reproduces the recorded rc.
"""
import json
import subprocess
from pathlib import Path

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run")
GATE = "/home/callensxavier_gmail_com/.claude/jobs/4d188676/tmp/elenchus_survey/SocrateAI-Scientific-Elenchus/tools/ledger.py"
PY = "/mnt/disks/disk-socrateai-local-1/venv-pta/bin/python"
OUT = WT / "results/cosmo_synthesis/referee_round1_formal_ledger_mutations.json"
RUNS = {
    "bao_flcdm": ("BAO-L-0002", "BAO-A-0001"),
    "desi_dr2_bao": ("DR2-L-0006", "DR2-A-0001"),
    "bao_bbn_h0": ("BBNH0-L-0008", "BBNH0-A-0001"),
    "eboss_vs_desi": ("EVD-L-0006", "EVD-A-0001"),
}


def run_gate(ledger_path: Path, evidence_dir: Path) -> dict:
    p = subprocess.run([PY, GATE, "--json", "--evidence-dir", str(evidence_dir), str(ledger_path)],
                       capture_output=True, text=True)
    try:
        body = json.loads(p.stdout)
        codes = sorted({f["code"] for f in body["findings"]})
    except (ValueError, KeyError):
        codes = ["<unparseable>"]
    return {"rc": p.returncode, "finding_codes": codes}


def main() -> None:
    report: dict = {}
    for run, (l_id, a_id) in RUNS.items():
        src = WT / "results" / run / "ledger" / "ledger.json"
        ev = WT / "results" / run / "ledger" / "evidence"
        base = json.loads(src.read_text())
        cases: dict = {}
        tmp = Path("/tmp") / f"referee_ledger_{run}_unmodified.json"
        tmp.write_text(json.dumps(base))
        cases["unmodified"] = run_gate(tmp, ev)

        # M1: a comparison-with-literature row (tier L) refiled as Tier B exact_harness.
        m = json.loads(json.dumps(base))
        for c in m["claims"]:
            if c["id"] == l_id:
                c["tier"] = "B"
                c["kind"] = "exact_harness"
                c["id"] = l_id.replace("-L-", "-B-") + "9"
        tmp = Path("/tmp") / f"referee_ledger_{run}_m1.json"
        tmp.write_text(json.dumps(m))
        cases["M1_L_refiled_as_B"] = run_gate(tmp, ev)

        # M2: a Tier A row's evidence digest pointed at a different, existing blob.
        m = json.loads(json.dumps(base))
        other = next(c["evidence"] for c in m["claims"] if c["id"] != a_id)
        for c in m["claims"]:
            if c["id"] == a_id:
                c["evidence"] = other
        tmp = Path("/tmp") / f"referee_ledger_{run}_m2.json"
        tmp.write_text(json.dumps(m))
        cases["M2_A_evidence_swapped"] = run_gate(tmp, ev)

        # M3: a Tier A row's audit replaced by a bare string (a model 'signature' without an object).
        m = json.loads(json.dumps(base))
        for c in m["claims"]:
            if c["id"] == a_id:
                c["audit"] = "audited by model"
        tmp = Path("/tmp") / f"referee_ledger_{run}_m3.json"
        tmp.write_text(json.dumps(m))
        cases["M3_A_audit_string"] = run_gate(tmp, ev)

        # M4: a Tier A row's audit replaced by an empty object (type-checks; carries no content).
        m = json.loads(json.dumps(base))
        for c in m["claims"]:
            if c["id"] == a_id:
                c["audit"] = {}
        tmp = Path("/tmp") / f"referee_ledger_{run}_m4.json"
        tmp.write_text(json.dumps(m))
        cases["M4_A_audit_empty_object"] = run_gate(tmp, ev)

        report[run] = cases
        OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
