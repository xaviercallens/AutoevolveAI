"""Tests for ``anse.v2.premise_prompt`` (card M-1)."""

from __future__ import annotations

from anse.v2.premise_prompt import HEADER, build, run_ab_arms


def test_build_prompt_header_k_and_identity() -> None:
    stmt = "theorem t1 : W.Δ = -16 := by\n  sorry"
    hits = [
        ("WeierstrassCurve.b₂", "WeierstrassCurve R → R"),
        ("WeierstrassCurve.b₄", "WeierstrassCurve R → R"),
        ("WeierstrassCurve.Δ", "WeierstrassCurve R → R"),
    ]
    assert build(stmt, hits, k=0) == stmt
    assert build(stmt, [], k=5) == stmt

    out = build(stmt, hits, k=2)
    lines = out.splitlines()
    assert lines[0] == HEADER
    assert lines[1] == "-- (WeierstrassCurve.b₂ : WeierstrassCurve R → R)"
    assert lines[2] == "-- (WeierstrassCurve.b₄ : WeierstrassCurve R → R)"
    assert "WeierstrassCurve.Δ : WeierstrassCurve" not in out
    assert out.endswith(stmt)


def test_run_ab_arms_bookkeeping_with_fake_prover_and_retriever() -> None:
    items = [
        {"id": "t1_a_T", "tier": "T1", "truth": True, "statement": "theorem t1_a_T : P"},
        {"id": "t1_a_F", "tier": "T1", "truth": False, "statement": "theorem t1_a_F : ¬P"},
        {"id": "t3_b_T", "tier": "T3", "truth": True, "statement": "theorem t3_b_T : Q"},
    ]

    def fake_retriever(stmt: str, k: int) -> list[tuple[str, str]]:
        return [(f"lemma_{i}", f"Sig {i} for {stmt}") for i in range(k)]

    def fake_prover(model: str, prompt: str, item: dict) -> bool:
        if not item["truth"]:
            return False
        if model == "deepseek" and HEADER in prompt:
            return True
        return item["tier"] == "T1" and model == "goedel"

    res = run_ab_arms(items, ["deepseek", "goedel"], fake_retriever, fake_prover, k=5)
    assert [r["id"] for r in res["runs"]["deepseek"]["k0"]] == [
        r["id"] for r in res["runs"]["deepseek"]["k5"]
    ]
    assert res["summary"]["deepseek"]["k0"]["T1"]["true_pass"] == 0
    assert res["summary"]["deepseek"]["k5"]["T1"]["true_pass"] == 1
    assert res["summary"]["deepseek"]["k5"]["T3"]["true_pass"] == 1
    assert res["summary"]["deepseek"]["k5"]["T1"]["false_accepted"] == 0
    assert res["summary"]["goedel"]["k0"]["T1"]["true_pass"] == 1
    assert res["summary"]["goedel"]["k0"]["T1"]["false_total"] == 1
    assert res["summary"]["goedel"]["k0"]["T1"]["false_accepted"] == 0

    # Also test negative control where an unsound fake prover accepts a false item
    unsound = run_ab_arms(
        items,
        ["bad"],
        fake_retriever,
        lambda _m, _p, _item: True,
        k=2,
    )
    assert unsound["summary"]["bad"]["k2"]["T1"]["false_accepted"] == 1
