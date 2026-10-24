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

import math

# The only axioms a kernel-checked Mathlib proof may depend on. Anything else
# (e.g. a smuggled `axiom cheat : False`) compiles with exit code 0 and would
# previously pass this gate — verified empirically on 2026-09-27.
TRUSTED_AXIOMS: frozenset[str] = frozenset({"propext", "Classical.choice", "Quot.sound"})


def compute_hierarchical_lean_energy(
    source: str,
    output: str,
    compiled_successfully: bool,
    has_sorry: bool,
    untrusted_axioms: Sequence[str] = (),
    has_forgery: bool = False,
    alpha: float = 1.5,
) -> float:
    """Compute the Hierarchical Continuous Energy Functional E(tau) for Lean 4 trajectories.

     Implements the 4-regime dense progress-based energy shaping:
      1. Sound & kernel-verified (E <= 0): -alpha * CompressionRatio(tau)
      2. Partial elaboration (unsolved goals / localized type errors):
         100 * (N_unsolved / N_total) + 10 * N_type_errors
      3. Syntax failure, sorryAx, untrusted axiom, or forgery attempt: 10^6
    """
    if has_forgery or has_sorry or untrusted_axioms:
        return 1000000.0
    if compiled_successfully:
        non_empty_lines = [ln for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("--")]
        compression_ratio = max(0.25, min(4.0, 20.0 / max(len(non_empty_lines), 5)))
        return round(-alpha * compression_ratio, 4)

    lowered = output.lower()
    if "unknown identifier" in lowered or "expected token" in lowered or "unexpected end of input" in lowered:
        return 1000000.0

    unsolved = len(re.findall(r"unsolved goals", lowered))
    type_errors = len(
        re.findall(r"type mismatch|application type mismatch|failed to synthesize|linarith failed|omega_1|norm_num failed", lowered)
    )
    if unsolved > 0 or type_errors > 0:
        n_total = max(unsolved + 2, 3)
        return round(100.0 * (unsolved / n_total) + 10.0 * max(type_errors, 1), 4)
    return 1000000.0


def compute_hierarchical_numeric_energy(
    ham_drift: float,
    dec_drift: float = 0.0,
    eps_ham: float = 1e-8,
    eps_dec: float = 1e-12,
    compression_ratio: float = 1.0,
    alpha: float = 1.5,
) -> float:
    """Compute the Hierarchical Continuous Energy Functional E(tau) for numeric/topological trajectories.

    If ham_drift <= eps_ham and dec_drift <= eps_dec, returns -alpha * compression_ratio <= 0.
    Otherwise returns 10^3 * log10(1 + ham_drift/eps_ham + dec_drift/eps_dec).
    """
    if math.isnan(ham_drift) or math.isnan(dec_drift) or math.isinf(ham_drift) or math.isinf(dec_drift):
        return 1000000.0
    if ham_drift <= eps_ham and dec_drift <= eps_dec:
        return round(-alpha * max(compression_ratio, 0.1), 4)
    ratio = max(0.0, ham_drift / max(eps_ham, 1e-30)) + max(0.0, dec_drift / max(eps_dec, 1e-30))
    return round(min(1000000.0, 1000.0 * math.log10(1.0 + ratio)), 4)


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
    hierarchical_energy: float = 0.0

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
        if self.hierarchical_energy == 0.0:
            self.hierarchical_energy = compute_hierarchical_lean_energy(
                source="",
                output=self.output,
                compiled_successfully=self.compiled_successfully,
                has_sorry=self.has_sorry,
                untrusted_axioms=self.untrusted_axioms,
            )

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
                hierarchical_energy=compute_hierarchical_lean_energy(
                    source=source,
                    output=raw,
                    compiled_successfully=clean,
                    has_sorry=has_sorry,
                    untrusted_axioms=untrusted,
                ),
            ))
        return results

    def verify_against_spec(
        self,
        candidate_file: Path | str,
        spec_file: Path | str,
        theorem_to_spec_map: dict[str, str],
        timeout_s: float = 1800.0,
        require_coverage_of_spec: bool = False,
    ) -> dict[str, object]:
        """Environment-level DefEq & ConstantInfo audit against a read-only Spec.lean file.

        Combines the frozen `Spec.lean` propositions with the candidate proofs in a fresh
        kernel environment and checks `example : <SpecProp> := <CandidateThm>` for every
        target theorem, preventing macro/notation hijacking or type-alias obfuscation.
        """
        import hashlib
        import tempfile

        # `len(theorem_to_spec_map) >= 1` below rejects a vacuous audit, but it
        # does not require the obligations to COVER the spec: a caller may check
        # one easy proposition and ignore the rest. For a generic verifier that
        # is correct -- only the caller knows which propositions matter -- but it
        # means a search could be judged against a weak subset it chose itself.
        # `require_coverage_of_spec` lets a caller close that without hard-coding
        # a spec-specific count: coverage is derived from the spec's own declared
        # theorems.
        cand_path = Path(candidate_file).resolve()
        spec_path = Path(spec_file).resolve()
        cand_src = cand_path.read_text(encoding="utf-8")
        spec_src = spec_path.read_text(encoding="utf-8")
        spec_sha256 = hashlib.sha256(spec_src.encode("utf-8")).hexdigest()

        forgeries = detect_lean_source_forgeries(cand_src, reject_vacuous=True)
        if forgeries:
            return {
                "passed": False,
                "rc": -2,
                "spec_sha256": spec_sha256,
                "forgeries": forgeries,
                "defeq_checked": 0,
                "results": [],
                "error": "; ".join(forgeries),
            }

        # Collect union of imports from spec and candidate
        imports: list[str] = []
        spec_body_lines: list[str] = []
        cand_body_lines: list[str] = []
        for line in spec_src.splitlines():
            if line.strip().startswith("import "):
                if line.strip() not in imports:
                    imports.append(line.strip())
            else:
                spec_body_lines.append(line)
        for line in cand_src.splitlines():
            stripped = line.strip()
            if stripped.startswith("import "):
                if stripped.endswith(spec_path.stem):
                    continue
                if stripped not in imports:
                    imports.append(stripped)
            else:
                cand_body_lines.append(line)

        defeq_lines = defeq_obligation_lines(theorem_to_spec_map)

        combined_src = (
            "\n".join(imports)
            + "\n\n"
            + "\n".join(spec_body_lines)
            + "\n\n"
            + "\n".join(cand_body_lines)
            + "\n"
            + "\n".join(defeq_lines)
            + "\n"
        )
        # `verify_file` wants an `#print axioms` line for the declarations it
        # gates, and the obligations emitted above are new top-level theorems
        # that no input file could have anticipated, so their axiom lines are
        # supplied here.
        #
        # Only the obligations. An earlier attempt added a line for every name
        # `declared_theorems` returned, which silently broke everything: that
        # helper yields UNQUALIFIED names (`det_eq_one`) while a spec's own
        # directives are fully qualified (`#print axioms ANSE.Verlet.det_eq_one`),
        # so nothing matched, seven unresolvable directives were appended after
        # the namespace had closed, and the audit file stopped compiling. The
        # obligations are emitted at top level, so their bare names resolve.
        obligation_axiom_lines = [
            f"#print axioms {defeq_theorem_name(name)}" for name in theorem_to_spec_map
        ]
        if obligation_axiom_lines:
            combined_src += "\n".join(obligation_axiom_lines) + "\n"

        with tempfile.TemporaryDirectory(prefix="lean_spec_audit_") as td:
            audit_file = Path(td) / "SpecDefEqAudit.lean"
            audit_file.write_text(combined_src, encoding="utf-8")
            results = self.verify_file(audit_file, timeout_s=timeout_s, reject_vacuous=True)

        # `defeq_checked` is MEASURED, not derived. It previously read
        # `len(theorem_to_spec_map) if all_ok else 0`, which made it a tautology
        # of `passed`: a caller asserting `defeq_checked == len(map)` learned
        # nothing beyond `passed`, so the conjunct carried no information. The
        # obligations are now emitted as NAMED theorems, so each one produces its
        # own `#print axioms` row and can be counted independently.
        spec_declared = set(declared_theorems(spec_src))
        # An obligation key may be qualified (`Ns.thm`); the spec's declarations
        # come back unqualified, so compare on the final component.
        covered = {name.rsplit(".", 1)[-1] for name in theorem_to_spec_map}
        uncovered = sorted(spec_declared - covered)
        obligation_names = {defeq_theorem_name(name) for name in theorem_to_spec_map}
        defeq_checked = sum(
            1
            for r in results
            if r.theorem_name in obligation_names
            and r.compiled_successfully
            and not r.has_sorry
            and not r.untrusted_axioms
        )
        every_result_clean = all(
            r.compiled_successfully and not r.has_sorry and not r.untrusted_axioms
            for r in results
        )
        # An EMPTY obligation set must not pass. The old predicate was
        # `len(results) >= len(theorem_to_spec_map) and all(...)`, and with an
        # empty map `len(results) >= 0` is vacuously true while `all()` over an
        # empty sequence is also true -- so `verify_against_spec` returned
        # passed=True having checked nothing at all. That is the one gate the
        # proof-carrying fitness ladder calls load-bearing, so a vacuous pass
        # there collapses the whole ladder back to the empirical objective it
        # was written to replace.
        all_ok = (
            len(theorem_to_spec_map) >= 1
            and len(results) >= len(theorem_to_spec_map)
            and defeq_checked == len(theorem_to_spec_map)
            and every_result_clean
            and not (require_coverage_of_spec and uncovered)
        )
        return {
            "passed": all_ok,
            "rc": 0 if all_ok else 1,
            "spec_file": str(spec_path),
            "spec_sha256": spec_sha256,
            "forgeries": [],
            "obligations_requested": len(theorem_to_spec_map),
            "defeq_checked": defeq_checked,
            # Spec propositions the caller did NOT ask about. Reported always,
            # enforced only under `require_coverage_of_spec`, so a caller that
            # checks a weak subset can at least be seen doing it.
            "spec_theorems_declared": sorted(spec_declared),
            "spec_theorems_uncovered": uncovered,
            "coverage_enforced": bool(require_coverage_of_spec),
            "every_result_clean": every_result_clean,
            "results": results,
        }

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


DEFEQ_PREFIX = "defeqAudit_"


def defeq_theorem_name(theorem_name: str) -> str:
    """The name given to the definitional-equality obligation for `theorem_name`.

    Obligations used to be emitted as anonymous ``example : P := thm``, which
    declares nothing, so no obligation could be counted and `defeq_checked` had
    to be derived from the overall pass flag -- making it a tautology. Naming
    each obligation is what lets it be measured.
    """
    safe = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in theorem_name)
    return f"{DEFEQ_PREFIX}{safe}"


def defeq_obligation_lines(theorem_to_spec_map: dict[str, str]) -> list[str]:
    """Named definitional-equality obligations, one per mapped theorem.

    Each becomes a real declaration, so `verify_file` reports a row for it and
    the caller can count how many obligations actually elaborated with clean
    axioms rather than trusting an aggregate flag.
    """
    lines = ["", "section EnvironmentDefEqAudit"]
    for thm_name, spec_prop in theorem_to_spec_map.items():
        lines.append(
            f"theorem {defeq_theorem_name(thm_name)} : {spec_prop} := {thm_name}"
        )
    lines.append("end EnvironmentDefEqAudit")
    return lines


def detect_lean_source_forgeries(source: str, reject_vacuous: bool = True) -> list[str]:
    """Detect source-level, definition-hole, and macro/alias formal verification bypasses.

    Checks stripped Lean source code (outside comments/docstrings) for:
      - ``#exit`` directive (truncates elaboration before broken proofs or after forged prints)
      - ``#print "..."`` string literals (spoofs ``'thm' depends on axioms: ...`` lines)
      - ``#eval`` / ``run_cmd`` / ``IO.println`` metaprogramming stdout spoofing
      - Macro / notation hijacking (``macro_rules``, ``local notation``, ``scoped notation``)
      - Vacuous ``theorem/lemma ... : True :=`` or type-alias ``abbrev/def ... := True``
      - Definition-hole ``sorry`` smuggling (``def/abbrev ... := sorry``, from OpenAI-NSE/MavNan audit)
    """
    code = _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", source))
    violations: list[str] = []
    if re.search(r"(?:^|\s)#exit\b", code):
        violations.append("FORGERY_EXIT_TRUNCATION: '#exit' command truncates Lean elaboration")
    if re.search(r"#print\s+\"", code):
        violations.append("FORGERY_PRINT_STRING: '#print \"...\"' string literal spoofs axiom output")
    if re.search(r"(?:^|\s)(?:#eval|run_cmd)\b|\bIO\.print(?:ln)?\b", code):
        violations.append("FORGERY_META_STDOUT: '#eval'/'run_cmd'/'IO.println' stdout spoofing")
    if re.search(r"(?:^|\s)(?:macro_rules|(?:local|scoped)\s+notation)\b", code):
        violations.append("FORGERY_NOTATION_HIJACK: macro_rules or local/scoped notation override")
    if reject_vacuous:
        if re.search(r"\b(?:theorem|lemma)\s+([^\s:({\[]+)(?:(?!:=)[\s\S])*:\s*True\s*:=", code):
            violations.append("VACUOUS_TRUE_THEOREM: vacuous ': True :=' theorem statement")
        if re.search(r"\b(?:abbrev|def)\s+([^\s:({\[]+)(?:(?!:=)[^\n])*:=\s*(?:True|Trivial)\b", code):
            violations.append("FORGERY_VACUOUS_ALIAS: type alias ':= True' obfuscation (Comparator definition-hole exploit)")
        if re.search(r"\b(?:abbrev|def)\s+([^\s:({\[]+)(?:(?!:=)[^\n])*:=\s*(?:by\s+)?sorry\b", code):
            violations.append("FORGERY_DEFINITION_SORRY: 'def/abbrev ... := sorry' definition-hole smuggling")
    return violations


def extract_lean_definition_bodies(source: str) -> dict[str, str]:
    """Extract normalized bodies of top-level `def`/`abbrev` declarations for Comparator hole auditing."""
    code = _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", source))
    pattern = re.compile(
        r"^[ \t]*(?:noncomputable[ \t]+)?(?:def|abbrev)[ \t]+([^\s:({\[]+)(?:(?!:=|\bwhere\b)[\s\S])*?(?::=|\bwhere\b)\s*(.*?)(?=\n[ \t]*(?:noncomputable[ \t]+)?(?:def|abbrev|theorem|lemma|structure|inductive|end|namespace|#print)\b|\Z)",
        re.M | re.S,
    )
    bodies: dict[str, str] = {}
    for m in pattern.finditer(code):
        name = m.group(1).strip()
        body = " ".join(m.group(2).split())
        bodies[name] = body
    return bodies


def verify_definition_holes_against_spec(
    candidate_src: str,
    spec_src: str,
    definition_names: Sequence[str],
) -> dict[str, object]:
    """Close the `openai/math` Comparator `definitionHoleMatches` vulnerability (LL.md §16, §25d).

    Comparator's `definitionHoleMatches` checks only `(name, levelParams, type, safety)` of a
    definition in `definition_names`, allowing a candidate to replace `def MainStatement : Prop := ...`
    with `def MainStatement : Prop := True`. This verifier enforces that every listed definition exists
    in both `spec_src` and `candidate_src`, is neither `True` nor `sorry`, and has an identical
    normalized body.
    """
    spec_defs = extract_lean_definition_bodies(spec_src)
    cand_defs = extract_lean_definition_bodies(candidate_src)
    mismatches: list[str] = []
    checked: list[str] = []
    for dname in definition_names:
        short = dname.split(".")[-1]
        s_body = spec_defs.get(dname) or spec_defs.get(short)
        c_body = cand_defs.get(dname) or cand_defs.get(short)
        if s_body is None:
            mismatches.append(f"MISSING_IN_SPEC:{dname}")
            continue
        if c_body is None:
            mismatches.append(f"MISSING_IN_CANDIDATE:{dname}")
            continue
        if c_body in {"True", "Trivial", "sorry", "by sorry"}:
            mismatches.append(f"VACUOUS_OR_SORRY_HOLE:{dname}={c_body}")
            continue
        if s_body != c_body:
            mismatches.append(f"BODY_DRIFT:{dname}: spec='{s_body}' vs cand='{c_body}'")
            continue
        checked.append(dname)
    return {
        "sound": len(mismatches) == 0,
        "passed": len(mismatches) == 0,
        "checked_count": len(checked),
        "checked_definitions": checked,
        "mismatches": mismatches,
    }


def verify_manuscript_data_consistency(
    tex_source: str,
    required_tokens: Sequence[str],
    require_proof_per_theorem: bool = True,
) -> dict[str, object]:
    """Audit a LaTeX manuscript against single-source JSON tokens and proof completeness (LL.md §25a, §25e)."""
    thm_count = len(re.findall(r"\\begin\{theorem\}", tex_source))
    proof_count = len(re.findall(r"\\begin\{proof\}", tex_source))
    missing_tokens = [tok for tok in required_tokens if tok not in tex_source]
    neg_zero_hits = re.findall(r"\$-0\$|\\mathbf\{-0\}", tex_source)
    errors: list[str] = []
    if require_proof_per_theorem and proof_count < thm_count:
        errors.append(f"MISSING_PROOFS: {proof_count} proofs for {thm_count} theorems")
    if missing_tokens:
        errors.append(f"MISSING_HARNESS_TOKENS: {missing_tokens}")
    if neg_zero_hits:
        errors.append(f"NEGATIVE_ZERO_ARTIFACT: {neg_zero_hits}")
    return {
        "sound": len(errors) == 0,
        "passed": len(errors) == 0,
        "theorem_count": thm_count,
        "proof_count": proof_count,
        "missing_tokens": missing_tokens,
        "negative_zero_hits": neg_zero_hits,
        "errors": errors,
    }


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
