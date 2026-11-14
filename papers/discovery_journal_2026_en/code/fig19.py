"""Figure c19 (G-AUTOEVOLVE): what the exit code says versus what the harness's axiom gate says.

Live run, 2026-10: five tiny import-free Lean files are compiled with the local `lean`, and each is gated by
anse/formal/lean_runner.py (LeanKernelVerifier.verify_file with lean_cmd=["lean"]), the harness's only sound Lean gate
(compile, then `#print axioms` per theorem, rejecting sorryAx and any axiom outside {propext, Classical.choice,
Quot.sound}). The five files:
  honest   : theorem honest (n : Nat) : n + 0 = n := rfl
  sorry    : theorem looks_fine (n : Nat) : n + 0 = n := by sorry       (unproved)
  axiom    : axiom cheat : False ; theorem one_eq_two : 1 = 2 := cheat.elim
  vacuous  : theorem grand_claim : True := trivial                      (says nothing)
  false    : theorem wrong : 1 = 2 := rfl                               (does not compile)
Asserted outcome: exit code 0 for the first four (a naive gate accepts them all); the gate rejects sorry and axiom,
rejects the non-compiling file, accepts honest -- and also accepts vacuous, which is the documented blind spot
(statement review is the only defence).
Run: .venv/bin/python -I papers/discovery_journal_2026_en/code/fig19.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402

OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
FILES = [
    ("honest", "honest proof\n$n+0=n$", "theorem honest (n : Nat) : n + 0 = n := rfl\n#print axioms honest\n"),
    ("sorry", "\"sorry\" hole\n$n+0=n$",
     "theorem looks_fine (n : Nat) : n + 0 = n := by sorry\n#print axioms looks_fine\n"),
    ("axiom", "hidden axiom\n$1=2$",
     "axiom cheat : False\ntheorem one_eq_two : 1 = 2 := cheat.elim\n#print axioms one_eq_two\n"),
    ("vacuous", "empty statement\n\"True\"", "theorem grand_claim : True := trivial\n#print axioms grand_claim\n"),
    ("false", "false statement\n$1=2$ by rfl", "theorem wrong : 1 = 2 := rfl\n#print axioms wrong\n"),
]
EXPECT = {"honest": (0, True), "sorry": (0, False), "axiom": (0, False), "vacuous": (0, True), "false": (1, False)}


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "pdf.fonttype": 42, "mathtext.fontset": "dejavuserif"})


def main() -> None:
    style()
    results: dict[str, tuple[int, bool, str]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        verifier = LeanKernelVerifier(formal_dir=Path(tmp), lean_cmd=["lean"])
        for key, _lab, src in FILES:
            f = Path(tmp) / f"Demo_{key}.lean"
            f.write_text(src, encoding="utf-8")
            rc = subprocess.run(["lean", str(f)], cwd=tmp, capture_output=True, text=True, timeout=300).returncode
            gate = verifier.verify_file(f, timeout_s=300)
            clean = bool(gate) and all(r.compiled_successfully and not r.has_sorry and not r.untrusted_axioms
                                       for r in gate)
            axioms = "; ".join(f"{r.theorem_name}: {r.axioms}" for r in gate)
            results[key] = (rc, clean, axioms)
            print(f"{key:8s} exit={rc}  gate={'ACCEPT' if clean else 'REJECT'}  axioms={axioms}")
    for key, (rc, clean) in EXPECT.items():
        assert results[key][0] == rc, (key, results[key])
        assert results[key][1] == clean, (key, results[key])

    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    rows = [("The compiler\n(exit code 0?)", lambda k: results[k][0] == 0),
            ("The test bench gate\n(axiom audit)", lambda k: results[k][1])]
    for j, (key, lab, _src) in enumerate(FILES):
        ax.text(j + 0.5, 2.15, lab, ha="center", va="bottom", fontsize=7.5)
        for i, (_rl, fn) in enumerate(rows):
            ok = fn(key)
            col = OKABE["vert"] if ok else OKABE["vermillon"]
            ax.add_patch(Rectangle((j + 0.06, 1 - i + 0.08), 0.88, 0.84, color=col))
            ax.text(j + 0.5, 1 - i + 0.5, "accepts" if ok else "rejects", ha="center", va="center",
                    color="white", fontsize=8.5, fontweight="bold")
    for i, (rl, _fn) in enumerate(rows):
        ax.text(-0.08, 1 - i + 0.5, rl, ha="right", va="center", fontsize=8)
    ax.text(3.5, -0.12, "accepted although it says nothing:\nonly a reading of the statement sees it",
            ha="center", va="top", fontsize=7, color=OKABE["noir"], style="italic")
    ax.set_xlim(-1.6, 5.05)
    ax.set_ylim(-0.6, 2.75)
    ax.axis("off")
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "c19_portail.pdf", dpi=300)
    fig.savefig(OUT / "c19_portail.png", dpi=300)
    print("wrote", OUT / "c19_portail.pdf")


if __name__ == "__main__":
    main()
