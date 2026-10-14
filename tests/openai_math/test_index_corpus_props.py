"""Property tests for the pure helpers in scripts/openai_math/index_corpus.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "openai_math" / "index_corpus.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("index_corpus_props", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ic = _load()
LEAN_KEYWORDS = {"namespace", "end", "theorem", "lemma", "import", "axiom", "sorry", "private", "protected"}
IDENT = st.from_regex(r"[A-Za-z][A-Za-z0-9_]{0,8}", fullmatch=True).filter(lambda s: s not in LEAN_KEYWORDS)
AXIOM = st.sampled_from(["propext", "Classical.choice", "Quot.sound", "Lean.ofReduceBool", "sorryAx", "cheat"])


@given(st.lists(AXIOM, max_size=6))
def test_untrusted_axioms_is_exactly_the_complement_of_the_whitelist(axioms: list[str]) -> None:
    bad = ic.untrusted_axioms(axioms)
    assert set(bad) == set(axioms) - {"propext", "Classical.choice", "Quot.sound"}
    assert bad == sorted(bad)


@given(st.lists(IDENT, min_size=1, max_size=4), IDENT)
def test_theorem_is_qualified_by_its_enclosing_namespaces(namespaces: list[str], thm: str) -> None:
    opening = "".join(f"namespace {n}\n" for n in namespaces)
    closing = "".join(f"end {n}\n" for n in reversed(namespaces))
    src = f"{opening}theorem {thm} : True := trivial\n{closing}theorem after : True := trivial\n"
    names = ic.declared_theorem_names(src)
    assert names[0] == ".".join([*namespaces, thm])
    assert names[1] == "after"
    assert len(names) == 2


@given(IDENT)
def test_commented_out_declarations_are_ignored(thm: str) -> None:
    src = f"-- theorem {thm} : True := trivial\n/- theorem {thm}2 : True := trivial -/\n"
    assert ic.declared_theorem_names(src) == []
    assert ic.lean_imports(f"-- import {thm}\nimport Real.{thm}\n") == [f"Real.{thm}"]
