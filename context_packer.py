#!/usr/bin/env python3
"""
Context Packer: Dynamic Code Skeletonizer for Gemini Ultra.
Parses source files into structural skeletons (imports, class/function definitions, type annotations, docstrings).
Strips implementation bodies (replaces with '...') to minimize prompt token footprint
until Gemini explicitly requests full function bodies via tool calls.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


class CodeSkeletonVisitor(ast.NodeTransformer):
    """
    Transforms an AST into a high-level API skeleton.
    Preserves docstrings, arguments, and type signatures while eliding function bodies.
    """

    def __init__(self, keep_docstrings: bool = True) -> None:
        self.keep_docstrings = keep_docstrings

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._skeletonize_callable(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        return self._skeletonize_callable(node)

    def _skeletonize_callable(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        # Extract docstring if present
        docstring_node = None
        if (
            self.keep_docstrings
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]

        # Replace implementation body with Ellipsis (...)
        ellipsis_stmt = ast.Expr(value=ast.Constant(value=Ellipsis))

        if docstring_node:
            node.body = [docstring_node, ellipsis_stmt]
        else:
            node.body = [ellipsis_stmt]

        return node


def pack_code_skeleton(source_code: str, keep_docstrings: bool = True) -> str:
    """
    Parse Python code and return an AST-clean structural skeleton.
    If code cannot be parsed as valid Python AST (e.g. other language or syntax error),
    returns the original code safely.
    """
    try:
        tree = ast.parse(source_code)
    except (SyntaxError, UnicodeDecodeError):
        return source_code

    visitor = CodeSkeletonVisitor(keep_docstrings=keep_docstrings)
    transformed_tree = visitor.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return ast.unparse(transformed_tree)


def pack_file_skeleton(file_path: Path, keep_docstrings: bool = True) -> str:
    """Reads a file and returns its skeleton."""
    content = file_path.read_text(encoding="utf-8")
    return pack_code_skeleton(content, keep_docstrings=keep_docstrings)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pack code file into minimal structural skeleton for LLM context"
    )
    parser.add_argument("file", type=Path, help="Target file to skeletonize")
    parser.add_argument("--no-docstrings", action="store_true", help="Omit docstrings")
    args = parser.parse_args()

    skeleton = pack_file_skeleton(args.file, keep_docstrings=not args.no_docstrings)
    print(skeleton)


if __name__ == "__main__":
    main()
