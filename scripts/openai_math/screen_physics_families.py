#!/usr/bin/env python3
"""Screen the openai/math families for physics content and Lean availability.

Reads CONTENTS.md and lean/docs/ from the local clone and prints, for every family whose title or first
paragraph matches a physics keyword, whether it has a Lean scope note (a Comparator-checked statement).
Output also goes to results/openai_math/physics_screen.json. Read-only; no model is called.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_corpus import DEFAULT_CLONE  # noqa: E402

KEYWORDS = re.compile(
    r"physic|quantum|Heisenberg|Ising|spin glass|Parisi|Boltzmann|Vlasov|Maxwell|Navier|Euler|Schr|gravity|relativ|"
    r"Einstein|black hole|turbulen|plasma|magnet|thermodynamic|statistical mechanics|field theory|Yang|entropy|"
    r"Hamiltonian|lattice|percolation|hard sphere|soliton|NLS|spectral gap|Hubbard|ferromagnet|critical|Penrose|"
    r"mass gap|gauge|string|supersym|Bose|Fermi|channel|capacity|decoherence",
    re.I,
)


def main() -> int:
    clone = DEFAULT_CLONE
    text = (clone / "CONTENTS.md").read_text()
    entries = re.findall(r"^\*\*(\d{3})\. (.+?)\*\*\s*(.*?)(?=^\*\*\d{3}\. |\Z)", text, re.M | re.S)
    docs = {p.stem for p in (clone / "lean" / "docs").glob("*.md")}
    rows = []
    for num, title, body in entries:
        first = body.strip().split("\n\n")[0].replace("\n", " ")
        if KEYWORDS.search(title + " " + first):
            rows.append({"family": num, "lean": num in docs, "title": title.strip(), "summary": first[:300]})
    out = REPO / "results" / "openai_math" / "physics_screen.json"
    out.write_text(json.dumps({"families_total": len(entries), "with_lean_note": len(docs), "hits": rows}, indent=1) + "\n")
    print(len(entries), "families;", len(docs), "with a Lean scope note;", len(rows), "keyword hits;",
          sum(r["lean"] for r in rows), "of them with Lean")
    for r in rows:
        print(("L " if r["lean"] else "- ") + r["family"], r["title"], "|", r["summary"][:170])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
