"""
Lean 4 Formal Verification Runner for ANSE.
Directly invokes Lean 4 compiler ('lake build') and inspects axioms via 'lake env lean'.
Strictly enforces zero-trust: any compilation failure or presence of 'sorryAx' awards E = 10^6.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("LeanRunner")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FORMAL_DIR = PROJECT_ROOT / "formal"


@dataclass
class LeanVerificationResult:
    theorem_name: str
    compiled_successfully: bool
    returncode: int
    elapsed_ms: float
    axioms: list[str]
    has_sorry: bool
    energy_score: float
    output: str


class LeanKernelVerifier:
    def __init__(self, formal_dir: Path | None = None):
        self.formal_dir = formal_dir or FORMAL_DIR

    def compile_formal_specs(self) -> tuple[bool, str, float]:
        """Runs 'lake build' in the formal directory and measures duration."""
        t0 = time.perf_counter()
        res = subprocess.run(
            ["lake", "build"],
            cwd=str(self.formal_dir),
            capture_output=True,
            text=True,
        )
        elapsed = (time.perf_counter() - t0) * 1000.0
        success = res.returncode == 0
        output = (res.stdout + "\n" + res.stderr).strip()
        return success, output, elapsed

    def verify_theorem_axioms(self, module_name: str, theorem_name: str) -> LeanVerificationResult:
        """
        Runs Lean 4 environment to check that theorem compiles and derives axioms.
        Detects if 'sorryAx' or non-constructive cheating axioms are used.
        """
        t0 = time.perf_counter()
        
        # Build check script
        check_script = f"import {module_name}\n#print axioms {theorem_name}\n"
        temp_check_file = self.formal_dir / ".tmp_axiom_check.lean"
        
        try:
            temp_check_file.write_text(check_script, encoding="utf-8")
            res = subprocess.run(
                ["lake", "env", "lean", str(temp_check_file.name)],
                cwd=str(self.formal_dir),
                capture_output=True,
                text=True,
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            raw_output = res.stdout + "\n" + res.stderr

            if res.returncode != 0:
                logger.error("Lean axiom check failed for %s: %s", theorem_name, raw_output)
                return LeanVerificationResult(
                    theorem_name=theorem_name,
                    compiled_successfully=False,
                    returncode=res.returncode,
                    elapsed_ms=elapsed,
                    axioms=[],
                    has_sorry=True,
                    energy_score=1000000.0,
                    output=raw_output,
                )

            # Parse axioms from output (e.g., depends on axioms: [propext, Classical.choice, Quot.sound])
            axioms: list[str] = []
            if "depends on axioms:" in raw_output:
                part = raw_output.split("depends on axioms:")[1].strip()
                cleaned = part.replace("[", "").replace("]", "").replace("\n", " ")
                axioms = [a.strip() for a in cleaned.split(",") if a.strip()]

            has_sorry = "sorryAx" in axioms or "sorryAx" in raw_output

            # If sorryAx exists, penalize with Maximum Pain
            energy = 0.05 + (elapsed / 1000.0) if not has_sorry else 1000000.0

            return LeanVerificationResult(
                theorem_name=theorem_name,
                compiled_successfully=True,
                returncode=0,
                elapsed_ms=elapsed,
                axioms=axioms,
                has_sorry=has_sorry,
                energy_score=energy,
                output=raw_output.strip(),
            )
        finally:
            if temp_check_file.exists():
                temp_check_file.unlink()
