"""Proof-length comparison from the REAL dependency closure computed by Lean (Closure.lean -> closure_raw.json).

For each root theorem, the closure is the set of repo declarations (modules Programmes.* and Autoresearch.*) reachable
through the kernel terms (types and values) of the root. Mathlib, upstream openai/math (OAI.*) and the repository's own
Triangular.* modules are excluded on BOTH sides (overlapping structure/field ranges are counted twice on both sides). Per declaration, lines = non-blank, non-comment source lines in Lean's declaration range (docstring
excluded by the range); chars = non-whitespace characters of those lines.
Usage: python -I proof_length.py closure_raw.json OUT.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
FORMAL = REPO / "formal_cert"

PAIRS = [
    ("H2 Yukawa", "AutoresearchYukawa.yukawa_admissible", "ProgCM.Applications.H2_yukawa_admissible"),
    ("H1 dipolar (all d)", "AutoresearchDipolarMultipolar.dipolar_admissible_all", "ProgCM.Applications.H1_dipolar_admissible"),
    ("H1 dipolar (d>0)", "AutoresearchDipolar.dipolar_admissible", "ProgCM.Applications.H1_dipolar_admissible"),
    ("H3 Keldysh", "AutoresearchKeldysh.keldysh_admissible", "ProgCM.Applications.H3_keldysh_admissible"),
]
NEW = ["ProgCM.Applications.screenedDipolar_cm", "ProgCM.Applications.yukawaSpectrum_cm",
       "ProgCM.Applications.yukawaExpSpectrum_cm", "ProgCM.Applications.secondDiff_cm",
       "ProgCM.Applications.quadrupolarCoulomb_cm", "ProgCM.Applications.quadrupolarYukawa_cm"]


def src_path(module: str) -> Path:
    return FORMAL / (module.replace(".", "/") + ".lean")


def strip_comments(lines: list[str]) -> list[str]:
    text = "\n".join(lines)
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    return [ln for ln in text.splitlines() if ln.strip()]


def measure(module: str, start: int, end: int, cache: dict[str, list[str]]) -> tuple[int, int]:
    if module not in cache:
        cache[module] = src_path(module).read_text().splitlines()
    body = strip_comments(cache[module][start - 1:end])
    return len(body), sum(len("".join(ln.split())) for ln in body)


def main(raw: str, out: str) -> None:
    text = json.loads(Path(raw).read_text())["output"]
    closure: dict[str, dict[str, tuple[str, int, int]]] = defaultdict(dict)
    for root, const, mod, a, b in re.findall(r"CLOSURE (\S+) (\S+) (\S+) (\d+) (\d+)", text):
        closure[root][const] = (mod, int(a), int(b))
    cache: dict[str, list[str]] = {}
    res: dict[str, object] = {}

    def summarize(root: str) -> dict[str, object]:
        decls = closure[root]
        # the root's own measured size
        mod, a, b = decls[root]
        hl, hc = measure(mod, a, b, cache)
        tot = {"Programmes": [0, 0, 0], "Autoresearch": [0, 0, 0]}
        for const, (m, s, e) in decls.items():
            ln, ch = measure(m, s, e, cache)
            key = m.split(".")[0]
            tot[key][0] += 1
            tot[key][1] += ln
            tot[key][2] += ch
        return {"headline_lines": hl, "headline_chars": hc,
                "closure_decls": sum(v[0] for v in tot.values()),
                "closure_lines_total": sum(v[1] for v in tot.values()),
                "closure_chars_total": sum(v[2] for v in tot.values()),
                "closure_lines_library_Programmes": tot["Programmes"][1],
                "closure_lines_original_Autoresearch": tot["Autoresearch"][1],
                "closure_decls_library": tot["Programmes"][0], "closure_decls_original": tot["Autoresearch"][0]}

    for label, orig, new in PAIRS:
        res[label] = {"original": orig, "original_stats": summarize(orig), "library": new, "library_stats": summarize(new)}
    for new in NEW:
        res[new] = {"library_stats": summarize(new)}
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    for k, v in res.items():
        print(k)
        for kk, vv in v.items():  # type: ignore[union-attr]
            print("   ", kk, vv)


def union_stats(raw: str) -> dict[str, object]:
    """Amortisation: union of closures. Library roots H1-H3 (3 original potentials) and H1-H3 + the two new ones,
    versus the union of the original closures of H1 (all d), H2, H3."""
    text = json.loads(Path(raw).read_text())["output"]
    closure: dict[str, dict[str, tuple[str, int, int]]] = defaultdict(dict)
    for root, const, mod, a, b in re.findall(r"CLOSURE (\S+) (\S+) (\S+) (\d+) (\d+)", text):
        closure[root][const] = (mod, int(a), int(b))
    cache: dict[str, list[str]] = {}

    def union(roots: list[str]) -> dict[str, int]:
        seen: dict[str, tuple[str, int, int]] = {}
        for r in roots:
            seen.update(closure[r])
        lines = sum(measure(m, s, e, cache)[0] for m, s, e in seen.values())
        return {"decls": len(seen), "lines": lines}

    a = "ProgCM.Applications."
    return {
        "original_H1all_H2_H3": union(["AutoresearchDipolarMultipolar.dipolar_admissible_all",
                                       "AutoresearchYukawa.yukawa_admissible", "AutoresearchKeldysh.keldysh_admissible"]),
        "library_H1_H2_H3": union([a + "H1_dipolar_admissible", a + "H2_yukawa_admissible", a + "H3_keldysh_admissible"]),
        "library_H1_H2_H3_plus_screened_spectrum": union([a + "H1_dipolar_admissible", a + "H2_yukawa_admissible",
                                                          a + "H3_keldysh_admissible", a + "screenedDipolar_cm",
                                                          a + "yukawaSpectrum_cm"]),
        "library_H1_H2_H3_plus_screened_spectrum_quadrupolar": union(
            [a + "H1_dipolar_admissible", a + "H2_yukawa_admissible", a + "H3_keldysh_admissible",
             a + "screenedDipolar_cm", a + "yukawaSpectrum_cm", a + "quadrupolarCoulomb_cm",
             a + "quadrupolarYukawa_cm"]),
    }


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
    u = union_stats(sys.argv[1])
    print("UNION", json.dumps(u))
    with open(sys.argv[2].replace(".json", "_union.json"), "w") as fh:
        json.dump(u, fh, indent=1)
