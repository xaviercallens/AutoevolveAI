"""Generate verbatim Lean listings (statements only, proofs elided) and axiom transcripts for the N4 paper.

Reuses the extraction helpers and glyph map of the P7 generator (papers/prog_population_genetics_fixation/gen/gen_listings.py).
Sources: formal_cert/Programmes/EvoGraph/*.lean ; transcripts: results/proposal3/2026-10-26/N4/compile_*.json.
Outputs in this directory: <key>.lst (non-ASCII replaced by LaTeX glyphs for `listings`), axioms_*.txt, sources.tex.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_listings.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
LEAN = W / "formal_cert/Programmes/EvoGraph"
N4 = W / "results/proposal3/2026-10-26/N4"
P7GEN = W / "papers/prog_population_genetics_fixation/gen/gen_listings.py"

spec = importlib.util.spec_from_file_location("p7gen", P7GEN)
assert spec is not None and spec.loader is not None
p7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p7)
UMAP: dict[str, str] = dict(p7.UMAP)
UMAP.update({"ᵗ": r"$^t$", "⁻¹": r"$^{-1}$", "𝟙": "1", "ᵢ": r"$_i$", "∪": r"$\cup$", "ℓ": r"$\ell$", "ₘ": r"$_m$",
             "ᵣ": r"$_r$", "ˢ": r"$^s$", "∀": r"$\forall$", "⟶": r"$\to$", "⇒": r"$\Rightarrow$", "∉": r"$\notin$", "⦃": r"$\{$", "⦄": r"$\}$"})
block = p7.block


def src(name: str) -> list[str]:
    return (LEAN / name).read_text().splitlines()


def main() -> int:
    BD, TR, EX, PC = src("BirthDeath.lean"), src("Transport.lean"), src("Examples.lean"), src("EvoGraphPlantedControls.lean")
    texts = {
        "model": block(BD, [("fit", "def"), ("ind", "def"), ("upd", "def"), ("totFit", "def"), ("coef", "def"), ("bdK", "def"), ("cutOut", "def"), ("cutIn", "def"),
                            ("upP", "def"), ("downP", "def"), ("RowStochastic", "def"), ("Isothermal", "def"),
                            ("StronglyConnected", "def"), ("CutPositive", "def")]),
        "transport": block(TR, [("sPow", "def"), ("TwoAbsorbing", "def"), ("two_absorbing_limit", "thm")]),
        "fb": block(BD, [("up_eq", "thm"), ("down_eq", "thm"), ("cut_balance", "thm"), ("forward_bias", "thm")]),
        "harm": block(BD, [("moranFix_card_harmonic", "thm"), ("moranFix_card_var_pos", "thm")]),
        "conn": block(BD, [("cutPositive_of_strongly_connected", "thm")]),
        "main": block(BD, [("stationary_fixation", "thm"), ("isothermal_fixation", "thm"), ("isothermal_fixation_single", "thm"),
                           ("isothermal_fixation_neutral", "thm"), ("isothermal_fixation_uniform", "thm"), ("bd_fixation_mono", "thm")]),
        "ctl_pos": block(EX, [("wellMixed_up", "thm"), ("wellMixed_down", "thm"), ("wellMixed3_fixation", "thm"),
                              ("starStationary_fixation", "thm")]),
        "ctl_star": block(EX, [("star_bias", "thm"), ("star_fixation_centre", "thm"), ("star_fixation_leaf", "thm"),
                               ("star_fixation_uniform", "thm"), ("star_ne_moran", "thm")]),
        "ctl_cyc": block(EX, [("Wcyc", "def"), ("cycle4_not_lumpable", "thm"), ("identity_no_fixation", "thm")]),
        "ctl_planted": block(PC, [("ctl_sorry", "thm"), ("ctl_axiom", "thm"), ("ctl_axiom_lumpable", "thm")]),
    }
    used: set[str] = set()
    for key, txt in texts.items():
        (HERE / f"{key}.lean").write_text(txt)
        used |= {c for c in txt if ord(c) > 127}
    missing = sorted(c for c in used if c not in UMAP)
    if missing:
        raise SystemExit(f"unmapped codepoints: {[hex(ord(c)) + ' ' + c for c in missing]}")
    for key, txt in texts.items():
        t = txt
        for c in sorted(used, key=len, reverse=True):
            t = t.replace(c, "(*@" + UMAP[c] + "@*)")
        (HERE / f"{key}.lst").write_text(t)

    # verbatim axiom transcripts
    for jf, out in (("compile_ImportAll.json", "axioms_claimed.txt"), ("compile_PlantedControls.json", "axioms_planted.txt")):
        j = json.loads((N4 / jf).read_text())
        (HERE / out).write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + j["output"].replace(str(W) + "/", ""))

    # source table
    rows = []
    files = [("Transport.lean", "compile_Transport.json"), ("BirthDeath.lean", "compile_BirthDeath.json"),
             ("Examples.lean", "compile_Examples.json"), ("EvoGraphImportAll.lean", "compile_ImportAll.json"),
             ("EvoGraphPlantedControls.lean", "compile_PlantedControls.json")]
    for f, cj in files:
        j = json.loads((N4 / cj).read_text())
        h = hashlib.sha256((LEAN / f).read_bytes()).hexdigest()
        rows.append(rf"\texttt{{{f.replace('_', chr(92) + '_')}}} & \texttt{{{h[:16]}\dots}} & {j['rc']} & {j['seconds']}\\")
    for f in ("Absorption.lean", "MoranModel.lean"):
        h = hashlib.sha256((W / "formal_cert/Programmes/PopGen" / f).read_bytes()).hexdigest()
        rows.append(rf"\texttt{{PopGen/{f}}} (P7, unchanged) & \texttt{{{h[:16]}\dots}} & -- & --\\")
    (HERE / "sources.tex").write_text("\n".join(rows) + "\n")
    print("ok", sorted(texts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
