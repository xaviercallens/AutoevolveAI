"""Tests for the master-math run-two instrument: the kernel-verdict parser,
proof extraction, the locked problem set, and the run summary."""

from __future__ import annotations

import sys
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "hardness"))  # run_ladder's own flat import

from scripts.hardness import run_ladder as rl  # noqa: E402
from scripts.master_math import problems, run_master  # noqa: E402

bl = rl.bl

SRC = "theorem foo (n : Nat) : n + 0 = n := by simp\n\n#print axioms foo\n"


def test_verdict_requires_the_axioms_line_for_this_theorem() -> None:
    # `#exit` (or an aborted elaboration) suppresses the #print line; rc stays 0.
    # The old parser read that as "no axioms" -> clean. Measured live 2026-09-27.
    exited = bl.verdict(SRC, 0, "warning: declaration uses 'sorry'\n")
    assert exited["clean"] is False
    assert exited["axioms_printed"] is False
    other = bl.verdict(SRC, 0, "'bar' depends on axioms: [propext]\n")
    assert other["clean"] is False


def test_verdict_accepts_only_trusted_axioms_and_rc_zero() -> None:
    assert bl.verdict(SRC, 0, "'foo' depends on axioms: [propext, Quot.sound]\n")["clean"] is True
    assert bl.verdict(SRC, 0, "'foo' does not depend on any axioms\n")["clean"] is True
    assert bl.verdict(SRC, 0, "'foo' depends on axioms: [propext, sorryAx]\n")["clean"] is False
    assert bl.verdict(SRC, 0, "'foo' depends on axioms: [cheat]\n")["clean"] is False
    assert bl.verdict(SRC, 1, "'foo' depends on axioms: [propext]\n")["clean"] is False


def test_axioms_line_for_parses_names() -> None:
    out = "'a.b' depends on axioms: [propext, Classical.choice]\n"
    assert bl.axioms_line_for(out, "a.b") == ["propext", "Classical.choice"]
    assert bl.axioms_line_for(out, "a") is None


body_text = st.text(alphabet=st.characters(blacklist_characters="`", blacklist_categories=("Cs",)),
                    min_size=1, max_size=80).filter(lambda s: "sorry" not in s and s.strip() != "")


@given(body_text)
def test_extract_proof_returns_body_of_last_block(body: str) -> None:
    item = {"id": "mm_x"}
    first = "```lean4\ntheorem mm_x : True := by\n  sorry\n```\n"
    last = f"```lean4\ntheorem mm_x : True := by {body}\n```\n"
    got = rl.extract_proof(first + last, item)
    assert got is not None
    assert got == f"by {body}".strip()
    assert "sorry" not in got


def test_extract_proof_ignores_sorry_only_answers() -> None:
    text = "```lean4\ntheorem mm_x : 1 = 1 := by\n  sorry\n```"
    assert rl.extract_proof(text, {"id": "mm_x"}) is None
    assert rl.extract_proof("no code at all", {"id": "mm_x"}) is None


def test_problem_set_is_locked_and_pinned() -> None:
    ids = problems.item_ids()
    # 20 receipts problems with #10 split in two, plus 3 regen-only titles
    assert len(ids) == len(set(ids)) == 24
    for p in problems.PROBLEMS:
        assert p["statement"].startswith(f"theorem {p['id']} ")
        assert "import Mathlib\n" not in p["header"]
        assert "sorry" not in p["reference"] and "sorry" not in p["refutation"]
        assert p["fidelity"] in {"faithful", "proxy", "special-case"}
        # a proxy must say what it leaves out
        if p["fidelity"] != "faithful":
            assert p.get("note")
    assert all(b["reason"] for b in problems.BLOCKED)
    assert len(problems.BLOCKED) == 7


def test_summarize_counts_repair_and_false_acceptance() -> None:
    runs = [
        {"model": "m", "id": "a", "truth": True, "round": 0, "clean": True},
        {"model": "m", "id": "b", "truth": True, "round": 0, "clean": False},
        {"model": "m", "id": "b", "truth": True, "round": 1, "clean": True},
        {"model": "m", "id": "c", "truth": True, "round": 0, "clean": False},
        {"model": "m", "id": "c_F", "truth": False, "round": 0, "clean": False},
        {"model": "m", "id": "c_F", "truth": False, "round": 1, "clean": True},
    ]
    s = run_master.summarize(runs)["m"]
    assert (s["true_n"], s["pass_r0"], s["pass_r1"]) == (3, 1, 2)
    assert (s["false_n"], s["false_accepted"]) == (1, 1)
