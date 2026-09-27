#!/usr/bin/env python3
"""Validate the master-math instrument before any prover sees it.

Per item, three kernel compiles (the gate is `build_ladder.compile_one`):
  positive  our statement + reference proof           -> must be clean
  negative  false variant + the same reference proof  -> must NOT be clean
  refute    `¬ (false variant)` + refutation proof    -> must be clean
            (so the false item is well-formed AND actually false)

Writes results/master_math_run2/{validation,ladder,controls}.json. The ladder
holds true and false items without references; prompts never see controls.
Exit 1 if any control fails.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # repo root: `scripts.*` packages

from scripts.hardness import build_ladder as bl  # noqa: E402
from scripts.master_math.problems import BLOCKED, PROBLEMS  # noqa: E402

OUT = HERE.parents[1] / "results" / "master_math_run2"


def true_item(p: dict) -> dict:
    return {"id": p["id"], "tier": p["fidelity"], "truth": True, "defs": "",
            "header": p["header"], "statement": p["statement"]}


def false_item(p: dict) -> dict:
    fid = p["id"] + "_F"
    return {"id": fid, "tier": p["fidelity"], "truth": False, "defs": "",
            "header": p["header"], "statement": f"theorem {fid} : {p['false_prop']}"}


def refute_item(p: dict) -> dict:
    rid = p["id"] + "_F_refuted"
    return {"id": rid, "defs": "", "header": p["header"],
            "statement": f"theorem {rid} : ¬ ({p['false_prop']})"}


def validate(p: dict) -> dict:
    pos = bl.compile_one(bl.lean_file(true_item(p), p["reference"]), f"pos_{p['id']}")
    neg = bl.compile_one(bl.lean_file(false_item(p), p["reference"]), f"neg_{p['id']}")
    ref = bl.compile_one(bl.lean_file(refute_item(p), p["refutation"]), f"refute_{p['id']}")
    row = {"id": p["id"], "fidelity": p["fidelity"],
           "positive_clean": pos["clean"], "positive_axioms": pos["axioms"],
           "negative_rejected": not neg["clean"],
           "refutation_clean": ref["clean"], "refutation_axioms": ref["axioms"],
           "secs": round(pos["secs"] + neg["secs"] + ref["secs"], 1)}
    for tag, v in (("positive", pos), ("refutation", ref)):
        if not v["clean"]:
            row[f"{tag}_errors"] = v["errors"] or v["tail"]
    row["ok"] = row["positive_clean"] and row["negative_rejected"] and row["refutation_clean"]
    print(json.dumps({k: row[k] for k in ("id", "ok", "positive_clean", "negative_rejected",
                                          "refutation_clean", "secs")}), flush=True)
    return row


def main() -> int:
    only = set(sys.argv[1:])
    todo = [p for p in PROBLEMS if not only or p["id"] in only]
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(validate, todo))
    OUT.mkdir(parents=True, exist_ok=True)
    prev = {}
    vpath = OUT / "validation.json"
    if only and vpath.exists():
        prev = {r["id"]: r for r in json.loads(vpath.read_text())["items"]}
    prev.update({r["id"]: r for r in rows})
    ordered = [prev[p["id"]] for p in PROBLEMS if p["id"] in prev]
    vpath.write_text(json.dumps({"items": ordered, "blocked": BLOCKED}, indent=1))
    usable = [p for p in PROBLEMS if prev.get(p["id"], {}).get("ok")]
    ladder = [true_item(p) for p in usable] + [false_item(p) for p in usable]
    (OUT / "ladder.json").write_text(json.dumps(ladder, indent=1))
    (OUT / "controls.json").write_text(json.dumps(
        {p["id"]: {"reference": p["reference"], "refutation": p["refutation"]} for p in usable},
        indent=1))
    bad = [r["id"] for r in ordered if not r["ok"]]
    print(f"\nitems={len(PROBLEMS)} validated={len(ordered)} usable={len(usable)} "
          f"blocked={len(BLOCKED)} failing={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
