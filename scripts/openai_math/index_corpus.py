#!/usr/bin/env python3
"""Index and audit a local clone of github.com/openai/math (stage D0 of the
openai_math sub-project, see docs/OPENAI_MATH_STUDY.md).

This script only reads the clone. It never compiles Lean and never trusts the
upstream README's counts: every number in the output is recounted from the
files on disk. It fails closed: if the clone is missing it prints BLOCKED and
exits 2 without writing any result file.

What it audits, per Comparator challenge (``lean/ComparatorChallenges/*.json``
plus the matching ``.lean`` statement file):

* the config has the required keys;
* ``permitted_axioms`` is a subset of the repo whitelist
  {propext, Classical.choice, Quot.sound} (LL.md section 2);
* every name in ``theorem_names`` is declared in the challenge file;
* the challenge file is a statement only: it contains ``sorry`` and no
  ``axiom`` declaration;
* the challenge imports (``import Mathlib`` cannot be built in ``formal/``,
  LL.md section 3).

Run:
    .venv/bin/python scripts/openai_math/index_corpus.py \
        --clone /mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CLONE = Path(
    "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/"
    "SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math"
)
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "results" / "openai_math" / "corpus_index.json"
LOCAL_TOOLCHAIN_FILE = REPO / "formal" / "lean-toolchain"

TRUSTED_AXIOMS: frozenset[str] = frozenset({"propext", "Classical.choice", "Quot.sound"})
REQUIRED_CONFIG_KEYS: tuple[str, ...] = (
    "challenge_module",
    "solution_module",
    "theorem_names",
    "permitted_axioms",
)
EXIT_BLOCKED = 2

_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:private|protected|noncomputable|nonrec)\s+)*"
    r"(?:theorem|lemma)\s+([^\s:(\[{.]+(?:\.[^\s:(\[{.]+)*(?:\.\{[^}]*\})?)",
    re.M,
)
_NAMESPACE_RE = re.compile(r"^\s*(namespace|end)\s+([^\s]+)\s*$", re.M)
_IMPORT_RE = re.compile(r"^\s*import\s+([^\s]+)", re.M)
_AXIOM_RE = re.compile(r"^\s*axiom\s+([^\s:({\[]+)", re.M)
_UNIVERSE_SUFFIX_RE = re.compile(r"\.\{[^}]*\}$")
_SORRY_RE = re.compile(r"\bsorry\b")
_COMMENT_RE = re.compile(r"/-.*?-/|--[^\n]*", re.S)


class CorpusBlocked(RuntimeError):
    """Raised when the clone is absent or not a checkout of openai/math."""


@dataclass
class ChallengeAudit:
    name: str
    challenge_module: str
    solution_module: str
    theorem_names: list[str]
    permitted_axioms: list[str]
    imports: list[str]
    declared_theorems: list[str]
    sorry_count: int
    problems: list[str] = field(default_factory=list)
    definition_names: list[str] = field(default_factory=list)
    declared_axioms: list[str] = field(default_factory=list)
    # Not defects, but things a reviewer must look at (e.g. definition holes).
    notes: list[str] = field(default_factory=list)


def strip_lean_comments(source: str) -> str:
    """Remove ``--`` line comments and non-nested ``/- ... -/`` blocks."""
    return _COMMENT_RE.sub("", source)


def lean_imports(source: str) -> list[str]:
    return _IMPORT_RE.findall(strip_lean_comments(source))


def declared_theorem_names(source: str) -> list[str]:
    """Fully qualified theorem/lemma names, resolving ``namespace``/``end`` blocks.

    Names written with a leading ``_root_.`` are taken as already absolute.
    """
    text = strip_lean_comments(source)
    events: list[tuple[int, str, str]] = []
    for m in _NAMESPACE_RE.finditer(text):
        events.append((m.start(), m.group(1), m.group(2)))
    for m in _DECL_RE.finditer(text):
        # `theorem foo.{u}` declares `foo` with universe parameter u.
        events.append((m.start(), "decl", _UNIVERSE_SUFFIX_RE.sub("", m.group(1))))
    events.sort(key=lambda e: e[0])
    stack: list[str] = []
    names: list[str] = []
    for _, kind, value in events:
        if kind == "namespace":
            stack.extend(value.split("."))
        elif kind == "end":
            parts = value.split(".")
            if stack[-len(parts):] == parts:
                del stack[-len(parts):]
        elif value.startswith("_root_."):
            names.append(value[len("_root_."):])
        else:
            names.append(".".join([*stack, value]))
    return names


def untrusted_axioms(permitted: list[str]) -> list[str]:
    return sorted(set(permitted) - TRUSTED_AXIOMS)


def _str_list(config: dict[str, object], key: str) -> list[str]:
    value = config.get(key) or []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


def audit_challenge(name: str, config: dict[str, object], lean_source: str | None) -> ChallengeAudit:
    """Audit one Comparator challenge.

    ``problems`` are defects (the check cannot mean what it claims). ``notes`` are
    legitimate-but-review-worthy patterns:
    * a definition hole (``definition_names``) -- the Comparator README says these
      "must always be checked with an additional (potentially human) verifier";
    * a statement posed as ``axiom X : P`` + ``theorem main : P := X`` instead of
      ``sorry``. That is sound under Comparator only because the solution may use no
      axiom outside ``permitted_axioms``; if a declared axiom is permitted, it is a defect.
    """
    problems: list[str] = []
    notes: list[str] = []
    missing = [k for k in REQUIRED_CONFIG_KEYS if k not in config]
    if missing:
        problems.append(f"config missing keys: {missing}")
    theorem_names = _str_list(config, "theorem_names")
    definition_names = _str_list(config, "definition_names")
    permitted = _str_list(config, "permitted_axioms")
    bad_axioms = untrusted_axioms(permitted)
    if bad_axioms:
        problems.append(f"permits untrusted axioms: {bad_axioms}")
    if not theorem_names and not definition_names:
        problems.append("theorem_names and definition_names are both empty")
    if definition_names:
        notes.append(f"definition hole {definition_names}: needs an additional verifier")
    imports: list[str] = []
    declared: list[str] = []
    axioms: list[str] = []
    sorry_count = 0
    if lean_source is None:
        problems.append("challenge .lean file missing")
    else:
        stripped = strip_lean_comments(lean_source)
        imports = lean_imports(lean_source)
        declared = declared_theorem_names(lean_source)
        axioms = _AXIOM_RE.findall(stripped)
        sorry_count = len(_SORRY_RE.findall(stripped))
        undeclared = [t for t in theorem_names if t not in declared]
        if undeclared:
            problems.append(f"theorem_names not declared in challenge file: {undeclared}")
        permitted_declared = [
            a for a in axioms if any(p == a or p.endswith("." + a) for p in permitted)
        ]
        if permitted_declared:
            problems.append(f"challenge axiom is in permitted_axioms: {permitted_declared}")
        if axioms:
            notes.append(f"statement posed via axiom {axioms} (not permitted to the solution)")
        if sorry_count == 0 and not axioms and theorem_names:
            problems.append("challenge file has no sorry (expected a statement-only file)")
    return ChallengeAudit(
        name=name,
        challenge_module=str(config.get("challenge_module", "")),
        solution_module=str(config.get("solution_module", "")),
        theorem_names=theorem_names,
        permitted_axioms=permitted,
        imports=imports,
        declared_theorems=declared,
        sorry_count=sorry_count,
        problems=problems,
        definition_names=definition_names,
        declared_axioms=axioms,
        notes=notes,
    )


def read_head_commit(clone: Path) -> str | None:
    """Resolve HEAD to a commit sha by reading .git files (no subprocess)."""
    git_dir = clone / ".git"
    head_file = git_dir / "HEAD"
    if not head_file.is_file():
        return None
    head = head_file.read_text().strip()
    if not head.startswith("ref: "):
        return head
    ref = head[len("ref: "):]
    ref_file = git_dir / ref
    if ref_file.is_file():
        return ref_file.read_text().strip()
    packed = git_dir / "packed-refs"
    if packed.is_file():
        for line in packed.read_text().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    return None


def require_clone(clone: Path) -> None:
    markers = [clone / "README.md", clone / "lean" / "lakefile.lean", clone / "preprints"]
    absent = [str(m) for m in markers if not m.exists()]
    if absent:
        raise CorpusBlocked(f"clone at {clone} is missing {absent}")


def audit_challenges(lean_dir: Path) -> list[ChallengeAudit]:
    challenge_dir = lean_dir / "ComparatorChallenges"
    audits: list[ChallengeAudit] = []
    for cfg_path in sorted(challenge_dir.glob("*.json")):
        try:
            config = json.loads(cfg_path.read_text())
        except json.JSONDecodeError as exc:
            audits.append(
                ChallengeAudit(cfg_path.stem, "", "", [], [], [], [], 0, [f"invalid JSON: {exc}"])
            )
            continue
        lean_path = cfg_path.with_suffix(".lean")
        source = lean_path.read_text() if lean_path.is_file() else None
        audits.append(audit_challenge(cfg_path.stem, config, source))
    return audits


def comparator_links(doc_text: str) -> list[str]:
    return sorted(set(re.findall(r"ComparatorChallenges/([A-Za-z0-9_]+)\.lean", doc_text)))


def build_index(clone: Path) -> dict[str, object]:
    require_clone(clone)
    lean_dir = clone / "lean"
    audits = audit_challenges(lean_dir)
    docs = sorted((lean_dir / "docs").glob("*.md")) if (lean_dir / "docs").is_dir() else []
    doc_entries = []
    for doc in docs:
        text = doc.read_text()
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), "")
        doc_entries.append({"family": doc.stem, "title": title, "challenges": comparator_links(text)})
    linked = {c for d in doc_entries for c in d["challenges"]}  # type: ignore[union-attr]
    challenge_names = {a.name for a in audits}
    preprint_dirs = sorted(p for p in (clone / "preprints").iterdir() if p.is_dir())
    toolchain_file = lean_dir / "lean-toolchain"
    upstream_toolchain = toolchain_file.read_text().strip() if toolchain_file.is_file() else None
    local_toolchain = (
        LOCAL_TOOLCHAIN_FILE.read_text().strip() if LOCAL_TOOLCHAIN_FILE.is_file() else None
    )
    lean_files = list((lean_dir / "OAI").rglob("*.lean")) if (lean_dir / "OAI").is_dir() else []
    return {
        "source": "https://github.com/openai/math",
        "clone_path": str(clone),
        "clone_head": read_head_commit(clone),
        "indexed_utc": datetime.now(timezone.utc).isoformat(),
        "readme_sha256": hashlib.sha256((clone / "README.md").read_bytes()).hexdigest(),
        "counts": {
            "preprint_dirs": len(preprint_dirs),
            # PDF names vary upstream (paper.pdf, main.pdf, manuscript.pdf, article.pdf, ...).
            "preprint_dirs_with_pdf": sum(1 for p in preprint_dirs if any(p.glob("*.pdf"))),
            "preprint_dirs_with_paper_pdf": sum(1 for p in preprint_dirs if (p / "paper.pdf").is_file()),
            "formalization_docs": len(doc_entries),
            "comparator_challenges": len(audits),
            "challenges_with_problems": sum(1 for a in audits if a.problems),
            "challenges_with_notes": sum(1 for a in audits if a.notes),
            "definition_hole_challenges": sum(1 for a in audits if a.definition_names),
            "axiom_posed_challenges": sum(1 for a in audits if a.declared_axioms),
            "oai_lean_files": len(lean_files),
            "reasoning_traces": len(list((clone / "reasoning_traces").glob("*.pdf")))
            if (clone / "reasoning_traces").is_dir()
            else 0,
        },
        "toolchain": {
            "upstream": upstream_toolchain,
            "local_formal": local_toolchain,
            "compatible": upstream_toolchain is not None and upstream_toolchain == local_toolchain,
        },
        "challenges_not_linked_from_docs": sorted(challenge_names - linked),
        "doc_links_to_missing_challenges": sorted(linked - challenge_names),
        "challenges": [asdict(a) for a in audits],
        "formalization_docs": doc_entries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--clone", type=Path, default=Path(os.environ.get("OPENAI_MATH_CLONE", DEFAULT_CLONE)))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    try:
        index = build_index(args.clone)
    except CorpusBlocked as exc:
        print(f"BLOCKED: {exc}. Clone it first:\n  git clone https://github.com/openai/math {args.clone}")
        return EXIT_BLOCKED
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    counts = index["counts"]
    print(json.dumps(counts, indent=2))
    print(f"toolchain: {index['toolchain']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
