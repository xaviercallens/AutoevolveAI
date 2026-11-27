"""Check, for all 34 generated Lean files, that the typed literals `v` and `s` equal the certificate JSON and that the
statement lines are the same template with only n substituted. Writes data/logs/lean_literal_check.json.

Not a proof (the kernel is the judge of `cover`); it closes the gap between "this .lean compiles" and "this .lean is about
the certificate in data/certificates". Uses only the standard library; run:  python3 -I check_lean_literals.py
"""
from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
REPO = PAPER.parent.parent
LEAN = REPO / "formal_cert" / "Programmes" / "SLR18"
CERTS = PAPER / "data" / "certificates"

STATEMENT_LINES = [
    "theorem v_injective : Function.Injective v := by decide",
    "theorem v_pos : ∀ i, 0 < v i := by decide",
]


def main() -> int:
    rows = []
    for n in range(5, 39):
        name = f"N{n:02d}"
        src = (LEAN / f"SLR{name}.lean").read_text()
        cert = json.loads((CERTS / f"cert_n{n:03d}.json").read_text())
        mv = re.search(r"^def v : Fin (\d+) → ℕ := !\[([^\]]*)\]", src, re.M)
        ms = re.search(r"^def s : Fin (\d+) → ℚ := !\[([^\]]*)\]", src, re.M)
        assert mv and ms, name
        v = [int(x) for x in mv.group(2).split(",")]
        s = [Fraction(x.strip().replace(" ", "")) for x in ms.group(2).split(",")]
        want_s = [Fraction(a, cert["D"]) for a in cert["a"]]
        mc = re.search(r"^theorem cover : ([^\n]*(?:\n[^\n]*)?)\s*:= by", src, re.M)
        cover = " ".join(mc.group(1).split()) if mc else ""
        expected_cover = (f"∀ t : ℝ, ∃ i : Fin {n}, ∃ k : ℤ, |((s i : ℚ) : ℝ) + ((v i : ℕ) : ℝ) * t - (k : ℝ)| < 1 / {n + 1}")
        banned = [w for w in ("sorry", "admit", "native_decide", "\naxiom ", "unsafe", "implemented_by") if w in src]
        rows.append({
            "n": n, "file": f"SLR{name}.lean",
            "v_matches_cert": v == cert["v"] and int(mv.group(1)) == n,
            "s_matches_cert": s == want_s and int(ms.group(1)) == n,
            "cover_statement_is_template": cover == expected_cover,
            "cover_statement_found": cover,
            "template_lines_present": all(line in src for line in STATEMENT_LINES),
            "imports": re.findall(r"^import .*$", src, re.M),
            "banned_tokens": banned,
        })
    ok = all(r["v_matches_cert"] and r["s_matches_cert"] and r["cover_statement_is_template"] and r["template_lines_present"]
             and r["imports"] == ["import Mathlib.Tactic"] and not r["banned_tokens"] for r in rows)
    out = {"all_ok": ok, "files": len(rows), "rows": rows}
    (PAPER / "data" / "logs" / "lean_literal_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("all_ok", ok, "files", len(rows))
    for r in rows:
        if not (r["v_matches_cert"] and r["s_matches_cert"] and r["cover_statement_is_template"]):
            print("FAIL", r["n"], r["cover_statement_found"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
