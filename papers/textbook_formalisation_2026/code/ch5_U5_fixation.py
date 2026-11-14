"""Chapter 5, use case U5: fixation of a mutation (Moran chain with selection).

Steps (all real computations, nothing is hand-entered):
  1. Hugging Face dataset katarinagresova/Genomic_Benchmarks_demo_coding_vs_intergenomic_seqs, pinned revision:
     check the sha256 of the test split, then count sequences per label, lengths and GC fraction.
     The dataset illustrates what sequence data look like; it does NOT estimate any fitness r.
  2. rusty-SUNDIALS crate qf-popgen, binary fixation_ode: CVODE (BDF) integration of d pi/dt = pi (P - I) with a
     fail-closed absorption certificate (115 rows expected: 106 accepted runs, 9 refused negative controls).
  3. Exact rationals (Python Fraction) for (1 - r^-i)/(1 - r^-N), compared with the CVODE values.
  4. LeanFlow data certificates (lean.certify, tactic decide_kernel, core Lean 4.34.1):
     (a) the CVODE value for N=3, r=2, i=1 lies within 1e-11 of 4/7;
     (b) the vector (0, 4/7, 6/7, 1) solves the first-step (harmonic) equations of the Moran chain N=3, r=2 exactly;
     negative controls: the neutral value 1/3, a bound that is too tight (1e-14), and the neutral vector i/N
     must all be rejected.
  5. Figure figures/ch5_U5_fixation.pdf and a JSON summary.

Usage:
  python -I ch5_U5_fixation.py OUT_DIR [--bin DIR] [--lean PATH] [--leanflow-src DIR] [--hf-dir DIR]
Defaults: --bin /home/callensxavier_gmail_com/rusty-target-ar/release (build it with
  CARGO_TARGET_DIR=... cargo build --release -j 2 -p qf-popgen),
  --lean ~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean, --leanflow-src ~/LeanFlow-wt-p1/src.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from fractions import Fraction
from pathlib import Path

HOME = Path("/home/callensxavier_gmail_com")
REPO = "katarinagresova/Genomic_Benchmarks_demo_coding_vs_intergenomic_seqs"
REV = "85458172cab6cffad46cb172e64ca94780506ed6"
TEST_FILE = "data/test-00000-of-00001-6fccc31405110e30.parquet"
TEST_SHA = "dfe13715a0227204cbae1ff6a167b2138337b749ca4f748da7c5a838a0049afe"
FIG = Path(__file__).resolve().parent.parent / "figures" / "ch5_U5_fixation.pdf"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dataset_stats(hf_dir: Path) -> dict:
    """Download (if missing) the pinned test split and compute plain sequence statistics."""
    local = hf_dir / TEST_FILE
    if not local.is_file():
        local.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/datasets/{REPO}/resolve/{REV}/{TEST_FILE}"
        local.write_bytes(urllib.request.urlopen(url, timeout=120).read())
    digest = sha256(local)
    if digest != TEST_SHA:
        raise SystemExit(f"sha256 mismatch for {local}: {digest}")
    import pyarrow.parquet as pq

    tab = pq.read_table(local).to_pydict()
    per: dict[int, dict] = {}
    for seq, lab in zip(tab["seq"], tab["label"]):
        d = per.setdefault(int(lab), {"n": 0, "len_min": 10**9, "len_max": 0, "gc": 0, "acgt": 0, "other": 0})
        s = seq.upper()
        d["n"] += 1
        d["len_min"] = min(d["len_min"], len(s))
        d["len_max"] = max(d["len_max"], len(s))
        gc = s.count("G") + s.count("C")
        acgt = gc + s.count("A") + s.count("T")
        d["gc"] += gc
        d["acgt"] += acgt
        d["other"] += len(s) - acgt
    out = {}
    for lab, d in sorted(per.items()):
        out[str(lab)] = {"n": d["n"], "len_min": d["len_min"], "len_max": d["len_max"],
                         "gc_fraction": d["gc"] / d["acgt"], "non_acgt_symbols": d["other"]}
    # per-sequence GC fractions for the histogram
    gcs: dict[str, list[float]] = {"0": [], "1": []}
    for seq, lab in zip(tab["seq"], tab["label"]):
        s = seq.upper()
        acgt = sum(s.count(c) for c in "ACGT")
        gcs.setdefault(str(int(lab)), []).append((s.count("G") + s.count("C")) / max(acgt, 1))
    return {"repo": REPO, "revision": REV, "file": TEST_FILE, "sha256": digest, "rows": len(tab["seq"]),
            "per_label": out, "license_on_card": None, "_gc_lists": gcs}


def moran_fix(n: int, r: Fraction, i: int) -> Fraction:
    """Exact S_i / S_N with S_m = sum_{k<m} r^-k (equals i/N when r = 1)."""
    s = lambda m: sum((Fraction(1) / r) ** k for k in range(m))  # noqa: E731
    return s(i) / s(n)


def run_cvode(bin_dir: Path, out: Path) -> tuple[dict, list[dict]]:
    res = out / "qf_popgen"
    res.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([str(bin_dir / "fixation_ode"), str(res)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"fixation_ode exited {proc.returncode}: {proc.stdout} {proc.stderr}")
    summary = json.loads((res / "summary.json").read_text())
    rows = [json.loads(line) for line in (res / "results.jsonl").read_text().splitlines() if line.strip()]
    return summary, rows


def certify_all(rows: list[dict], lean: Path, leanflow_src: Path) -> dict:
    sys.path.insert(0, str(leanflow_src))
    from leanflow_mcp.lean import LeanConfig, certify  # noqa: PLC0415

    cfg = LeanConfig(lean_cmd=(str(lean),), timeout_s=300)
    row = next(r for r in rows if r["label"] == "control_lean_N3_r2" and r["i"] == 1)
    literal = repr(float(row["p_fix"]))  # shortest decimal that round-trips the f64 printed by the binary
    target = moran_fix(3, Fraction(2), 1)
    assert target == Fraction(4, 7)

    def closeness(name: str, rhs_lo: str, rhs_hi: str) -> dict:
        return {"name": name, "tactic": "decide_kernel",
                "enclosures": {"p": [literal, literal]},
                "assertions": [{"label": "p.lo > lower", "endpoint": "p.lo", "op": ">", "rhs": rhs_lo},
                               {"label": "p.hi < upper", "endpoint": "p.hi", "op": "<", "rhs": rhs_hi}]}

    eps = Fraction(1, 10**11)
    tight = Fraction(1, 10**14)
    claims = {
        "pos_cvode_within_1e-11_of_4_7": closeness("cvodeN3", str(target - eps), str(target + eps)),
        "neg_neutral_1_3": closeness("neutralN3", str(Fraction(1, 3) - eps), str(Fraction(1, 3) + eps)),
        "neg_too_tight_1e-14": closeness("tightN3", str(target - tight), str(target + tight)),
    }
    # Harmonic (first-step) equations of the Moran chain N = 3, r = 2: p_i (x_{i+1} - x_i) + q_i (x_{i-1} - x_i) = 0.
    n, r = 3, Fraction(2)
    up = {i: r * i / (r * i + n - i) * Fraction(n - i, n) for i in (1, 2)}
    down = {i: Fraction(n - i) / (r * i + n - i) * Fraction(i, n) for i in (1, 2)}

    def harmonic(name: str, x: list[Fraction]) -> dict:
        enc = {f"x{k}": [str(v), str(v)] for k, v in enumerate(x)}
        asr = [{"label": "x0 == 0", "endpoint": "x0.lo", "op": "==", "rhs": "0"},
               {"label": "x3 == 1", "endpoint": "x3.lo", "op": "==", "rhs": "1"}]
        for i in (1, 2):
            asr.append({"label": f"harmonic at i={i}",
                        "terms": [[str(up[i]), f"x{i + 1}.lo"], [str(down[i]), f"x{i - 1}.lo"],
                                  [str(-(up[i] + down[i])), f"x{i}.lo"]],
                        "op": "==", "rhs": "0"})
        return {"name": name, "tactic": "decide_kernel", "enclosures": enc, "assertions": asr}

    claims["pos_harmonic_moran_N3_r2"] = harmonic("harmN3", [moran_fix(3, r, i) for i in range(4)])
    claims["neg_harmonic_neutral_i_over_N"] = harmonic("harmNeutral", [Fraction(i, 3) for i in range(4)])
    out = {"literal": literal, "p_fix_jsonl": row["p_fix"], "target": str(target),
           "abs_err": float(abs(Fraction(literal) - target)), "up": {k: str(v) for k, v in up.items()},
           "down": {k: str(v) for k, v in down.items()}, "results": {}}
    for key, claim in claims.items():
        res = certify(claim, cfg)
        out["results"][key] = {"status": res.status, "code": res.code, "tier": res.tier, "verified": res.verified,
                               "failed": list(res.failed), "seconds": res.seconds, "lean_version": res.lean_version,
                               "axioms": {k: v.get("axioms") for k, v in res.axioms.items()},
                               "statement": res.statement}
    exp = {"pos_cvode_within_1e-11_of_4_7": "ok", "pos_harmonic_moran_N3_r2": "ok", "neg_neutral_1_3": "rejected",
           "neg_too_tight_1e-14": "rejected", "neg_harmonic_neutral_i_over_N": "rejected"}
    out["all_as_expected"] = all(out["results"][k]["status"] == v for k, v in exp.items())
    return out


def figure(rows: list[dict], gcs: dict[str, list[float]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    col = {"0.8": "#eb6834", "1": "#52514e", "1.5": "#2a78d6"}
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.4))
    for lab, r in (("moran_N10_r0.8", Fraction(4, 5)), ("moran_N10_neutral", Fraction(1)), ("moran_N10_r1.5", Fraction(3, 2))):
        pts = [(x["i"], x["p_fix"]) for x in rows if x["label"] == lab and x["verdict"] == "accepted"]
        key = {Fraction(4, 5): "0.8", Fraction(1): "1", Fraction(3, 2): "1.5"}[r]
        xs = [k / 10 for k in range(11)]
        ax[0].plot(xs, [float(moran_fix(10, r, k)) for k in range(11)], color=col[key], lw=1.5,
                   label=f"exact, r = {key}")
        ax[0].plot([p[0] / 10 for p in pts], [p[1] for p in pts], "o", ms=5, mfc="white", mec=col[key])
    ax[0].set_xlabel("fréquence initiale i/N  (N = 10)")
    ax[0].set_ylabel("probabilité de fixation")
    ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_title("(a) CVODE (cercles) et formule exacte", fontsize=9)
    row = next(x for x in rows if x["label"] == "control_lean_N3_r2" and x["i"] == 1)
    t = [p[0] for p in row["trace"]]
    ax[1].semilogx(t, [p[1] for p in row["trace"]], "o-", color="#2a78d6", ms=5, lw=1.5, label="masse en N (fixation)")
    ax[1].semilogx(t, [p[2] for p in row["trace"]], "s-", color="#eb6834", ms=5, lw=1.5, label="masse intérieure")
    ax[1].axhline(4 / 7, color="#52514e", lw=1, ls="--")
    ax[1].text(t[0], 4 / 7 + 0.03, "4/7", fontsize=8, color="#52514e")
    ax[1].set_xlabel("temps (unités de pas de Moran)")
    ax[1].set_title("(b) N = 3, r = 2, i = 1", fontsize=9)
    ax[1].legend(frameon=False, fontsize=8)
    bins = [k / 50 for k in range(51)]
    ax[2].hist(gcs["0"], bins=bins, histtype="step", color="#2a78d6", lw=1.5, label="label 0")
    ax[2].hist(gcs["1"], bins=bins, histtype="step", color="#1baf7a", lw=1.5, label="label 1")
    ax[2].set_xlabel("fraction GC par séquence")
    ax[2].set_ylabel("nombre de séquences")
    ax[2].set_title("(c) Genomic Benchmarks (test, 25 000 seq.)", fontsize=9)
    ax[2].legend(frameon=False, fontsize=8)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--bin", type=Path, default=HOME / "rusty-target-ar" / "release")
    ap.add_argument("--lean", type=Path, default=HOME / ".elan/toolchains/leanprover--lean4---v4.34.1/bin/lean")
    ap.add_argument("--leanflow-src", type=Path, default=HOME / "LeanFlow-wt-p1" / "src")
    ap.add_argument("--hf-dir", type=Path,
                    default=HOME / "hf-data/textbook2/genomic_benchmarks_demo_coding_vs_intergenomic_seqs")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    data = dataset_stats(a.hf_dir)
    gcs = data.pop("_gc_lists")
    summary, rows = run_cvode(a.bin, a.out)
    acc = [x for x in rows if x["verdict"] == "accepted" and x["kind"] != "negative_control"]
    exact_err = max(float(abs(Fraction(x["p_fix"]) - moran_fix(x["N"], Fraction(str(x["r"])), x["i"])))
                    for x in acc if x["kind"] == "moran")
    cert = certify_all(rows, a.lean, a.leanflow_src)
    figure(rows, gcs)
    result = {"dataset": data, "cvode_summary": summary,
              "max_abs_err_cvode_vs_exact_fraction_moran": exact_err,
              "refused_controls": [(x["label"], x["i"], x["reason"][:60]) for x in rows if x["verdict"] == "refused"],
              "leanflow": cert, "figure": str(FIG)}
    (a.out / "ch5_U5_result.json").write_text(json.dumps(result, indent=1))
    print(json.dumps({"rows": summary["rows"], "accepted": summary["accepted"], "refused": summary["refused"],
                      "max_err_vs_exact": exact_err, "dataset_rows": data["rows"], "per_label": data["per_label"],
                      "leanflow": {k: v["status"] for k, v in cert["results"].items()},
                      "leanflow_all_as_expected": cert["all_as_expected"], "literal": cert["literal"]}, indent=1))
    if summary["controls_or_runs_not_as_expected"] != 0 or not cert["all_as_expected"]:
        sys.exit(1)


if __name__ == "__main__":
    os.environ.setdefault("MPLBACKEND", "Agg")
    main()
