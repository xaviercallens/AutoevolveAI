"""Generate the figures, tables and macros of the P7 paper from the CVODE results (Tier X).

Inputs : ../data/results.jsonl (written by rusty-SUNDIALS crates/qf-popgen `fixation_ode`),
         ../data/numerics_fixation.json (mpmath matrix powers, WORK1).
Outputs: fig_fixation_vs_i.pdf, fig_convergence.pdf, fig_residuals.pdf, table_cvode.tex,
         gen_numbers.tex, independent_check.json.

Independent check: the Moran and Wright-Fisher kernels are rebuilt here in numpy (separate code from the
Rust constructors) and exp(t (P - I)) is evaluated with scipy.linalg.expm at the CVODE stopping time; the
CVODE absorption mass is compared with it. Nothing here supports a claim.

Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_all.py
"""
from __future__ import annotations

import json
from math import comb
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
rows = [json.loads(line) for line in (DATA / "results.jsonl").read_text().splitlines()]
acc = [r for r in rows if r["verdict"] == "accepted"]
ref = [r for r in rows if r["verdict"] == "refused"]

plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 150})
C = {"r0.8": "#1b6ca8", "r1": "#555555", "r1.5": "#c4492b", "wf": "#2a8a4a"}


def moran_np(n: int, r: float) -> np.ndarray:
    p = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        up = r * i / (r * i + n - i) * (n - i) / n
        dn = (n - i) / (r * i + n - i) * i / n
        if i < n:
            p[i, i + 1] = up
        if i > 0:
            p[i, i - 1] = dn
        p[i, i] = 1.0 - up - dn
    return p


def wf_np(n: int) -> np.ndarray:
    p = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        x = i / n
        for j in range(n + 1):
            p[i, j] = comb(n, j) * x**j * (1 - x) ** (n - j)
    return p


def moran_fix(n: int, r: float, i: int) -> float:
    return i / n if r == 1.0 else (1 - r ** (-i)) / (1 - r ** (-n))


def flipped(n: int, r: float, i: int) -> float:
    return (1 - r**i) / (1 - r**n)


# ---- independent check: scipy expm at the CVODE stopping time ----------------------------------
worst = 0.0
worst_by = {}
for r in acc:
    n, rr, i = r["N"], r["r"], r["i"]
    p = wf_np(n) if r["kind"] == "wright_fisher" else moran_np(n, rr)
    e = expm(r["t_stop"] * (p - np.eye(n + 1)))
    d = abs(e[i, n] - r["p_fix"])
    worst = max(worst, d)
    worst_by[r["label"]] = max(worst_by.get(r["label"], 0.0), d)
(HERE / "independent_check.json").write_text(
    json.dumps({"tier": "X", "max_abs_diff_cvode_vs_scipy_expm": worst, "by_label": worst_by}, indent=1)
)

# ---- figure 1: fixation probability vs i, N = 10 --------------------------------------------------
fig, ax = plt.subplots(figsize=(5.2, 3.3))
for lab, key, rr in [("moran_N10_r0.8", "r0.8", 0.8), ("moran_N10_neutral", "r1", 1.0), ("moran_N10_r1.5", "r1.5", 1.5)]:
    pts = sorted([x for x in acc if x["label"] == lab], key=lambda x: x["i"])
    ii = np.arange(0, 11)
    ax.plot(ii, [moran_fix(10, rr, int(k)) for k in ii], "-", color=C[key], lw=1.2,
            label=f"closed form (Lean), r = {rr:g}")
    ax.plot([x["i"] for x in pts], [x["p_fix"] for x in pts], "o", ms=4, color=C[key], mfc="none")
ii = np.arange(1, 10)
ax.plot(ii, [flipped(10, 1.5, int(k)) for k in ii], "--", color="#999999", lw=1.0,
        label="negative control: exponent-flipped, r = 1.5")
ax.set_xlabel("initial mutants i  (N = 10)")
ax.set_ylabel(r"absorption mass at N  (circles: CVODE)")
ax.legend(fontsize=6.5, loc="upper left")
fig.tight_layout()
fig.savefig(HERE / "fig_fixation_vs_i.pdf")
plt.close(fig)

# ---- figure 2: convergence in time ----------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0))
picks = [("moran_N10_r1.5", 1, "Moran r = 1.5, i = 1", C["r1.5"]),
         ("moran_N10_neutral", 3, "Moran r = 1, i = 3", C["r1"]),
         ("wf_neutral", 5, "Wright-Fisher, N = 10, i = 5", C["wf"])]
for lab, i0, name, col in picks:
    cand = [x for x in acc if x["label"] == lab and x["i"] == i0 and (lab != "wf_neutral" or x["N"] == 10)]
    x = cand[0]
    t = np.array([a[0] for a in x["trace"]])
    err = np.abs(np.array([a[1] for a in x["trace"]]) - x["target"])
    inter = np.array([a[2] for a in x["trace"]])
    axs[0].loglog(t, np.maximum(inter, 1e-18), "o-", ms=3, color=col, label=name)
    axs[1].loglog(t, np.maximum(err, 1e-18), "o-", ms=3, color=col, label=name)
axs[0].set_title("interior mass", fontsize=9)
axs[1].set_title(r"$|\pi_N(t) - h(i)|$", fontsize=9)
for a in axs:
    a.set_xlabel("t (uniformised time)")
axs[0].legend(fontsize=6)
fig.tight_layout()
fig.savefig(HERE / "fig_convergence.pdf")
plt.close(fig)

# ---- figure 3: residuals over all accepted runs ----------------------------------------------------
fig, ax = plt.subplots(figsize=(5.2, 3.0))
labels = [k for k in dict.fromkeys(x["label"] for x in acc)]
for k, lab in enumerate(labels):
    errs = [max(x["abs_err"], 1e-17) for x in acc if x["label"] == lab]
    ax.semilogy([k] * len(errs), errs, "o", ms=3, color="#1b6ca8")
ax.axhline(1e-8, color="#c4492b", ls="--", lw=1, label="acceptance tolerance 1e-8")
ax.set_xticks(range(len(labels)))
ax.set_xticklabels([l.replace("moran_", "").replace("control_lean_", "ctl_") for l in labels], rotation=35, ha="right", fontsize=6.5)
ax.set_ylabel("|CVODE - closed form|")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(HERE / "fig_residuals.pdf")
plt.close(fig)

# ---- table + macros --------------------------------------------------------------------------------
by = {}
for x in acc:
    by.setdefault(x["label"], []).append(x)
tex = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
       "run & $N$ & $r$ & starts & max $|$err$|$ & max interior & max $t_{\\rm stop}$ \\\\", "\\midrule"]
for lab, v in by.items():
    name = lab.replace("_", "\\_")
    ns = ", ".join(str(n) for n in sorted({a["N"] for a in v}))  # a label may pool several N (wf_neutral: 10 and 20)
    tex.append(f"\\texttt{{{name}}} & {ns} & {v[0]['r']:g} & {len(v)} & "
               f"${max(a['abs_err'] for a in v):.1e}$ & ${max(a['interior'] for a in v):.1e}$ & {max(a['t_stop'] for a in v):g} \\\\")
tex += ["\\bottomrule", "\\end{tabular}"]
(HERE / "table_cvode.tex").write_text("\n".join(tex) + "\n")

neg = []
for x in ref:
    lab_tex = x["label"].replace("_", "\\_")
    kind = x["reason"].split("{")[0].split("(")[0].strip()
    neg.append("\\texttt{" + lab_tex + "} & " + str(x["i"]) + " & \\texttt{" + kind + "} \\\\")
(HERE / "table_negative.tex").write_text(
    "\\begin{tabular}{lrl}\n\\toprule\ncontrol & start $i$ & refused as\\\\\n\\midrule\n" + "\n".join(neg) + "\n\\bottomrule\n\\end{tabular}\n")

maxerr = max(x["abs_err"] for x in acc)
maxint = max(x["interior"] for x in acc)
maxdrift = max(x["mass_drift"] for x in acc)
mincomp = min(x["min_component"] for x in acc)
nm = json.loads((DATA / "numerics_fixation.json").read_text())
mac = {
    "nRows": len(rows), "nAcc": len(acc), "nRef": len(ref),
    "maxErr": f"{maxerr:.1e}", "maxInterior": f"{maxint:.1e}", "maxDrift": f"{maxdrift:.1e}",
    "expmDiff": f"{worst:.1e}",
    "minComp": f"{mincomp:.1e}",
    "nMoranRuns": sum(1 for x in acc if x["kind"] == "moran"),
    "nWFRuns": sum(1 for x in acc if x["kind"] == "wright_fisher"),
}
(HERE / "gen_numbers.tex").write_text(
    "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
print(json.dumps(mac, indent=1))
