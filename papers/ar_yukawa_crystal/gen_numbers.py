"""Generate gen/gen_numbers.tex (LaTeX macros) and gen/table_relax.tex from the result files; no number is typed by hand.

Sources: data/ (copies of the rusty-SUNDIALS exact-potential results), figures/fig_signs.json,
results/autoresearch/2026-10-25/H2/contribution/*.json, and the Elenchus ledger gate, re-run here.
Usage: python -I gen_numbers.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
DATA = HERE / "data"
GEN = HERE / "gen"
H2 = W / "results/autoresearch/2026-10-25/H2/contribution"
ELENCHUS = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py")


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def sci(x: float, d: int = 2) -> str:
    if x == 0:
        return "0"
    m, e = f"{x:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def main() -> int:
    GEN.mkdir(exist_ok=True)
    s = json.loads((DATA / "exact_summary.json").read_text())
    refs = [r for r in jl(DATA / "exact_refs.jsonl") if r["kind"] == "lattice"]
    box = {r["kappa"]: r for r in jl(DATA / "exact_refs.jsonl") if r["kind"] == "box"}
    mp = json.loads((DATA / "mpmath_control.json").read_text())
    sad = {r["kappa"]: r for r in jl(DATA / "exact_saddle.jsonl")}
    oc = json.loads((DATA / "oc20_shard_check.json").read_text())
    sig = json.loads((HERE / "figures/fig_signs.json").read_text())
    m: dict[str, str] = {}
    for r in refs:
        tag = {1: "One", 2: "Two"}[r["kappa"]]
        m[f"R{tag}"] = str(r["R"])
        m[f"ETri{tag}"] = f"{r['tri']['exact_partial']:.13f}"
        m[f"ESq{tag}"] = f"{r['square']['exact_partial']:.13f}"
        m[f"SfTri{tag}"] = f"{r['tri']['shifted_force_rc8']:.13f}"
        m[f"SfSq{tag}"] = f"{r['square']['shifted_force_rc8']:.13f}"
        m[f"DTri{tag}"] = sci(r["tri"]["exact_minus_sf"], 4)
        m[f"DSq{tag}"] = sci(r["square"]["exact_minus_sf"], 4)
        m[f"Tail{tag}"] = sci(max(r["tri"]["tail_bound"], r["square"]["tail_bound"]), 1)
        m[f"GapEx{tag}"] = sci(r["gap_exact"], 6)
        m[f"GapSf{tag}"] = sci(r["gap_sf_rc8"], 6)
        m[f"GapCh{tag}"] = sci(r["gap_change"], 2)
        m[f"TwiceTri{tag}"] = f"{2 * r['tri']['exact_partial']:.10f}"
        b = box[r["kappa"]]
        m[f"BoxDiff{tag}"] = sci(max(abs(b["tri_box_minus_lattice"]), abs(b["square_box_minus_lattice"])), 1)
        m[f"SelfImg{tag}"] = sci(b["tri_self_image"], 2)
        sd = sad[r["kappa"]]
        m[f"SadNeg{tag}"] = str(sd["hess_negative"])
        m[f"SadAfter{tag}"] = sci(sd["e_after_minus_e_tri_exact"], 6)
    m["MpMaxRust"] = sci(max(float(r["abs_diff_rust"]) for r in mp["rows"]), 1)
    m["MpMaxEwald"] = sci(max(abs(float(r["direct_minus_ewald"])) for r in mp["rows"]), 1)
    m["MpMaxTextbook"] = sci(max(float(r["abs_diff_textbook_scratch_R60"]) for r in mp["rows"]), 1)
    m["MpDps"] = str(mp["dps"])
    relax = s["relax"]
    m["NRelax"] = str(len(relax))
    m["NRelaxOne"] = str(sum(1 for r in relax if r["kappa"] == 1))
    m["NRelaxTwo"] = str(sum(1 for r in relax if r["kappa"] == 2))
    m["NBelow"] = str(sum(1 for r in relax if r["below_exact_floor"]))
    # below_exact_floor is exact_gap < 0 with zero tolerance (scripts/exact_figures.py); report the stages that sit at
    # the floor within f64 resolution separately (stage-5 audit correction C2).
    zero = [r for r in relax if r["exact_gap"] == 0.0]
    m["NZeroGap"] = str(len(zero))
    m["ZeroGapStage"] = "; ".join(f"$\\kappa={r['kappa']}$ \\texttt{{{r['label'].replace('_', chr(92) + '_')}}} "
                                  f"{r['stage'].replace('_', ' ')}" for r in zero)
    m["TriBoxDiffOne"] = sci(box[1]["tri_box_minus_lattice"], 1)
    m["OcMtime"] = datetime.fromtimestamp(Path(oc["local_path"]).stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    m["NNegModes"] = str(sum(1 for r in relax if r["hess_negative"] > 0))
    m["NSfRepro"] = str(sum(1 for r in relax if r["sf_reproduces_published"]))
    m["NConv"] = str(sum(1 for r in relax if r["converged"]))
    m["MaxGapChOne"] = sci(max(abs(r["gap_change"]) for r in relax if r["kappa"] == 1), 1)
    m["MaxGapChTwo"] = sci(max(abs(r["gap_change"]) for r in relax if r["kappa"] == 2), 1)
    m["MinGapOne"] = sci(min(r["sf_gap"] for r in relax if r["kappa"] == 1 and r["sf_gap"] > 1e-10), 3)
    m["OcRev"] = oc["current_revision"]
    m["OcSha"] = oc["local_sha256"]
    m["OcBytes"] = str(oc["hub_file_at_current_revision"]["size"])
    m["OcLicense"] = oc["license"].upper()
    m["SigMin"] = sci(min(sig["min_signed_derivative_by_order"].values()), 2)
    m["MixQuarter"] = f"{sig['signed_mix_at_quarter']:.4f}"
    for name, f in (("Yk", "compile_yukawa.json"), ("Mix", "compile_yukawamix.json"), ("YkCtl", "compile_yukawa_controls.json"),
                    ("MixCtl", "compile_yukawamix_controls.json"), ("Ver", "verify/compile_verify_yukawamix.json")):
        c = json.loads((H2 / f).read_text())
        m[f"Rc{name}"] = str(c["rc"])
        m[f"Sec{name}"] = f"{c['seconds']}"
    led = HERE / "ledger"
    res = subprocess.run([sys.executable, str(ELENCHUS), str(led / "ledger.json"), "--evidence-dir", str(led / "evidence"), "--json"],
                         capture_output=True, text=True)
    (led / "gate_output.json").write_text(res.stdout)
    (led / "gate_exit_code.txt").write_text(f"{res.returncode}\n")
    g = json.loads(res.stdout)
    m["LedgerExit"] = str(res.returncode)
    m["LedgerClaims"] = str(g["claims"])
    m["LedgerBlocks"] = str(sum(1 for f in g["findings"] if f["severity"] == "block"))
    m["LedgerFlags"] = str(sum(1 for f in g["findings"] if f["severity"] == "flag"))
    led_claims = json.loads((led / "ledger.json").read_text())["claims"]
    for t in "ALCX":
        m[f"LedgerN{t}"] = str(sum(1 for c in led_claims if c["tier"] == t))
    (GEN / "gen_numbers.tex").write_text("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in m.items()))
    rows = []
    for r in sorted(relax, key=lambda r: (r["kappa"], r["family"], r["label"], r["stage"])):
        rows.append(f"{r['kappa']} & \\texttt{{{r['label'].replace('_', chr(92) + '_')}}} & {r['stage'].replace('_', ' ')} & "
                    f"${sci(r['sf_gap'], 4)}$ & ${sci(r['exact_gap'], 4)}$ & ${sci(r['gap_change'], 1)}$ & "
                    f"{r['sf_defects']}/{r['exact_defects']} & {r['hess_negative']} \\\\")
    (GEN / "table_relax.tex").write_text("\n".join(rows) + "\n\\bottomrule\n")
    print(f"{len(m)} macros; ledger exit {res.returncode}; {len(rows)} relax rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
