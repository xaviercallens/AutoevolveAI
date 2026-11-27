"""Annexe F, exemple 10 : certifier avec LeanFlow (lean.certify, tactique decide_kernel) les probabilites de
fixation exactes de l'etoile a 3 sommets (exemple 5), et voir une affirmation plantee etre rejetee.

Affirmations soumises (Lean 4.34.1, coeur seul, aucun import) :
  pos_star_harmonic    le tableau x_S calcule a l'exemple 5 verifie EXACTEMENT les 6 equations du premier pas ;
  pos_mean_above_moran 7/12 > 4/7 (l'etoile amplifie la selection a r = 2, n = 3) ;
  neg_moran_vector     temoin plante : le vecteur de Moran (0, 4/7, 6/7, 1 selon |S|) serait harmonique sur l'etoile ;
  neg_reversed         temoin plante : 7/12 < 4/7.
LeanFlow n'audite que '#print axioms'. Pour la porte du Niveau A on complete : chaque source acceptee est recompilee
en .olean puis rejouee par leanchecker, et l'on cherche skipKernelTC, addDecl, native_decide, implemented_by.
Temoin du rejeu : un module inexistant doit sortir avec un code non nul.
Usage : python -I f10_leanflow_certify.py SCRATCH OUT.json
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path[:0] = [str(HERE), str(Path.home() / "LeanFlow-wt-p1" / "src"), str(WORKTREE / "scripts" / "certified_numerics")]
import f05_graph_fixation as g  # noqa: E402
import lean_pinned  # noqa: E402
from leanflow_mcp.lean import LeanConfig, certify  # noqa: E402

LEAN = lean_pinned.TOOLCHAIN_BIN / "lean"


def harmonic_claim(name: str, x: list[Fraction], r: Fraction) -> dict:
    """Affirmation LeanFlow : x_vide = 0, x_tout = 1 et sum_S' P(S,S') (x_S' - x_S) = 0 pour S interieur."""
    w, full = g.star(3), 7
    enc = {f"x{s}": [str(v), str(v)] for s, v in enumerate(x)}
    asr = [{"label": "x0 == 0", "endpoint": "x0.lo", "op": "==", "rhs": "0"},
           {"label": "x7 == 1", "endpoint": "x7.lo", "op": "==", "rhs": "1"}]
    for s in range(1, full):
        tr = g.transitions(w, r, s)
        terms = [[str(p), f"x{t}.lo"] for t, p in sorted(tr.items())] + [[str(-sum(tr.values())), f"x{s}.lo"]]
        asr.append({"label": f"harmonique en S={s:03b}", "terms": terms, "op": "==", "rhs": "0"})
    return {"name": name, "tactic": "decide_kernel", "enclosures": enc, "assertions": asr}


def compare_claim(name: str, value: Fraction, op: str, rhs: Fraction) -> dict:
    return {"name": name, "tactic": "decide_kernel", "enclosures": {"m": [str(value), str(value)]},
            "assertions": [{"label": f"m {op} {rhs}", "endpoint": "m.lo", "op": op, "rhs": str(rhs)}]}


def replay(source: str, module: str, scratch: Path, env: dict[str, str]) -> dict:
    """Compile la source en .olean (module AppF.<module>) puis la rejoue avec leanchecker."""
    src = scratch / "src" / "AppF" / f"{module}.lean"
    ol = scratch / "olean" / "AppF" / f"{module}.olean"
    src.parent.mkdir(parents=True, exist_ok=True)
    ol.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(source)
    comp = subprocess.run([str(LEAN), f"--root={scratch / 'src'}", "-o", str(ol), str(src)], env=env,
                          capture_output=True, text=True, timeout=600)
    chk = subprocess.run([str(lean_pinned.TOOLCHAIN_BIN / "leanchecker"), f"AppF.{module}"], env=env,
                         capture_output=True, text=True, timeout=600)
    bad = re.findall(r"skipKernelTC|addDecl|native_decide|implemented_by", source)
    return {"compile_rc": comp.returncode, "leanchecker_rc": chk.returncode, "forbidden_tokens": bad}


def main(scratch: Path, out: Path) -> int:
    r = Fraction(2)
    x = g.fixation(g.star(3), r)
    moran_vec = [g.moran(3, r, bin(s).count("1")) if 0 < s < 7 else Fraction(s // 7) for s in range(8)]
    print("tableau de l'etoile (S en binaire):", ", ".join(f"{s:03b}:{v}" for s, v in enumerate(x)))
    claims = {
        "pos_star_harmonic": harmonic_claim("starN3", x, r),
        "pos_mean_above_moran": compare_claim("meanStar", sum(x[1 << v] for v in range(3)) / 3, ">", Fraction(4, 7)),
        "neg_moran_vector": harmonic_claim("moranOnStar", moran_vec, r),
        "neg_reversed": compare_claim("reversed", Fraction(7, 12), "<", Fraction(4, 7)),
    }
    expected = {"pos_star_harmonic": "ok", "pos_mean_above_moran": "ok", "neg_moran_vector": "rejected",
                "neg_reversed": "rejected"}
    cfg = LeanConfig(lean_cmd=(str(LEAN),), timeout_s=300)
    lp = lean_pinned.lean_path().replace(str(lean_pinned.OUT), str(scratch / "olean"))
    env = dict(os.environ, LEAN_PATH=lp)
    rows, ok = {}, True
    for key, claim in claims.items():
        res = certify(claim, cfg)
        row = {"status": res.status, "code": res.code, "tier": res.tier, "failed": list(res.failed),
               "axioms": {k: v.get("axioms") for k, v in res.axioms.items()}, "statement": res.statement}
        if res.status == "ok":
            row["replay"] = replay(res.statement, key.title().replace("_", ""), scratch, env)
            ok = ok and row["replay"] == {"compile_rc": 0, "leanchecker_rc": 0, "forbidden_tokens": []}
        ok = ok and res.status == expected[key]
        rows[key] = row
        axioms = sorted({str(a) for v in row["axioms"].values() for a in (v or [])})
        print(f"{key:<21} statut={res.status:<9} niveau={res.tier} theoremes refuses={list(res.failed)}"
              f" axiomes={axioms}" + (f" rejeu={row['replay']}" if "replay" in row else ""))
    missing = subprocess.run([str(lean_pinned.TOOLCHAIN_BIN / "leanchecker"), "AppF.ModuleInexistant"], env=env,
                             capture_output=True, text=True, timeout=600)
    ok = ok and missing.returncode != 0
    print(f"temoin du rejeu (module inexistant): leanchecker rc={missing.returncode}")
    out.write_text(json.dumps({"claims": claims, "results": rows, "missing_rc": missing.returncode}, indent=1))
    print("temoins conformes:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
