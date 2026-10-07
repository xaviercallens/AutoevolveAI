#!/usr/bin/env python3
"""Static scan of an upstream solution module and its in-repo import closure.

Stage D1 helper for the openai_math sub-project (docs/OPENAI_MATH_STUDY.md). It does
NOT compile anything and is not a proof check: Comparator (D2) is. It answers a cheaper
question first: does the source the proof depends on contain `sorry`, `admit`, `axiom`,
or a `set_option` that weakens kernel checking? Imports resolved inside the clone's
`lean/` directory are followed; imports of external packages (Mathlib, PNT+, ...) are
listed but not scanned.

Run:
    python3 scripts/openai_math/scan_solution.py OAI.NumberTheory.DirichletL.Nonvanishing
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_corpus import DEFAULT_CLONE, lean_imports  # type: ignore[import-not-found]  # noqa: E402

_FLAG_PATTERNS: dict[str, re.Pattern[str]] = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "axiom": re.compile(r"^\s*(?:private\s+|protected\s+)?axiom\s+", re.M),
    "set_option_unsafe": re.compile(
        r"set_option\s+(?:debug\.skipKernelTC|maxRecDepth\s+\d{6,}|trust\s+\d)"
    ),
    "implemented_by": re.compile(r"@\[\s*implemented_by"),
    "extern": re.compile(r"@\[\s*extern"),
}


@dataclass
class ScanResult:
    root_module: str
    local_files: int
    local_lines: int
    external_imports: list[str]
    missing_local: list[str]
    flags: dict[str, list[str]] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not any(self.flags.values()) and not self.missing_local


def module_path(lean_dir: Path, module: str) -> Path:
    return lean_dir.joinpath(*module.split(".")).with_suffix(".lean")


def flag_lines(source: str, rel: str) -> dict[str, list[str]]:
    """Return {flag: ["rel:line", ...]} for flagged lines, comments stripped.

    Comment stripping keeps line numbers by replacing comments with equal newlines.
    """
    def keep_newlines(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")

    text = re.sub(r"/-.*?-/|--[^\n]*", keep_newlines, source, flags=re.S)
    found: dict[str, list[str]] = {}
    lines = text.splitlines()
    for name, pattern in _FLAG_PATTERNS.items():
        hits = [f"{rel}:{i}" for i, line in enumerate(lines, start=1) if pattern.search(line)]
        if hits:
            found[name] = hits
    return found


def scan(lean_dir: Path, root_module: str) -> ScanResult:
    seen: set[str] = set()
    stack = [root_module]
    external: set[str] = set()
    missing: list[str] = []
    flags: dict[str, list[str]] = {}
    lines = 0
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        path = module_path(lean_dir, module)
        if not path.is_file():
            top = module.split(".")[0]
            if top in {"OAI", "ComparatorChallenges"}:
                missing.append(module)
            else:
                external.add(top)
            continue
        source = path.read_text()
        lines += source.count("\n")
        rel = str(path.relative_to(lean_dir))
        for name, hits in flag_lines(source, rel).items():
            flags.setdefault(name, []).extend(hits)
        stack.extend(lean_imports(source))
    local = sum(1 for m in seen if module_path(lean_dir, m).is_file())
    return ScanResult(root_module, local, lines, sorted(external), sorted(missing), flags)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("modules", nargs="+")
    parser.add_argument("--clone", type=Path, default=DEFAULT_CLONE)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    lean_dir = args.clone / "lean"
    if not lean_dir.is_dir():
        print(f"BLOCKED: no lean/ directory under {args.clone}")
        return 2
    results = [scan(lean_dir, m) for m in args.modules]
    payload = [dict(asdict(r), clean=r.clean) for r in results]
    for r in results:
        summary = {k: len(v) for k, v in r.flags.items()}
        print(f"{r.root_module}: {r.local_files} local files, {r.local_lines} lines, "
              f"flags={summary or 'none'}, missing={r.missing_local or 'none'}, "
              f"external={r.external_imports}")
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n")
    return 0 if all(r.clean for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
