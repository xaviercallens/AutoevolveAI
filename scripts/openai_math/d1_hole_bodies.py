"""D1: extract Comparator definition-hole declarations from Lean source and compare them.

Comparator's ``definitionHoleMatches`` checks a hole's name, universe levels, type and
safety, not its body. This tool does the missing body check *textually*: it strips
comments, tokenises, and compares the challenge declaration of each hole with the
solution declaration found in the solution module's import closure, allowing only a
consistent renaming of identifiers that are bound inside the declaration.

Text comparison is not elaboration. A MATCHES verdict here means "token-identical up to
bound-variable renaming", never "elaborates to the same Expr"; the surrounding ``open`` /
``variable`` / ``universe`` lines are recorded so that a human can check the context.

Mechanical verdicts, applied in this order (fixed in the D1 preregistration):

1. NOT_FOUND            -- the hole is missing on the challenge or the solution side.
2. AMBIGUOUS            -- the name is declared more than once on one side (parser flag).
3. SORRIED_IN_CHALLENGE -- the challenge declaration contains a ``sorry``/``admit`` token.
4. MATCHES              -- same kind, token-equal up to a bound-variable bijection.
5. DIFFERS              -- anything else; the first differing token window is quoted.

Subcommands (all read-only on the upstream clone):

* ``run``      one JSON chunk per challenge into ``<out>/chunks/`` (finished chunks skipped).
* ``controls`` positive / negative controls on real challenge files and mutated copies.
* ``assemble`` merge chunks (+ optional by-eye review JSON) into the final JSON and table.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- lexing

DECL_KINDS: tuple[str, ...] = (
    "def",
    "abbrev",
    "theorem",
    "lemma",
    "instance",
    "structure",
    "inductive",
    "class",
    "opaque",
    "axiom",
    "example",
    "irreducible_def",
)
MODIFIERS: tuple[str, ...] = ("private", "protected", "noncomputable", "partial", "unsafe", "nonrec")
# Column-0 words that start a new command and therefore end the current declaration.
COMMAND_STARTS: frozenset[str] = frozenset(
    set(DECL_KINDS)
    | set(MODIFIERS)
    | {
        "end",
        "namespace",
        "section",
        "open",
        "variable",
        "universe",
        "attribute",
        "mutual",
        "set_option",
        "macro",
        "macro_rules",
        "syntax",
        "notation",
        "infix",
        "infixl",
        "infixr",
        "prefix",
        "postfix",
        "scoped",
        "local",
        "elab",
        "import",
        "export",
        "omit",
        "include",
    }
)
KEYWORDS: frozenset[str] = frozenset(
    {
        "fun",
        "λ",
        "let",
        "have",
        "show",
        "from",
        "by",
        "do",
        "if",
        "then",
        "else",
        "match",
        "with",
        "at",
        "in",
        "where",
        "sorry",
        "admit",
        "Type",
        "Sort",
        "Prop",
        "true",
        "false",
        "calc",
        "suffices",
        "obtain",
        "using",
    }
    | set(DECL_KINDS)
    | set(MODIFIERS)
)
# Tokens after which identifiers up to a terminator are binders.
BINDER_INTRO: frozenset[str] = frozenset({"fun", "λ", "∀", "∃", "∃!", "∑", "∏", "⋃", "⋂", "∫", "∮", "Π", "Σ", "let", "have"})
BINDER_STOP: frozenset[str] = frozenset({",", "=>", "↦", ":", "∈", ":=", "in", "|", "∉", "<", "≤", ">", "≥", "≠", "⊆"})
OPEN_BRACKETS: dict[str, str] = {"(": ")", "{": "}", "[": "]", "⦃": "⦄", "⟨": "⟩"}

_IDENT_PART = r"(?:«[^»]*»|[^\W\d][\w'!?₀-₉ₐ-ₜ]*)"
_IDENT = rf"{_IDENT_PART}(?:\.{_IDENT_PART})*"
_MULTI = [":=", "=>", "->", "<-", "<->", "::", "++", "//", "∃!", "⁻¹", "≫=", "|>.", "<|", "|>", "..", ".."]
_MULTI_RE = "|".join(re.escape(m) for m in sorted(set(_MULTI), key=len, reverse=True))
TOKEN_RE = re.compile(rf'"(?:[^"\\]|\\.)*"|\d+(?:\.\d+)?|{_MULTI_RE}|{_IDENT}|\S')


def strip_comments(src: str) -> str:
    """Remove ``--`` line comments and (nested) ``/- -/`` block comments, keep strings.

    Newlines inside removed block comments are kept so that line numbers survive.
    """
    out: list[str] = []
    i = 0
    n = len(src)
    depth = 0
    while i < n:
        two = src[i : i + 2]
        if depth > 0:
            if two == "/-":
                depth += 1
                i += 2
            elif two == "-/":
                depth -= 1
                i += 2
            else:
                if src[i] == "\n":
                    out.append("\n")
                i += 1
            continue
        if two == "/-":
            depth = 1
            i += 2
        elif two == "--":
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(src[i : j + 1])
            i = j + 1
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def tokenize(text: str) -> list[str]:
    """Tokenise comment-free Lean text; whitespace is dropped."""
    return TOKEN_RE.findall(text)


def normalise_ws(text: str) -> str:
    """Collapse all whitespace runs to single spaces."""
    return " ".join(text.split())


# --------------------------------------------------------------------------- declarations


@dataclass
class Decl:
    """One column-0 declaration with its scope context."""

    full_name: str
    kind: str
    modifiers: list[str]
    attributes: list[str]
    file: str
    line: int
    end_line: int
    text: str  # comment-stripped declaration text, from the kind keyword on
    context: list[str] = field(default_factory=list)  # active open/variable/universe lines

    @property
    def tokens_after_name(self) -> list[str]:
        """Tokens after ``kind name`` (signature + body), name and universe params removed."""
        toks = tokenize(self.text)
        k = 1  # toks[0] is the kind keyword
        if self.kind == "class inductive":
            k = 2
        if k < len(toks) and toks[k] not in (":", "(", "{", "[", "⦃", "where"):
            k += 1  # the name
            if k + 1 < len(toks) and toks[k] == "." and toks[k + 1] == "{":
                close = toks.index("}", k)
                k = close + 1
        return toks[k:]


_HEAD_RE = re.compile(
    r"^(?P<attrs>(?:@\[[^\]]*\]\s*)*)(?P<mods>(?:(?:" + "|".join(MODIFIERS) + r")\s+)*)"
    r"(?P<kind>class\s+inductive|" + "|".join(DECL_KINDS) + r")\b\s*(?P<rest>.*)$"
)
_ATTR_ONLY_RE = re.compile(r"^(?:@\[[^\]]*\]\s*)+$")


def _first_word(line: str) -> str:
    m = re.match(r"[^\s(\[{]+", line)
    return m.group(0) if m else ""


def _starts_command(line: str) -> bool:
    if not line or line[0].isspace():
        return False
    if line.startswith("@[") or line.startswith("#"):
        return True
    return _first_word(line) in COMMAND_STARTS


def _decl_name(rest: str) -> str:
    m = re.match(_IDENT, rest)
    if not m:
        return ""
    name = m.group(0)
    return name


def extract_decls(src: str, file: str = "<string>") -> list[Decl]:
    """Extract column-0 declarations with fully qualified names from Lean source."""
    lines = strip_comments(src).split("\n")
    # scope stack: (kind, namespace components, context lines)
    scopes: list[tuple[str, list[str], list[str]]] = [("file", [], [])]
    decls: list[Decl] = []
    pending_attrs: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line or line[0].isspace():
            i += 1
            continue
        word = _first_word(line)
        if _ATTR_ONLY_RE.match(line):
            pending_attrs.extend(re.findall(r"@\[[^\]]*\]", line))
            i += 1
            continue
        if word == "namespace":
            for comp in line.split()[1].split("."):
                scopes.append(("namespace", [comp], []))
            i += 1
            continue
        if word == "section" or line.startswith("noncomputable section"):
            scopes.append(("section", [], []))
            i += 1
            continue
        if word == "end":
            parts = line.split()
            n_pop = len(parts[1].split(".")) if len(parts) > 1 else 1
            for _ in range(n_pop):
                if len(scopes) > 1:
                    scopes.pop()
            i += 1
            continue
        if word in ("open", "variable", "universe", "omit", "include") and not re.search(r"\bin\s*$", line):
            j = i + 1
            block = [line]
            while j < len(lines) and lines[j][:1].isspace() and lines[j].strip():
                block.append(lines[j].rstrip())
                j += 1
            scopes[-1][2].append(normalise_ws(" ".join(block)))
            i = j
            continue
        m = _HEAD_RE.match(line)
        if m:
            kind = re.sub(r"\s+", " ", m.group("kind"))
            rest = m.group("rest")
            name = _decl_name(rest) if kind not in ("example",) else ""
            if name in KEYWORDS:
                name = ""
            j = i + 1
            while j < len(lines) and not _starts_command(lines[j]):
                j += 1
            body_lines = [lines[i][m.start("kind") :]] + lines[i + 1 : j]
            while body_lines and not body_lines[-1].strip():
                body_lines.pop()
            ns = [c for s in scopes for c in s[1]]
            bare = name.split(".{")[0]
            if bare.startswith("_root_."):
                full = bare[len("_root_.") :]
            else:
                full = ".".join(ns + [bare]) if bare else ""
            attrs = pending_attrs + re.findall(r"@\[[^\]]*\]", m.group("attrs"))
            pending_attrs = []
            decls.append(
                Decl(
                    full_name=full,
                    kind=kind,
                    modifiers=m.group("mods").split(),
                    attributes=attrs,
                    file=file,
                    line=i + 1,
                    end_line=i + len(body_lines),
                    text="\n".join(body_lines),
                    context=[c for s in scopes for c in s[2]],
                )
            )
            i = j
            continue
        pending_attrs = []
        i += 1
    return decls


# --------------------------------------------------------------------------- binders and comparison


def bound_identifiers(tokens: list[str]) -> set[str]:
    """Identifiers that occur in a binder position somewhere in ``tokens``.

    Binder positions: after ``fun λ ∀ ∃ ∑ ∏ ⋃ ⋂ ∫ let have`` up to a terminator; the
    leading identifiers of a bracket group followed by ``:``, ``//`` or ``|``
    (``(a b : T)``, ``{x // p}``, ``{x | p}``, ``[inst : C]``); and pattern variables
    between a match-arm ``|`` and ``=>``.
    """
    bound: set[str] = set()

    def is_ident(t: str) -> bool:
        return bool(re.fullmatch(_IDENT, t)) and "." not in t and t not in KEYWORDS

    n = len(tokens)
    # A "|" is a match arm only at bracket depth 0 or after a match/fun at the same depth.
    arm_ok: list[bool] = []
    seen_with: list[bool] = [True]
    for tok in tokens:
        if tok in OPEN_BRACKETS:
            seen_with.append(False)
        elif tok in OPEN_BRACKETS.values() and len(seen_with) > 1:
            seen_with.pop()
        elif tok in ("with", "fun", "λ"):
            seen_with[-1] = True
        arm_ok.append(seen_with[-1])
    for idx, tok in enumerate(tokens):
        if tok in BINDER_INTRO:
            j = idx + 1
            depth = 0
            while j < n:
                t = tokens[j]
                if t in OPEN_BRACKETS:
                    depth += 1
                elif t in OPEN_BRACKETS.values():
                    depth -= 1
                    if depth < 0:
                        break
                elif depth == 0 and t in BINDER_STOP:
                    break
                if is_ident(t) and (depth == 0 or tokens[j - 1] in ("⟨", "(", ",")):
                    bound.add(t)
                j += 1
        elif tok in OPEN_BRACKETS and tok != "⟨":
            j = idx + 1
            names: list[str] = []
            while j < n and is_ident(tokens[j]):
                names.append(tokens[j])
                j += 1
            if names and j < n and tokens[j] in (":", "//", "|"):
                bound.update(names)
        elif tok == "|" and arm_ok[idx]:
            j = idx + 1
            seg: list[str] = []
            while j < n and tokens[j] not in ("=>", "|", ":="):
                seg.append(tokens[j])
                j += 1
            if j < n and tokens[j] == "=>":
                bound.update(t for t in seg if is_ident(t))
    return bound


def alpha_compare(a: list[str], b: list[str]) -> tuple[bool, int, dict[str, str]]:
    """Compare token lists up to a consistent bijection of bound identifiers.

    Returns ``(equal, first_mismatch_index, renaming)``; ``first_mismatch_index`` is -1
    when equal. Identifiers may be renamed only if bound on both sides; dotted names,
    keywords and free (global) identifiers must match exactly.
    """
    bound_a = bound_identifiers(a)
    bound_b = bound_identifiers(b)
    fwd: dict[str, str] = {}
    bwd: dict[str, str] = {}
    for idx, (x, y) in enumerate(zip(a, b)):
        if x in fwd or y in bwd:
            if fwd.get(x) != y or bwd.get(y) != x:
                return False, idx, {k: v for k, v in fwd.items() if k != v}
            continue
        if x == y:
            head = x.partition(".")[0]
            if "." in x and (fwd.get(head, head) != head or bwd.get(head, head) != head):
                return False, idx, {k: v for k, v in fwd.items() if k != v}
            if x in bound_a or y in bound_b:
                fwd[x] = y
                bwd[y] = x
            continue
        if x in bound_a and y in bound_b:
            fwd[x] = y
            bwd[y] = x
            continue
        hx, _, tx = x.partition(".")
        hy, _, ty = y.partition(".")
        if tx and tx == ty and hx != hy:
            # ``index.succ`` vs ``i.succ``: the head is a bound variable, the tail a field.
            if fwd.get(hx) == hy and bwd.get(hy) == hx:
                continue
            if hx not in fwd and hy not in bwd and hx in bound_a and hy in bound_b:
                fwd[hx] = hy
                bwd[hy] = hx
                continue
        return False, idx, {k: v for k, v in fwd.items() if k != v}
    renaming = {k: v for k, v in fwd.items() if k != v}
    if len(a) != len(b):
        return False, min(len(a), len(b)), renaming
    return True, -1, renaming


def _signature_length(tokens: list[str]) -> int:
    """Index of the first ``:=``/``where``/match-arm ``|`` at bracket depth 0."""
    depth = 0
    for idx, t in enumerate(tokens):
        if t in OPEN_BRACKETS:
            depth += 1
        elif t in OPEN_BRACKETS.values():
            depth -= 1
        elif depth == 0 and (t in (":=", "where") or (t == "|" and idx > 0)):
            return idx
    return len(tokens)


def _window(tokens: list[str], idx: int, width: int = 10) -> str:
    lo = max(0, idx - width)
    hi = min(len(tokens), idx + width)
    return " ".join(tokens[lo:hi])


def has_sorry(decl: Decl) -> bool:
    """True if the comment-stripped declaration contains a ``sorry``/``admit`` token."""
    return any(t in ("sorry", "admit") for t in tokenize(decl.text))


def sorry_only(decl: Decl) -> bool:
    """True if everything after the signature is ``sorry``/``admit`` (optionally ``by``)."""
    toks = decl.tokens_after_name
    body = toks[_signature_length(toks) :]
    if body[:1] == [":="]:
        body = body[1:]
    if body[:1] == ["by"]:
        body = body[1:]
    return body in (["sorry"], ["admit"])


def compare_hole(name: str, chal: list[Decl], sol: list[Decl]) -> dict[str, Any]:
    """Mechanical verdict for one hole given its challenge and solution declarations."""
    rec: dict[str, Any] = {
        "hole": name,
        "challenge": [_loc(d) for d in chal],
        "solution": [_loc(d) for d in sol],
    }
    if chal:
        rec["challenge_has_sorry"] = any(has_sorry(d) for d in chal)
        rec["challenge_sorry_only"] = all(sorry_only(d) for d in chal)
        rec["challenge_text"] = normalise_ws(chal[0].text)
        rec["challenge_context"] = chal[0].context
    if sol:
        rec["solution_has_sorry"] = any(has_sorry(d) for d in sol)
        rec["solution_text"] = normalise_ws(sol[0].text)
        rec["solution_context"] = sol[0].context
    if not chal or not sol:
        rec["verdict"] = "NOT_FOUND"
        rec["reason"] = "missing in " + ("challenge" if not chal else "solution import closure")
        return rec
    if len(chal) > 1 or len(sol) > 1:
        rec["verdict"] = "AMBIGUOUS"
        rec["reason"] = f"{len(chal)} challenge / {len(sol)} solution declarations"
        return rec
    c, s = chal[0], sol[0]
    rec["context_differs"] = c.context != s.context
    ca, sa = c.tokens_after_name, s.tokens_after_name
    equal, at, renaming = alpha_compare(ca, sa)
    rec["renaming"] = renaming
    rec["textually_identical"] = ca == sa
    rec["kind"] = {"challenge": c.kind, "solution": s.kind}
    if rec["challenge_has_sorry"]:
        rec["verdict"] = "SORRIED_IN_CHALLENGE"
        rec["reason"] = "challenge declaration contains sorry/admit: genuine hole, meaning set by the solution"
        return rec
    if c.kind != s.kind:
        rec["verdict"] = "DIFFERS"
        rec["reason"] = f"declaration kind {c.kind!r} vs {s.kind!r}"
        return rec
    if equal:
        rec["verdict"] = "MATCHES"
        rec["reason"] = "token-identical" if not renaming else "token-identical up to bound-variable renaming"
        return rec
    sig_len = _signature_length(ca)
    rec["verdict"] = "DIFFERS"
    rec["difference_in"] = "signature" if at < sig_len else "body"
    rec["reason"] = f"first differing token #{at} ({rec['difference_in']})"
    rec["challenge_window"] = _window(ca, at)
    rec["solution_window"] = _window(sa, at)
    return rec


def _loc(d: Decl) -> dict[str, Any]:
    return {"file": d.file, "line": d.line, "end_line": d.end_line, "kind": d.kind, "modifiers": d.modifiers, "attributes": d.attributes}


# --------------------------------------------------------------------------- import closure


def module_path(root: Path, module: str) -> Path:
    """``OAI.A.B`` -> ``<root>/OAI/A/B.lean``."""
    return root / (module.replace(".", "/") + ".lean")


def imports_of(src: str) -> list[str]:
    """Modules named by ``import`` lines in the file header."""
    out: list[str] = []
    for line in strip_comments(src).split("\n"):
        s = line.strip()
        if not s or s.startswith("prelude") or s.startswith("module"):
            continue
        if s.startswith("import ") or s.startswith("public import "):
            out.extend(s.split()[1:] if s.startswith("import ") else s.split()[2:])
            continue
        break
    return out


def import_closure(root: Path, module: str) -> list[Path]:
    """Files of ``module`` and every import of it that exists under ``root``."""
    seen: set[str] = set()
    order: list[Path] = []
    stack = [module]
    while stack:
        mod = stack.pop()
        if mod in seen:
            continue
        seen.add(mod)
        p = module_path(root, mod)
        if not p.is_file():
            continue
        order.append(p)
        stack.extend(imports_of(p.read_text(encoding="utf-8")))
    return order


def index_files(paths: list[Path], root: Path) -> dict[str, list[Decl]]:
    """Map full name -> declarations over the given files."""
    idx: dict[str, list[Decl]] = {}
    for p in paths:
        rel = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
        for d in extract_decls(p.read_text(encoding="utf-8"), rel):
            if d.full_name:
                idx.setdefault(d.full_name, []).append(d)
    return idx


def _opened_namespaces(context: list[str]) -> list[str]:
    """Namespaces named by ``open`` lines (``open scoped`` included; ``hiding``/``renaming`` cut)."""
    out: list[str] = []
    for line in context:
        toks = line.split()
        if not toks or toks[0] != "open":
            continue
        for t in toks[1:]:
            if t in ("scoped", "in") or t.startswith("("):
                continue
            if t in ("hiding", "renaming"):
                break
            out.append(t)
    return out


def shadow_candidates(decl: Decl, sol_idx: dict[str, list[Decl]], chal_idx: dict[str, list[Decl]], holes: set[str]) -> list[str]:
    """Free identifiers of ``decl`` that may resolve to a constant declared in the solution
    closure but not in the challenge file (same text, possibly a different meaning).

    Candidates are ``prefix.ident`` for every prefix of the declaration's own namespace
    and every namespace opened in its context; other hole names are excluded because they
    are compared on their own.
    """
    toks = decl.tokens_after_name
    bound = bound_identifiers(toks)
    ns = decl.full_name.split(".")[:-1]
    prefixes = [".".join(ns[:k]) for k in range(len(ns), 0, -1)] + _opened_namespaces(decl.context)
    hits: set[str] = set()
    for t in toks:
        if not re.fullmatch(_IDENT, t) or t in KEYWORDS:
            continue
        if t.partition(".")[0] in bound:
            continue
        for pre in prefixes:
            cand = f"{pre}.{t}"
            if cand in sol_idx and cand not in chal_idx and cand not in holes and cand != decl.full_name:
                hits.add(cand)
    return sorted(hits)


def name_hints(paths: list[Path], root: Path, name: str) -> list[str]:
    """``file:line`` of raw lines mentioning the last name component after a decl keyword."""
    last = re.escape(name.split(".")[-1])
    pat = re.compile(rf"\b(?:{'|'.join(DECL_KINDS)})\s+(?:[\w.]*\.)?{last}\b")
    hits: list[str] = []
    for p in paths:
        for k, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if pat.search(line):
                hits.append(f"{p.relative_to(root)}:{k}")
    return hits[:20]


# --------------------------------------------------------------------------- challenge level


def audit_challenge(root: Path, name: str) -> dict[str, Any]:
    """Compare every definition hole of one ComparatorChallenges config."""
    cfg_path = root / "ComparatorChallenges" / f"{name}.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    chal_path = root / "ComparatorChallenges" / f"{name}.lean"
    chal_idx = index_files([chal_path], root)
    closure = import_closure(root, cfg["solution_module"])
    sol_idx = index_files(closure, root)
    holes = []
    hole_names = set(cfg.get("definition_names", []))
    for hole in cfg.get("definition_names", []):
        rec = compare_hole(hole, chal_idx.get(hole, []), sol_idx.get(hole, []))
        if rec["verdict"] == "NOT_FOUND":
            rec["hints"] = name_hints(closure + [chal_path], root, hole)
        if sol_idx.get(hole):
            rec["shadow_candidates"] = shadow_candidates(sol_idx[hole][0], sol_idx, chal_idx, hole_names)
        holes.append(rec)
    return {
        "challenge": name,
        "config": str(cfg_path.relative_to(root)),
        "solution_module": cfg["solution_module"],
        "solution_closure_files": len(closure),
        "theorem_names": cfg.get("theorem_names", []),
        "holes": holes,
    }


def compare_sources(chal_src: str, sol_src: str, holes: list[str]) -> list[dict[str, Any]]:
    """Compare holes between two in-memory sources (used by controls and tests)."""
    ci: dict[str, list[Decl]] = {}
    si: dict[str, list[Decl]] = {}
    for d in extract_decls(chal_src, "challenge"):
        ci.setdefault(d.full_name, []).append(d)
    for d in extract_decls(sol_src, "solution"):
        si.setdefault(d.full_name, []).append(d)
    return [compare_hole(h, ci.get(h, []), si.get(h, [])) for h in holes]


# --------------------------------------------------------------------------- controls

NINE: tuple[str, ...] = (
    "Brenier",
    "DefocusingNLS",
    "ElementaryPositivity",
    "EuclideanFiveColor",
    "KServer",
    "Naimark",
    "OccupiedOverlap",
    "Rokhlin",
    "SpinAngle",
)


def _perturb_layout(src: str) -> str:
    """Add comments and change indentation/line breaks without changing tokens."""
    out = []
    for line in src.split("\n"):
        if line.startswith("  ") and line.strip():
            out.append("    " + line.strip() + "  -- control comment")
        else:
            out.append(line)
    return "/- header /- nested -/ comment -/\n" + "\n".join(out)


def run_controls(root: Path, outdir: Path) -> dict[str, Any]:
    """Positive and negative controls on real challenge files; mutated copies saved."""
    cdir = outdir / "controls"
    cdir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    def check(cid: str, chal: str, sol: str, hole: str, expect: set[str]) -> None:
        rec = compare_sources(chal, sol, [hole])[0]
        results.append({"id": cid, "hole": hole, "expected": sorted(expect), "got": rec["verdict"], "pass": rec["verdict"] in expect, "reason": rec.get("reason", "")})

    # Positive: every challenge compared with itself (and with a layout-perturbed copy).
    for name in NINE:
        cfg = json.loads((root / "ComparatorChallenges" / f"{name}.json").read_text(encoding="utf-8"))
        src = (root / "ComparatorChallenges" / f"{name}.lean").read_text(encoding="utf-8")
        pert = _perturb_layout(src)
        (cdir / f"{name}.layout.lean").write_text(pert, encoding="utf-8")
        for hole in cfg.get("definition_names", []):
            selfrec = compare_sources(src, src, [hole])[0]
            want = {"SORRIED_IN_CHALLENGE"} if selfrec.get("challenge_has_sorry") else {"MATCHES"}
            check(f"self:{name}", src, src, hole, want)
            check(f"layout:{name}", src, pert, hole, want)

    efc = (root / "ComparatorChallenges" / "EuclideanFiveColor.lean").read_text(encoding="utf-8")
    ks = (root / "ComparatorChallenges" / "KServer.lean").read_text(encoding="utf-8")
    pc = "OAI.EuclideanFiveColor.ProperColoring"
    mutants: dict[str, tuple[str, str, str, set[str]]] = {
        "alpha_rename_bound": (efc, efc.replace("otherPoint", "q").replace("point", "p"), pc, {"MATCHES"}),
        "neg_eq1_to_eq2": (efc, efc.replace("‖ = 1", "‖ = 2"), pc, {"DIFFERS"}),
        "neg_body_true": (
            ks,
            re.sub(r"def MainStatement : Prop :=\n(?:  .*\n|\n)*?(?=\ntheorem)", "def MainStatement : Prop := True\n", ks),
            "OAI.KServer.MainStatement",
            {"DIFFERS"},
        ),
        "neg_global_swap_dist_edist": (ks, ks.replace("dist (s (labels 0))", "edist (s (labels 0))"), "OAI.KServer.serviceCost", {"DIFFERS"}),
        "neg_dotted_swap_log_exp": (ks, ks.replace("Real.log", "Real.exp"), "OAI.KServer.MainStatement", {"DIFFERS"}),
        "neg_abbrev_to_def": (ks, ks.replace("abbrev Configuration", "def Configuration"), "OAI.KServer.Configuration", {"DIFFERS"}),
        "neg_sorried_challenge": (
            efc.replace("‖point - otherPoint‖ = 1 → coloring point ≠ coloring otherPoint", "sorry"),
            efc,
            pc,
            {"SORRIED_IN_CHALLENGE"},
        ),
        "neg_not_found": (efc, efc, "OAI.EuclideanFiveColor.NoSuchDefinition", {"NOT_FOUND"}),
    }
    for cid, (chal, sol, hole, expect) in mutants.items():
        if chal == sol and cid not in ("neg_not_found",):
            results.append({"id": cid, "hole": hole, "expected": sorted(expect), "got": "MUTATION_NOT_APPLIED", "pass": False, "reason": "mutation did not change the source"})
            continue
        (cdir / f"{cid}.challenge.lean").write_text(chal, encoding="utf-8")
        (cdir / f"{cid}.solution.lean").write_text(sol, encoding="utf-8")
        check(cid, chal, sol, hole, expect)
    return {"n": len(results), "n_pass": sum(r["pass"] for r in results), "all_pass": all(r["pass"] for r in results), "results": results}


# --------------------------------------------------------------------------- assemble


def assemble(outdir: Path, eye_path: Path | None) -> dict[str, Any]:
    """Merge chunks and the optional by-eye review into definition_holes.json/.md."""
    chunks = [json.loads((outdir / "chunks" / f"{n}.json").read_text(encoding="utf-8")) for n in NINE if (outdir / "chunks" / f"{n}.json").is_file()]
    eye: dict[str, dict[str, str]] = {}
    if eye_path is not None and eye_path.is_file():
        eye = json.loads(eye_path.read_text(encoding="utf-8"))
    disagreements = []
    rows = []
    for ch in chunks:
        for h in ch["holes"]:
            e = eye.get(h["hole"])
            if e is not None:
                h["eye_verdict"] = e.get("verdict", "")
                h["eye_note"] = e.get("note", "")
                h["meaning_pinned"] = e.get("meaning_pinned", "")
                if h["eye_verdict"] != h["verdict"]:
                    disagreements.append({"hole": h["hole"], "mechanical": h["verdict"], "eye": h["eye_verdict"], "note": h["eye_note"]})
            sol = h["solution"][0] if h["solution"] else None
            chal = h["challenge"][0] if h["challenge"] else None
            rows.append(
                (
                    ch["challenge"],
                    h["hole"].split(".")[-1],
                    (("sorry" if h.get("challenge_sorry_only") else "body with sorry") if h.get("challenge_has_sorry") else "body") if chal else "-",
                    f"`{sol['file']}:{sol['line']}`" if sol else "-",
                    h["verdict"],
                    h.get("eye_verdict", "(not reviewed)"),
                    (h.get("eye_note") or h.get("reason", "")).replace("|", "\\|"),
                )
            )
    counts: dict[str, int] = {}
    for ch in chunks:
        for h in ch["holes"]:
            counts[h["verdict"]] = counts.get(h["verdict"], 0) + 1
    out = {"challenges": chunks, "mechanical_counts": counts, "eye_disagreements": disagreements, "n_holes": sum(counts.values())}
    (outdir / "definition_holes.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["| Challenge | Hole | Challenge def | Solution def | Mechanical | By eye | Note |", "|---|---|---|---|---|---|---|"]
    md += ["| " + " | ".join(r) + " |" for r in rows]
    (outdir / "definition_holes.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("run", "controls", "assemble"):
        p = sub.add_parser(c)
        p.add_argument("--root", type=Path, required=c != "assemble", help="openai-math/lean directory")
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--names", default=",".join(NINE))
        p.add_argument("--eye", type=Path, default=None)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "run":
        (a.out / "chunks").mkdir(exist_ok=True)
        for name in [n for n in a.names.split(",") if n]:
            dest = a.out / "chunks" / f"{name}.json"
            if dest.is_file():
                print(f"skip {name} (chunk exists)")
                continue
            res = audit_challenge(a.root, name)
            dest.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(name, {h["hole"].split(".")[-1]: h["verdict"] for h in res["holes"]})
    elif a.cmd == "controls":
        res = run_controls(a.root, a.out)
        (a.out / "controls.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"controls {res['n_pass']}/{res['n']} pass, all_pass={res['all_pass']}")
        return 0 if res["all_pass"] else 1
    else:
        res = assemble(a.out, a.eye)
        print(res["mechanical_counts"], "eye disagreements:", len(res["eye_disagreements"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
