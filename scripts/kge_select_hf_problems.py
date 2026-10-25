#!/usr/bin/env python3
"""Select the SRSD-Feynman problems that Kernel-Gated Evolution can be asked to solve.

The SRSD-Feynman datasets (yoshitomo-matsubara/srsd-feynman_{easy,medium,hard} on
the Hugging Face Hub, CC-BY-4.0) describe 120 physics equations with a sympy
string each. KGE's reference grammar is {+, -, *} over four variables with
dyadic-rational constants, so an equation is a candidate only if it is a
polynomial in at most four variables whose coefficients lie in Z[1/2]. Everything
else -- divisions by a variable, roots, exponentials, trigonometry, pi, physical
constants given as floats -- is outside the grammar and is REFUSED, not
approximated. The refusals are recorded with their reason, because the share of
the benchmark the grammar covers is itself a result.

SAFETY. The equation strings are untrusted data. They are never passed to
`eval`, `sympify` or `parse_expr`, all of which evaluate arbitrary code. They are
parsed with `ast.parse(mode="eval")` and the tree is WALKED; any node other than
arithmetic over numbers and `x<n>` names is a refusal.

Ranking among the candidates: smallest expression first, one representative per
structure (several Feynman laws are literally `x0*x1`), so the five selected span
distinct shapes rather than five copies of a product.

Usage:
    python3 -I scripts/kge_select_hf_problems.py --supp DIR --out results/kge_hf_selection.json
"""

from __future__ import annotations

import argparse
import ast
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

VARS = ("h", "w", "q", "p")
MAX_VARS = 4


class Refuse(Exception):
    pass


def dyadic(value: Fraction) -> bool:
    d = value.denominator
    return d & (d - 1) == 0 and abs(value.numerator) <= 64


def leaf_const(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def to_prefix(node: ast.AST, mapping: dict[str, str]) -> tuple[str, Fraction | None]:
    """Prefix text and, if the subtree is a pure constant, its value.

    Constants are folded so that `3/2 * x` becomes a single leaf `3/2 * x` rather
    than a division node the grammar does not have.
    """
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise Refuse("non-numeric constant")
        value = Fraction(str(node.value)) if isinstance(node.value, float) else Fraction(node.value)
        if not dyadic(value):
            raise Refuse(f"coefficient {node.value} is not a small dyadic rational")
        return leaf_const(value), value
    if isinstance(node, ast.Name):
        if node.id not in mapping:
            raise Refuse(f"name {node.id!r} outside x0..x3")
        return mapping[node.id], None
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            text, value = to_prefix(node.operand, mapping)
            if value is not None:
                return leaf_const(-value), -value
            return f"(- 0 {text})", None
        if isinstance(node.op, ast.UAdd):
            return to_prefix(node.operand, mapping)
        raise Refuse("unary operator")
    if isinstance(node, ast.BinOp):
        left, lv = to_prefix(node.left, mapping)
        if isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, int):
                raise Refuse("non-integer power")
            n = node.right.value
            if n < 1 or n > 4:
                raise Refuse(f"power {n} outside 1..4")
            text = left
            for _ in range(n - 1):
                text = f"(* {text} {left})"
            return text, (lv ** n if lv is not None else None)
        right, rv = to_prefix(node.right, mapping)
        if isinstance(node.op, ast.Add):
            if lv is not None and rv is not None:
                return leaf_const(lv + rv), lv + rv
            return f"(+ {left} {right})", None
        if isinstance(node.op, ast.Sub):
            if lv is not None and rv is not None:
                return leaf_const(lv - rv), lv - rv
            return f"(- {left} {right})", None
        if isinstance(node.op, ast.Mult):
            if lv is not None and rv is not None:
                return leaf_const(lv * rv), lv * rv
            return f"(* {left} {right})", None
        if isinstance(node.op, ast.Div):
            if rv is None:
                raise Refuse("division by a variable")
            inv = 1 / rv
            if not dyadic(inv):
                raise Refuse(f"division by {rv} leaves a non-dyadic coefficient")
            if lv is not None:
                return leaf_const(lv * inv), lv * inv
            return f"(* {left} {leaf_const(inv)})", None
        raise Refuse(f"operator {type(node.op).__name__}")
    raise Refuse(f"syntax {type(node).__name__}")


def prefix_size(text: str) -> int:
    return sum(1 for tok in text.replace("(", " ").replace(")", " ").split() if tok not in "+-*")


def structure_key(text: str) -> str:
    """The shape with variables and constants erased, for de-duplication."""
    out = []
    for tok in text.replace("(", " ( ").replace(")", " ) ").split():
        if tok in ("(", ")", "+", "-", "*"):
            out.append(tok)
        elif tok in VARS:
            out.append("v")
        else:
            out.append("c")
    return " ".join(out)


def classify(problem: str, info: dict[str, Any]) -> dict[str, Any]:
    text = str(info.get("sympy_eq_str", ""))
    row: dict[str, Any] = {"problem": problem, "sympy_eq_str": text,
                           "symbols": info.get("symbols"), "symbols_descs": info.get("symbols_descs")}
    try:
        tree = ast.parse(text, mode="eval").body
    except SyntaxError as exc:
        row.update(fits=False, reason=f"unparsable: {exc.msg}")
        return row
    names = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)})
    if any(not (n.startswith("x") and n[1:].isdigit()) for n in names):
        row.update(fits=False, reason="uses a function or constant outside the grammar: "
                   + ", ".join(n for n in names if not n.startswith("x")))
        return row
    if len(names) > MAX_VARS:
        row.update(fits=False, reason=f"{len(names)} variables, grammar has {MAX_VARS}")
        return row
    mapping = {name: VARS[i] for i, name in enumerate(names)}
    try:
        prefix, _ = to_prefix(tree, mapping)
    except Refuse as exc:
        row.update(fits=False, reason=str(exc))
        return row
    row.update(fits=True, prefix=prefix, size=prefix_size(prefix),
               mapping={f"{k} ({(info.get('symbols') or ['?']*9)[i+1] if i+1 < len(info.get('symbols') or []) else '?'})": v
                        for i, (k, v) in enumerate(mapping.items())},
               structure=structure_key(prefix))
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supp", type=Path, required=True, help="directory with supp_{easy,medium,hard}.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for level in ("easy", "medium", "hard"):
        data = json.loads((args.supp / f"supp_{level}.json").read_text())
        for problem, info in data.items():
            row = classify(problem, info)
            row["level"] = level
            rows.append(row)

    fitting = [r for r in rows if r["fits"]]
    fitting.sort(key=lambda r: (r["size"], r["problem"]))
    chosen: list[dict[str, Any]] = []
    seen_structures: set[str] = set()
    for r in fitting:
        if r["structure"] in seen_structures:
            continue
        seen_structures.add(r["structure"])
        chosen.append(r)
        if len(chosen) >= args.top:
            break

    reasons: dict[str, int] = {}
    for r in rows:
        if not r["fits"]:
            key = r["reason"].split(":")[0]
            reasons[key] = reasons.get(key, 0) + 1

    report = {
        "source": "yoshitomo-matsubara/srsd-feynman_{easy,medium,hard} (Hugging Face Hub, CC-BY-4.0); supp_info.json",
        "grammar": "{+,-,*} over at most 4 variables, coefficients in Z[1/2] with |numerator| <= 64",
        "safety": "equation strings parsed with ast.parse and walked; never eval/sympify",
        "total_problems": len(rows),
        "fitting_grammar": len(fitting),
        "coverage_fraction": round(len(fitting) / len(rows), 3),
        "refusal_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "selected_top": chosen,
        "all_fitting": fitting,
        "all": rows,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{len(rows)} problems; {len(fitting)} fit the grammar ({report['coverage_fraction']:.1%})")
    for r in chosen:
        print(f"  {r['problem']:<20} size={r['size']:>2}  {r['sympy_eq_str']:<28} -> {r['prefix']}")
    print("refusals:", report["refusal_reasons"])
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
