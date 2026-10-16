"""
Lean 4 Formal Verification Runner for ANSE.
Directly invokes Lean 4 compiler ('lake build') and inspects axioms via 'lake env lean'.
Strictly enforces zero-trust: any compilation failure or presence of 'sorryAx' awards E = 10^6.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("LeanRunner")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FORMAL_DIR = PROJECT_ROOT / "formal"

# The only axioms a kernel-checked Mathlib proof may depend on. Anything else
# (e.g. a smuggled `axiom cheat : False`) compiles with exit code 0 and would
# previously pass this gate — verified empirically on 2026-09-27.
TRUSTED_AXIOMS: frozenset[str] = frozenset({"propext", "Classical.choice", "Quot.sound"})


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
    untrusted_axioms: list[str] = None  # type: ignore[assignment]
    footprint_status: str = ""

    def __post_init__(self) -> None:
        if self.untrusted_axioms is None:
            self.untrusted_axioms = []
        if not self.footprint_status:
            if not self.compiled_successfully:
                self.footprint_status = "missing"
            elif self.untrusted_axioms:
                self.footprint_status = "rejected"
            elif self.has_sorry:
                self.footprint_status = "target"
            else:
                self.footprint_status = "proven"

    @property
    def verification_label(self) -> str:
        """Explicit epistemic status label (Reviewer 2 W7: sorry obligations are targets, never verified)."""
        if self.footprint_status == "proven":
            return "[Verified — Tier A kernel-checked]"
        if self.footprint_status == "target":
            return "[Unverified — sorry obligation pending]"
        if self.footprint_status == "rejected":
            return f"[Rejected — untrusted axioms: {', '.join(self.untrusted_axioms)}]"
        return "[Unchecked — missing or failed elaboration]"


def classify_axiom_footprint(axioms: list[str] | None) -> dict[str, object]:
    """Classify a `#print axioms` footprint per OptimalEnergyAI H0.3 contract.

    Returns a dict with:
      - status: 'proven' | 'target' | 'rejected' | 'missing'
      - axioms: list[str] | None
      - untrusted: list[str]
      - verification_label: human/audit-readable epistemic label
    """
    if axioms is None:
        return {
            "status": "missing",
            "axioms": None,
            "untrusted": [],
            "verification_label": "[Unchecked — missing or failed elaboration]",
        }
    untrusted = [a for a in axioms if a not in TRUSTED_AXIOMS and a != "sorryAx"]
    if untrusted:
        return {
            "status": "rejected",
            "axioms": list(axioms),
            "untrusted": untrusted,
            "verification_label": f"[Rejected — untrusted axioms: {', '.join(untrusted)}]",
        }
    if "sorryAx" in axioms:
        return {
            "status": "target",
            "axioms": list(axioms),
            "untrusted": [],
            "verification_label": "[Unverified — sorry obligation pending]",
        }
    return {
        "status": "proven",
        "axioms": list(axioms),
        "untrusted": [],
        "verification_label": "[Verified — Tier A kernel-checked]",
    }


class LeanKernelVerifier:
    def __init__(
        self,
        formal_dir: Path | None = None,
        lean_cmd: Sequence[str] | None = None,
        env: dict[str, str] | None = None,
    ):
        self.formal_dir = Path(formal_dir) if formal_dir else FORMAL_DIR
        # None -> `lake env lean` (needs a built formal_dir). Tests pass ["lean"] for import-free files.
        self.lean_cmd = list(lean_cmd) if lean_cmd else None
        self.env = dict(env) if env is not None else None

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
            untrusted = [a for a in axioms if a not in TRUSTED_AXIOMS and a != "sorryAx"]

            # sorryAx or any non-whitelisted axiom awards Maximum Pain: a proof
            # from `axiom cheat : False` is not a proof.
            clean = not has_sorry and not untrusted
            energy = 0.05 + (elapsed / 1000.0) if clean else 1000000.0
            if untrusted:
                logger.error(
                    "Untrusted axioms in %s: %s -- rejecting", theorem_name, untrusted
                )

            return LeanVerificationResult(
                theorem_name=theorem_name,
                compiled_successfully=True,
                returncode=0,
                elapsed_ms=elapsed,
                axioms=axioms,
                has_sorry=has_sorry,
                energy_score=energy,
                output=raw_output.strip(),
                untrusted_axioms=untrusted,
            )
        finally:
            if temp_check_file.exists():
                temp_check_file.unlink()

    def verify_file(
        self,
        lean_file: Path | str,
        timeout_s: float = 1800.0,
        env: dict[str, str] | None = None,
        reject_vacuous: bool = True,
    ) -> list[LeanVerificationResult]:
        """Gate a standalone ``.lean`` file that lives anywhere (e.g. a git worktree).

        ``verify_theorem_axioms`` imports a module, so the module must already be built
        into an olean, and it writes a temp file into the shared ``formal/`` directory.
        Neither is possible for a file staged in an isolated worktree. This mode instead
        compiles the file in place with ``lean_cmd`` (default ``lake env lean``, run from
        an existing built environment) and reads the kernel's own ``#print axioms``
        output that the file must contain for every ``theorem``/``lemma`` it declares.

        One result is returned per declared theorem. A file is only clean when:
          1. Source-level forgery scan passes (no ``#exit`` truncation, no ``#print "..."``
             string spoofing, no ``#eval``/``run_cmd``/``IO.println`` stdout injection, and
             no vacuous ``: True :=`` theorem statements when ``reject_vacuous=True``).
          2. The compile exits 0 without ``using 'exit' to interrupt Lean``.
          3. Every declared theorem has an axioms line AND none of those depends on
             ``sorryAx`` or a non-whitelisted axiom.
        """
        path = Path(lean_file).resolve()
        t0 = time.perf_counter()
        source = path.read_text(encoding="utf-8")
        forgeries = detect_lean_source_forgeries(source, reject_vacuous=reject_vacuous)
        if forgeries:
            elapsed = (time.perf_counter() - t0) * 1000.0
            reason = "Lean source forgery/vacuity guard rejected file: " + "; ".join(forgeries)
            logger.error("%s (%s)", reason, path.name)
            return [_failed(path.name, -2, elapsed, reason)]

        declared = declared_theorems(source)
        run_env = env if env is not None else self.env

        cmd = list(self.lean_cmd) if self.lean_cmd else self._lake_env_cmd()
        try:
            res = subprocess.run(
                [*cmd, str(path)],
                cwd=str(self.formal_dir),
                env=run_env,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return [_failed(path.name, -1, (time.perf_counter() - t0) * 1000.0,
                            f"lean timed out after {timeout_s:.0f}s")]
        elapsed = (time.perf_counter() - t0) * 1000.0
        raw = (res.stdout + "\n" + res.stderr).strip()
        if res.returncode != 0:
            return [_failed(path.name, res.returncode, elapsed, raw)]
        if "using 'exit' to interrupt Lean" in raw:
            return [_failed(path.name, -2, elapsed,
                            "Lean elaboration interrupted early by #exit: unchecked\n" + raw)]
        if not declared:
            return [_failed(path.name, 0, elapsed,
                            "file declares no theorem/lemma: nothing was verified\n" + raw)]

        printed = parse_axiom_lines(raw)
        results: list[LeanVerificationResult] = []
        for name in declared:
            axioms = _lookup_axioms(name, printed)
            if axioms is None:
                results.append(_failed(name, 0, elapsed,
                                       f"no '#print axioms' line for {name}: unchecked\n" + raw))
                continue
            has_sorry = "sorryAx" in axioms
            untrusted = [a for a in axioms if a not in TRUSTED_AXIOMS and a != "sorryAx"]
            clean = not has_sorry and not untrusted
            if untrusted:
                logger.error("Untrusted axioms in %s: %s -- rejecting", name, untrusted)
            results.append(LeanVerificationResult(
                theorem_name=name,
                compiled_successfully=True,
                returncode=0,
                elapsed_ms=elapsed,
                axioms=axioms,
                has_sorry=has_sorry,
                energy_score=0.05 + elapsed / 1000.0 if clean else 1000000.0,
                output=raw,
                untrusted_axioms=untrusted,
            ))
        return results

    def probe_footprints(
        self,
        module_name: str,
        theorem_names: Sequence[str],
        timeout_s: float = 900.0,
        env: dict[str, str] | None = None,
    ) -> dict[str, object]:
        """Probe `#print axioms` footprints for a list of theorems in `module_name` (OptimalEnergyAI H0.3).

        Also runs the negative control `__anse_ctl_does_not_exist__` to verify that a theorem nobody
        printed is classified as `'missing'` and never silently passes.
        """
        import tempfile

        sentinel = f"{module_name}.__anse_ctl_does_not_exist__"
        probe_names = [*theorem_names, sentinel]
        src = f"import {module_name}\n" + "".join(f"#print axioms {n}\n" for n in probe_names)
        run_env = env if env is not None else self.env
        cmd = list(self.lean_cmd) if self.lean_cmd else self._lake_env_cmd()

        with tempfile.TemporaryDirectory() as tmp_dir:
            probe_file = Path(tmp_dir) / "Probe.lean"
            probe_file.write_text(src, encoding="utf-8")
            res = subprocess.run(
                [*cmd, str(probe_file)],
                cwd=str(self.formal_dir),
                env=run_env,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        raw = res.stdout + "\n" + res.stderr
        printed = parse_axiom_lines(raw)
        footprints: dict[str, dict[str, object]] = {}
        for name in probe_names:
            ax = _lookup_axioms(name, printed)
            footprints[name] = classify_axiom_footprint(ax)

        sentinel_entry = footprints.pop(sentinel)
        controls = {
            "unknown_name_is_missing": sentinel_entry["status"] == "missing",
            "probe_ran": any(v["status"] != "missing" for v in footprints.values()),
        }
        return {
            "module": module_name,
            "footprints": footprints,
            "controls": controls,
            "raw_output": raw.strip(),
        }

    def _lake_env_cmd(self) -> list[str]:
        """``lake env lean``, but only inside a directory whose Mathlib is already BUILT.

        In a directory without ``.lake/packages`` (every fresh git worktree) ``lake env``
        does not fail fast: it starts cloning Mathlib (measured 2026-09-28: 1.6 GB written
        into the worktree before it aborted). Checking only that ``.lake/packages`` is a
        directory is not enough: that same aborted clone leaves
        ``.lake/packages/mathlib`` behind as a real, checked-out git worktree with source
        files but ZERO oleans anywhere under it (measured 2026-09-28, this worktree,
        after the incident above) — a directory-only check would call this environment
        usable and let ``lake env`` resume the fetch/build.

        There is no ``Mathlib.olean`` umbrella to check for even on a legitimate build:
        this project's own partial build (3,431 of ~7,000 oleans, imports pinned to
        individual built modules, see CLAUDE.md) never produces one either — checking for
        it would reject the real, working environment. The signal that actually separates
        the two, measured on both: the built lib directory holds 3,431 oleans; the aborted
        clone holds 0. So the check is "at least one olean exists under
        ``.lake/build/lib/lean``", not any specific file.
        """
        build_dir = self.formal_dir / ".lake" / "packages" / "mathlib" / ".lake" / "build" / "lib" / "lean"
        # Oleans are nested by module path (e.g. Mathlib/GroupTheory/...olean), never directly
        # under build_dir (measured: 0 at depth 1, 3,431 recursively) -- rglob, not glob.
        if not build_dir.is_dir() or not any(build_dir.rglob("*.olean")):
            raise LeanEnvironmentError(
                f"{self.formal_dir} has no built Mathlib ({build_dir} has no .olean files); "
                "running `lake env` there could start fetching or building it. Point "
                "formal_dir (or ANSE_FORMAL_DIR) at a checkout whose formal/.lake is "
                "actually built."
            )
        return ["lake", "env", "lean"]


class LeanEnvironmentError(RuntimeError):
    """No usable, already-built Lean environment to compile against."""


_BLOCK_COMMENT = re.compile(r"/-.*?-/", re.S)
_LINE_COMMENT = re.compile(r"--[^\n]*")
_DECL = re.compile(
    r"^[ \t]*(?:@\[[^\]\n]*\][ \t]*)*(?:(?:private|protected|noncomputable|unsafe)[ \t]+)*"
    r"(?:theorem|lemma)[ \t]+([^\s:({\[]+)",
    re.M,
)
# The name is quoted but may itself contain `'` (a theorem called `em'` prints as `'em''`), so
# anchor on the phrase that follows it instead of on the next quote.
_AXIOMS_LINE = re.compile(
    r"^'([^\n]+?)' (?:depends on axioms: \[(.*?)\]|does not depend on any axioms)", re.S | re.M
)


def declared_theorems(source: str) -> list[str]:
    """Names of every ``theorem``/``lemma`` declared outside comments and docstrings."""
    code = _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", source))
    return [m.group(1) for m in _DECL.finditer(code)]


def detect_lean_source_forgeries(source: str, reject_vacuous: bool = True) -> list[str]:
    """Detect source-level formal verification bypasses and vacuous statements (TODO 27, TODO 9).

    Checks stripped Lean source code (outside comments/docstrings) for:
      - ``#exit`` directive (truncates elaboration before broken proofs or after forged prints)
      - ``#print "..."`` string literals (spoofs ``'thm' depends on axioms: ...`` lines)
      - ``#eval`` / ``run_cmd`` / ``IO.println`` metaprogramming stdout spoofing
      - Vacuous ``theorem/lemma ... : True :=`` statements (when ``reject_vacuous=True``)
    """
    code = _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", source))
    violations: list[str] = []
    if re.search(r"(?:^|\s)#exit\b", code):
        violations.append("FORGERY_EXIT_TRUNCATION: '#exit' command truncates Lean elaboration")
    if re.search(r"#print\s+\"", code):
        violations.append("FORGERY_PRINT_STRING: '#print \"...\"' string literal spoofs axiom output")
    if re.search(r"(?:^|\s)(?:#eval|run_cmd)\b|\bIO\.print(?:ln)?\b", code):
        violations.append("FORGERY_META_STDOUT: '#eval'/'run_cmd'/'IO.println' stdout spoofing")
    if reject_vacuous and re.search(
        r"\b(?:theorem|lemma)\s+([^\s:({\[]+)[^:=]*:\s*True\s*:=", code
    ):
        violations.append("VACUOUS_TRUE_THEOREM: vacuous ': True :=' theorem statement")
    return violations


def parse_axiom_lines(output: str) -> dict[str, list[str]]:
    """Map fully qualified declaration name -> axioms, from ``#print axioms`` output."""
    found: dict[str, list[str]] = {}
    for m in _AXIOMS_LINE.finditer(output):
        body = m.group(2)
        found[m.group(1)] = (
            [a.strip() for a in body.replace("\n", " ").split(",") if a.strip()] if body else []
        )
    return found


def _lookup_axioms(declared: str, printed: dict[str, list[str]]) -> list[str] | None:
    """Find the printed axioms for a declared (possibly namespace-relative) name."""
    if declared in printed:
        return printed[declared]
    hits = [k for k in printed if k.endswith("." + declared)]
    return printed[hits[0]] if len(hits) == 1 else None


def _failed(name: str, returncode: int, elapsed_ms: float, output: str) -> LeanVerificationResult:
    return LeanVerificationResult(
        theorem_name=name,
        compiled_successfully=False,
        returncode=returncode,
        elapsed_ms=elapsed_ms,
        axioms=[],
        has_sorry=True,
        energy_score=1000000.0,
        output=output,
    )


def main(argv: list[str] | None = None) -> int:
    """``python -m anse.formal.lean_runner FILE.lean``: exit 0 only if every theorem is clean."""
    ap = argparse.ArgumentParser(description="Gate a standalone Lean file (compile + axiom whitelist).")
    ap.add_argument("lean_file", type=Path)
    ap.add_argument("--formal-dir", type=Path, default=None,
                    help="built Lean environment (default: $ANSE_FORMAL_DIR or <repo>/formal)")
    args = ap.parse_args(argv)
    formal = args.formal_dir or (Path(os.environ["ANSE_FORMAL_DIR"]) if os.environ.get("ANSE_FORMAL_DIR") else None)
    results = LeanKernelVerifier(formal).verify_file(args.lean_file)
    ok = all(r.compiled_successfully and not r.has_sorry and not r.untrusted_axioms for r in results)
    print(json.dumps([
        {"theorem": r.theorem_name, "compiled": r.compiled_successfully, "axioms": r.axioms,
         "has_sorry": r.has_sorry, "untrusted": r.untrusted_axioms}
        for r in results
    ], indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
