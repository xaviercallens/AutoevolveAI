"""Advisory (deviations.md item 1c, refined): namespace-aware scan of a local Mathlib tree.

eye_aid.py's grep for Mathlib captures matched at file level and gave false positives (e.g. `structure Finset`
at the root of a file that also opens `namespace Finset`). This scan parses, with d1_hole_bodies.extract_decls
(which tracks the namespace stack), every Mathlib file that has a column-0 `namespace <NS>...` line, and reports
any declaration whose full name is exactly `<NS>.<ident>` for a free identifier of a hole declaration whose
solution side opens <NS> and whose challenge side does not.

The tree is LeanMaster's Mathlib checkout (rev 85e3a25e...), not upstream's pin (d13f23b7...): indicative only.
Usage: /usr/bin/python3 mathlib_scan.py <lane_dir> <mathlib_dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "scripts" / "openai_math"))
import d1_hole_bodies as d1  # noqa: E402


def main() -> int:
    lane, mathlib = Path(sys.argv[1]), Path(sys.argv[2])
    aid = json.loads((lane / "eye_aid.json").read_text(encoding="utf-8"))
    wanted: dict[str, set[str]] = {}
    holes_by_ns: dict[str, list[str]] = {}
    for name in d1.NINE:
        chunk = json.loads((lane / "chunks" / f"{name}.json").read_text(encoding="utf-8"))
        texts = {h["hole"]: h.get("solution_text", "") for h in chunk["holes"]}
        for rec in aid["challenges"][name]:
            for ns in rec.get("solution_only_external_opens", []):
                toks = d1.tokenize(texts[rec["hole"]])
                bound = d1.bound_identifiers(toks)
                idents = {t for t in toks if re.fullmatch(d1._IDENT, t) and t not in d1.KEYWORDS and t.partition(".")[0] not in bound}
                wanted.setdefault(ns, set()).update(idents)
                holes_by_ns.setdefault(ns, []).append(rec["hole"])
    out: dict[str, Any] = {"mathlib_dir": str(mathlib), "namespaces": {}}
    files = sorted(mathlib.rglob("*.lean"))
    for ns, idents in sorted(wanted.items()):
        pat = re.compile(rf"^namespace {re.escape(ns)}(\.|\s|$)", re.M)
        dotted = re.compile(rf"\b{re.escape(ns)}\.")
        scanned = 0
        in_ns = 0
        hits: list[dict[str, Any]] = []
        targets = {f"{ns}.{i}" for i in idents}
        for f in files:
            src = f.read_text(encoding="utf-8", errors="replace")
            if not (pat.search(src) or dotted.search(src)):
                continue
            scanned += 1
            for d in d1.extract_decls(src, str(f.relative_to(mathlib))):
                if d.full_name.startswith(ns + "."):
                    in_ns += 1
                if d.full_name in targets:
                    hits.append({"full_name": d.full_name, "file": d.file, "line": d.line, "kind": d.kind})
        out["namespaces"][ns] = {"holes": holes_by_ns[ns], "idents": sorted(idents), "files_scanned": scanned, "decls_in_namespace": in_ns, "hits": hits}
        print(ns, "files scanned", scanned, "decls in ns", in_ns, "hits", [h["full_name"] + "@" + h["file"] + ":" + str(h["line"]) for h in hits])
    (lane / "mathlib_scan.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
