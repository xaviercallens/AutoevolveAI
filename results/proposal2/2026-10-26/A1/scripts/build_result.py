"""Assemble results/proposal2/2026-10-26/A1/result.json from the compile logs (never from hand-typed numbers where a
log exists). Usage: build_result.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

A1 = Path(__file__).resolve().parents[1]
REPO = A1.parents[3]
SS = REPO / "formal_cert/Programmes/SandierSerfaty"
LOGS = A1 / "logs"


def log(name: str) -> dict:
    p = LOGS / f"compile_{name}.json"
    if not p.exists():
        return {"present": False}
    d = json.loads(p.read_text())
    out = d["output"]
    return {"present": True, "rc": d["rc"], "seconds": d["seconds"], "sorry_warning": "declaration uses 'sorry'" in out,
            "errors": len(re.findall(r": error", out)), "log_mtime": p.stat().st_mtime}


def counts() -> dict:
    res = {}
    for line in (LOGS / "counted_run.err").read_text().splitlines():
        m = re.match(r"COUNTS (\S+) (.*)", line)
        if m:
            res[m.group(1)] = {k: int(v) for k, v in (kv.split("=") for kv in m.group(2).split())}
    return res


def main() -> None:
    genuine = ["IV", "Constants", "Asserts", "Bcons", "CalcKCore", "CalcK", "CalcLamCore", "CalcLam", "SignedEndpoints",
               "Bridge", "Chain", "CalcKPilot"] + [f"CalcKS{i}" for i in range(4)] + [f"CalcKF{i}" for i in range(8)] + \
              [f"CalcLamF{i}" for i in range(10)] + [f"CalcLamE{i}" for i in range(10)]
    must_compile_controls = ["Controls", "CalcControls"]
    must_fail = ["ControlsReject", "CalcKReject", "CalcControlsReject"]
    audits = ["Axioms", "AxiomsCalcK", "AxiomsAll"]
    files = {}
    stale = []
    for f in sorted(SS.glob("*.lean")):
        files[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
        lg = log(f.stem)
        if lg.get("present") and lg["rc"] == 0 and lg["log_mtime"] < f.stat().st_mtime:
            stale.append(f.name)
    c = counts()
    lf = {t: json.loads((A1 / "leanflow" / f"result_{t}.json").read_text()) for t in ("exact", "planted")}
    ax = {}
    axp = LOGS / "axioms_all_summary.json"
    if axp.exists():
        ax = json.loads(axp.read_text())
    stages = [
        {"stage": "init_constants", "level": "L1+L2 complete", "theorems": ["ln2_comp_eq", "pi_comp_eq", "p_comp_eq", "R_comp_eq", "a_comp_eq",
                                                                            "log_two_mem", "pi_mem", "p_mem", "R_mem", "a_mem", "a_mem_triScale", "p_mem_triScale"]},
        {"stage": "cs + init_after_co", "level": "A only (|c1|<1 on exact endpoints); computation not ported", "theorems": ["cpp_asserts"]},
        {"stage": "table", "level": "not ported (premise of calcLam, calcK, bdsup, global_grid, inside_hess)", "theorems": []},
        {"stage": "core_test", "level": "not ported", "theorems": []},
        {"stage": "bcons/eps", "level": "L1 complete (premise: co[1..38] from cs)", "theorems": ["bcons_comp_eq", "premises_chain"]},
        {"stage": "calcLam", "level": "L1 complete, conditional on the table enclosures", "theorems": ["calcLam_stage (600 chunks + calcLam_chunk_sums + calcLam_eq)"]},
        {"stage": "calcK", "level": "L1 complete, conditional on the table enclosures", "theorems": ["calcK_stage (97 + 194 chunks + calcK_mesh + calcK_K_eq)"]},
        {"stage": "asserts after calcK", "level": "A on exact endpoints + conditional L2", "theorems": ["cpp_asserts", "rat_consts_eq", "lambda_real", "K_real", "fl_real", "slope_real"]},
        {"stage": "bdsup", "level": "printed hulls A only; computation not ported", "theorems": ["printed_pairs"]},
        {"stage": "global_grid outer", "level": "final assertion A + conditional L2; computation not ported", "theorems": ["cpp_asserts", "grid_margins", "gmf_real"]},
        {"stage": "global_grid negative", "level": "final assertion A + conditional L2; computation not ported", "theorems": ["cpp_asserts", "grid_margins", "neglhs_real"]},
        {"stage": "inside_hess", "level": "hull minima A; computation not ported", "theorems": ["cpp_asserts"]},
    ]
    result = {
        "item": "A1", "date": "2026-10-26",
        "claim_boundary": "The Sandier-Serfaty conjecture is NOT formally proved. Kernel-checked: the stages listed with their level; "
                          "L1 = kernel re-execution of the C++ interval computation from stated premises, bit-equal to the C++ output.",
        "stages_total": len(stages),
        "stages_L1_complete": ["init_constants", "bcons/eps", "calcLam", "calcK"],
        "stages_L2_complete": ["init_constants"],
        "stages_arith_on_exact_endpoints": ["asserts after calcK", "global_grid outer", "global_grid negative", "inside_hess", "cs (|c1|<1)", "22 printed pairs"],
        "stages": stages,
        "share_of_cpp_ivops_reexecuted": None,
        "op_counts": c,
        "compile_logs": {n: log(n) for n in genuine + must_compile_controls + must_fail + audits},
        "must_fail_rejected": {n: (log(n).get("rc") not in (0, None)) for n in must_fail},
        "stale_oleans": stale,
        "axiom_audit": ax,
        "leanflow": {"worktree": "/home/callensxavier_gmail_com/LeanFlow-wt-p1", "commit": "06084ef5c40057c66c476feba18ea3da8fb150ba",
                     "tests": "94 passed", "exact": {k: lf["exact"][k] for k in ("status", "code", "tier", "seconds")},
                     "planted": {k: lf["planted"][k] for k in ("status", "code", "tier", "failed", "seconds")}},
        "a1b": {"theorem": "ProgSandierSerfaty.Reduction.signed_endpoints", "also": ["assembly_algebra", "b_lt_dstar"],
                "controls": ["ctl_signed_without_sum_false", "ctl_signed_hyps"]},
        "lean_sources_sha256": files,
    }
    ops = {k: v.get("mul", 0) + v.get("inv", 0) for k, v in c.items()}
    done = ops.get("init_constants", 0) + ops.get("calcLam", 0) + ops.get("calcK", 0) + ops.get("bcons_eps", 0)
    total = sum(v for k, v in ops.items() if k not in ("init_constants_again", "init_core_rest"))
    result["share_of_cpp_ivops_reexecuted"] = {"mul_plus_inv_reexecuted": done, "mul_plus_inv_total": total, "fraction": done / total}
    (A1 / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("stages_total", "stages_L1_complete", "share_of_cpp_ivops_reexecuted", "must_fail_rejected", "stale_oleans")}, indent=1))


if __name__ == "__main__":
    main()
