"""Figure for chapter 15 (English edition): rejeu par le noyau du corpus openai/NavierStokesAndEuler (doi:10.5281/zenodo.23661381).

(a) déclarations envoyées au noyau par fermeture, lues dans le tableau de rejeu de
papers/p2_navier_stokes_audit/main.tex, et auxiliaires sautés par conception, lus dans AUDIT.md.
(b) ce que chaque contrôle voit d'une fausse déclaration plantée (journaux de AUDIT.md, section R2).
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "p2_navier_stokes_audit"
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"
OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "blue": "#0072B2", "vermillion": "#D55E00", "grey": "#999999"}
IVORY = "#FFFFF0"


def to_int(s: str) -> int:
    return int(s.replace(",", ""))


def replay_table(tex: str) -> dict[str, tuple[int, int, int]]:
    out: dict[str, tuple[int, int, int]] = {}
    pat = re.compile(r"^(Navier--Stokes|Euler) & ([\d,]+) & ([\d,]+) & \\texttt\{REPLAY OK\} in ([\d,]+) ms, rc 0")
    for line in tex.splitlines():
        m = pat.match(line.strip())
        if m:
            out[m.group(1)] = (to_int(m.group(2)), to_int(m.group(3)), to_int(m.group(4)))
    return out


def skipped(audit: str) -> list[int]:
    return [int(x) for x in re.findall(r"AUDITREPLAY corpus_constants=\d+ \(unsafe_or_partial, skipped by Replay: (\d+)\)", audit)]


def main() -> None:
    tex = (REC / "main.tex").read_text(encoding="utf-8")
    audit = (REC / "AUDIT.md").read_text(encoding="utf-8")
    tab = replay_table(tex)
    assert set(tab) == {"Navier--Stokes", "Euler"}, tab
    ns, eu = tab["Navier--Stokes"], tab["Euler"]
    assert ns[1] + eu[1] == 88400
    assert ns[0] + eu[0] + 2 == 2440
    sk = skipped(audit)
    assert sk == [0, 12, 39], sk  # contrôle forgé (0), NS (12), Euler (39)
    sk_ns, sk_eu = sk[1], sk[2]
    # Ce que voient les trois contrôles, d'après les journaux R2 de AUDIT.md.
    seen_axioms = ("'AuditForgeUser.anything' does not depend on any axioms" in audit
                   and "'AuditForge.false_of_forge' does not depend on any axioms" in audit)
    lc_user_rc0 = "leanchecker AuditForgeUser rc=0" in audit
    lc_forge_rc1 = "leanchecker AuditForge rc=1" in audit
    replay_rej = "AUDITREPLAY RESULT REJECTED" in audit
    assert seen_axioms and lc_user_rc0 and lc_forge_rc1 and replay_rej

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 8.5})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.9), dpi=300, gridspec_kw={"width_ratios": [1, 1.25]})
    fig.patch.set_facecolor(IVORY)
    for ax in (ax1, ax2):
        ax.set_facecolor(IVORY)

    names = ["Navier–Stokes", "Euler"]
    decl = [ns[1], eu[1]]
    sks = [sk_ns, sk_eu]
    mins = [ns[2] / 60000.0, eu[2] / 60000.0]
    ax1.bar(names, decl, color=[OKABE["sky"], "#F0E442"], width=0.75)
    for i, (d, s, m, mod) in enumerate(zip(decl, sks, mins, [ns[0], eu[0]])):
        ax1.text(i, d + 1200, f"{d:,}", ha="center", fontsize=7.5)
        ax1.text(i, d / 2, f"{mod:,}" + " modules\n" + f"{m:.1f} min"
                 + "\n" + f"{s} auxiliary\ndeclarations skipped", ha="center", va="center", fontsize=6.2, color="black")
    ax1.set_ylim(0, 62000)
    ax1.set_yticks([0, 20000, 40000, 60000])
    ax1.set_yticklabels(["0", "20,000", "40,000", "60,000"])
    ax1.set_title("(a) declarations sent to the kernel", fontsize=8.5)
    ax1.set_xlim(-0.5, 1.5)
    for side in ("top", "right"):
        ax1.spines[side].set_visible(False)

    checks = ["axiom list", "module-by-module\nchecker", "full replay\nby the kernel"]
    cols = ["rigged module", "honest module\nthat imports it"]
    # True = la fausse déclaration est détectée.
    caught = [[not seen_axioms, not seen_axioms], [lc_forge_rc1, not lc_user_rc0], [replay_rej, replay_rej]]
    for i in range(len(checks)):
        for j in range(len(cols)):
            ok = caught[i][j]
            y = len(checks) - 1 - i
            ax2.add_patch(plt.Rectangle((j, y), 0.95, 0.9, color=OKABE["green"] if ok else OKABE["vermillion"], alpha=0.85))
            ax2.text(j + 0.475, y + 0.45, "caught" if ok else "goes\nunnoticed", ha="center", va="center",
                     fontsize=7.5, color="white")
    ax2.set_xlim(-0.05, len(cols))
    ax2.set_ylim(-0.05, len(checks))
    ax2.set_xticks([j + 0.475 for j in range(len(cols))])
    ax2.set_xticklabels(cols, fontsize=7)
    ax2.set_yticks([len(checks) - 1 - i + 0.45 for i in range(len(checks))])
    ax2.set_yticklabels(checks, fontsize=7)
    ax2.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax2.spines[side].set_visible(False)
    ax2.set_title("(b) a planted false proof of \"2 = 3\"", fontsize=8.5)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c15_rejeu.{ext}", dpi=300, facecolor=IVORY)
    print("table:", tab, "skipped:", sk, "minutes:", [round(m, 1) for m in mins])


if __name__ == "__main__":
    main()
