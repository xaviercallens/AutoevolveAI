"""Cut verbatim Lean listings and axiom-audit output from the real files into LaTeX fragments.

Nothing is retyped: every listing line is a byte copy of a line of the source file (statement lines up to and
including the line that holds `:=`, or a whole declaration up to the next blank line). Every non-ASCII code point
that appears is mapped through UNI to a \\DeclareUnicodeCharacter line in gen_unicode.tex; an unmapped code point
stops the script.

Usage: python -I gen_listings.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
FC = W / "formal_cert" / "Autoresearch"
H2 = W / "results" / "autoresearch" / "2026-10-25" / "H2"
D2SRC = W / "formal_cert" / "Triangular" / "AnyDensity.lean"
UPSTREAM_BASIC = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy/Basic.lean")
UPSTREAM_UNIV = UPSTREAM_BASIC.parent / "Universal.lean"
UPSTREAM_DEFS = UPSTREAM_BASIC.parent / "Definitions.lean"

UNI = {
    "κ": r"\ensuremath{\kappa}", "ρ": r"\ensuremath{\rho}", "ι": r"\ensuremath{\iota}", "φ": r"\ensuremath{\varphi}",
    "π": r"\ensuremath{\pi}", "α": r"\ensuremath{\alpha}", "√": r"\ensuremath{\surd}", "∑": r"\ensuremath{\Sigma}",
    "≤": r"\ensuremath{\le}", "≥": r"\ensuremath{\ge}", "≠": r"\ensuremath{\ne}", "⊤": r"\ensuremath{\top}",
    "∈": r"\ensuremath{\in}", "∉": r"\ensuremath{\notin}", "⁻": r"\ensuremath{^{-}}", "¹": r"\ensuremath{^{1}}",
    "•": r"\ensuremath{\bullet}", "ℝ": r"\ensuremath{\mathbb{R}}", "ℕ": r"\ensuremath{\mathbb{N}}",
    "ℤ": r"\ensuremath{\mathbb{Z}}", "₁": r"\ensuremath{_1}", "₂": r"\ensuremath{_2}", "ᵢ": r"\ensuremath{_i}",
    "→": r"\ensuremath{\to}", "∀": r"\ensuremath{\forall}", "∃": r"\ensuremath{\exists}",
    "↔": r"\ensuremath{\leftrightarrow}", "⟨": r"\ensuremath{\langle}", "⟩": r"\ensuremath{\rangle}",
    "∧": r"\ensuremath{\wedge}", "∨": r"\ensuremath{\vee}", "¬": r"\ensuremath{\neg}", "∞": r"\ensuremath{\infty}",
    "·": r"\ensuremath{\cdot}", "‖": r"\ensuremath{\Vert}", "∩": r"\ensuremath{\cap}", "×": r"\ensuremath{\times}",
    "≥": r"\ensuremath{\ge}", "∘": r"\ensuremath{\circ}", "𝓝": r"\ensuremath{\mathcal{N}}", "≃": r"\ensuremath{\simeq}",
    "←": r"\ensuremath{\leftarrow}", "∂": r"\ensuremath{\partial}", "ℓ": r"\ensuremath{\ell}", "⦃": "{", "⦄": "}",
    "∅": r"\ensuremath{\emptyset}", "₀": r"\ensuremath{_0}", "∫": r"\ensuremath{\int}", "λ": r"\ensuremath{\lambda}",
    "≥": r"\ensuremath{\ge}", "∣": "|", "ⁿ": r"\ensuremath{^{n}}", "²": r"\ensuremath{^{2}}", "³": r"\ensuremath{^{3}}",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def statement(lines: list[str], name: str) -> list[str]:
    """Lines of `theorem/lemma/def name` up to and including the first line containing ':='."""
    for i, l in enumerate(lines):
        s = l.lstrip()
        if any(s.startswith(f"{k} {name} ") or s.startswith(f"{k} {name}\n") or s == f"{k} {name}"
               for k in ("theorem", "lemma", "def", "noncomputable def")):
            out = []
            for m in lines[i:]:
                out.append(m)
                if ":=" in m:
                    return out
    raise SystemExit(f"declaration {name} not found")


def whole(lines: list[str], name: str) -> list[str]:
    st = statement(lines, name)
    i = lines.index(st[0])
    out = []
    for m in lines[i:]:
        if not m.strip():
            break
        out.append(m)
    return out


def block(chunks: list[list[str]]) -> str:
    body = "\n\n".join("\n".join(c) for c in chunks)
    return "\\begin{Verbatim}[fontsize=\\scriptsize,frame=single,framesep=1.5mm]\n" + body + "\n\\end{Verbatim}\n"


def axiom_block(json_path: Path, keep: list[str] | None = None) -> str:
    out = json.loads(json_path.read_text())["output"]
    rows = []
    for l in out.splitlines():
        l = l.strip()
        if not l:
            continue
        if "warning: declaration uses `sorry`" in l:
            l = ".../" + l.split("/")[-1]
        if keep is None or any(k in l for k in keep):
            rows.append(l.replace("depends on axioms:", "->"))
    return "\\begin{Verbatim}[fontsize=\\scriptsize,frame=single,framesep=1.5mm]\n" + "\n".join(rows) + "\n\\end{Verbatim}\n"


def main() -> int:
    yk = (FC / "Yukawa.lean").read_text().splitlines()
    mix = (FC / "YukawaMix.lean").read_text().splitlines()
    basic = UPSTREAM_BASIC.read_text().splitlines()
    univ = UPSTREAM_UNIV.read_text().splitlines()
    defs = UPSTREAM_DEFS.read_text().splitlines()
    d2 = D2SRC.read_text().splitlines()
    frags = {
        "lst_upstream.tex": block([whole(basic, "AdmissiblePotential"), whole(basic, "diskEnergy"),
                                   whole(basic, "energy"), whole(defs, "latticeEnergy"),
                                   statement(univ, "universal_energy_minimum")[:3]]),
        "lst_d2.tex": block([whole(d2, "DensityRho"), statement(d2, "universal_any_density")[:3]]),
        "lst_defs.tex": block([whole(yk, "phi"), whole(yk, "g"), whole(yk, "c")]),
        "lst_mul_sign.tex": block([whole(yk, "mul_sign")]),
        "lst_phi_sign.tex": block([whole(yk, "phi_sign")]),
        "lst_yk_main.tex": block([statement(yk, n) for n in ("admissible_mul", "admissible_congr", "phi_admissible",
                                                             "yukawa_admissible", "triangular_yukawa_optimal")]),
        "lst_yk_fin.tex": block([whole(yk, "g_le")[:1] + statement(yk, "g_le")[1:], statement(yk, "latticeEnergy_yukawa_lt_top")]),
        "lst_yk_neg.tex": block([whole(yk, "c_neg_at_pi"), whole(yk, "c_not_admissible")]),
        "lst_mix_closure.tex": block([statement(mix, n) for n in ("admissible_add", "admissible_smul", "admissible_sum")]),
        "lst_mix_rescale.tex": block([statement(mix, "g_rescale"), statement(mix, "yukawa_optimal_any_density"),
                                      statement(mix, "latticeEnergy_yukawa_rho_lt_top")]),
        "lst_mix_main.tex": block([whole(mix, "yukawaMix"), statement(mix, "yukawaMix_admissible"),
                                   statement(mix, "triangular_yukawaMix_optimal"),
                                   statement(mix, "latticeEnergy_yukawaMix_lt_top")]),
        "lst_mix_neg.tex": block([whole(mix, "signedMix"), statement(mix, "signedMix_neg"),
                                  statement(mix, "signedMix_not_admissible")]),
        "ax_yukawa.tex": axiom_block(H2 / "contribution" / "compile_yukawa.json"),
        "ax_yukawamix.tex": axiom_block(H2 / "contribution" / "compile_yukawamix.json"),
        "ax_controls.tex": axiom_block(H2 / "contribution" / "compile_yukawa_controls.json", ["ctl_", "sorry"]),
        "ax_mixcontrols.tex": axiom_block(H2 / "contribution" / "compile_yukawamix_controls.json", ["ctl_", "pos_", "sorry"]),
        "ax_verify.tex": axiom_block(H2 / "contribution" / "verify" / "compile_verify_yukawamix.json", ["VerifierH2Mix", "sorry"]),
    }
    outdir = HERE / "gen"
    outdir.mkdir(exist_ok=True)
    seen: set[str] = set()
    for name, text in frags.items():
        (outdir / name).write_text(text)
        seen.update(ch for ch in text if ord(ch) > 127)
    missing = sorted(ch for ch in seen if ch not in UNI)
    if missing:
        print("unmapped code points:", [f"U+{ord(c):04X} {c}" for c in missing])
        return 1
    decl = [f"\\DeclareUnicodeCharacter{{{ord(c):04X}}}{{{UNI[c]}}}" for c in sorted(seen)]
    (outdir / "gen_unicode.tex").write_text("\n".join(decl) + "\n")
    hashes = {p.name: sha(p) for p in (FC / "Yukawa.lean", FC / "YukawaMix.lean", FC / "YukawaControls.lean",
                                       FC / "YukawaMixControls.lean",
                                       H2 / "contribution" / "verify" / "VerifyYukawaMix.lean")}
    (outdir / "lean_hashes.json").write_text(json.dumps(hashes, indent=1))
    print(f"{len(frags)} fragments, {len(seen)} non-ASCII code points mapped")
    for k, v in hashes.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
