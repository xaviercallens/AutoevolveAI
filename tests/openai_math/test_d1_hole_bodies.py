"""Tests for scripts/openai_math/d1_hole_bodies.py (synthetic Lean snippets only).

Positive controls: identical, re-laid-out and alpha-renamed declarations must MATCH.
Negative controls: a changed constant, a body replaced by ``True``, a swapped global, a
``def``/``abbrev`` swap, a sorried challenge and a missing name must not MATCH.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "openai_math" / "d1_hole_bodies.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("d1_hole_bodies", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


d1 = _load()

CHAL = """import Mathlib

namespace OAI

namespace Toy

universe u

abbrev Config (k : ℕ) (X : Type u) := Fin k → X

def Proper (n : ℕ) (c : ℂ → Fin n) : Prop :=
  ∀ p q : ℂ, ‖p - q‖ = 1 → c p ≠ c q

def cost {X : Type u} [MetricSpace X] (s : Fin 2 → X) : (rs : List X) → ℝ
  | [] => 0
  | r :: rs => dist (s 0) r + cost s rs

def Main : Prop :=
  ∃ C : ℝ, 0 < C ∧ ∀ k : ℕ, Real.log (k + 1) ≤ C * k

def Hole (n : ℕ) : Fin n → ℕ := by
  sorry

theorem main_theorem : Main := by
  sorry

end Toy

end OAI
"""


def verdict(chal: str, sol: str, hole: str) -> str:
    return d1.compare_sources(chal, sol, [hole])[0]["verdict"]


def test_strip_comments_nested_and_line() -> None:
    src = "a /- x /- y -/ z -/ b -- tail\nc /-- doc -/ d"
    out = d1.strip_comments(src)
    assert d1.tokenize(out) == ["a", "b", "c", "d"]
    assert out.count("\n") == 1


def test_strip_comments_keeps_strings() -> None:
    out = d1.strip_comments('def s := "a -- not a comment"')
    assert '"a -- not a comment"' in out
    assert d1.tokenize(out)[-1] == '"a -- not a comment"'


def test_full_names_and_kinds() -> None:
    decls = {d.full_name: d for d in d1.extract_decls(CHAL)}
    assert decls["OAI.Toy.Config"].kind == "abbrev"
    assert decls["OAI.Toy.Proper"].kind == "def"
    assert decls["OAI.Toy.main_theorem"].kind == "theorem"
    assert decls["OAI.Toy.Proper"].line == 11
    assert "universe u" in decls["OAI.Toy.cost"].context


def test_pattern_match_body_stays_inside_decl() -> None:
    d = {x.full_name: x for x in d1.extract_decls(CHAL)}["OAI.Toy.cost"]
    assert "dist (s 0) r" in d.text
    assert "def Main" not in d.text


def test_dotted_and_root_names() -> None:
    src = "namespace A\nnamespace B.C\ndef D.e : ℕ := 1\ndef _root_.Z : ℕ := 2\nend B.C\nsection\ndef f : ℕ := 3\nend\nend A\n"
    names = {d.full_name for d in d1.extract_decls(src)}
    assert names == {"A.B.C.D.e", "Z", "A.f"}


def test_namespace_closed_component_wise() -> None:
    src = "namespace A.B\ndef x : ℕ := 1\nend B\ndef y : ℕ := 2\nend A\ndef z : ℕ := 3\n"
    names = {d.full_name for d in d1.extract_decls(src)}
    assert names == {"A.B.x", "A.y", "z"}


def test_sorry_only_vs_partial_sorry() -> None:
    src = "def a : ℕ := by\n  sorry\ndef b : ℕ := sorry\ndef c (n : ℕ) : ℕ := n + 1\ndecreasing_by sorry\n"
    d = {x.full_name: x for x in d1.extract_decls(src)}
    assert d1.sorry_only(d["a"]) and d1.sorry_only(d["b"])
    assert d1.has_sorry(d["c"]) and not d1.sorry_only(d["c"])


def test_not_found_keeps_challenge_sorry_flag() -> None:
    rec = d1.compare_sources(CHAL, "namespace OAI\nend OAI\n", ["OAI.Toy.Hole"])[0]
    assert rec["verdict"] == "NOT_FOUND"
    assert rec["challenge_has_sorry"] is True and rec["challenge_sorry_only"] is True


def test_shadow_candidates() -> None:
    sol = CHAL.replace("universe u", "universe u\n\ndef dist {X : Type u} (a b : X) : ℝ := 0")
    si: dict = {}
    for x in d1.extract_decls(sol, "solution"):
        si.setdefault(x.full_name, []).append(x)
    ci: dict = {}
    for x in d1.extract_decls(CHAL, "challenge"):
        ci.setdefault(x.full_name, []).append(x)
    rec = d1.compare_sources(CHAL, sol, ["OAI.Toy.cost"])[0]
    assert rec["verdict"] == "MATCHES"  # textually identical ...
    shadows = d1.shadow_candidates(si["OAI.Toy.cost"][0], si, ci, {"OAI.Toy.cost"})
    assert shadows == ["OAI.Toy.dist"]  # ... but `dist` may now mean OAI.Toy.dist
    assert d1.shadow_candidates(ci["OAI.Toy.cost"][0], ci, ci, {"OAI.Toy.cost"}) == []


def test_positive_self_match() -> None:
    for hole in ("OAI.Toy.Config", "OAI.Toy.Proper", "OAI.Toy.cost", "OAI.Toy.Main"):
        assert verdict(CHAL, CHAL, hole) == "MATCHES"


def test_positive_layout_and_comments() -> None:
    sol = CHAL.replace("  ∀ p q : ℂ,", "  -- a comment\n      ∀ p q : ℂ, /- inline -/").replace(
        "def Main : Prop :=\n  ∃", "def Main : Prop := ∃"
    )
    assert sol != CHAL
    assert verdict(CHAL, sol, "OAI.Toy.Proper") == "MATCHES"
    assert verdict(CHAL, sol, "OAI.Toy.Main") == "MATCHES"


def test_positive_alpha_rename() -> None:
    sol = CHAL.replace("∀ p q : ℂ, ‖p - q‖ = 1 → c p ≠ c q", "∀ x y : ℂ, ‖x - y‖ = 1 → c x ≠ c y")
    rec = d1.compare_sources(CHAL, sol, ["OAI.Toy.Proper"])[0]
    assert rec["verdict"] == "MATCHES"
    assert rec["renaming"] == {"p": "x", "q": "y"}
    assert rec["textually_identical"] is False


def test_alpha_rename_of_dotted_head() -> None:
    a = d1.tokenize("fun index => labels index.succ")
    b = d1.tokenize("fun i => labels i.succ")
    c = d1.tokenize("fun i => labels index.succ")
    assert d1.alpha_compare(a, b)[0] is True
    assert d1.alpha_compare(a, c)[0] is False


def test_negative_constant_changed() -> None:
    sol = CHAL.replace("‖p - q‖ = 1", "‖p - q‖ = 2")
    rec = d1.compare_sources(CHAL, sol, ["OAI.Toy.Proper"])[0]
    assert rec["verdict"] == "DIFFERS"
    assert rec["difference_in"] == "body"
    assert "1" in rec["challenge_window"] and "2" in rec["solution_window"]


def test_negative_body_true() -> None:
    sol = CHAL.replace("def Main : Prop :=\n  ∃ C : ℝ, 0 < C ∧ ∀ k : ℕ, Real.log (k + 1) ≤ C * k", "def Main : Prop := True")
    assert sol != CHAL
    assert verdict(CHAL, sol, "OAI.Toy.Main") == "DIFFERS"


def test_negative_global_swaps_are_not_renamings() -> None:
    undotted = CHAL.replace("dist (s 0) r", "edist (s 0) r")
    dotted = CHAL.replace("Real.log", "Real.exp")
    assert verdict(CHAL, undotted, "OAI.Toy.cost") == "DIFFERS"
    assert verdict(CHAL, dotted, "OAI.Toy.Main") == "DIFFERS"


def test_negative_bound_to_free_is_not_renaming() -> None:
    # Replacing the bound ``q`` by the free ``p``'s sibling global ``z`` breaks the binder.
    sol = CHAL.replace("‖p - q‖ = 1 → c p ≠ c q", "‖p - z‖ = 1 → c p ≠ c z")
    assert verdict(CHAL, sol, "OAI.Toy.Proper") == "DIFFERS"


def test_negative_kind_swap() -> None:
    sol = CHAL.replace("abbrev Config", "def Config")
    rec = d1.compare_sources(CHAL, sol, ["OAI.Toy.Config"])[0]
    assert rec["verdict"] == "DIFFERS"
    assert "abbrev" in rec["reason"]


def test_sorried_and_not_found() -> None:
    assert verdict(CHAL, CHAL, "OAI.Toy.Hole") == "SORRIED_IN_CHALLENGE"
    rec = d1.compare_sources(CHAL, "namespace OAI\nend OAI\n", ["OAI.Toy.Proper"])[0]
    assert rec["verdict"] == "NOT_FOUND"
    assert "solution" in rec["reason"]


def test_ambiguous_duplicate() -> None:
    dup = CHAL + "\nnamespace OAI\nnamespace Toy\ndef Main : Prop := True\nend Toy\nend OAI\n"
    assert verdict(CHAL, dup, "OAI.Toy.Main") == "AMBIGUOUS"
    assert verdict(dup, CHAL, "OAI.Toy.Main") == "AMBIGUOUS"


def test_set_builder_bar_is_not_match_arm() -> None:
    toks = d1.tokenize("{x | p x ∧ fun y => g y}")
    bound = d1.bound_identifiers(toks)
    assert "x" in bound and "y" in bound
    assert "g" not in bound and "p" not in bound


def test_import_closure(tmp_path: Path) -> None:
    (tmp_path / "OAI" / "A").mkdir(parents=True)
    (tmp_path / "OAI" / "A" / "Main.lean").write_text("import Mathlib\nimport OAI.A.Defs\n\nnamespace OAI\nend OAI\n", encoding="utf-8")
    (tmp_path / "OAI" / "A" / "Defs.lean").write_text("namespace OAI\ndef h : ℕ := 1\nend OAI\n", encoding="utf-8")
    (tmp_path / "OAI" / "A" / "Unused.lean").write_text("namespace OAI\ndef h : ℕ := 2\nend OAI\n", encoding="utf-8")
    files = d1.import_closure(tmp_path, "OAI.A.Main")
    assert sorted(p.name for p in files) == ["Defs.lean", "Main.lean"]
    idx = d1.index_files(files, tmp_path)
    assert [d.file for d in idx["OAI.h"]] == ["OAI/A/Defs.lean"]


try:
    from hypothesis import given
    from hypothesis import strategies as st

    HAVE_HYPOTHESIS = True
except ImportError:  # hypothesis is not installed for /usr/bin/python3 on this host
    HAVE_HYPOTHESIS = False

if HAVE_HYPOTHESIS:

    @given(st.lists(st.sampled_from(["a", "b", "x", "+", "(", ")", "1", "Real.log"]), max_size=30))
    def test_alpha_compare_reflexive(toks: list[str]) -> None:
        equal, at, renaming = d1.alpha_compare(toks, toks)
        assert equal and at == -1
        assert renaming == {}

else:

    @pytest.mark.skip(reason="hypothesis not installed for /usr/bin/python3")
    def test_alpha_compare_reflexive() -> None:
        assert d1.alpha_compare(["a"], ["a"])[0]
