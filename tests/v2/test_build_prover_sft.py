"""SFT rows for the prover adapter come only from kernel-verified, non-frozen proofs."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

REPO = Path(__file__).resolve().parents[2]


def _mod() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_prover_sft_under_test", REPO / "scripts/hardness/build_prover_sft.py"
    )
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _pair(item: str, chosen: str = "```lean4\ntheorem t : 1 = 1 := by rfl\n```", **kw: object) -> dict:
    base = {"id": f"dpo_{item}", "item_id": item, "tier": "T1", "prompt": f"prove {item}",
            "chosen": chosen, "provenance": "{'verifier': 'lean4_kernel'}"}
    base.update(kw)
    return base


def test_rows_are_verified_and_counted_by_drop_reason() -> None:
    m = _mod()
    pairs = [
        _pair("a"),
        _pair("a", id="dpo_a2"),  # duplicate item
        _pair("b", chosen="```lean4\ntheorem t : 1 = 1 := by sorry\n```"),
        _pair("c", provenance="{'verifier': 'none'}"),
        _pair("d", chosen=""),
        _pair("e", chosen="```lean4\ntheorem t : (a b : ℕ) : a + b = b + a := by omega\n```"),
    ]
    rows, drops = m.build_sft_rows(pairs, ["(a b : ℕ) : a + b = b + a"])
    assert [r["item_id"] for r in rows] == ["a"]
    assert rows[0]["verdict"] is True and rows[0]["completion"].startswith("```lean4")
    assert drops == {"no_proof": 1, "unsound_text": 1, "not_kernel_verified": 1,
                     "frozen_leak": 1, "duplicate_item": 1}


def test_rows_pass_the_trainers_verified_gate_and_cli_blocks_on_no_rows(tmp_path: Path) -> None:
    m = _mod()
    rows, _ = m.build_sft_rows([_pair("a")], [])
    wf_spec = importlib.util.spec_from_file_location(
        "wf_for_sft_test", REPO / "scripts/night_training_workflow.py")
    assert wf_spec is not None and wf_spec.loader is not None
    wf = importlib.util.module_from_spec(wf_spec)
    sys.modules[wf_spec.name] = wf  # its dataclasses resolve annotations via sys.modules
    wf_spec.loader.exec_module(wf)
    assert wf._is_verified_row(rows[0]) is True
    pairs = tmp_path / "p.jsonl"
    pairs.write_text(json.dumps(_pair("x", chosen="sorry")) + "\n")
    frozen = tmp_path / "f.json"
    frozen.write_text("[]")
    out = tmp_path / "o.jsonl"
    assert m.main(["--pairs", str(pairs), "--frozen", str(frozen), "--out", str(out)]) == 2
    assert not out.exists()
    assert m.main(["--pairs", str(tmp_path / "missing"), "--frozen", str(frozen)]) == 2
