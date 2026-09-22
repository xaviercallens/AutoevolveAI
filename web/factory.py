"""
PR Factory API Router — Jules Mission Dispatch, CI Gatekeeper Status & PR Review Feed.

Provides endpoints for the PR Factory dashboard tab. Missions are stored locally
in an SQLite database; GitHub status polling uses the GitHub REST API via httpx.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger("anse.web.factory")

router = APIRouter(prefix="/api/factory", tags=["pr-factory"])

# ── Database ────────────────────────────────────────────────────────────────

DB_PATH = Path(os.getenv("FACTORY_DB_PATH", "results/factory/missions.db"))

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS missions (
    id          TEXT PRIMARY KEY,
    repo        TEXT NOT NULL,
    mission_type TEXT NOT NULL,
    target      TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    god_prompt  TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'queued',
    pr_url      TEXT DEFAULT NULL,
    ci_passed   INTEGER DEFAULT NULL,
    error       TEXT DEFAULT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


@contextmanager
def _db() -> Generator[sqlite3.Connection, None, None]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(_CREATE_TABLE)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Models ──────────────────────────────────────────────────────────────────


class MissionType(StrEnum):
    performance = "performance"
    qa_fuzzing = "qa_fuzzing"
    security = "security"
    lean_proof = "lean_proof"
    custom = "custom"


class MissionStatus(StrEnum):
    queued = "queued"
    dispatched = "dispatched"
    running = "running"
    pr_ready = "pr_ready"
    ci_passed = "ci_passed"
    ci_failed = "ci_failed"
    merged = "merged"
    error = "error"


# God Prompt templates — injected as suffix to every mission
GOD_PROMPT_RULES = (
    "CONTRAINTES STRICTES:\n"
    "1. ANTI-STUB: Interdiction absolue d'utiliser 'pass', 'TODO' ou des mocks non contractuels.\n"
    "2. LEAN: Chaque modification logique doit s'accompagner d'une mise à jour de la spécification .lean.\n"
    "3. PERFORMANCE: Refactorise pour atteindre une complexité spatiale/temporelle O(1) ou O(n log n).\n"
    "4. EXÉCUTION: Tu as accès au terminal. Tu DOIS lancer 'make verify-all'. "
    "Corrige tes erreurs tant que le make échoue. N'ouvre la PR que lorsque tout est au vert."
)

MISSION_TEMPLATES: dict[MissionType, str] = {
    MissionType.performance: (
        "Mission Perf: Optimise le composant {target}. "
        "Profiling: identifie les hot paths, élimine les allocations inutiles, "
        "et atteins une complexité O(1) ou O(n log n)."
    ),
    MissionType.qa_fuzzing: (
        "Mission QA: Développe la matrice de tests fuzzing pour {target}. "
        "Utilise Hypothesis pour les property-based tests. "
        "Couvre les edge cases: entrées vides, valeurs limites, types incorrects."
    ),
    MissionType.security: (
        "Mission Sécu: Patche les failles d'injection SQL potentielles sur {target}. "
        "Audite les entrées utilisateur, les requêtes dynamiques, et les chemins de fichiers."
    ),
    MissionType.lean_proof: (
        "Mission Lean: Ajoute la preuve formelle Lean 4 pour {target}. "
        "Le théorème doit compiler sans 'sorry'. Mets à jour formal/ANSE/."
    ),
    MissionType.custom: "{description}",
}


class DispatchRequest(BaseModel):
    repo: str = Field(default="xaviercallens/AutoevolveAI")
    mission_type: MissionType = MissionType.performance
    target: str = Field(default="anse/symbolic/sandbox.py", description="Component or module path")
    description: str = Field(default="", description="Free-form description (used for custom type)")
    custom_prompt: str = Field(default="", description="Override the template prompt entirely")


class MissionResponse(BaseModel):
    id: str
    repo: str
    mission_type: str
    target: str
    description: str
    status: str
    pr_url: str | None
    ci_passed: bool | None
    error: str | None
    created_at: str
    updated_at: str


class PillarStatus(BaseModel):
    name: str
    passed: bool | None  # None = not yet run
    details: str


class CIStatusResponse(BaseModel):
    pr_number: int | None
    pillars: list[PillarStatus]
    overall: str  # "passed" | "failed" | "pending" | "no_pr"


class ReviewVerdict(BaseModel):
    pr_number: int
    reviewer: str
    verdict: str  # "APPROVE" | "BLOCKING" | "COMMENT"
    reason: str
    timestamp: str


# ── Helpers ─────────────────────────────────────────────────────────────────


def _build_god_prompt(req: DispatchRequest) -> str:
    """Build the full mission prompt from template + God Prompt rules."""
    if req.custom_prompt:
        base = req.custom_prompt
    else:
        template = MISSION_TEMPLATES[req.mission_type]
        base = template.format(target=req.target, description=req.description)
    return f"{base}\n\n{GOD_PROMPT_RULES}"


def _row_to_mission(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    if d.get("ci_passed") is not None:
        d["ci_passed"] = bool(d["ci_passed"])
    return d


def _dispatch_jules(repo: str, session_prompt: str, mission_id: str) -> str:
    """
    Dispatch a Jules mission. In production, this calls `jules remote new`.
    For now, it logs the dispatch and returns a simulated status.

    When the Jules CLI is available, uncomment the subprocess call.
    """
    logger.info(
        "Dispatching Jules mission %s to %s: %s",
        mission_id,
        repo,
        session_prompt[:120],
    )

    # Uncomment when jules CLI is available:
    # import subprocess
    # result = subprocess.run(
    #     ["jules", "remote", "new", "--repo", repo, "--session", session_prompt],
    #     capture_output=True, text=True, check=False
    # )
    # if result.returncode != 0:
    #     raise RuntimeError(f"Jules dispatch failed: {result.stderr}")
    # return "dispatched"

    return "dispatched"


# ── GitHub Helpers ──────────────────────────────────────────────────────────

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


async def _github_get(url: str) -> Any:
    """Make an authenticated GET to the GitHub REST API."""
    headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        return None


# ── Endpoints ───────────────────────────────────────────────────────────────


@router.post("/dispatch", response_model=MissionResponse)
async def dispatch_mission(req: DispatchRequest) -> dict[str, Any]:
    """Dispatch a new Jules mission with God Prompt rules."""
    mission_id = str(uuid.uuid4())[:12]
    now = datetime.now(UTC).isoformat()
    prompt = _build_god_prompt(req)

    try:
        status = _dispatch_jules(req.repo, prompt, mission_id)
    except Exception:
        status = "error"
        logger.exception("Failed to dispatch mission %s", mission_id)

    with _db() as conn:
        conn.execute(
            """INSERT INTO missions
               (id, repo, mission_type, target, description, god_prompt,
                status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                mission_id,
                req.repo,
                req.mission_type.value,
                req.target,
                req.description,
                prompt,
                status,
                now,
                now,
            ),
        )

    with _db() as conn:
        row = conn.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
    return _row_to_mission(row)


@router.get("/missions")
async def list_missions(limit: int = 50) -> dict[str, Any]:
    """List active and recent missions."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    missions = [_row_to_mission(r) for r in rows]

    active = [m for m in missions if m["status"] in ("queued", "dispatched", "running")]
    completed = [m for m in missions if m["status"] not in ("queued", "dispatched", "running")]

    return {
        "total": len(missions),
        "active": active,
        "completed": completed,
    }


@router.get("/ci-status")
async def get_ci_status(pr_number: int | None = None) -> dict[str, Any]:
    """Get CI gatekeeper status for a PR or the latest open PR."""
    repo = os.getenv("FACTORY_REPO", "xaviercallens/AutoevolveAI")
    base_url = f"https://api.github.com/repos/{repo}"

    # Find the PR
    target_pr = pr_number
    if target_pr is None:
        prs = await _github_get(f"{base_url}/pulls?state=open&per_page=1&sort=created&direction=desc")
        if prs and len(prs) > 0:
            target_pr = prs[0]["number"]

    if target_pr is None:
        return CIStatusResponse(
            pr_number=None,
            pillars=[],
            overall="no_pr",
        ).model_dump()

    # Get check runs for the PR
    pillars = [
        PillarStatus(name="Lean Verification", passed=None, details="Awaiting check run"),
        PillarStatus(name="QA Tests (Hypothesis)", passed=None, details="Awaiting check run"),
        PillarStatus(name="Security (Semgrep)", passed=None, details="Awaiting check run"),
        PillarStatus(name="UI Regression (Playwright)", passed=None, details="Awaiting check run"),
    ]

    checks = await _github_get(
        f"{base_url}/commits/refs/pull/{target_pr}/head/check-runs"
    )
    if checks and "check_runs" in checks:
        pillar_map = {
            "test-lean": 0,
            "test-qa": 1,
            "test-sec": 2,
            "test-ui": 3,
            "Validation des Piliers Antigravity": None,  # maps all 4
            "SLM Critic Review": None,
        }
        for run in checks["check_runs"]:
            name = run.get("name", "")
            conclusion = run.get("conclusion")
            status_val = run.get("status")
            for key, idx in pillar_map.items():
                if key.lower() in name.lower() and idx is not None:
                    pillars[idx].passed = conclusion == "success"
                    pillars[idx].details = (
                        f"{status_val}: {conclusion or 'in_progress'}"
                    )

    all_passed = all(p.passed is True for p in pillars)
    any_failed = any(p.passed is False for p in pillars)
    overall = "passed" if all_passed else ("failed" if any_failed else "pending")

    return {
        "pr_number": target_pr,
        "pillars": [p.model_dump() for p in pillars],
        "overall": overall,
    }


@router.get("/reviews")
async def get_reviews(limit: int = 20) -> dict[str, Any]:
    """Get Jules code review verdicts from GitHub PRs."""
    repo = os.getenv("FACTORY_REPO", "xaviercallens/AutoevolveAI")
    base_url = f"https://api.github.com/repos/{repo}"

    reviews: list[dict[str, Any]] = []
    prs = await _github_get(f"{base_url}/pulls?state=all&per_page={limit}&sort=updated")
    if prs:
        for pr in prs[:5]:  # Limit API calls
            pr_reviews = await _github_get(
                f"{base_url}/pulls/{pr['number']}/reviews"
            )
            if pr_reviews:
                for rev in pr_reviews:
                    verdict = "APPROVE" if rev.get("state") == "APPROVED" else (
                        "BLOCKING" if rev.get("state") == "CHANGES_REQUESTED" else "COMMENT"
                    )
                    reviews.append({
                        "pr_number": pr["number"],
                        "reviewer": rev.get("user", {}).get("login", "unknown"),
                        "verdict": verdict,
                        "reason": (rev.get("body") or "")[:500],
                        "timestamp": rev.get("submitted_at", ""),
                    })

    return {"reviews": reviews[:limit]}


@router.get("/history")
async def get_history(page: int = 1, per_page: int = 25) -> dict[str, Any]:
    """Get paginated dispatch history."""
    offset = (page - 1) * per_page
    with _db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM missions").fetchone()[0]
        rows = conn.execute(
            "SELECT * FROM missions ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "missions": [_row_to_mission(r) for r in rows],
    }
