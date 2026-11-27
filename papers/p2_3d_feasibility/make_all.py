"""Generate gen_numbers.tex and fig/*.pdf for the B3 feasibility preprint from data/ and code/ JSON only.

Every number below is read from results copied from results/proposal2/2026-10-26/B3/, except (i) the Muratov-Novaga margin quoted
from their eq. (11) and (ii) the 2D lattice energies W_tri, W_square, which are typed constants in code/n1_energies.py and
code/n3_green_obstruction.py (source: the manuscript normalization as quoted in the P1 audit; not recomputed here).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I make_all.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
CODE = HERE / "code"
FIG = HERE / "fig"
FIG.mkdir(exist_ok=True)

N1 = json.loads((CODE / "n1_energies.json").read_text())
N2 = json.loads((CODE / "n2_voronoi.json").read_text())
N3 = json.loads((CODE / "n3_green_obstruction.json").read_text())
N3B = json.loads((CODE / "n3b_cubic.json").read_text())
RES = json.loads((HERE / "data" / "result.json").read_text())

BLUE, VERM, GREY, INK, GREEN = "#0072B2", "#D55E00", "#8a8a8a", "#222222", "#009E73"
plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 7.5, "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "lines.linewidth": 1.2, "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "figure.dpi": 150, "pdf.fonttype": 42,
})


def sci(x: float, d: int = 3) -> str:
    """LaTeX scientific notation, e.g. 1.059\\times10^{-4}."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    if abs(round(m, d) - 10) < 1e-12:
        m, e = 1.0, e + 1
    return f"{m:.{d}f}\\times10^{{{e}}}"


def fix(x: float, d: int) -> str:
    return f"{x:.{d}f}"


S = N3["bcc_bounds_replicates"]
gap = N1["structures"]["fcc"]["gap_above_bcc"]  # computed by n1 (the n3 script carries a hand-typed 8.969424e-05; not used)
e_bcc = N1["structures"]["bcc"]["e_per_particle"]
gap_hcp = N1["structures"]["hcp"]["gap_above_bcc"]
rad = N3["radial_lb_mean"]
axc = N3["axial_lb_combined_mean"]
hier = N3["hier_lb_mean"]
azi = N3["axial_lb_mean"]
axh = N3["axial_lb_hex_share_mean"]
axs = N3["axial_lb_square_share_mean"]
tr_h = N3["face_traces"]["hex"]["circles"]
tr_s = N3["face_traces"]["square"]["circles"]
ws = N3["positive_control_ws_radial_field"]
d2 = N3["two_d_reference"]
n_sigma_hier = hier / (sum(r["hier_lb_mc_se"] for r in S) / len(S))
n_sigma_axc = axc / (sum(r["axial_lb_mc_se"] for r in S) / len(S))
off_modes_hex = max(v for c in tr_h for k, v in c["fourier_amplitudes"].items() if k != "6")
off_modes_sq = max(v for c in tr_s for k, v in c["fourier_amplitudes"].items() if k not in ("4", "8"))
mn_margin = 1.7938403e-4  # quoted from Muratov-Novaga arXiv:2610.29732 eq. (11); compared with 2*gap below

# certificate-size estimate (assumptions (a)-(d) of the text)
nodes2d = 2184 * 3611
ratio_margin = 8.0e-3 / 6.2e-5
refine = math.sqrt(ratio_margin)
n1d = 2808 * refine
nodes3d = n1d ** 3
tot2d = nodes2d + 2.4e6 + 4.2e5  # outer + Hessian + global-derivative meshes of the 2D record
core_s_per_node = 2.3e3 / tot2d
core_years = nodes3d * core_s_per_node / (3600 * 24 * 365.25)
nodes5d = n1d ** 5

mac = {
    "EBcc": fix(e_bcc, 7), "GapFcc": sci(gap, 3), "GapHcp": sci(gap_hcp, 3),
    "RelGapFcc": sci(N1["structures"]["fcc"]["rel_gap_above_bcc"], 2),
    "SlackRadial": sci(rad, 3), "SlackAxial": sci(axc, 3), "SlackHier": sci(hier, 3), "SlackAzi": sci(azi, 3),
    "SlackAxHex": sci(axh, 3), "SlackAxSq": sci(axs, 3),
    "RatioRadial": fix(rad / gap, 1), "RatioAxial": fix(axc / gap, 2),
    "RatioHier": fix(hier / gap, 2), "RatioAxialHcp": fix(axc / gap_hcp, 2),
    "NSigmaHier": fix(n_sigma_hier, 0), "NSigmaAx": fix(n_sigma_axc, 0),
    "SeedAxA": sci(S[0]["axial_lb_combined"], 4), "SeedAxB": sci(S[1]["axial_lb_combined"], 4),
    "SeedHierA": sci(S[0]["hier_lb"], 4), "SeedHierB": sci(S[1]["hier_lb"], 4),
    "WSAx": sci(ws["axial_lb_combined"], 1), "WSRad": sci(ws["radial_lb"], 1), "WSHier": sci(ws["hier_lb"], 1),
    "LapFD": fix(N3["laplacian_fd_off_site"]["value"], 4), "LapExp": fix(N3["laplacian_fd_off_site"]["expected"], 4),
    "GradDev": sci(N3["gradient_fd_max_abs_dev"], 1),
    "HexA": sci(tr_h[0]["trace_max_minus_min"], 2), "HexB": sci(tr_h[1]["trace_max_minus_min"], 2),
    "HexC": sci(tr_h[2]["trace_max_minus_min"], 2), "HexSixC": sci(tr_h[2]["fourier_amplitudes"]["6"], 2),
    "SqFourC": sci(tr_s[2]["fourier_amplitudes"]["4"], 2),
    "OffHex": sci(off_modes_hex, 1), "OffSq": sci(off_modes_sq, 1),
    "CFour": fix(N3B["bcc"]["c4"], 2), "CFourFcc": fix(N3B["fcc"]["c4"], 2), "CFourSc": fix(N3B["sc"]["c4"], 2),
    "CReg": fix(N3B["bcc"]["C_regular"], 5), "TwoMad": fix(N3B["bcc"]["two_times_madelung"], 5),
    "DRadTwoD": sci(d2["radial_lb_2d"], 2), "DGapTwoD": fix(d2["gap_square_minus_tri_2d"], 5),
    "DRatioTwoD": fix(d2["ratio_radial_lb_over_gap_2d"], 3),
    "TwoGap": sci(2 * gap, 4), "MNMargin": sci(mn_margin, 4),
    "NodesTwoD": sci(nodes2d, 2), "MarginRatio": fix(ratio_margin, 0), "Refine": fix(refine, 1),
    "NodesThreeD": sci(nodes3d, 1), "CoreYears": fix(core_years, 0), "NodesFiveD": sci(nodes5d, 1),
    "EpsPerNode": sci(core_s_per_node, 1),
    "NEulerCfg": str(sum(1 for v in N2.values() if abs(v["mean_euler_weight"] - 12) < 1e-9)),
    "NCfgAll": str(len(N2)),
    "AlphaSpread": sci(max(v["alpha_spread"] for v in N1["structures"].values()), 1),
    "MadDev": sci(max(N1["structures"][k]["abs_dev_from_literature"] for k in ("bcc", "fcc", "hcp")), 1),
    "MadDevSc": sci(N1["structures"]["sc"]["abs_dev_from_literature"], 1),
    "NegSpread": fix(N1["negative_control_no_background"]["spread"], 2),
}

# every simple-cell Euler weight over all 32 configurations: those whose mean differs from 12
non12 = {k: v["mean_euler_weight"] for k, v in N2.items() if abs(v["mean_euler_weight"] - 12) > 1e-9}
mac["NNotTwelve"] = str(len(non12))
mac["HcpArtifact"] = fix(N2["hcp_pert_amp0.002_seed1"]["mean_euler_weight"], 4)
# face counts for the table
rows = []
order = [("bcc", "bcc"), ("fcc", "fcc"), ("hcp", "hcp"), ("A15", "A15 (Weaire--Phelan)"), ("C15", "C15"), ("sc", "sc"),
         ("fcc_pert_amp0.002_seed1", r"fcc, perturbed (rms amplitude 0.002, seed 1)"),
         ("poisson400_seed1", r"Poisson, $N=400$, seed 1")]
for key, label in order:
    v = N2[key]
    base = key.split("_")[0].replace("poisson400", "poisson")
    gap_k = v["e_per_particle"] - e_bcc
    egap = "--" if key.startswith("poisson") else (f"${sci(gap_k, 2)}$" if gap_k > 1e-12 else "0")
    rows.append(f"{label} & {v['N']} & {egap} & {v['mean_faces']:.2f} & {v['mean_euler_weight']:.2f} & {v['G_site']:.7f}\\\\")
(HERE / "gen_numbers.tex").write_text(
    "% generated by make_all.py from code/*.json; do not edit\n"
    + "".join(f"\\newcommand{{\\B{k}}}{{{v}}}\n" if k in ("NNotTwelve", "NEulerCfg", "NCfgAll")
              else f"\\newcommand{{\\B{k}}}{{\\ensuremath{{{v}}}}}\n" for k, v in mac.items())
    + "\\newcommand{\\BTableConfigs}{%\n" + "\n".join(rows) + "}\n")

# ---------------------------------------------------------------- figure 1: face traces
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.3))
xs = [c["rho_over_inradius"] for c in tr_h]
ax[0].semilogy(xs, [c["fourier_amplitudes"]["6"] for c in tr_h], "o-", color=VERM, label=r"hex face, $\cos6\psi$")
ax[0].semilogy([c["rho_over_inradius"] for c in tr_s], [c["fourier_amplitudes"]["4"] for c in tr_s], "s-", color=BLUE,
               label=r"square face, $\cos4\psi$")
ax[0].semilogy([c["rho_over_inradius"] for c in tr_s], [max(c["fourier_amplitudes"]["8"], 1e-12) for c in tr_s], "s:", color=GREY,
               label=r"square face, $\cos8\psi$")
ax[0].set_xlabel(r"$\rho/$inradius of the face (circle at fixed $t$)")
ax[0].set_ylabel("Fourier amplitude of trace")
ax[0].set_title("Trace on a circle of fixed $t$", loc="left")
ax[0].legend(frameon=False)
modes = [str(k) for k in range(1, 9)]
hexc = tr_h[2]["fourier_amplitudes"]
sqc = tr_s[2]["fourier_amplitudes"]
w = 0.38
ax[1].bar([i - w / 2 for i in range(8)], [max(hexc[m], 1e-18) for m in modes], w, color=VERM, label=r"hex face, $\rho=0.9$")
ax[1].bar([i + w / 2 for i in range(8)], [max(sqc[m], 1e-18) for m in modes], w, color=BLUE, label=r"square face, $\rho=0.9$")
ax[1].set_yscale("log")
ax[1].set_ylim(1e-18, 1e-1)
ax[1].set_xticks(range(8), modes)
ax[1].set_xlabel("azimuthal mode $m$ (amplitude of $\\cos m\\psi$)")
ax[1].set_title("Modes at $\\rho=0.9$ inradius", loc="left")
ax[1].legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "fig_traces.pdf")
plt.close(fig)

# ---------------------------------------------------------------- figure 2: forced slack by trial class
fig, ax = plt.subplots(figsize=(5.4, 2.7))
labels = ["3D radial", "3D axial\n(combined)", "3D hierarchical\n(piece-intrinsic)", "2D radial\n(vs square$-$tri gap)"]
vals = [rad / gap, axc / gap, hier / gap, d2["ratio_radial_lb_over_gap_2d"]]
cols = [GREY, VERM, VERM, BLUE]
ax.bar(range(4), vals, color=cols, width=0.6)
ax.set_yscale("log")
ax.set_ylim(1e-2, 1e2)
ax.axhline(1.0, color=INK, lw=0.8, ls="--")
ax.text(3.45, 1.08, "slack = gap", ha="right", fontsize=7)
for i, v in enumerate(vals):
    ax.text(i, v * 1.15, f"{v:.3g}", ha="center", fontsize=7.5)
ax.set_xticks(range(4), labels)
ax.set_ylabel("forced slack / competitor gap")
ax.set_title("forced slack relative to the competitor gap", loc="left")
fig.tight_layout()
fig.savefig(FIG / "fig_slack.pdf")
plt.close(fig)

# ---------------------------------------------------------------- figure 3: energy above bcc vs second moment G
fig, ax = plt.subplots(figsize=(5.0, 2.7))
pts = {"bcc": ("bcc", N1["structures"]["bcc"]["e_per_particle"]), "fcc": ("fcc", N1["structures"]["fcc"]["e_per_particle"]),
       "hcp": ("hcp", N1["structures"]["hcp"]["e_per_particle"]), "A15": ("A15", N1["structures"]["A15"]["e_per_particle"]),
       "C15": ("C15", N1["structures"]["C15"]["e_per_particle"]), "sc": ("sc", N1["structures"]["sc"]["e_per_particle"])}
for k, (lab, e) in pts.items():
    g = N2[k]["G_site"]
    ax.scatter(g, e - e_bcc + 1e-6, color=BLUE if k == "bcc" else VERM, s=22, zorder=3)
    ax.annotate(lab, (g, e - e_bcc + 1e-6), textcoords="offset points", xytext=(4, 4), fontsize=7)
ax.set_yscale("symlog", linthresh=1e-5)
ax.set_xlabel("dimensionless second moment $G$ of the Voronoi cell")
ax.set_ylabel("jellium energy above bcc (per particle) + $10^{-6}$")
ax.set_title("bcc is lowest in both $e$ and $G$", loc="left")
fig.tight_layout()
fig.savefig(FIG / "fig_energy_G.pdf")
plt.close(fig)
print("ok", len(mac), "macros")
