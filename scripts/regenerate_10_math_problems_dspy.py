import os
import json
import logging
from pathlib import Path
from anse.core.red_team import DeepThinkAuditor
from anse.core.api_extractor import APIExtractor
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DSPy-DeepSeek-Regenerator")

# Simulated DSPy Signature / Pipeline for Lean 4 Proof Generation
class DSPyLeanProver:
    def __init__(self, call_log_path: str | Path | None = None):
        # In a real environment, this connects to the GCP T4 Serverless Endpoint
        # or local Ollama (deepseek-r1:14b)
        # timeout_s was 1.0 until 2026-09-27: every call timed out and the old
        # except-branch substituted a fake `True := by trivial` proof, so the
        # run-one "20/20 rejected" result measured the fallback, not the model.
        self.llm = APIExtractor(timeout_s=900.0, call_log_path=call_log_path)
        self.auditor = DeepThinkAuditor(extractor=self.llm)

    @staticmethod
    def _prepare_lean_source_for_kernel(lean_code: str) -> str:
        """Ensure declared theorems carry `#print axioms <name>` for `lean_runner.verify_file`."""
        from anse.formal.lean_runner import declared_theorems

        code = lean_code.strip()
        for thm in declared_theorems(code):
            marker = f"#print axioms {thm}"
            if marker not in code:
                code = f"{code}\n{marker}\n"
        return code

    def verify_lean_code(self, lean_code: str) -> dict:
        """Verify generated Lean 4 source via `lean_runner` (`LeanKernelVerifier.verify_file`)."""
        import tempfile

        prepared = self._prepare_lean_source_for_kernel(lean_code)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False, encoding="utf-8") as tmp:
            tmp.write(prepared)
            tmp_path = Path(tmp.name)
        try:
            return self.auditor.verify_with_lean_kernel(str(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)

    def generate_proof(self, theorem_statement: str) -> dict:
        logger.info(f"Generating proof for: {theorem_statement}")

        prompt = f"Write a Lean 4 formal proof for the following theorem. Do not use 'sorry'. Provide topologically sound proof.\nTheorem: {theorem_statement}"

        try:
            response, _ = self.llm.extract(prompt=prompt, system_prompt="You are an expert Lean 4 mathematician.")
        except Exception as exc:
            logger.error("Generation failed for %s: %s", theorem_statement, exc)
            return {
                "theorem": theorem_statement,
                "generated_code": "",
                "audit_verdict": f"GENERATION_FAILED: {type(exc).__name__}",
                "kernel_clean": False,
                "kernel_theorems": [],
                "thoughts": [],
            }

        if "unknown identifier" in response or "import" not in response:
            logger.info("Missing imports detected; asking the model to repair them.")
            try:
                rag_prompt = f"Compilation failed: unknown identifier. Search Mathlib4, find the missing import, add it to the header, and re-submit.\n{response}"
                response, _ = self.llm.extract(prompt=rag_prompt, system_prompt="You are a RAG agent connected to LeanDojo.")
            except Exception as exc:
                logger.error("Import repair failed for %s: %s", theorem_statement, exc)

        # Improvement A: Semantic Typeclass Radar (Anti-Cheat Gate)
        # Fast-fail before invoking Lean kernel
        is_geometry = "Gauss-Bonnet" in theorem_statement or "Manifold" in theorem_statement or "Riemann" in theorem_statement
        if is_geometry and "import Mathlib.Geometry" not in response:
            logger.warning("Semantic Radar Triggered: Heavy topology modules missing. Applying E=10^6 Penalty.")
            return {
                "theorem": theorem_statement,
                "generated_code": response,
                "audit_verdict": "REJECT: EPISTEMIC CHEATING (SEMANTIC RADAR)",
                "kernel_clean": False,
                "kernel_theorems": [],
                "thoughts": ["<think>Intercepted by Semantic Typeclass Radar before kernel evaluation. E=10^6.</think>"],
            }

        # 2. Ground-Truth Formal Verification via lean_runner (TODO 7)
        kernel_result = self.verify_lean_code(response)
        logger.info(f"Lean Runner Verdict: {kernel_result['verdict']}")

        return {
            "theorem": theorem_statement,
            "generated_code": response,
            "audit_verdict": kernel_result["verdict"],
            "kernel_clean": kernel_result["clean"],
            "kernel_theorems": kernel_result["theorems"],
            "thoughts": [],
        }

def run_regeneration(num_problems: int = 10, call_log_path: str | Path | None = None):
    call_log_path = call_log_path or os.environ.get("ANSE_CALL_LOG")
    prover = DSPyLeanProver(call_log_path=call_log_path)

    problems_all = [
        "Lagrange's Subgroup Index Multiplicativity",
        "Parallelogram Identity in Real Hilbert Spaces",
        "Banach Contraction Mapping & Unique Fixed Point",
        "Cauchy-Riemann Equations Implies Harmonicity",
        "Gauss-Bonnet Total Curvature Quantization on S2",
        "Coboundary Nilpotency in Discrete Exterior Calculus (d2 = 0)",
        "Discrete Gronwall Lemma & Dynamic Dissipation Bound",
        "Fermat's Little Theorem in Modular Arithmetic ZpZ",
        "Markov-Chebyshev Level Set Functional Inequality",
        "Cauchy-Schwarz Inequality in Real Inner Product Space",
        "Stokes' Theorem: Boundary Integration & Vector Calculus",
        "Fundamental Theorem of Algebra: Polynomial Roots",
        "Picard-Lindelöf Uniqueness of ODEs",
        "Gromov-Witten Invariants in Algebraic Geometry",
        "Elliptic Regularity & Sobolev Space Embedding",
        "Kähler-Einstein Metrics & Fano Surfaces",
        "Intersection Theory: Bézout's Theorem",
        "Morse Theory: Critical Points & Homology",
        "Stable Homotopy & Cohomology Operations",
        "Derived Categories & Homological Algebra",
    ]

    problems = problems_all[:num_problems]
    logger.info(f"Regenerating {len(problems)} master-level math problems")
    if call_log_path:
        logger.info(f"LLM call logging enabled: {call_log_path}")

    results = []
    for i, prob in enumerate(problems, 1):
        logger.info(f"[{i}/{len(problems)}] {prob}")
        res = prover.generate_proof(prob)
        results.append(res)
        time.sleep(1) # Rate limit

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / f"dspy_deepseek_{len(problems)}_problems_generation.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Generation complete. Results saved to {results_file}")
    return results_file

if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_regeneration(num_problems=num)
