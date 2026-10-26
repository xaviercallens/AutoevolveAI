"""Generate gen_numbers.tex and data/ from the A1 run (results/proposal2/2026-10-26/A1) so that no number in main.tex is typed by hand.

Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
Reads result.json, logs/compile_*.json, Chain.lean, the LeanFlow results, the gate output (if present); copies the evidence files into data/.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
A1 = W / "results/proposal2/2026-10-26/A1"
LOGS = A1 / "logs"
LEAN = W / "formal_cert/Programmes/SandierSerfaty"
DATA = HERE / "data"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cj(name: str) -> dict:
    return json.loads((LOGS / f"compile_{name}.json").read_text())


def secs(names: list[str]) -> float:
    return round(sum(cj(n)["seconds"] for n in names), 1)


def main() -> int:
    DATA.mkdir(exist_ok=True)
    res = json.loads((A1 / "result.json").read_text())
    oc = res["op_counts"]

    # --- copy evidence
    keep = ["Axioms", "AxiomsCalcK", "AxiomsAll", "Controls", "CalcControls", "ControlsReject", "CalcKReject", "CalcControlsReject",
            "Constants", "Bcons", "Bridge", "Chain", "SignedEndpoints", "Asserts", "IV", "CalcKCore", "CalcK", "CalcLam", "CalcKPilot"]
    for n in keep:
        shutil.copy(LOGS / f"compile_{n}.json", DATA / f"compile_{n}.json")
    for f in ["sha256.txt", "axioms_all_summary.json", "bench_results.json", "bench_calck_trial.json", "counted_run.err", "counted_run.out",
              "dump_driver_time.log", "dump_scalars.txt"]:
        shutil.copy(LOGS / f, DATA / f)
    shutil.copy(A1 / "result.json", DATA / "result.json")
    shutil.copy(A1 / "CERTIFICATE_PORT.md", DATA / "CERTIFICATE_PORT.md")
    shutil.copy(A1 / "REDUCTION_LEMMA.md", DATA / "REDUCTION_LEMMA.md")
    for f in ["claim_exact.json", "claim_planted.json", "result_exact.json", "result_planted.json"]:
        shutil.copy(A1 / "leanflow" / f, DATA / f"leanflow_{f}")

    # --- op counts
    mi = lambda k: oc[k]["mul"] + oc[k]["inv"]
    total_mi = sum(mi(k) for k in oc)
    total_mi_no_again = total_mi - mi("init_constants_again")
    done_keys = ["init_constants", "bcons_eps", "calcLam", "calcK"]
    done_mi = sum(mi(k) for k in done_keys)
    assert done_mi == res["share_of_cpp_ivops_reexecuted"]["mul_plus_inv_reexecuted"], done_mi
    assert total_mi_no_again == res["share_of_cpp_ivops_reexecuted"]["mul_plus_inv_total"], total_mi_no_again
    total_mi = total_mi_no_again
    frac = done_mi / total_mi

    # --- compile seconds
    calck_files = [f"CalcKS{i}" for i in range(4)] + [f"CalcKF{i}" for i in range(8)]
    calclam_files = [f"CalcLamF{i}" for i in range(10)] + [f"CalcLamE{i}" for i in range(10)]
    t_calck_chunks = secs(calck_files)
    t_calck_all = round(t_calck_chunks + secs(["CalcK", "CalcKCore"]), 1)
    t_calclam_chunks = secs(calclam_files)
    t_calclam_all = round(t_calclam_chunks + secs(["CalcLam", "CalcLamCore"]), 1)
    t_S = secs([f"CalcKS{i}" for i in range(4)])
    t_F = secs([f"CalcKF{i}" for i in range(8)])
    t_lam = t_calclam_chunks
    ops_kl = mi("calcK") + mi("calcLam")
    rate_low = ops_kl / (t_calck_all + t_calclam_all)       # all ported files incl. core + final
    rate_chunks = ops_kl / (t_calck_chunks + t_calclam_chunks)
    bench = json.loads((LOGS / "bench_results.json").read_text())
    base = json.loads(bench[0]["lean_report"])["seconds"]
    brates = []
    for b in bench[1:]:
        n = int(re.search(r"BenchIV(\d+)", b["file"]).group(1))
        s = json.loads(b["lean_report"])["seconds"] - base
        brates.append(round(6 * n / s))
    rate_hi = max(brates)
    def n_chunks(stem: str, i: int, kind: str) -> int:
        return len(re.findall(rf"^theorem chunk_{kind}\d+ ", (LEAN / f"{stem}{i}.lean").read_text(), re.M))
    base0 = base  # seconds of the import-only benchmark file (BenchIV0), subtracted as the fixed import cost
    s_units = [(n_chunks("CalcKS", i, "S") * 32 - (1 if i == 3 else 0), cj(f"CalcKS{i}")["seconds"]) for i in range(4)]
    f_units = [(n_chunks("CalcKF", i, "F") * 8, cj(f"CalcKF{i}")["seconds"]) for i in range(8)]
    assert sum(n for n, _ in s_units) == 3103 and sum(n for n, _ in f_units) == 1552, (s_units, f_units)
    g_per = [(t - base0) / n for n, t in s_units]
    gf_per = [(t - base0) / n for n, t in f_units]
    G_lo, G_hi = min(g_per), max(g_per)
    GF_lo, GF_hi = min(gf_per), max(gf_per)
    g_lo = round((t_S - 4 * base0) / 3103, 3)
    gf_avg = round((t_F - 8 * base0) / 1552, 3)
    lookup_avg = round(t_lam / 90000, 3)                          # value lookup per calcLam step (F and E files together)
    proj = {
        "global_grid": (oc["global_grid"]["G"] * G_lo / 3600, oc["global_grid"]["G"] * G_hi / 3600),
        "inside_hess": (oc["inside_hess"]["Gfull"] * GF_lo / 3600, oc["inside_hess"]["Gfull"] * GF_hi / 3600),
        "bdsup": (oc["bdsup"]["Gfull"] * GF_lo / 3600, oc["bdsup"]["Gfull"] * GF_hi / 3600),
        "table": (mi("table") / rate_hi / 3600, mi("table") / rate_low / 3600),
        "core_test": (mi("core_test") / rate_hi / 3600, mi("core_test") / rate_low / 3600),
        "cs": (1.0, 3.0),
    }
    tot_lo = sum(v[0] for v in proj.values())
    tot_hi = sum(v[1] for v in proj.values())

    # --- must-fail error mapping
    mapping = {}
    expected = {
        "ControlsReject": {19: "rej_pi_shift", 23: "rej_ln2_199", 25: "rej_pair", 27: "rej_gmf_121", 29: "rej_erdrop_x2", 31: "rej_det", 36: "rej_G_eight_to_four"},
        "CalcKReject": {32: "rej_S0_ulp", 35: "rej_F0_ulp"},
        "CalcControlsReject": {13: "rej_calcK_er12", 16: "rej_calcLam_evipp12"},
    }
    ok_map = True
    for n, exp in expected.items():
        out = cj(n)["output"]
        errs = re.findall(rf"{n}\.lean:(\d+):\d+: error: (.*)", out)
        lines = {int(a): b for a, b in errs}
        kinds = {}
        for ln, name in exp.items():
            kinds[name] = lines.get(ln, "MISSING")
        extra = set(lines) - set(exp)
        # the declared name at each line must be the rej_ theorem of that line in the source
        src = (LEAN / f"{n}.lean").read_text().split("\n")
        for ln, name in exp.items():
            seg = "\n".join(src[max(0, ln - 6):ln + 1])
            if f"theorem {name}" not in seg:
                ok_map = False
        if extra or any(v == "MISSING" for v in kinds.values()) or len(errs) != len(exp):
            ok_map = False
        mapping[n] = {"rc": cj(n)["rc"], "n_errors": len(errs), "errors": kinds, "extra_error_lines": sorted(extra)}
    (DATA / "reject_map.json").write_text(json.dumps({"all_mapped": ok_map, "files": mapping}, indent=1))

    # --- tiling check of the chunks in Chain.lean (X observation; Lean itself does not check the tiling)
    chain = (LEAN / "Chain.lean").read_text()
    tiles = {}
    for kind in ["chunkF", "chunkS", "chunkEacc", "chunkFacc"]:
        spans = [(int(a), int(b)) for a, b in re.findall(rf"\({kind} \w+_nodes \w+_cells (\d+) (\d+) ", chain)]
        pos, ok = 0, True
        for a, b in spans:
            if a != pos:
                ok = False
            pos = a + b
        tiles[kind] = {"chunks": len(spans), "covers": [spans[0][0], pos] if spans else None, "contiguous_from_0": ok}
    (DATA / "tiling_check.json").write_text(json.dumps(tiles, indent=1))

    # --- axioms audit counts
    aa = res["axiom_audit"]
    lf = json.loads((A1 / "leanflow/result_exact.json").read_text())
    lp = json.loads((A1 / "leanflow/result_planted.json").read_text())
    pyt = (DATA / "leanflow_pytest.txt").read_text() if (DATA / "leanflow_pytest.txt").exists() else ""
    m = re.search(r"(\d+) passed in ([\d.]+)s", pyt)
    gate = HERE / "ledger/gate_output.txt"
    gtxt = gate.read_text() if gate.exists() else ""
    gm = re.search(r"exit_code=(\d+)", gtxt)
    gblock = len(re.findall(r"^\s*(?:block|BLOCK)\b", gtxt, re.M))
    gflag = len(re.findall(r"^\s*flag\b", gtxt, re.M))
    lcl = json.loads((HERE / "ledger/ledger.json").read_text())["claims"] if (HERE / "ledger/ledger.json").exists() else []
    tcount = {t: sum(1 for c in lcl if c["tier"] == t) for t in "ALCX"}

    nums = {
        "frac": frac, "done_mi": done_mi, "total_mi": total_mi, "total_mi_no_again": total_mi_no_again,
        "t_calck_chunks": t_calck_chunks, "t_calck_all": t_calck_all, "t_calclam_chunks": t_calclam_chunks, "t_calclam_all": t_calclam_all,
        "rate_low": rate_low, "rate_chunks": rate_chunks, "bench_rates": brates, "rate_hi": rate_hi,
        "G_per_file": g_per, "GF_per_file": gf_per, "G_avg": g_lo, "GF_avg": gf_avg, "lookup_avg": lookup_avg, "proj": {k: list(v) for k, v in proj.items()},
        "tot_lo": tot_lo, "tot_hi": tot_hi, "tiling": tiles, "reject_all_mapped": ok_map, "pytest": [m.group(1), m.group(2)] if m else None,
        "gate_exit": gm.group(1) if gm else None, "gate_block": gblock, "gate_flag": gflag, "ledger_tiers": tcount,
    }
    (DATA / "numbers.json").write_text(json.dumps(nums, indent=1, default=str))
    cost_keys = ["frac", "done_mi", "total_mi", "t_calck_chunks", "t_calck_all", "t_calclam_chunks", "t_calclam_all", "rate_low", "rate_chunks", "bench_rates", "rate_hi", "G_per_file", "GF_per_file", "G_avg", "GF_avg", "lookup_avg", "proj", "tot_lo", "tot_hi", "tiling"]
    (DATA / "cost_numbers.json").write_text(json.dumps({k: nums[k] for k in cost_keys}, indent=1, default=str))

    def mac(name: str, val: str) -> str:
        return "\\newcommand{\\%s}{%s}\n" % (name, val)

    def f0(x: float) -> str:
        return f"{x:,.0f}".replace(",", "{,}")

    tex = "% generated by gen_inputs.py; do not edit\n"
    tex += mac("PTFrac", f"{100 * frac:.3f}")
    tex += mac("PTDoneOps", f0(done_mi)) + mac("PTTotalOps", f0(total_mi))
    tex += mac("PTCalcKChunksSec", f"{t_calck_chunks:,.1f}") + mac("PTCalcKAllSec", f"{t_calck_all:,.1f}")
    tex += mac("PTCalcLamChunksSec", f"{t_calclam_chunks:,.1f}") + mac("PTCalcLamAllSec", f"{t_calclam_all:,.1f}")
    tex += mac("PTRateLow", f"{rate_low:.0f}") + mac("PTRateHigh", f"{rate_hi:d}")
    tex += mac("PTBenchRates", ", ".join(str(r) for r in brates))
    tex += mac("PTGLo", f"{G_lo:.2f}") + mac("PTGHi", f"{G_hi:.2f}") + mac("PTGFLo", f"{GF_lo:.2f}") + mac("PTGFHi", f"{GF_hi:.2f}") + mac("PTBaseSec", f"{base0:.1f}")
    tex += mac("PTGavg", f"{g_lo:.2f}") + mac("PTGFavg", f"{gf_avg:.2f}") + mac("PTLookupAvg", f"{lookup_avg:.2f}")
    for k, (lo, hi) in proj.items():
        key = k.replace("_", "")
        tex += mac("PTProj" + key.capitalize() + "Lo", f"{lo:.0f}") + mac("PTProj" + key.capitalize() + "Hi", f"{hi:.0f}")
    tex += mac("PTProjTotLo", f"{tot_lo:.0f}") + mac("PTProjTotHi", f"{tot_hi:,.0f}".replace(",", "{,}"))
    tex += mac("PTDaysTwoLo", f"{tot_lo / 2 / 24:.0f}") + mac("PTDaysTwoHi", f"{tot_hi / 2 / 24:.0f}")
    tex += mac("PTDaysSixtyfourLo", f"{tot_lo / 64 / 24:.1f}") + mac("PTDaysSixtyfourHi", f"{tot_hi / 64 / 24:.1f}")
    tex += mac("PTAxReports", str(aa["reports"])) + mac("PTAxPropext", str(aa["axiom_sets"]["propext"]))
    tex += mac("PTAxNone", str(aa["axiom_sets"]["none"])) + mac("PTAxFull", str(aa["axiom_sets"]["Classical.choice,Quot.sound,propext"]))
    tex += mac("PTLFTests", m.group(1) if m else "?") + mac("PTLFTestSec", m.group(2) if m else "?")
    tex += mac("PTLFSecExact", f"{lf['seconds']:.2f}") + mac("PTLFSecPlanted", f"{lp['seconds']:.2f}")
    tex += mac("PTGateExit", gm.group(1) if gm else "?") + mac("PTGateBlock", str(gblock)) + mac("PTGateFlag", str(gflag))
    tex += mac("PTLedgerN", str(sum(tcount.values()))) + "".join(mac("PTLedger" + t, str(tcount[t])) for t in "ALCX")
    skip = {"ControlsReject", "CalcKReject", "CalcControlsReject", "Axioms", "AxiomsCalcK", "AxiomsAll"}
    tot_c = sum(cj(p.name[8:-5])["seconds"] for p in LOGS.glob("compile_*.json") if p.name[8:-5] not in skip)
    tex += mac("PTCompileTotalSec", f"{tot_c:,.0f}".replace(",", "{,}")) + mac("PTCompileTotalH", f"{tot_c / 3600:.1f}")
    tex += mac("PTLeanCommit", "06084ef5c40057c66c476feba18ea3da8fb150ba")
    tex += mac("PTBase", "d4cc150a7c2e34058c24e92d08c2485b4d683f08")
    tex += mac("PTShaCore", sha(W / "results/proposal2/2026-10-26/A1/CERTIFICATE_PORT.md"))
    sh = res["lean_sources_sha256"]
    tex += mac("PTShaIV", sh["IV.lean"]) + mac("PTShaSigned", sh["SignedEndpoints.lean"]) + mac("PTShaChain", sh["Chain.lean"])
    (HERE / "gen_numbers.tex").write_text(tex)
    print(json.dumps({k: v for k, v in nums.items() if k not in ("tiling",)}, indent=1, default=str)[:3500])
    print("tiling", tiles)
    return 0


if __name__ == "__main__":
    sys.exit(main())
