"""Figure c18 (Z-GWAYA): the 26 labelled cases of the GWAYA v3 gate, and a live replay of the 1 = 2 demonstration.

Data: results/gwaya_v3_oracle_eval.json from the Zenodo bundle gwaya_v3_repro_bundle.tar.gz of doi:10.5281/zenodo.23119953,
copied unchanged to papers/discovery_journal_2026/data/zenodo23119953_gwaya_v3_oracle_eval.json (sha256 asserted).
No code from the bundle is executed: the JSON is only read.
The figure counts, per group of cases, how many verdicts were right and wrong (computed from the per-case rows) and
asserts the published totals: in scope 24 cases, 8 true accepts, 16 true rejects, 0 errors; 2 blind-spot cases (code
that subtracts instead of adding) both falsely accepted.

Live replay (our own run, not GWAYA's code): the Lean file of the report's section 2.3 is written to a temporary
directory and compiled with the local `lean`; the script asserts exit status 0 and that `#print axioms` names the
hidden axiom `bad`. Output is printed so the chapter can quote it.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig18.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "papers" / "discovery_journal_2026"
OUT = BOOK / "figures"
DATA = BOOK / "data" / "zenodo23119953_gwaya_v3_oracle_eval.json"
SHA = "ba2712798d94fb4ff14dc85b9c96b061f1c1e10c1bc56d5aa6fe9066c64c4b0c"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
LEAN_DEMO = 'def s : String := "--" axiom bad : False\ntheorem t : 1 = 2 := bad.elim\n#print axioms t\n'
GROUPS = [("valid", "programmes et preuves corrects"), ("stub", "bouche-trous (pass, ..., mock)"),
          ("empty", "vides ou seulement des commentaires"), ("syntax", "fautes de syntaxe"),
          ("type", "fautes de type ou énoncé faux"), ("escape", "échappatoires Lean (sorry, axiome...)"),
          ("regression", "cas de régression"), ("limitation", "angle mort : bug de sens")]


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42, "mathtext.fontset": "dejavuserif"})


def lean_replay() -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "OneEqTwo.lean"
        f.write_text(LEAN_DEMO, encoding="utf-8")
        res = subprocess.run(["lean", str(f)], cwd=tmp, capture_output=True, text=True, timeout=300)
        return res.returncode, (res.stdout + res.stderr).strip()


def main() -> None:
    style()
    raw = DATA.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    d = json.loads(raw)
    cases = d["cases"]
    assert len(cases) == 26
    ins = [c for c in cases if c["tag"] != "limitation"]
    lim = [c for c in cases if c["tag"] == "limitation"]
    ta = sum(c["accepted"] and c["label"] == "accept" for c in ins)
    tr = sum((not c["accepted"]) and c["label"] == "reject" for c in ins)
    fa = sum(c["accepted"] and c["label"] == "reject" for c in ins)
    fr = sum((not c["accepted"]) and c["label"] == "accept" for c in ins)
    assert (len(ins), ta, tr, fa, fr) == (24, 8, 16, 0, 0) == (d["in_scope"]["n"], d["in_scope"]["true_accept"],
                                                              d["in_scope"]["true_reject"], d["in_scope"]["false_accept"],
                                                              d["in_scope"]["false_reject"])
    assert len(lim) == 2 and all(c["accepted"] for c in lim)
    assert all(c["deterministic"] for c in cases) and d["repeats_per_case"] == 5
    print(f"in scope: n={len(ins)} TA={ta} TR={tr} FA={fa} FR={fr}; blind spots accepted: {[c['id'] for c in lim]}")

    rc, out = lean_replay()
    print("lean replay exit code:", rc)
    print("lean replay output:", out)
    assert rc == 0 and "bad" in out and "depends on axioms" in out

    labels, ok_acc, ok_rej, wrong = [], [], [], []
    for tag, lab in GROUPS:
        g = [c for c in cases if c["tag"] == tag]
        assert g, tag
        labels.append(f"{lab} ({len(g)})")
        ok_acc.append(sum(c["correct"] and c["accepted"] for c in g))
        ok_rej.append(sum(c["correct"] and not c["accepted"] for c in g))
        wrong.append(sum(not c["correct"] for c in g))
    assert sum(ok_acc) + sum(ok_rej) + sum(wrong) == 26 and sum(wrong) == 2

    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    y = list(range(len(labels)))[::-1]
    ax.barh(y, ok_acc, color=OKABE["vert"], label="accepté à raison")
    ax.barh(y, ok_rej, left=ok_acc, color=OKABE["bleu"], label="refusé à raison")
    ax.barh(y, wrong, left=[a + b for a, b in zip(ok_acc, ok_rej)], color=OKABE["vermillon"],
            hatch="//", edgecolor=IVOIRE, label="accepté à tort")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("nombre de cas (chacun passé 5 fois, verdicts identiques)")
    ax.set_xticks(range(0, 8))
    ax.set_xlim(0, 7.4)
    ax.set_title("Le portail GWAYA v3 sur ses 26 cas d'essai (corpus écrit par l'auteur)", fontsize=9)
    ax.legend(fontsize=7, loc="lower right", frameon=False)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c18_portail.pdf", dpi=300)
    fig.savefig(OUT / "c18_portail.png", dpi=300)
    print("wrote", OUT / "c18_portail.pdf")


if __name__ == "__main__":
    main()
