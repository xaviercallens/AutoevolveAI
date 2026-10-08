"""Advisory eye aid for lane D1 (see deviations.md, item 1). It never changes a mechanical verdict.

For every hole of the nine challenges:
  (a) DIFFERS: every differing token span after applying the recorded challenge->solution renaming.
  (b) name resolution: for every free identifier of each side's declaration, the set of OAI declarations
      it can resolve to on that side (enclosing namespace prefixes, plus every non-scoped ``open`` resolved
      against every enclosing prefix and against the root), compared between the two sides.
  (c) opened namespaces that resolve to no OAI namespace (Mathlib ones): a grep of a local Mathlib tree
      for a declaration of ``<NS>.<ident>``. The tree is LeanMaster's checkout, which pins a different
      Mathlib revision from upstream's lake-manifest, so a hit or miss there is indicative only.

Usage: /usr/bin/python3 eye_aid.py <lean_root> <lane_dir> <mathlib_dir>
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "scripts" / "openai_math"))
import d1_hole_bodies as d1  # noqa: E402


def rename_tokens(toks: list[str], ren: dict[str, str]) -> list[str]:
    """Apply a challenge->solution renaming, including the head of dotted tokens ``x.f``."""
    out = []
    for t in toks:
        head, dot, rest = t.partition(".")
        if t in ren:
            out.append(ren[t])
        elif dot and head in ren:
            out.append(ren[head] + "." + rest)
        else:
            out.append(t)
    return out


def diff_spans(a: list[str], b: list[str]) -> list[dict[str, Any]]:
    """All non-equal opcodes between two token streams, with 4 tokens of context."""
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    spans = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        spans.append(
            {
                "op": tag,
                "challenge_at": i1,
                "challenge": " ".join(a[i1:i2]),
                "solution": " ".join(b[j1:j2]),
                "context_before": " ".join(a[max(0, i1 - 4) : i1]),
                "context_after": " ".join(a[i2 : i2 + 4]),
            }
        )
    return spans


def name_opens(context: list[str]) -> list[str]:
    """Namespaces opened for names (``open scoped`` opens notation/instances only, not names)."""
    out: list[str] = []
    for line in context:
        toks = line.split()
        if not toks or toks[0] != "open" or (len(toks) > 1 and toks[1] == "scoped"):
            continue
        for t in toks[1:]:
            if t in ("hiding", "renaming"):
                break
            if t.startswith("(") or t == "in":
                continue
            out.append(t)
    return out


def scopes(decl: d1.Decl, known_ns: set[str]) -> tuple[list[str], list[str]]:
    """(namespaces whose members are visible unqualified, opened namespaces resolving to nothing known)."""
    ns = decl.full_name.split(".")[:-1]
    enclosing = [".".join(ns[:k]) for k in range(len(ns), 0, -1)]
    vis = list(enclosing)
    unresolved = []
    for o in name_opens(decl.context):
        cands = [f"{p}.{o}" for p in enclosing] + [o]
        hit = [c for c in cands if c in known_ns]
        vis.extend(hit if hit else [o])
        if not hit:
            unresolved.append(o)
    return vis, unresolved


def free_idents(decl: d1.Decl) -> list[str]:
    toks = decl.tokens_after_name
    bound = d1.bound_identifiers(toks)
    out = []
    for t in toks:
        if re.fullmatch(d1._IDENT, t) and t not in d1.KEYWORDS and t.partition(".")[0] not in bound and t not in out:
            out.append(t)
    return out


def namespaces_of(idx: dict[str, list[d1.Decl]]) -> set[str]:
    out: set[str] = set()
    for name in idx:
        parts = name.split(".")
        for k in range(1, len(parts)):
            out.add(".".join(parts[:k]))
    return out


def resolve(ident: str, vis: list[str], idx: dict[str, list[d1.Decl]]) -> list[str]:
    cands = [f"{v}.{ident}" for v in vis] + [ident]
    return sorted({c for c in cands if c in idx})


def mathlib_hits(ns: str, ident: str, mathlib: Path) -> list[str]:
    """Grep the Mathlib tree for a declaration of ``ns.ident`` (dotted, or inside ``namespace ns``)."""
    last = ident.split(".")[0]
    pat = rf"^(@\[[^]]*\] *)*((private|protected|noncomputable|nonrec) +)*(def|theorem|lemma|abbrev|instance|structure|class|inductive) +({re.escape(ns)}\.)?{re.escape(last)}\b"
    try:
        res = subprocess.run(["grep", "-rlE", pat, str(mathlib), "--include=*.lean"], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return ["GREP_TIMEOUT"]
    hits = []
    for f in res.stdout.split():
        src = Path(f).read_text(encoding="utf-8", errors="replace")
        dotted = re.search(rf"^\S.*\b(def|theorem|lemma|abbrev|instance|structure|class|inductive) +{re.escape(ns)}\.{re.escape(last)}\b", src, re.M)
        inside = re.search(rf"^namespace {re.escape(ns)}\s*$", src, re.M) and re.search(
            rf"^(@\[[^]]*\] *)*((private|protected|noncomputable|nonrec) +)*(def|theorem|lemma|abbrev|instance|structure|class|inductive) +{re.escape(last)}\b", src, re.M
        )
        if dotted or inside:
            hits.append(str(Path(f).relative_to(mathlib)))
    return hits[:10]


def audit(root: Path, name: str, chunk: dict[str, Any], mathlib: Path, cache: dict[str, list[str]]) -> list[dict[str, Any]]:
    cfg = json.loads((root / "ComparatorChallenges" / f"{name}.json").read_text(encoding="utf-8"))
    chal_idx = d1.index_files([root / "ComparatorChallenges" / f"{name}.lean"], root)
    sol_idx = d1.index_files(d1.import_closure(root, cfg["solution_module"]), root)
    chal_ns, sol_ns = namespaces_of(chal_idx), namespaces_of(sol_idx)
    out = []
    for h in chunk["holes"]:
        rec: dict[str, Any] = {"hole": h["hole"], "verdict": h["verdict"]}
        c = chal_idx.get(h["hole"], [])
        s = sol_idx.get(h["hole"], [])
        if len(c) != 1 or len(s) != 1:
            rec["skipped"] = f"challenge decls {len(c)}, solution decls {len(s)}"
            out.append(rec)
            continue
        cd, sd = c[0], s[0]
        if h["verdict"] == "DIFFERS":
            rec["diff_spans"] = diff_spans(rename_tokens(cd.tokens_after_name, h.get("renaming", {})), sd.tokens_after_name)
        cvis, cun = scopes(cd, chal_ns)
        svis, sun = scopes(sd, sol_ns)
        rec["challenge_visible_namespaces"] = cvis
        rec["solution_visible_namespaces"] = svis
        res_diff = []
        for ident in sorted(set(free_idents(cd)) | set(free_idents(sd))):
            cr = resolve(ident, cvis, chal_idx)
            sr = resolve(ident, svis, sol_idx)
            if cr != sr:
                res_diff.append({"ident": ident, "challenge_resolves_to": cr, "solution_resolves_to": sr})
        rec["resolution_differences"] = res_diff
        extra_opens = sorted(set(sun) - set(cun))
        ml: list[dict[str, Any]] = []
        for ns in extra_opens:
            for ident in free_idents(sd):
                key = f"{ns}|{ident.split('.')[0]}"
                if key not in cache:
                    cache[key] = mathlib_hits(ns, ident, mathlib)
                if cache[key]:
                    ml.append({"namespace": ns, "ident": ident, "mathlib_files": cache[key]})
        rec["solution_only_external_opens"] = extra_opens
        rec["mathlib_capture_candidates"] = ml
        rec["challenge_scoped_opens"] = [l for l in cd.context if l.startswith("open scoped")]
        rec["solution_scoped_opens"] = [l for l in sd.context if l.startswith("open scoped")]
        out.append(rec)
    return out


def main() -> int:
    root, lane, mathlib = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    cache: dict[str, list[str]] = {}
    res = {}
    for name in d1.NINE:
        chunk = json.loads((lane / "chunks" / f"{name}.json").read_text(encoding="utf-8"))
        res[name] = audit(root, name, chunk, mathlib, cache)
    payload = {"mathlib_dir": str(mathlib), "note": "advisory only; see deviations.md item 1", "challenges": res}
    (lane / "eye_aid.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, recs in res.items():
        for r in recs:
            print(name, r["hole"].split(".")[-1], r["verdict"], "spans:", len(r.get("diff_spans", [])), "resdiff:", len(r.get("resolution_differences", [])), "extra_opens:", r.get("solution_only_external_opens"), "ml:", len(r.get("mathlib_capture_candidates", [])), r.get("skipped", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
