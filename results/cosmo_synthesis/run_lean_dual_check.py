"""Dual-environment kernel check of the four cosmology Lean modules (sequential).

Revision 2 (round-1 referee fix). Every key the paper reads is written here;
nothing in the output JSON is hand-edited. Changes versus revision 1:
  * '#print axioms' commands are counted on comment-stripped source with an
    anchored regex (revision 1 counted a substring inside a comment);
  * accepted_count, status (BLOCKED_ENV), summary and caveat are computed;
  * toolchain and Mathlib revision are measured per environment;
  * a second negative control smuggles an 'axiom' declaration;
  * the history of the hand-corrected revision-1 JSON is recorded with its hash.
Scratch files go to /tmp (nothing is written outside results/cosmo_synthesis/).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

WT = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/cosmo3-run")
SCRATCH = Path("/tmp/cosmo_synthesis_lean_scratch")
OUT = WT / "results/cosmo_synthesis/lean_dual_check.json"
V1 = WT / "results/cosmo_synthesis/lean_dual_check_v1_handedited.json"
ENVS = {
    "env1_pinned_partial_mathlib": ("/home/callensxavier_gmail_com/AutoevolveAI/formal", 1800),
    "env2_leanmaster_full_mathlib": ("/home/callensxavier_gmail_com/SocrateAI-Scientific-Agora-LeanMaster", 3600),
}
FILES = ["BAO_FlatLCDM.lean", "DESI_DR2_wCDM.lean", "BAO_BBN_H0.lean", "BAO_Consistency.lean"]
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}


def strip_comments(text: str) -> str:
    """Remove Lean block comments (nested) and line comments."""
    out: list[str] = []
    depth = 0
    i = 0
    while i < len(text):
        if text.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth and text.startswith("-/", i):
            depth -= 1
            i += 2
            continue
        if depth:
            if text[i] == "\n":
                out.append("\n")
            i += 1
            continue
        if text.startswith("--", i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def count_print_axioms(text: str) -> int:
    return len(re.findall(r"^\s*#print\s+axioms\s", strip_comments(text), re.M))


def count_theorems(text: str) -> int:
    return len(re.findall(r"^\s*(?:private\s+)?(?:theorem|lemma)\s", strip_comments(text), re.M))


def parse_axioms(out: str) -> list[dict[str, Any]]:
    res = []
    for m in re.finditer(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", out, re.S):
        axs = [a.strip() for a in (m.group(3) or "").replace("\n", " ").split(",") if a.strip()]
        res.append({"decl": m.group(1), "axioms": axs, "line": m.group(0).replace("\n", " ")})
    return res


def env_info(env: str) -> dict[str, Any]:
    cwd, _ = ENVS[env]
    p = subprocess.run(["lake", "env", "lean", "--version"], cwd=cwd, capture_output=True, text=True)
    info: dict[str, Any] = {"cwd": cwd, "lean_version_output": (p.stdout + p.stderr).strip(),
                            "lean_toolchain_file": (Path(cwd) / "lean-toolchain").read_text().strip()}
    man = json.loads((Path(cwd) / "lake-manifest.json").read_text())
    for pkg in man.get("packages", []):
        if pkg.get("name") == "mathlib":
            info["mathlib_inputRev"] = pkg.get("inputRev")
            info["mathlib_rev"] = pkg.get("rev")
    return info


def run(env: str, path: Path) -> dict[str, Any]:
    cwd, to = ENVS[env]
    t0 = time.time()
    p = subprocess.run(["timeout", str(to), "lake", "env", "lean", str(path)], cwd=cwd, capture_output=True, text=True)
    wall = time.time() - t0
    out = p.stdout + p.stderr
    axs = parse_axioms(out)
    allax = {a for d in axs for a in d["axioms"]}
    errors = [ln for ln in out.splitlines() if ": error" in ln][:20]
    r: dict[str, Any] = {"rc": p.returncode, "wall_s": round(wall, 1), "print_axioms": axs,
                         "axiom_union": sorted(allax), "errors": errors,
                         "output_tail": out[-1500:] if p.returncode != 0 else ""}
    if p.returncode != 0 and "unknown module prefix" in out and not axs:
        r["status"] = "BLOCKED_ENV"
    return r


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    src = (WT / "formal/ANSE/BAO_FlatLCDM.lean").read_text()
    old = "  unfold E\n  rw [Real.sqrt_pos]\n  nlinarith [pow_pos (show (0:ℝ) < 1 + z by linarith) 3]\n"
    assert src.count(old) == 1
    neg_sorry = SCRATCH / "BAO_FlatLCDM_negctrl_sorry.lean"
    neg_sorry.write_text(src.replace(old, "  sorry\n"))
    neg_axiom = SCRATCH / "BAO_FlatLCDM_negctrl_axiom.lean"
    anchor = "namespace ANSE.BAOFlatLCDM\n"
    assert src.count(anchor) == 1
    smuggled = "axiom smuggled_E_pos_fact : False\n"
    neg_axiom.write_text(src.replace(old, "  exact smuggled_E_pos_fact.elim\n").replace(anchor, anchor + smuggled, 1))

    report: dict[str, Any] = {
        "script": "results/cosmo_synthesis/run_lean_dual_check.py (revision 2)",
        "date": datetime.date.today().isoformat(),
        "whitelist": sorted(WHITELIST), "environments": {}, "files": {}, "negative_control": {},
        "negative_control_axiom": {},
    }
    for env in ENVS:
        report["environments"][env] = env_info(env)
    tcs = {v["lean_toolchain_file"] for v in report["environments"].values()}
    report["toolchain"] = tcs.pop() if len(tcs) == 1 else "MISMATCH: " + ", ".join(sorted(tcs))
    for f in FILES:
        t = (WT / "formal/ANSE" / f).read_text()
        report["files"][f] = {"sha256": hashlib.sha256(t.encode()).hexdigest(),
                              "theorem_count": count_theorems(t),
                              "print_axioms_commands_in_source": count_print_axioms(t),
                              "print_axioms_substring_count_rev1_method": t.count("#print axioms"),
                              "envs": {}}
    for env in ENVS:
        for f in FILES:
            r = run(env, WT / "formal/ANSE" / f)
            n_cmd = report["files"][f]["print_axioms_commands_in_source"]
            r["accepted"] = (r["rc"] == 0 and set(r["axiom_union"]) <= WHITELIST
                             and len(r["print_axioms"]) == n_cmd and n_cmd > 0)
            report["files"][f]["envs"][env] = r
            OUT.write_text(json.dumps(report, indent=2))
        r = run(env, neg_sorry)
        r["sorryAx_seen"] = "sorryAx" in r["axiom_union"]
        r["control_passed"] = r["sorryAx_seen"]
        r["file"] = str(neg_sorry)
        report["negative_control"][env] = r
        r = run(env, neg_axiom)
        r["smuggled_axiom_seen"] = "ANSE.BAOFlatLCDM.smuggled_E_pos_fact" in r["axiom_union"] or any(
            "smuggled_E_pos_fact" in a for a in r["axiom_union"])
        r["whitelist_rejects"] = not set(r["axiom_union"]) <= WHITELIST
        r["control_passed"] = r["smuggled_axiom_seen"] and r["whitelist_rejects"]
        r["file"] = str(neg_axiom)
        report["negative_control_axiom"][env] = r
        OUT.write_text(json.dumps(report, indent=2))
    pairs = [e for f in report["files"].values() for e in f["envs"].values()]
    report["accepted_count"] = sum(1 for e in pairs if e["accepted"])
    report["pairs_total"] = len(pairs)
    report["all_accepted"] = report["accepted_count"] == len(pairs)
    report["negative_controls_passed"] = all(v["control_passed"] for v in report["negative_control"].values())
    report["negative_controls_axiom_passed"] = all(v["control_passed"] for v in report["negative_control_axiom"].values())
    report["total_theorems"] = sum(f["theorem_count"] for f in report["files"].values())
    summ = []
    for env in ENVS:
        acc = [f for f, v in report["files"].items() if v["envs"][env]["accepted"]]
        blk = [f for f, v in report["files"].items() if v["envs"][env].get("status") == "BLOCKED_ENV"]
        clean = sum(1 for v in report["files"].values() for pa in v["envs"][env]["print_axioms"]
                    if set(pa["axioms"]) <= WHITELIST)
        summ.append(f"{env}: {len(acc)}/{len(FILES)} files accepted, {clean} whitelist-only #print axioms outputs"
                    + (f"; BLOCKED_ENV: {', '.join(blk)}" if blk else ""))
    report["summary"] = "; ".join(summ)
    report["caveat"] = ("Wall times are single measurements on a shared machine (load average recorded below); "
                        "they are not benchmarks.")
    try:
        report["load_average_at_end"] = Path("/proc/loadavg").read_text().split()[:3]
    except OSError:
        report["load_average_at_end"] = None
    if V1.exists():
        report["history"] = {
            "revision_1_file": str(V1.relative_to(WT)),
            "revision_1_sha256": hashlib.sha256(V1.read_bytes()).hexdigest(),
            "revision_1_note": ("Revision 1 of this script counted the substring '#print axioms' including a comment "
                                "(BAO_FlatLCDM.lean line 71) and so rejected that file in both environments. The JSON was "
                                "then corrected by hand (keys accepted, accepted_count, print_axioms_commands_in_source, "
                                "status, note, summary, caveat were added or edited without re-running). Round-1 formal "
                                "referee found this. Revision 2 recomputes every key; revision 1 is kept for audit."),
        }
    OUT.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
