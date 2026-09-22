"""
Lean 4 Verifier: Interfacing with Lean 4 and Lake.
Validates mathematical soundness of formal proofs (ANSE.Performance, ANSE.MicroML, ANSE.Autopoiesis).
Rejects proofs containing ungrounded axioms or 'sorry'.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LeanVerificationResult:
    """Result of Lake build / Lean 4 verification."""

    success: bool
    lake_available: bool
    theorems_proven: list[str] = field(default_factory=list)
    sorry_count: int = 0
    errors: list[str] = field(default_factory=list)
    raw_output: str = ""
    exit_code: int = 0

    @property
    def summary(self) -> str:
        if not self.lake_available:
            return "Lean 4 verification SKIPPED: 'lake' tool not found on system PATH."
        if self.success and self.sorry_count == 0:
            return f"Lean 4 verification PASSED: {len(self.theorems_proven)} theorems formally verified without 'sorry'."
        return (
            f"Lean 4 verification FAILED (exit code {self.exit_code}, sorry={self.sorry_count}):\n"
            + "\n".join(f"  - {err}" for err in self.errors[:10])
        )


class Lean4Verifier:
    """Interacts with Lake to compile and verify Lean 4 specifications."""

    def __init__(self, formal_dir: str | Path = "formal", timeout_seconds: float = 60.0) -> None:
        self.formal_dir = Path(formal_dir)
        self.timeout_seconds = timeout_seconds

    @property
    def is_available(self) -> bool:
        """Check if 'lake' is available on PATH."""
        return shutil.which("lake") is not None

    def scan_for_sorry(self, lean_files_dir: Path | None = None) -> tuple[int, list[str]]:
        """Scans Lean 4 source files for 'sorry' tokens or ungrounded axioms."""
        target_dir = lean_files_dir or self.formal_dir
        sorry_count = 0
        occurrences: list[str] = []

        if not target_dir.exists():
            return 0, []

        sorry_pattern = re.compile(r"\bsorry\b")
        for lean_file in target_dir.rglob("*.lean"):
            try:
                content = lean_file.read_text(encoding="utf-8", errors="replace")
                clean_content = re.sub(
                    r"/-(?:[^-]|-(?!/))*-(?:/)?",
                    lambda m: "\n" * m.group(0).count("\n"),
                    content,
                    flags=re.DOTALL,
                )
                lines = content.splitlines()
                for lineno, line in enumerate(clean_content.splitlines(), start=1):
                    # Strip comments
                    code_part = line.split("--")[0]
                    # Strip string literals
                    code_part = re.sub(r'"[^"]*"', "", code_part)
                    if sorry_pattern.search(code_part):
                        sorry_count += 1
                        orig_line = lines[lineno - 1] if lineno - 1 < len(lines) else line
                        occurrences.append(f"{lean_file}:{lineno}: '{orig_line.strip()}'")
            except Exception:
                continue

        return sorry_count, occurrences

    def extract_theorems(self, lean_files_dir: Path | None = None) -> list[str]:
        """Extracts theorem and lemma declarations from Lean source files."""
        target_dir = lean_files_dir or self.formal_dir
        theorems: list[str] = []

        if not target_dir.exists():
            return []

        theorem_pattern = re.compile(r"^\s*(?:theorem|lemma)\s+([a-zA-Z0-9_'.]+)")
        for lean_file in target_dir.rglob("*.lean"):
            try:
                content = lean_file.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    match = theorem_pattern.match(line)
                    if match:
                        theorems.append(match.group(1))
            except Exception:
                continue

        return theorems

    def extract_proof_inventory(self, lean_files_dir: Path | None = None) -> dict[str, list[str]]:
        """
        Extracts formal declarations categorized by kind (theorems, lemmas, axioms, defs).
        """
        target_dir = lean_files_dir or self.formal_dir
        inventory: dict[str, list[str]] = {
            "theorems": [],
            "lemmas": [],
            "axioms": [],
            "definitions": [],
        }
        if not target_dir.exists():
            return inventory

        patterns = {
            "theorems": re.compile(r"^\s*theorem\s+([a-zA-Z0-9_'.]+)"),
            "lemmas": re.compile(r"^\s*lemma\s+([a-zA-Z0-9_'.]+)"),
            "axioms": re.compile(r"^\s*axiom\s+([a-zA-Z0-9_'.]+)"),
            "definitions": re.compile(r"^\s*(?:def|inductive|structure)\s+([a-zA-Z0-9_'.]+)"),
        }

        for lean_file in target_dir.rglob("*.lean"):
            try:
                content = lean_file.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    clean_line = line.split("--")[0]
                    for kind, pat in patterns.items():
                        match = pat.match(clean_line)
                        if match:
                            inventory[kind].append(match.group(1))
            except Exception:
                continue

        return inventory

    def check_soundness(self, lean_files_dir: Path | None = None) -> tuple[bool, str]:
        """
        Verifies mathematical soundness: zero 'sorry' tokens and zero ungrounded axioms.
        """
        sorry_count, sorry_occurrences = self.scan_for_sorry(lean_files_dir)
        inventory = self.extract_proof_inventory(lean_files_dir)
        axioms = inventory.get("axioms", [])

        if sorry_count > 0:
            return (
                False,
                f"Soundness violation: {sorry_count} unproven 'sorry' found ({sorry_occurrences[:3]})",
            )
        if axioms:
            return (
                False,
                f"Soundness violation: {len(axioms)} unverified axiom(s) declared ({axioms[:3]})",
            )
        return True, "Soundness verified: 0 sorry, 0 axioms."

    def verify(self, extra_args: list[str] | None = None) -> LeanVerificationResult:
        """Runs 'lake build' in formal directory and inspects proofs."""
        if not self.is_available:
            # Lake not installed on machine
            theorems = self.extract_theorems()
            sorry_count, _ = self.scan_for_sorry()
            return LeanVerificationResult(
                success=False,
                lake_available=False,
                theorems_proven=theorems,
                sorry_count=sorry_count,
                errors=["'lake' executable not found on PATH"],
            )

        if not self.formal_dir.exists():
            return LeanVerificationResult(
                success=False,
                lake_available=True,
                errors=[f"Formal directory '{self.formal_dir}' does not exist"],
                exit_code=-1,
            )

        # First scan statically for sorry
        sorry_count, sorry_occurrences = self.scan_for_sorry()
        theorems = self.extract_theorems()

        cmd = ["lake", "build"]
        if extra_args:
            cmd.extend(extra_args)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.formal_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            raw_output = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
            errors: list[str] = []

            if proc.returncode != 0:
                for line in raw_output.splitlines():
                    if "error:" in line.lower() or "failed" in line.lower():
                        errors.append(line.strip())

            if sorry_count > 0:
                errors.extend([f"Unsound 'sorry' token found: {s}" for s in sorry_occurrences])

            success = proc.returncode == 0 and sorry_count == 0

            return LeanVerificationResult(
                success=success,
                lake_available=True,
                theorems_proven=theorems if success else [],
                sorry_count=sorry_count,
                errors=errors,
                raw_output=raw_output,
                exit_code=proc.returncode,
            )

        except subprocess.TimeoutExpired:
            return LeanVerificationResult(
                success=False,
                lake_available=True,
                errors=[f"Lake build timed out after {self.timeout_seconds}s"],
                exit_code=-2,
            )
        except Exception as exc:
            return LeanVerificationResult(
                success=False,
                lake_available=True,
                errors=[f"Lake execution failed: {exc}"],
                exit_code=-3,
            )
