#!/usr/bin/env python3
"""
AutoevolveAI & SuperGravity Interactive Demonstration Web Server.
Exposes live execution, attestation auditing, JEPA latent simulation,
and autopoietic hot-swapping endpoints.
"""

from __future__ import annotations

import ast
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anse.symbolic.performance_evaluator import PerformanceEnergyEvaluator  # noqa: E402
from anse.symbolic.sandbox import SandboxExecutor  # noqa: E402
from execution_attestation import ImplementationAuditor, generate_attestation_proof  # noqa: E402

logger = logging.getLogger("anse.web")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AutoevolveAI / SuperGravity Interactive Demonstration",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = SandboxExecutor()
evaluator = PerformanceEnergyEvaluator()

STATIC_DIR = Path(__file__).parent


class CodeExecutionRequest(BaseModel):
    code: str
    timeout: float = 3.0
    expected_output: str | None = None


class CodeAuditRequest(BaseModel):
    code: str
    filename: str = "solution.py"


class JEPAPredictRequest(BaseModel):
    code: str
    latent_dim: int = 16
    gamma_margin: float = 1.0
    cov_weight: float = 0.01


class HotSwapRequest(BaseModel):
    parent_energy: float
    child_code: str


@app.get("/", response_class=HTMLResponse)
async def serve_index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)


@app.post("/api/execute")
async def execute_code(req: CodeExecutionRequest) -> dict[str, Any]:
    """Execute code in deterministic sandbox and compute physical energy E."""
    start_t = time.perf_counter()
    try:
        exec_res = executor.execute(req.code)
        eval_res = evaluator.evaluate(
            exec_res,
            expected_output=req.expected_output,
        )
        total_time_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "status": "success",
            "energy": round(eval_res.score, 4),
            "category": eval_res.category.value,
            "is_valid": eval_res.is_valid,
            "duration_ms": round(eval_res.duration_ms, 2),
            "peak_ram_mb": round(eval_res.peak_ram_mb, 2),
            "tier_used": exec_res.tier_used,
            "dangerous_imports": exec_res.dangerous_imports,
            "stdout": exec_res.stdout,
            "stderr": exec_res.stderr,
            "returncode": exec_res.returncode,
            "timed_out": exec_res.timed_out,
            "wall_clock_ms": round(total_time_ms, 2),
        }
    except Exception as e:
        logger.exception("Error executing code in sandbox")
        return {
            "status": "error",
            "energy": 1_000_000.0,
            "category": "crash",
            "is_valid": False,
            "error": str(e),
        }


@app.post("/api/audit")
async def audit_code(req: CodeAuditRequest) -> dict[str, Any]:
    """Run AST Anti-Stub & Anti-Simulation inspection."""
    try:
        tree = ast.parse(req.code, filename=req.filename)
        auditor = ImplementationAuditor(req.filename)
        auditor.visit(tree)
        violations = auditor.violations

        has_stubs = len(violations) > 0
        token = ""
        if not has_stubs:
            token = generate_attestation_proof("sandbox_interactive")

        return {
            "passed": not has_stubs,
            "violations": violations,
            "proof_token": token if not has_stubs else None,
            "zero_trust_status": "ATTESTED" if not has_stubs else "REJECTED",
        }
    except SyntaxError as e:
        return {
            "passed": False,
            "violations": [f"Syntax Error line {e.lineno}: {e.msg}"],
            "proof_token": None,
            "zero_trust_status": "SYNTAX_ERROR",
        }


@app.post("/api/jepa/predict")
async def predict_jepa(req: JEPAPredictRequest) -> dict[str, Any]:
    """Simulate Phase 2 JEPA latent space prediction & VICReg regularization."""
    import hashlib
    import math

    code_hash = hashlib.sha256(req.code.encode()).hexdigest()
    # Deterministic pseudo-embedding based on hash
    coords = []
    for i in range(req.latent_dim):
        sub = int(code_hash[i * 2 : (i + 1) * 2], 16) / 255.0
        coords.append(round(sub * 2.0 - 1.0, 4))

    # Variance across latent dims
    mean_val = sum(coords) / len(coords)
    var_val = sum((c - mean_val) ** 2 for c in coords) / len(coords)
    std_val = math.sqrt(var_val + 1e-6)

    # VICReg variance penalty: max(0, gamma - std)
    var_penalty = max(0.0, req.gamma_margin - std_val)

    # Covariance penalty simulation (decorrelation)
    cov_penalty = abs(coords[0] * coords[1] + coords[2] * coords[3]) * req.cov_weight

    # Predicted energy
    predicted_energy = round(abs(coords[0] * 50.0 + coords[1] * 20.0) + (1.0 if "pass" in req.code else 0.0), 3)

    return {
        "latent_vector": coords[:8],  # First 8 dimensions for display
        "2d_projection": {"x": round(coords[0] * 100, 2), "y": round(coords[1] * 100, 2)},
        "predicted_energy": predicted_energy,
        "vicreg": {
            "latent_std": round(std_val, 4),
            "variance_penalty": round(var_penalty, 4),
            "covariance_penalty": round(cov_penalty, 4),
            "total_vicreg_loss": round(var_penalty + cov_penalty, 4),
            "collapse_prevented": std_val >= (req.gamma_margin * 0.8),
        },
    }


@app.post("/api/autopoiesis/hotswap")
async def evaluate_hotswap(req: HotSwapRequest) -> dict[str, Any]:
    """Evaluate child mutant against parent process for autopoietic hot-swap."""
    exec_res = executor.execute(req.child_code)
    eval_res = evaluator.evaluate(exec_res)

    child_energy = eval_res.score
    delta_e = child_energy - req.parent_energy
    is_safe = delta_e < 0 and eval_res.is_valid

    return {
        "parent_energy": round(req.parent_energy, 4),
        "child_energy": round(child_energy, 4),
        "delta_energy": round(delta_e, 4),
        "thermodynamically_admissible": is_safe,
        "action": "HOT_SWAP_EXECUTED" if is_safe else "REJECTED_HIGH_ENERGY",
        "child_valid": eval_res.is_valid,
        "child_category": eval_res.category.value,
        "improvement_pct": round((-delta_e / max(req.parent_energy, 1e-4)) * 100.0, 2) if is_safe else 0.0,
    }


def main() -> None:
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "127.0.0.1")
    print("\n=======================================================")
    print("🚀 AutoevolveAI / SuperGravity Interactive Web Demo")
    print(f"🌐 Running at: http://{host}:{port}")
    print("=======================================================\n")
    uvicorn.run("web.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
