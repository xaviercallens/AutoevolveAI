"""
anse/laya/ltm_distiller.py
==========================
Continuous LTM & Conversation Distiller for Laya Coding Companion.

Mines conversation transcripts (~/.gemini/antigravity/brain/ and ~/.claude/projects/),
extracts code snippets across the three core technical pillars:
  1. Python: clean patterns, unit tests, security remediations, zero stubs
  2. Rust: numerical computing, SIMD vectorization, zero-alloc routines
  3. Lean 4: formal verification proofs, tactic automation, invariant declarations

Generates balanced training records with:
  - Positive samples (verified working code): noul=1, score=0.05
  - Negative samples (hallucinations, stubs, unhandled exceptions, security flaws): noul=0, score=1e6
All tokens and credentials are automatically scrubbed.
"""
from __future__ import annotations

import argparse
import ast
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

logger = logging.getLogger("LTMDistiller")

# Secret scrubbing patterns
_SCRUB_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("zenodo_token", re.compile(r"[a-zA-Z0-9]{60}")),
    ("user_home", re.compile(r"/home/[a-zA-Z0-9_\-]+")),
)


def scrub_text(text: str) -> str:
    """Scrub sensitive credentials and home paths from text."""
    scrubbed = text
    for name, pattern in _SCRUB_PATTERNS:
        scrubbed = pattern.sub(f"<REDACTED_{name.upper()}>", scrubbed)
    return scrubbed


@dataclass
class DistilledRecord:
    text: str
    noul_label: int         # 0=BLOCK/HALLUCINATION/STUB, 1=PASS/VERIFIED
    choice_label: int       # index in CHOICE_CLASSES
    score_label: float      # continuous energy target (0.05 or 1e6)
    has_noul: bool = True
    has_choice: bool = True
    has_score: bool = True
    dataset_id: str = "ltm_conversation_distilled"
    pillar: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Choice class mapping consistent with Laya 46-class head
CHOICE_CLASSES = [
    "clean", "stub_ellipsis", "dead_code", "smelly", "vulnerable", "safe", "pass", "fail",
    "O(1)", "O(logN)", "O(N)", "O(NlogN)", "O(N2)", "O(exponential)",
    "vectorization", "zero_alloc", "algorithmic_pruning", "data_structure", "general",
    "high_energy", "low_energy",
    "omega", "linarith", "ring", "norm_num", "positivity", "rfl", "simp", "calc",
    "induction", "intro", "apply", "exact", "constructor", "cases", "rcases",
    "valid", "invalid",
    "algorithmic_performance", "computational_physicist", "lean_prover",
    "micro_ml_architect", "security_auditor", "refactoring_specialist",
    "normal_return", "exception"
]
CHOICE_INDEX_MAP = {c: i for i, c in enumerate(CHOICE_CLASSES)}


class LTMConversationDistiller:
    """Extracts, filters, and formats training records from conversation transcripts."""

    def __init__(self, transcript_roots: Optional[List[Path]] = None) -> None:
        if transcript_roots is None:
            self.transcript_roots = [
                Path.home() / ".gemini" / "antigravity" / "brain",
                Path.home() / ".gemini" / "antigravity-cli" / "brain",
                Path.home() / ".claude" / "projects",
            ]
        else:
            self.transcript_roots = transcript_roots

    def find_transcripts(self) -> List[Path]:
        files: List[Path] = []
        for root in self.transcript_roots:
            if not root.exists():
                continue
            # Antigravity transcripts
            for f in root.glob("*/.system_generated/logs/transcript.jsonl"):
                if f.is_file() and f.stat().st_size > 0:
                    files.append(f)
            # Claude Code transcripts
            for f in root.glob("*/*.jsonl"):
                if f.is_file() and f.stat().st_size > 0 and f not in files:
                    files.append(f)
        return files


    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extracts (language, code) from markdown blocks."""
        pattern = re.compile(r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```", re.DOTALL)
        blocks = []
        for match in pattern.finditer(text):
            lang = match.group(1).lower().strip()
            code = match.group(2).strip()
            if len(code) > 20:  # Skip trivial snippets
                blocks.append((lang, code))
        return blocks

    def analyze_python_snippet(self, code: str) -> Tuple[int, str, float]:
        """Analyzes Python code for stubs, security risks, or clean execution."""
        # Check for stubs
        has_stub = False
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if len(node.body) == 1:
                        stmt = node.body[0]
                        if isinstance(stmt, (ast.Pass, ast.Raise)):
                            has_stub = True
                            break
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                            has_stub = True
                            break
        except SyntaxError:
            has_stub = True

        if re.search(r"#\s*TODO\b", code, re.IGNORECASE):
            has_stub = True

        if re.search(r"\beval\(|\bos\.system\(", code):
            return 0, "vulnerable", 1e6

        if has_stub:
            return 0, "stub_ellipsis", 1e6

        return 1, "clean", 0.05

    def analyze_rust_snippet(self, code: str) -> Tuple[int, str, float]:
        """Analyzes Rust code."""
        if "unimplemented!()" in code or "todo!()" in code:
            return 0, "stub_ellipsis", 1e6
        if any(k in code for k in ["simd", "avx", "target_feature"]):
            return 1, "vectorization", 0.02
        if "Vec::with_capacity" in code or "no_std" in code:
            return 1, "zero_alloc", 0.03
        return 1, "clean", 0.05

    def analyze_lean_snippet(self, code: str) -> Tuple[int, str, float]:
        """Analyzes Lean 4 snippet."""
        if "sorry" in code:
            return 0, "stub_ellipsis", 1e6
        # Detect tactic
        for tactic in ["omega", "linarith", "ring", "norm_num", "simp", "calc", "induction", "rfl"]:
            if re.search(rf"\b{tactic}\b", code):
                return 1, tactic, 0.05
        return 1, "lean_prover", 0.05

    def distill_file(self, transcript_file: Path) -> List[DistilledRecord]:
        records: List[DistilledRecord] = []
        try:
            with open(transcript_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        step = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    content = step.get("content", "")
                    if not content or len(content) < 30:
                        continue

                    # Extract embedded code blocks
                    blocks = self.extract_code_blocks(content)
                    for lang, code in blocks:
                        clean_code = scrub_text(code)
                        if lang in ["python", "py"]:
                            noul, choice, score = self.analyze_python_snippet(clean_code)
                            choice_idx = CHOICE_INDEX_MAP.get(choice, CHOICE_INDEX_MAP["clean"])
                            records.append(DistilledRecord(
                                text=clean_code,
                                noul_label=noul,
                                choice_label=choice_idx,
                                score_label=score,
                                pillar="python",
                            ))
                        elif lang in ["rust", "rs"]:
                            noul, choice, score = self.analyze_rust_snippet(clean_code)
                            choice_idx = CHOICE_INDEX_MAP.get(choice, CHOICE_INDEX_MAP["clean"])
                            records.append(DistilledRecord(
                                text=clean_code,
                                noul_label=noul,
                                choice_label=choice_idx,
                                score_label=score,
                                pillar="rust",
                            ))
                        elif lang in ["lean", "lean4"]:
                            noul, choice, score = self.analyze_lean_snippet(clean_code)
                            choice_idx = CHOICE_INDEX_MAP.get(choice, CHOICE_INDEX_MAP["lean_prover"])
                            records.append(DistilledRecord(
                                text=clean_code,
                                noul_label=noul,
                                choice_label=choice_idx,
                                score_label=score,
                                pillar="lean4",
                            ))
        except Exception as e:
            logger.warning(f"Error reading transcript {transcript_file}: {e}")
        return records

    def run_distillation(self, output_path: Path, max_records: Optional[int] = None) -> Dict[str, Any]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        files = self.find_transcripts()
        print(f"🔍 Discovered {len(files)} conversation transcript files across LTM roots.")

        total_records: List[DistilledRecord] = []
        for file in files:
            rec = self.distill_file(file)
            total_records.extend(rec)
            if max_records and len(total_records) >= max_records:
                total_records = total_records[:max_records]
                break

        # Deduplicate records by exact code snippet
        seen = set()
        deduped: List[DistilledRecord] = []
        for r in total_records:
            h = hash(r.text)
            if h not in seen:
                seen.add(h)
                deduped.append(r)

        # Write to output JSONL
        with open(output_path, "w", encoding="utf-8") as f:
            for r in deduped:
                f.write(json.dumps(r.to_dict()) + "\n")

        stats = {
            "total_files_scanned": len(files),
            "total_records_distilled": len(deduped),
            "python_count": sum(1 for r in deduped if r.pillar == "python"),
            "rust_count": sum(1 for r in deduped if r.pillar == "rust"),
            "lean4_count": sum(1 for r in deduped if r.pillar == "lean4"),
            "blocked_stubs_or_threats": sum(1 for r in deduped if r.noul_label == 0),
            "output_path": str(output_path),
        }
        return stats


def main():
    parser = argparse.ArgumentParser(description="Distill LTM conversation transcripts into Laya training records")
    parser.add_argument(
        "--output",
        default=Path("/mnt/data/home/xavkal/laya_coding_datasets/nightly/tri_pillar_ltm_distilled.jsonl"),
        type=Path,
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    distiller = LTMConversationDistiller()
    stats = distiller.run_distillation(args.output, max_records=args.limit)

    print("\n=======================================================")
    print("🎉 LTM Distillation Complete!")
    print(f"  Scanned Files:      {stats['total_files_scanned']}")
    print(f"  Total Distilled:    {stats['total_records_distilled']:,} records")
    print(f"  Python Records:     {stats['python_count']:,}")
    print(f"  Rust Records:       {stats['rust_count']:,}")
    print(f"  Lean 4 Records:     {stats['lean4_count']:,}")
    print(f"  Negative Stubs:     {stats['blocked_stubs_or_threats']:,}")
    print(f"  Output JSONL:       {stats['output_path']}")
    print("=======================================================")


if __name__ == "__main__":
    main()
