"""Deterministic premise-retrieval prompt builder and A/B arm bookkeeping (card M-1)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

HEADER = "-- Retrieved premises (name : signature)"


def build(statement: str, hits: list[tuple[str, str]], k: int = 5) -> str:
    """Prepend up to *k* ``(name : signature)`` comment lines under a fixed header before *statement*.

    Deterministic; ``k <= 0`` or empty ``hits`` returns *statement* unchanged;
    never truncates a signature mid-token.
    """
    if k <= 0 or not hits:
        return statement

    selected = hits[:k]
    lines = [HEADER]
    for name, sig in selected:
        clean_name = name.strip()
        clean_sig = " ".join(sig.split())
        lines.append(f"-- ({clean_name} : {clean_sig})")
    lines.append("")
    lines.append(statement)
    return "\n".join(lines)


def run_ab_arms(
    items: list[dict[str, Any]],
    models: list[str],
    retriever: Callable[[str, int], list[tuple[str, str]]],
    prover: Callable[[str, str, dict[str, Any]], bool],
    k: int = 5,
) -> dict[str, Any]:
    """Run ``k=0`` and ``k=k`` premise-retrieval arms over the identical item list per model."""
    runs: dict[str, dict[str, list[dict[str, Any]]]] = {}
    summary: dict[str, dict[str, dict[str, Any]]] = {}

    for model in models:
        runs[model] = {"k0": [], f"k{k}": []}
        summary[model] = {}
        for arm_name, arm_k in (("k0", 0), (f"k{k}", k)):
            tier_totals: dict[str, dict[str, int]] = {}
            for item in items:
                stmt = str(item["statement"])
                hits = retriever(stmt, arm_k) if arm_k > 0 else []
                prompt = build(stmt, hits, k=arm_k)
                passed = bool(prover(model, prompt, item))
                rec = {
                    "id": item["id"],
                    "tier": item["tier"],
                    "truth": bool(item.get("truth", True)),
                    "passed": passed,
                    "prompt": prompt,
                }
                runs[model][arm_name].append(rec)
                tier = str(item["tier"])
                bucket = tier_totals.setdefault(
                    tier,
                    {"true_total": 0, "true_pass": 0, "false_total": 0, "false_accepted": 0},
                )
                if rec["truth"]:
                    bucket["true_total"] += 1
                    if passed:
                        bucket["true_pass"] += 1
                else:
                    bucket["false_total"] += 1
                    if passed:
                        bucket["false_accepted"] += 1
            summary[model][arm_name] = tier_totals

    return {"k": k, "runs": runs, "summary": summary}
