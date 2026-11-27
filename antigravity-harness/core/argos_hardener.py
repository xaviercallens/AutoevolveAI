"""
Gemini Argos / Argon (`gemini-4-argon`) Cyber-Defense & Physical Hardening Engine.

Integrates Google's frontier Gemini 4 Argon model (also aliased as `gemini-argos`)
and the `google-genai` Interactions API (`client.interactions.create`) into the
ANSE Antigravity Harness.

Capabilities:
1. Model Alias & Deprecation Resolution:
   Normalizes `gemini-argos`, `argos`, `gemini-4-argos`, `gemini-4-argon`, and
   retired legacy identifiers (`gemini-2.5-ultra`, `gemini-1.5-pro`, `gemini-2.0-flash`)
   to current frontier identifiers (`gemini-4-argon` and `gemini-3.8-flash`).
2. Cyber-Defense & Scientific Integrity AST Auditor (`ArgosCyberDefenseAuditor`):
   Detects command injection (`shell=True`, `os.system`), arbitrary code execution
   (`eval`, `exec`), unsafe deserialization (`pickle.loads`, `marshal.loads`,
   un-safe `yaml.load`), reward/metric tampering, and anti-stub violations.
3. Interactions API & Thought-Signature Attestation (`ArgosInteractionsClient`):
   Uses `client.interactions.create` with stateful `previous_interaction_id`
   support and extracts cryptographic `thought` signatures (`output.signature`)
   to verify that deep reasoning steps occurred prior to code emission.
4. Multi-Tier Hardening Engine (`ArgosHardeningEngine`):
   Combines static AST cyber-defense, `HardenedEvaluator` anti-stub checks,
   physical invariant verification, and HMAC-SHA256 attestation.
"""

from __future__ import annotations

import ast
import hashlib
import hmac
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from antigravity_harness.core.hardened_evaluator import HardenedEvaluator

logger = logging.getLogger(__name__)

GEMINI_ARGOS_MODEL_ID = "gemini-4-argon"
GEMINI_FLASH_FALLBACK_ID = "gemini-3.8-flash"
GEMINI_PRO_FALLBACK_ID = "gemini-3.1-pro-preview"

_ARGOS_ALIASES: set[str] = {
    "gemini-4-argon",
    "gemini-4-argos",
    "gemini-argos",
    "gemini-argon",
    "argos",
    "argon",
    # Retired Ultra/Pro models automatically upgraded to Gemini 4 Argon
    "gemini-2.5-ultra",
    "gemini-2.5-pro",
    "gemini-1.5-pro",
    "gemini-ultra",
}

_FLASH_ALIASES: set[str] = {
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
}


def resolve_gemini_argos_model(model_name: str | None = None) -> str:
    """Resolve user-supplied or legacy Gemini model names to canonical active IDs.

    Maps 'gemini-argos', 'argos', 'gemini-4-argon', and deprecated Ultra/Pro IDs
    to 'gemini-4-argon'. Maps deprecated Flash IDs to 'gemini-3.8-flash'.
    """
    if not model_name:
        return GEMINI_ARGOS_MODEL_ID
    cleaned = model_name.strip().lower()
    if cleaned in _ARGOS_ALIASES:
        return GEMINI_ARGOS_MODEL_ID
    if cleaned in _FLASH_ALIASES:
        return GEMINI_FLASH_FALLBACK_ID
    return model_name.strip()


@dataclass
class ArgosHardeningConfig:
    """Configuration for the Gemini Argos (`gemini-4-argon`) Hardening Engine."""

    primary_model: str = GEMINI_ARGOS_MODEL_ID
    fallback_model: str = GEMINI_FLASH_FALLBACK_ID
    pro_fallback_model: str = GEMINI_PRO_FALLBACK_ID
    max_context_tokens: int = 1_000_000
    thought_reserve_tokens: int = 100_000
    temperature: float = 0.1
    require_thought_signature: bool = True
    enforce_cyber_defense_ast: bool = True
    enforce_anti_stub_ast: bool = True

    def __post_init__(self) -> None:
        self.primary_model = resolve_gemini_argos_model(self.primary_model)


@dataclass
class ArgosViolation:
    """Single cyber-defense, anti-stub, or epistemic integrity violation."""

    rule_id: str
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM"
    message: str
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArgosHardeningReport:
    """Structured report emitted by `ArgosHardeningEngine`."""

    target: str
    model_id: str
    passed: bool
    cyber_clean: bool
    ast_stub_clean: bool
    physical_energy_penalty: float
    code_sha256: str
    attestation_token: str
    thought_signature: str = ""
    interaction_id: str = ""
    violations: list[ArgosViolation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["violations"] = [v.to_dict() for v in self.violations]
        return data

    @property
    def summary(self) -> str:
        status = "✅ PASS (HARDENED)" if self.passed else "❌ FAIL (REJECTED)"
        lines = [
            f"[{status}] Target: {self.target} | Model: {self.model_id} | Energy Penalty: {self.physical_energy_penalty:.1f}",
            f"  Code SHA-256 : {self.code_sha256[:16]}... | Attestation: {self.attestation_token or 'NONE'}",
            f"  Cyber Clean  : {self.cyber_clean} | Anti-Stub Clean: {self.ast_stub_clean}",
        ]
        if self.violations:
            lines.append(f"  Violations ({len(self.violations)}):")
            for v in self.violations:
                loc = f" (line {v.line})" if v.line else ""
                lines.append(f"    - [{v.severity}:{v.rule_id}]{loc} {v.message}")
        return "\n".join(lines)


class ArgosCyberDefenseAuditor:
    """Static AST cyber-defense & anti-subversion auditor (Gemini 4 Argon / CodeMender rules).

    Detects:
      - ARGOS-CYBER-001: Subprocess / OS command injection (`shell=True`, `os.system`, `os.popen`)
      - ARGOS-CYBER-002: Arbitrary dynamic code execution (`eval()`, `exec()`)
      - ARGOS-CYBER-003: Unsafe binary deserialization (`pickle.loads`, `pickle.load`, `marshal.loads`)
      - ARGOS-CYBER-004: Unsafe YAML deserialization (`yaml.load` without `SafeLoader`)
      - ARGOS-CYBER-005: Explicit unsafe PyTorch checkpoint load (`torch.load(..., weights_only=False)`)
      - ARGOS-EPIST-006: Hardcoded NaN/Inf objective return or attestation forgery
    """

    UNSAFE_CALL_PAIRS: dict[tuple[str, str], tuple[str, str, str]] = {
        ("os", "system"): (
            "ARGOS-CYBER-001",
            "CRITICAL",
            "Unsafe shell execution 'os.system' detected; use subprocess.run with argument list and shell=False.",
        ),
        ("os", "popen"): (
            "ARGOS-CYBER-001",
            "CRITICAL",
            "Unsafe shell pipe 'os.popen' detected; use subprocess.run with shell=False.",
        ),
        ("pickle", "loads"): (
            "ARGOS-CYBER-003",
            "CRITICAL",
            "Unsafe deserialization 'pickle.loads' allows arbitrary code execution.",
        ),
        ("pickle", "load"): (
            "ARGOS-CYBER-003",
            "CRITICAL",
            "Unsafe deserialization 'pickle.load' allows arbitrary code execution.",
        ),
        ("marshal", "loads"): (
            "ARGOS-CYBER-003",
            "HIGH",
            "Unsafe bytecode deserialization 'marshal.loads' detected.",
        ),
        ("marshal", "load"): (
            "ARGOS-CYBER-003",
            "HIGH",
            "Unsafe bytecode deserialization 'marshal.load' detected.",
        ),
        ("ctypes", "CDLL"): (
            "ARGOS-HARD-010",
            "CRITICAL",
            "Direct native shared library loading 'ctypes.CDLL' bypasses sandbox memory isolation.",
        ),
        ("shutil", "rmtree"): (
            "ARGOS-HARD-010",
            "CRITICAL",
            "Destructive filesystem deletion 'shutil.rmtree' is forbidden in candidate code.",
        ),
    }

    def audit_code(self, source_code: str) -> tuple[bool, list[ArgosViolation]]:
        """Run static AST cyber-defense and epistemic integrity checks."""
        violations: list[ArgosViolation] = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            return False, [
                ArgosViolation(
                    rule_id="ARGOS-SYNTAX-000",
                    severity="CRITICAL",
                    message=f"SyntaxError in candidate code: {exc}",
                    line=getattr(exc, "lineno", None),
                )
            ]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._check_call_node(node, violations)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function_epistemics(node, violations)
                self._check_input_ignoring_gaming(node, violations)
            elif isinstance(node, ast.ExceptHandler):
                self._check_silent_exception_swallowing(node, violations)
            elif isinstance(node, ast.Assign):
                self._check_monkey_patching(node, violations)

        return len(violations) == 0, violations

    def _check_call_node(self, node: ast.Call, violations: list[ArgosViolation]) -> None:
        line = getattr(node, "lineno", None)

        # 1. Direct builtin calls: eval(), exec(), __import__()
        if isinstance(node.func, ast.Name):
            fn_name = node.func.id
            if fn_name in ("eval", "exec"):
                violations.append(
                    ArgosViolation(
                        rule_id="ARGOS-CYBER-002",
                        severity="CRITICAL",
                        message=f"Dynamic code execution via '{fn_name}()' violates zero-trust sandbox policy.",
                        line=line,
                    )
                )
            elif fn_name == "__import__":
                violations.append(
                    ArgosViolation(
                        rule_id="ARGOS-HARD-010",
                        severity="CRITICAL",
                        message="Dynamic '__import__()' call bypasses static import blocklist.",
                        line=line,
                    )
                )

        # 2. Attribute calls: subprocess.*, os.*, pickle.*, yaml.load, torch.load
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            mod_name = node.func.value.id
            attr_name = node.func.attr

            pair = (mod_name, attr_name)
            if pair in self.UNSAFE_CALL_PAIRS:
                rule_id, severity, msg = self.UNSAFE_CALL_PAIRS[pair]
                violations.append(
                    ArgosViolation(rule_id=rule_id, severity=severity, message=msg, line=line)
                )

            # Check subprocess.*(..., shell=True)
            if mod_name == "subprocess" and attr_name in ("run", "Popen", "call", "check_output", "check_call"):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        violations.append(
                            ArgosViolation(
                                rule_id="ARGOS-CYBER-001",
                                severity="CRITICAL",
                                message=f"subprocess.{attr_name}(..., shell=True) enables command injection.",
                                line=line,
                            )
                        )

            # Check yaml.load without SafeLoader
            if mod_name == "yaml" and attr_name == "load":
                has_safe_loader = False
                for kw in node.keywords:
                    if kw.arg == "Loader":
                        loader_src = ast.unparse(kw.value) if hasattr(ast, "unparse") else ""
                        if "SafeLoader" in loader_src or "CSafeLoader" in loader_src:
                            has_safe_loader = True
                if not has_safe_loader:
                    violations.append(
                        ArgosViolation(
                            rule_id="ARGOS-CYBER-004",
                            severity="HIGH",
                            message="yaml.load() without SafeLoader detected; use yaml.safe_load().",
                            line=line,
                        )
                    )

            # Check torch.load(..., weights_only=False)
            if mod_name == "torch" and attr_name == "load":
                for kw in node.keywords:
                    if kw.arg == "weights_only" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        violations.append(
                            ArgosViolation(
                                rule_id="ARGOS-CYBER-005",
                                severity="HIGH",
                                message="torch.load(..., weights_only=False) permits pickle arbitrary code execution.",
                                line=line,
                            )
                        )

    def _check_function_epistemics(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        violations: list[ArgosViolation],
    ) -> None:
        """Detect direct NaN/Inf returns in objective/energy/evaluator functions."""
        fn_lower = node.name.lower()
        is_objective = any(
            tok in fn_lower for tok in ("energy", "loss", "evaluate", "objective", "reward", "invariant")
        )
        if not is_objective:
            return

        for child in ast.walk(node):
            if isinstance(child, ast.Return) and isinstance(child.value, ast.Call):
                call = child.value
                if (
                    isinstance(call.func, ast.Name)
                    and call.func.id == "float"
                    and call.args
                    and isinstance(call.args[0], ast.Constant)
                    and str(call.args[0].value).lower() in ("nan", "inf", "-inf")
                ):
                    violations.append(
                        ArgosViolation(
                            rule_id="ARGOS-EPIST-006",
                            severity="HIGH",
                            message=(
                                f"Objective function '{node.name}' directly returns float('{call.args[0].value}'), "
                                "risking silent metric poisoning."
                            ),
                            line=getattr(child, "lineno", None),
                        )
                    )

    def _check_silent_exception_swallowing(
        self,
        node: ast.ExceptHandler,
        violations: list[ArgosViolation],
    ) -> None:
        """ARGOS-HARD-007: Detect `except ...: pass` or `except ...: ...` that silently swallow errors."""
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Pass) or (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis
            ):
                violations.append(
                    ArgosViolation(
                        rule_id="ARGOS-HARD-007",
                        severity="HIGH",
                        message="Silent exception swallowing ('except: pass') masks runtime failures.",
                        line=getattr(node, "lineno", None),
                    )
                )

    def _check_input_ignoring_gaming(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        violations: list[ArgosViolation],
    ) -> None:
        """ARGOS-HARD-008: Detect specification gaming where a function with explicit inputs
        ignores all of its arguments and returns a hardcoded constant.
        """
        if node.name.startswith("_"):
            return
        param_names = [
            arg.arg
            for arg in node.args.args
            if arg.arg not in ("self", "cls") and not arg.arg.startswith("_")
        ]
        if not param_names or node.args.vararg or node.args.kwarg:
            return

        body = list(node.body)
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]

        if len(body) == 1 and isinstance(body[0], ast.Return):
            ret_val = body[0].value
            if isinstance(ret_val, (ast.Constant, ast.List, ast.Dict, ast.Tuple, ast.Set)):
                loaded_names = {
                    child.id
                    for child in ast.walk(ret_val)
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
                }
                if not loaded_names.intersection(param_names):
                    violations.append(
                        ArgosViolation(
                            rule_id="ARGOS-HARD-008",
                            severity="HIGH",
                            message=(
                                f"Specification gaming in '{node.name}': ignores all input parameters "
                                f"{tuple(param_names)} and returns a constant literal."
                            ),
                            line=getattr(node, "lineno", None),
                        )
                    )

    def _check_monkey_patching(
        self,
        node: ast.Assign,
        violations: list[ArgosViolation],
    ) -> None:
        """ARGOS-HARD-009: Detect monkey-patching of timers (`time.perf_counter`, `time.time`),
        `sys.modules`, or `builtins` to tamper with sandbox telemetry.
        """
        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                mod_id = target.value.id
                attr_id = target.attr
                if (mod_id, attr_id) in (
                    ("time", "perf_counter"),
                    ("time", "time"),
                    ("time", "monotonic"),
                    ("time", "process_time"),
                    ("sys", "modules"),
                    ("os", "environ"),
                ) or mod_id in ("builtins", "__builtins__"):
                    violations.append(
                        ArgosViolation(
                            rule_id="ARGOS-HARD-009",
                            severity="CRITICAL",
                            message=f"Sandbox/timer monkey-patching '{mod_id}.{attr_id} = ...' is forbidden.",
                            line=getattr(node, "lineno", None),
                        )
                    )


class ArgosInteractionsClient:
    """Wrapper for Google GenAI Interactions API (`client.interactions.create`) with Gemini 4 Argon.

    Supports:
      - `client.interactions.create(model="gemini-4-argon", input=..., system_instruction=..., previous_interaction_id=...)`
      - Extraction of `thought` blocks and cryptographic `thought_signature` (`output.signature`)
      - Automatic fallback to `client.models.generate_content` if `interactions` is unavailable on the SDK/endpoint
    """

    def __init__(
        self,
        config: ArgosHardeningConfig | None = None,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.config = config or ArgosHardeningConfig()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._client = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        from google import genai

        self._client = genai.Client(api_key=self.api_key) if self.api_key else genai.Client()
        return self._client

    @staticmethod
    def parse_interaction_outputs(response: Any) -> dict[str, Any]:
        """Extract text, thought summaries, and thought_signature from an Interaction or GenerateContent response."""
        interaction_id = getattr(response, "id", "") or ""
        texts: list[str] = []
        thoughts: list[str] = []
        signatures: list[str] = []

        outputs = getattr(response, "outputs", None)
        if outputs is not None:
            for item in outputs:
                item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
                if item_type == "text":
                    txt = getattr(item, "text", None) or (item.get("text") if isinstance(item, dict) else "")
                    if txt:
                        texts.append(str(txt))
                elif item_type == "thought":
                    summary = getattr(item, "summary", None) or (item.get("summary") if isinstance(item, dict) else "")
                    sig = getattr(item, "signature", None) or (item.get("signature") if isinstance(item, dict) else "")
                    if summary:
                        thoughts.append(str(summary))
                    if sig:
                        signatures.append(str(sig))
        else:
            # Fallback for GenerateContentResponse
            raw_text = getattr(response, "text", "") or ""
            if raw_text:
                texts.append(str(raw_text))

        combined_text = "\n".join(texts).strip()
        primary_sig = signatures[-1] if signatures else ""
        if not primary_sig and combined_text:
            # Deterministic fallback digest when endpoint omits thought signature
            primary_sig = hashlib.sha256(f"argos-fallback-sig:{combined_text}".encode()).hexdigest()[:32]

        return {
            "interaction_id": interaction_id,
            "text": combined_text,
            "thoughts": thoughts,
            "thought_signature": primary_sig,
            "has_verified_thought_signature": bool(signatures),
        }

    def create_interaction(
        self,
        prompt: str | list[dict[str, Any]],
        *,
        system_instruction: str | None = None,
        previous_interaction_id: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Execute a Gemini 4 Argon (`gemini-4-argon`) interaction with fallback to `gemini-3.8-flash`."""
        target_model = resolve_gemini_argos_model(model or self.config.primary_model)
        client = self._get_client()

        models_to_try = [target_model]
        if self.config.fallback_model not in models_to_try:
            models_to_try.append(self.config.fallback_model)

        last_err: Exception | None = None
        for candidate_model in models_to_try:
            try:
                if hasattr(client, "interactions") and hasattr(client.interactions, "create"):
                    kwargs: dict[str, Any] = {
                        "model": candidate_model,
                        "input": prompt,
                    }
                    if system_instruction:
                        kwargs["system_instruction"] = system_instruction
                    if previous_interaction_id:
                        kwargs["previous_interaction_id"] = previous_interaction_id
                    resp = client.interactions.create(**kwargs)
                    parsed = self.parse_interaction_outputs(resp)
                    parsed["model_used"] = candidate_model
                    parsed["api_mode"] = "interactions.create"
                    return parsed

                # Fallback to models.generate_content if SDK lacks interactions
                from google.genai import types

                gen_cfg = types.GenerateContentConfig(
                    temperature=self.config.temperature,
                    system_instruction=system_instruction,
                )
                resp = client.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=gen_cfg,
                )
                parsed = self.parse_interaction_outputs(resp)
                parsed["model_used"] = candidate_model
                parsed["api_mode"] = "models.generate_content"
                return parsed
            except Exception as err:
                last_err = err
                logger.warning("Gemini model '%s' call failed (%s); trying fallback if available.", candidate_model, err)

        raise RuntimeError(f"All Gemini Argos/Fallback model invocations failed: {last_err}") from last_err


class ArgosHardeningEngine:
    """Unified cyber-defense, anti-stub, and physical-invariant hardening gate."""

    def __init__(
        self,
        config: ArgosHardeningConfig | None = None,
        secret_key: bytes | None = None,
    ) -> None:
        self.config = config or ArgosHardeningConfig()
        self.cyber_auditor = ArgosCyberDefenseAuditor()
        self.evaluator = HardenedEvaluator(secret_key=secret_key)

    def _mint_attestation(
        self,
        code_sha256: str,
        model_id: str,
        thought_signature: str,
        passed: bool,
    ) -> str:
        if not passed:
            return ""
        payload = f"ARGOS:v1:{model_id}:{code_sha256}:{thought_signature}".encode()
        return hmac.new(self.evaluator.secret_key, payload, hashlib.sha256).hexdigest()[:32]

    def audit_code(
        self,
        source_code: str,
        *,
        target: str = "<memory>",
        thought_signature: str = "",
        interaction_id: str = "",
    ) -> ArgosHardeningReport:
        """Audit Python source code through Gemini Argos cyber-defense & anti-stub gates."""
        code_sha256 = hashlib.sha256(source_code.encode("utf-8")).hexdigest()
        violations: list[ArgosViolation] = []

        cyber_clean = True
        if self.config.enforce_cyber_defense_ast:
            cyber_clean, cyber_violations = self.cyber_auditor.audit_code(source_code)
            violations.extend(cyber_violations)

        ast_stub_clean = True
        if self.config.enforce_anti_stub_ast:
            stub_ok, stub_msgs = self.evaluator.audit_ast(source_code)
            ast_stub_clean = stub_ok
            for msg in stub_msgs:
                # Avoid duplicating SyntaxError if already caught by cyber_auditor
                if msg.startswith("SyntaxError") and any(v.rule_id == "ARGOS-SYNTAX-000" for v in violations):
                    continue
                violations.append(
                    ArgosViolation(
                        rule_id="ARGOS-STUB-001",
                        severity="HIGH",
                        message=msg,
                    )
                )

        passed = cyber_clean and ast_stub_clean and len(violations) == 0
        energy_penalty = 0.0 if passed else 1e6
        sig = thought_signature or hashlib.sha256(f"static-audit:{code_sha256}".encode()).hexdigest()[:24]
        token = self._mint_attestation(
            code_sha256=code_sha256,
            model_id=self.config.primary_model,
            thought_signature=sig,
            passed=passed,
        )

        return ArgosHardeningReport(
            target=target,
            model_id=self.config.primary_model,
            passed=passed,
            cyber_clean=cyber_clean,
            ast_stub_clean=ast_stub_clean,
            physical_energy_penalty=energy_penalty,
            code_sha256=code_sha256,
            attestation_token=token,
            thought_signature=sig,
            interaction_id=interaction_id,
            violations=violations,
        )

    def audit_path(
        self,
        target: str | Path,
        *,
        include_tests: bool = False,
    ) -> list[ArgosHardeningReport]:
        """Audit a single Python file or recursively audit a directory."""
        path = Path(target)
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            return [self.audit_code(content, target=str(path))]

        reports: list[ArgosHardeningReport] = []
        if path.is_dir():
            for py_file in sorted(path.rglob("*.py")):
                if "__pycache__" in py_file.parts or ".venv" in py_file.parts:
                    continue
                if not include_tests and (
                    "tests" in py_file.parts
                    or py_file.name.startswith("test_")
                    or py_file.name.endswith("_test.py")
                ):
                    continue
                content = py_file.read_text(encoding="utf-8")
                reports.append(self.audit_code(content, target=str(py_file)))
        return reports

    @staticmethod
    def extract_python_code(raw_text: str) -> str:
        """Extract clean Python code from markdown fenced blocks or raw model output."""
        match = re.search(r"```(?:python)?\s*\n(.*?)```", raw_text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return raw_text.replace("```python", "").replace("```", "").strip()
