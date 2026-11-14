"""Extract verbatim Lean statements (no proof bodies) with their source line numbers into listings/*.lean.

Usage: python -I make_listings.py
Each output file starts with a comment giving the source path, its sha256 and the line range of every block, so a
reader can check the excerpt against the compiled file. Statements end at the first ':= by' or trailing ':='.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
FLOW = W / "results/autoresearch/2026-10-25/H7/contribution/Autoresearch_EnstrophyFlow.lean"
CTL = W / "results/autoresearch/2026-10-25/H7/contribution/Autoresearch_EnstrophyFlowControls.lean"
QF = Path("/mnt/disks/disk-socrateai-local-1/leanmaster/SocrateAI-Scientific-QuantumFluids/lean_src")
OUT = HERE / "listings"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def statement(lines: list[str], name: str) -> tuple[int, int, list[str]]:
    """Return (first line, last line, text) of the declaration `name`, cut at its ':='."""
    start = next(i for i, l in enumerate(lines) if l.split("(")[0].split(":")[0].split()[-1:] == [name]
                 and (l.startswith("theorem ") or l.startswith("noncomputable def ") or l.startswith("def ")))
    out = []
    for j in range(start, len(lines)):
        l = lines[j]
        if l.strip().startswith("| "):  # proof by pattern matching: the statement ended on the previous line
            out[-1] = out[-1] + " := ..."
            return start + 1, j, out
        if ":= by" in l:
            out.append(l.split(":= by")[0].rstrip() + " := ...")
            return start + 1, j + 1, out
        if l.rstrip().endswith(":="):
            out.append(l.rstrip() + " ...")
            return start + 1, j + 1, out
        out.append(l.rstrip())
    raise SystemExit(f"no end for {name}")


def block(src: Path, names: list[str], full_defs: list[str], out: Path) -> None:
    lines = src.read_text().splitlines()
    body = [f"-- {src.name}  sha256 {sha(src)}"]
    for n in names:
        if n in full_defs:  # definitions are shown with their bodies, up to the next blank line
            a = next(i for i, l in enumerate(lines) if l.startswith(("noncomputable def ", "def "))
                     and l.split()[2 if l.startswith("noncomputable") else 1] == n) + 1
            j = a
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("theorem", "/--", "noncomputable", "/-!")):
                j += 1
            txt, b = [l.rstrip() for l in lines[a - 1:j]], j
        else:
            a, b, txt = statement(lines, n)
        body.append(f"-- lines {a}-{b}")
        body.extend(txt)
    out.write_text("\n".join(body) + "\n")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    block(FLOW, ["kk", "energy", "enstrophy", "ham3", "F", "R", "hamG", "dHam"],
          ["kk", "energy", "enstrophy", "ham3", "F", "R", "hamG", "dHam"], OUT / "defs.lean")
    block(FLOW, ["enstrophy_bound", "cross_weights_ok", "rate_zero", "ham_rate_zero", "energy_rate_zero",
                 "hasDerivAt_hamG", "const_on_Icc", "ham_conserved"], [], OUT / "algebra.lean")
    block(FLOW, ["enstrophy_bound_along_flow", "enstrophy_le_along_flow", "zero_trajectory_is_solution"], [],
          OUT / "flow.lean")
    block(FLOW, ["rate_v11_correct", "rate_v11_wrong_weight", "rate_v111_no_truncation"], [], OUT / "sens.lean")
    block(QF / "QuantumFluidsShell.lean", ["shellBc"], ["shellBc"], OUT / "owner_shell.lean")
    block(QF / "ShellHamiltonian.lean", ["weights_ok", "cubic_bound", "dispersive_norm_le"], [],
          OUT / "owner_ham.lean")
    flow_lines = FLOW.read_text().splitlines()
    for n in ["re_conj_mul_F", "re_B_zero", "re_B_succ", "energy_rate_zero", "dT_F", "quad_tel", "cross_weights_ok",
              "rate_zero", "ham_rate_zero", "hasDerivAt_hamG", "const_on_Icc", "ham_conserved", "energy_conserved",
              "enstrophy_bound", "enstrophy_bound_along_flow", "enstrophy_le_along_flow", "rate_v11_wrong_weight",
              "rate_v111_no_truncation", "zero_trajectory_is_solution"]:
        a, b, txt = statement(flow_lines, n)
        (OUT / f"st_{n}.lean").write_text(f"-- Autoresearch_EnstrophyFlow.lean lines {a}-{b}\n" + "\n".join(txt) + "\n")
    qh = (QF / "ShellHamiltonian.lean").read_text().splitlines()
    for n in ["weights_ok", "cubic_bound", "dispersive_norm_le"]:
        a, b, txt = statement(qh, n)
        (OUT / f"st_{n}.lean").write_text(f"-- owner ShellHamiltonian.lean lines {a}-{b}\n" + "\n".join(txt) + "\n")
    pr = (W / "results/autoresearch/2026-10-25/H7/Autoresearch_Enstrophy.lean").read_text().splitlines()
    a, b, txt = statement(pr, "drop_cubic_term_fails")
    (OUT / "st_drop_cubic_term_fails.lean").write_text(f"-- Autoresearch_Enstrophy.lean (prior round) lines {a}-{b}\n" + "\n".join(txt) + "\n")
    ctl = CTL.read_text().splitlines()
    i = next(k for k, l in enumerate(ctl) if l.startswith("theorem ctl_sorry"))
    j = next(k for k, l in enumerate(ctl) if l.startswith("theorem ctl_axiom"))
    keep = [f"-- {CTL.name}  sha256 {sha(CTL)}  lines {i + 1}-{j + 3}"] + [l.rstrip() for l in ctl[i:j + 3]]
    (OUT / "controls.lean").write_text("\n".join(keep) + "\n")
    print("listings:", sorted(p.name for p in OUT.glob("*.lean")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
