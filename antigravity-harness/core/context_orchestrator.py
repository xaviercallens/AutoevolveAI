"""
Context Orchestrator: Large-window manager for Gemini models (1M-2M tokens).
Manages context budgets, skeletonization of large codebases, and ephemeral offloading.
"""

from __future__ import annotations

import ast
import hashlib
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class ContextTier(StrEnum):
    """Context detail tier based on token budget."""

    FULL = "full"  # Full source text
    SKELETON = "skeleton"  # AST skeletons (signatures + docstrings, bodies replaced by ...)
    OFFLOADED = "offloaded"  # Truncated summary with pointer to .scratchpad/


@dataclass
class ContextBudget:
    """Token budget distribution for Gemini context window."""

    max_tokens: int = 1_000_000  # Gemini 1.5/2.0 context window
    system_reserve: int = 50_000
    scratchpad_reserve: int = 150_000
    active_turn_reserve: int = 200_000
    codebase_budget: int = field(init=False)

    def __post_init__(self) -> None:
        self.codebase_budget = (
            self.max_tokens
            - self.system_reserve
            - self.scratchpad_reserve
            - self.active_turn_reserve
        )


class CodeSkeletonVisitor(ast.NodeTransformer):
    """Transforms an AST into a high-level API skeleton, preserving signatures and docstrings."""

    def __init__(self, keep_docstrings: bool = True) -> None:
        self.keep_docstrings = keep_docstrings

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        res = self._skeletonize_callable(node)
        assert isinstance(res, ast.FunctionDef)
        return res

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        res = self._skeletonize_callable(node)
        assert isinstance(res, ast.AsyncFunctionDef)
        return res

    def _skeletonize_callable(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        docstring_node = None
        if (
            self.keep_docstrings
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]

        ellipsis_stmt = ast.Expr(value=ast.Constant(value=Ellipsis))
        if docstring_node:
            node.body = [docstring_node, ellipsis_stmt]
        else:
            node.body = [ellipsis_stmt]
        return node


class ContextOrchestrator:
    """
    Orchestrates large context windows for Gemini.
    Tracks token consumption, performs AST skeletonization when approaching thresholds,
    and offloads high-volume tool outputs to the scratchpad.
    """

    def __init__(
        self,
        budget: ContextBudget | None = None,
        scratchpad_dir: str | Path = ".scratchpad",
        chars_per_token: float = 3.8,
    ) -> None:
        self.budget = budget or ContextBudget()
        self.scratchpad_dir = Path(scratchpad_dir)
        self.scratchpad_dir.mkdir(parents=True, exist_ok=True)
        self.chars_per_token = chars_per_token
        self.turns: list[dict[str, Any]] = []

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from character length."""
        if not text:
            return 0
        return int(len(text) / self.chars_per_token) + 1

    def skeletonize_code(self, source_code: str, keep_docstrings: bool = True) -> str:
        """Compress Python code into an AST skeleton."""
        try:
            tree = ast.parse(source_code)
            transformer = CodeSkeletonVisitor(keep_docstrings=keep_docstrings)
            skeleton_tree = transformer.visit(tree)
            ast.fix_missing_locations(skeleton_tree)
            return ast.unparse(skeleton_tree)
        except Exception:
            # Fallback to source if unparseable
            return source_code

    def offload_large_output(
        self,
        identifier: str,
        output_text: str,
        max_inline_lines: int = 60,
        head_tail_lines: int = 25,
    ) -> str:
        """
        If output exceeds line threshold, store in scratchpad and return an addressable summary.
        """
        lines = output_text.splitlines()
        if len(lines) <= max_inline_lines:
            return output_text

        token = hashlib.sha256(f"{identifier}:{time.time()}".encode()).hexdigest()[:10]
        file_path = self.scratchpad_dir / f"{identifier}_{token}.log"
        file_path.write_text(output_text, encoding="utf-8")

        head = "\n".join(lines[:head_tail_lines])
        tail = "\n".join(lines[-head_tail_lines:])
        total_lines = len(lines)

        return (
            f"[CONTEXT OFF-LOADED: {total_lines} lines total]\n"
            f"--- HEAD (First {head_tail_lines} lines) ---\n{head}\n"
            f"...\n"
            f"--- TAIL (Last {head_tail_lines} lines) ---\n{tail}\n"
            f"--- SCRATCHPAD LOCATION: {file_path.resolve()} ---\n"
            f"Note: Use specific queries or grep to retrieve omitted lines."
        )

    def pack_codebase(
        self,
        files: dict[str, str],
        priority_files: set[str] | None = None,
    ) -> dict[str, tuple[str, ContextTier]]:
        """
        Packs a set of codebase files, switching non-priority files to skeletons
        if total estimated tokens exceed codebase budget.
        """
        priority_files = priority_files or set()
        packed: dict[str, tuple[str, ContextTier]] = {}

        # First pass: calculate full tokens
        total_tokens = sum(self.estimate_tokens(content) for content in files.values())

        if total_tokens <= self.budget.codebase_budget:
            # Everything fits in full
            for path, content in files.items():
                packed[path] = (content, ContextTier.FULL)
            return packed

        # Second pass: skeletonize non-priority files
        for path, content in files.items():
            if path in priority_files:
                packed[path] = (content, ContextTier.FULL)
            else:
                skeleton = self.skeletonize_code(content)
                packed[path] = (skeleton, ContextTier.SKELETON)

        return packed

    def build_gemini_contents(
        self,
        system_instruction: str,
        codebase: dict[str, str],
        user_prompt: str,
        priority_files: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Constructs a structured Gemini message payload respecting budget boundaries.
        """
        packed_code = self.pack_codebase(codebase, priority_files=priority_files)

        code_sections = []
        for path, (content, tier) in packed_code.items():
            code_sections.append(
                f"### File: {path} (Tier: {tier.value})\n```python\n{content}\n```"
            )

        context_block = "\n\n".join(code_sections)
        combined_prompt = f"{system_instruction}\n\n## Repository Context\n{context_block}\n\n## Task\n{user_prompt}"

        return [
            {
                "role": "user",
                "parts": [{"text": combined_prompt}],
            }
        ]
