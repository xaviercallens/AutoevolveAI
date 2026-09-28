"""Referee round 1 (formal lens): independent sequential recompilation of the four
cosmology Lean modules with the pinned build command, plus a per-theorem axiom parse.

Pinned command: cd /home/callensxavier_gmail_com/AutoevolveAI/formal && timeout 1800 lake env lean <abs path>
"""
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run")
FORMAL_CWD = "/home/callensxavier_gmail_com/AutoevolveAI/formal"
OUT = WT / "results/cosmo_synthesis/referee_round1_formal_lean_recheck.json"
FILES = ["BAO_FlatLCDM.lean", "DESI_DR2_wCDM.lean", "BAO_BBN_H0.lean", "BAO_Consistency.lean"]
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}


def parse_axioms(out: str) -> list[dict]:
    res: list[dict] = []
    for m in re.finditer(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", out, re.S):
        axs = [a.strip() for a in (m.group(3) or "").replace("\n", " ").split(",") if a.strip()]
        res.append({"decl": m.group(1), "axioms": axs})
    return res


def theorem_names(text: str) -> list[str]:
    return re.findall(r"^\s*(?:private\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)", text, re.M)


def main() -> None:
    report: dict = {"pinned_cwd": FORMAL_CWD, "files": {}}
    for f in FILES:
        p = WT / "formal/ANSE" / f
        text = p.read_text()
        names = theorem_names(text)
        t0 = time.time()
        proc = subprocess.run(
            ["timeout", "1800", "lake", "env", "lean", str(p)],
            cwd=FORMAL_CWD, capture_output=True, text=True,
        )
        wall = time.time() - t0
        out = proc.stdout + proc.stderr
        axs = parse_axioms(out)
        union = sorted({a for d in axs for a in d["axioms"]})
        printed = {d["decl"].split(".")[-1] for d in axs}
        missing = [n for n in names if n not in printed]
        errors = [line for line in out.splitlines() if ": error" in line]
        report["files"][f] = {
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "theorem_names": names,
            "theorem_count": len(names),
            "rc": proc.returncode,
            "wall_s": round(wall, 1),
            "print_axioms": axs,
            "axiom_union": union,
            "whitelist_only": set(union) <= WHITELIST and len(axs) > 0,
            "theorems_without_print_axioms": missing,
            "errors": errors,
            "sorry_warning": "declaration uses 'sorry'" in out,
            "output_tail": out[-2000:],
        }
        OUT.write_text(json.dumps(report, indent=2))
    report["all_rc0"] = all(v["rc"] == 0 for v in report["files"].values())
    report["all_whitelist_only"] = all(v["whitelist_only"] for v in report["files"].values())
    report["total_print_axioms_outputs"] = sum(len(v["print_axioms"]) for v in report["files"].values())
    OUT.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
