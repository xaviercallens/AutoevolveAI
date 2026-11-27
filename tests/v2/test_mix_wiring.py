"""Tests for ``ltm_learning_mix.py`` wiring into ``night_training_workflow.step_data`` (card C-0)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import night_training_workflow as ntw


def test_step_data_consumes_ltm_mix_and_records_unverified_share(tmp_path: Path) -> None:
    journal = ntw.ModelJournal(model="qwen-test", smoke=False)
    rows = ntw.step_data("qwen-test", journal, smoke=False)
    assert rows is not None and len(rows) > 0
    rec = journal.steps[-1]
    assert rec.step == ntw.Step.DATA
    assert rec.outcome == ntw.Outcome.OK
    assert str(ntw.LTM_MIX_PATH) in rec.detail
    assert rec.data["corpus_file"] == str(ntw.LTM_MIX_PATH)
    assert rec.data["unverified_share"] <= 0.30


def test_step_data_refuses_corpus_exceeding_30_percent_unverified(tmp_path: Path) -> None:
    """Negative control: a corpus at 31% unverified (31 unverified, 69 verified) is refused with BLOCKED."""
    bad_corpus = tmp_path / "diluted_31pct.jsonl"
    lines = []
    for i in range(69):
        lines.append(
            json.dumps(
                {
                    "prompt": f"verified task {i}",
                    "completion": f"def f_{i}(): return {i}",
                    "verified": True,
                    "verdict": True,
                    "origin": "sandbox",
                }
            )
        )
    for j in range(31):
        lines.append(
            json.dumps(
                {
                    "prompt": f"unverified row {j}",
                    "completion": f"def u_{j}(): return {j}",
                    "verified": False,
                    "verdict": None,
                    "origin": "sandbox",
                }
            )
        )
    bad_corpus.write_text("\n".join(lines) + "\n", encoding="utf-8")

    journal = ntw.ModelJournal(model="qwen-test", smoke=False)
    out = ntw.step_data("qwen-test", journal, smoke=False, corpus_override=bad_corpus)
    assert out is None
    rec = journal.steps[-1]
    assert rec.step == ntw.Step.DATA
    assert rec.outcome == ntw.Outcome.BLOCKED
    assert "31.00%" in rec.detail
    assert rec.data["unverified_share"] == 0.31
