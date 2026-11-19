#!/usr/bin/env python3
"""Turn kernel-verified hardness pairs into SFT rows for the prover adapter (TODO 1).

Input : data/training/hardness_dpo_pairs.jsonl (from build_dpo_pairs.py; every `chosen`
        was compiled in the Lean 4 kernel with the axiom whitelist before it was written).
Output: data/training/prover_sft.jsonl, one row per ladder item:
        {id, item_id, tier, prompt, completion, verdict: True, provenance}
        `verdict: True` is what night_training_workflow._is_verified_row accepts.

Rows are dropped, and counted by reason, when the proof is missing or mentions `sorry` or
`axiom`, when the pair does not name the Lean kernel as its verifier, or when the prompt
or proof contains a frozen-split proposition (same normalized-substring match that
step_data uses, so renamed copies are caught). A run that ends with no rows reports BLOCKED
and exits 2; it never writes an empty "success".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PAIRS = REPO / "data" / "training" / "hardness_dpo_pairs.jsonl"
FROZEN = REPO / "results" / "hardness" / "frozen_split.json"
OUT = REPO / "data" / "training" / "prover_sft.jsonl"


def _norm(text: str) -> str:
    return " ".join(text.split())


def build_sft_rows(
    pairs: list[dict[str, Any]], frozen_props: list[str]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Pure: pairs -> (SFT rows, drop counts by reason). First pair per item wins."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    drops = {"no_proof": 0, "unsound_text": 0, "not_kernel_verified": 0,
             "frozen_leak": 0, "duplicate_item": 0}
    props = [_norm(p) for p in frozen_props]
    for pair in pairs:
        prompt = str(pair.get("prompt", ""))
        chosen = str(pair.get("chosen", ""))
        item_id = str(pair.get("item_id", ""))
        if not prompt.strip() or not chosen.strip() or not item_id:
            drops["no_proof"] += 1
            continue
        lowered = chosen.lower()
        if "sorry" in lowered or "axiom" in lowered:
            drops["unsound_text"] += 1
            continue
        if "lean4_kernel" not in str(pair.get("provenance", "")):
            drops["not_kernel_verified"] += 1
            continue
        text = _norm(prompt + " " + chosen)
        if any(p in text for p in props):
            drops["frozen_leak"] += 1
            continue
        if item_id in seen:
            drops["duplicate_item"] += 1
            continue
        seen.add(item_id)
        rows.append({
            "id": f"sft_{item_id}",
            "item_id": item_id,
            "tier": pair.get("tier"),
            "prompt": prompt,
            "completion": chosen,
            "verdict": True,
            "provenance": {"source": "hardness_dpo_pairs", "pair_id": pair.get("id"),
                           "verifier": "lean4_kernel"},
        })
    return rows, drops


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", type=Path, default=PAIRS)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    for p in (args.pairs, args.frozen):
        if not p.exists():
            print(f"BLOCKED: {p} is missing", file=sys.stderr)
            return 2
    frozen_props = [str(f["prop"]) for f in json.loads(args.frozen.read_text())]
    rows, drops = build_sft_rows(_read_jsonl(args.pairs), frozen_props)
    if not rows:
        print(f"BLOCKED: no SFT rows survived; dropped {drops}", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(json.dumps({"rows": len(rows), "dropped": drops, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
