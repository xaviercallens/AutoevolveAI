"""
anse.harness — First-Class Experiment & Hardened Autoresearch Plugin API.

Integrates the methodological feedback from OptimalEnergyAI (v0.2.0 / v0.3.0,
docs/harness.md, docs/results/h0.md, docs/results/next_actions.md, and
docs/research/autoresearch_hypotheses.md):

1. Preregistration & Disclosed Revisions (`preregister`):
   Freezes `experiments/<poc>/preregistration.json` from `prereg.in.json`,
   hashing all runner scripts and `decide.py`. Refuses to overwrite after runs
   exist unless `revise="<reason>"` is supplied, which appends `runs_seen` to
   `revision_history` (disclosed, never hidden).
2. Immutable Run Records (`Run`):
   Refuses to start without a valid preregistration, records positive and
   negative controls (`run.control(name, ok, **info)`), tracks wall-clock budget,
   and writes immutable `results/<poc>/runs/<run_id>.json`.
3. Append-Only Ledger Gate (`build_ledger`, `crash_reasons`):
   Verifies runner SHA-256 hashes, preregistration SHA-256 hashes, non-empty
   passing controls, and budget compliance. Evaluates `decide(prereg, runs)`,
   appends to `results/<poc>/results.tsv` (`keep` | `discard` | `crash`), and
   returns exit code 1 on any `FAIL` or `crash`. Re-running with no new runs
   re-reports the last batch verdict so failures can never be hidden.
4. CI-Tolerant Theoretical Bound Guard (`ci_bound_guard`, Issue #32):
   Applies theoretical ceiling artefact guards (e.g. Fejes Tóth 3.775% hexagonal
   gain bound) to the confidence interval lower bound (`ci_low <= bound`) rather
   than a zero-tolerance point estimate, avoiding the 50% coin-flip rejection on
   an ideal source while catching genuine artefacts (`ci_low > bound`).
5. Two-Sided Oracle Cross-Check with Membership (`two_sided_oracle_check`, H0 Finding 1):
   Checks `|d_candidate - d_oracle| <= tol` in both directions AND verifies target
   set / lattice membership, preventing off-lattice points that sit closer to the
   query than any true lattice point from passing unnoticed.
6. Hardened Autoresearch Loop (`HardenedAutoresearchLoop`):
   Enforces pre-batch positive/negative controls and a 3-stage sequential keep rule:
   search split improvement -> held-out split improvement -> median of >= 3 seeds/chunks
   improvement, with preregistered batch/kill criteria.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import statistics
import subprocess
import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

LEDGER_COLUMNS = [
    "utc",
    "batch",
    "hypothesis",
    "status",
    "verdict",
    "value",
    "rule",
    "n_runs",
    "run_ids",
    "git_sha",
    "detail",
]


def sha256_file(path: Path | str) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_state(root: Path | str) -> dict[str, Any]:
    """Capture current git commit SHA and working tree dirty flag."""
    root_path = Path(root)

    def _git(*args: str) -> str:
        res = subprocess.run(["git", *args], cwd=root_path, capture_output=True, text=True)
        return res.stdout.strip() if res.returncode == 0 else ""

    sha = _git("rev-parse", "HEAD") or "nogit"
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    return {"git_sha": sha, "git_dirty": dirty}


def exp_dir(root: Path | str, poc: str) -> Path:
    return Path(root) / "experiments" / poc


def res_dir(root: Path | str, poc: str) -> Path:
    return Path(root) / "results" / poc


def prereg_path(root: Path | str, poc: str) -> Path:
    return exp_dir(root, poc) / "preregistration.json"


def load_prereg(root: Path | str, poc: str) -> dict[str, Any]:
    p = prereg_path(root, poc)
    if not p.is_file():
        raise FileNotFoundError(f"{p} missing: preregister before running (preregister({poc!r}))")
    return json.loads(p.read_text(encoding="utf-8"))


def preregister(poc: str, root: Path | str, revise: str | None = None) -> Path:
    """Freeze `experiments/<poc>/preregistration.json` from `prereg.in.json`.

    Refuses to overwrite an existing preregistration or preregister after runs exist
    unless `revise` provides an explicit reason, which is appended to `revision_history`
    alongside `runs_seen`.
    """
    root_path = Path(root).resolve()
    src = exp_dir(root_path, poc) / "prereg.in.json"
    if not src.is_file():
        raise FileNotFoundError(f"preregistration input {src} not found")
    spec = json.loads(src.read_text(encoding="utf-8"))
    out = prereg_path(root_path, poc)
    runs = sorted((res_dir(root_path, poc) / "runs").glob("*.json"))
    history: list[dict[str, Any]] = []

    if out.exists():
        if not revise:
            raise RuntimeError(f"{out} exists; pass revise='<reason>' to amend it")
        old = json.loads(out.read_text(encoding="utf-8"))
        history = list(old.get("revision_history", [])) + [
            {
                "utc": utc_now(),
                "reason": revise,
                "previous_sha256": sha256_file(out),
                "runs_seen": len(runs),
            }
        ]
    elif runs and not revise:
        raise RuntimeError(f"{len(runs)} runs already exist for {poc}: preregistration must precede runs")

    runners: dict[str, str] = {}
    for rel in spec.get("runners", {}):
        p = root_path / rel
        if not p.is_file():
            raise FileNotFoundError(f"runner {rel} not found under {root_path}")
        runners[rel] = sha256_file(p)
    if not any(r.endswith("decide.py") for r in runners):
        raise ValueError("runners must include the decision rule (experiments/<poc>/decide.py)")

    rec = {
        **spec,
        "problem": poc,
        "timestamp_utc": utc_now(),
        **git_state(root_path),
        "revision_history": history,
        "runners": runners,
        "stage": (
            "preregistration (no result of this problem has been produced or viewed)"
            if not runs
            else f"revision after {len(runs)} runs (disclosed in revision_history)"
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


class Run:
    """Context for one experiment runner invocation.

    Refuses to start without a frozen `preregistration.json` and writes an immutable
    run record carrying runner and preregistration SHA-256 digests plus controls.
    """

    def __init__(
        self,
        poc: str,
        runner: Path | str,
        seed: int,
        budget_s: float,
        config: dict[str, Any],
        root: Path | str,
        device: str = "cpu",
    ) -> None:
        self.root = Path(root).resolve()
        self.poc = poc
        self.runner = Path(runner).resolve()
        load_prereg(self.root, poc)
        self.seed = seed
        self.budget_s = budget_s
        self.config = config
        self.device = device
        self.t0 = time.perf_counter()
        self.controls: dict[str, dict[str, Any]] = {}
        self.metrics: dict[str, Any] = {}

    @property
    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def control(self, name: str, ok: bool, **info: Any) -> bool:
        """Record a positive or negative control outcome."""
        self.controls[name] = {"ok": bool(ok), **info}
        return bool(ok)

    def write(self) -> Path:
        out = res_dir(self.root, self.poc) / "runs"
        out.mkdir(parents=True, exist_ok=True)
        run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-s{self.seed}-{uuid.uuid4().hex[:6]}"
        wall_s = round(self.elapsed, 4)
        rec = {
            "run_id": run_id,
            "poc": self.poc,
            "utc": utc_now(),
            **git_state(self.root),
            "runner": str(self.runner.relative_to(self.root)),
            "runner_sha256": sha256_file(self.runner),
            "prereg_sha256": sha256_file(prereg_path(self.root, self.poc)),
            "seed": self.seed,
            "device": self.device,
            "host": platform.node(),
            "cpus": os.cpu_count(),
            "budget_s": self.budget_s,
            "wall_s": wall_s,
            "budget_exceeded": wall_s > self.budget_s,
            "config": self.config,
            "controls": self.controls,
            "metrics": self.metrics,
        }
        path = out / f"{run_id}.json"
        path.write_text(json.dumps(rec, indent=2, default=float) + "\n", encoding="utf-8")
        return path


def crash_reasons(root: Path | str, poc: str, prereg: dict[str, Any], runs: Sequence[dict[str, Any]]) -> list[str]:
    """Identify any integrity, control, or budget violations that invalidate a batch as `crash`."""
    root_path = Path(root).resolve()
    why: list[str] = []
    for rel, expected_hash in prereg.get("runners", {}).items():
        p = root_path / rel
        if not p.is_file() or sha256_file(p) != expected_hash:
            why.append(f"runner {rel} changed after preregistration")
    psha = sha256_file(prereg_path(root_path, poc))
    for r in runs:
        rid = r.get("run_id", "unknown")
        if r.get("prereg_sha256") != psha:
            why.append(f"{rid}: ran under a different preregistration")
        if prereg.get("runners", {}).get(r.get("runner")) != r.get("runner_sha256"):
            why.append(f"{rid}: runner hash differs from the preregistered one")
        controls = r.get("controls", {})
        if not controls:
            why.append(f"{rid}: no controls recorded")
        bad = [k for k, c in controls.items() if not c.get("ok")]
        if bad:
            why.append(f"{rid}: control(s) failed: {', '.join(bad)}")
        if r.get("budget_exceeded"):
            why.append(f"{rid}: budget exceeded ({r.get('wall_s')} s > {r.get('budget_s')} s)")
    return why


def _load_decide_fn(root: Path, poc: str) -> Callable[[dict[str, Any], list[dict[str, Any]]], list[dict[str, Any]]]:
    path = exp_dir(root, poc) / "decide.py"
    spec = importlib.util.spec_from_file_location(f"_decide_{poc}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load decision rule from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.decide  # type: ignore[no-any-return]


def _read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build_ledger(poc: str, root: Path | str) -> int:
    """Evaluate new runs against the preregistered decision rule and append to `results.tsv`.

    Returns 0 iff all evaluated hypotheses in the batch have status `keep`, else 1.
    """
    root_path = Path(root).resolve()
    prereg = load_prereg(root_path, poc)
    tsv = res_dir(root_path, poc) / "results.tsv"
    rows = _read_tsv(tsv)
    seen = {rid for r in rows for rid in r["run_ids"].split(",") if rid}
    runs_dir = res_dir(root_path, poc) / "runs"
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(runs_dir.glob("*.json"))] if runs_dir.is_dir() else []
    new = [r for r in runs if r["run_id"] not in seen]

    if not new:
        if not rows:
            return 1
        last_batch = rows[-1]["batch"]
        last = [r for r in rows if r["batch"] == last_batch]
        bad = [r for r in last if r["status"] != "keep"]
        return 1 if bad else 0

    batch = f"b{len({r['batch'] for r in rows}) + 1:03d}"
    ids = ",".join(r["run_id"] for r in new)
    base = {
        "utc": utc_now(),
        "batch": batch,
        "n_runs": str(len(new)),
        "run_ids": ids,
        "git_sha": git_state(root_path)["git_sha"][:12],
    }
    why = crash_reasons(root_path, poc, prereg, new)
    out: list[dict[str, str]] = []
    if why:
        for h in prereg.get("hypotheses", [{"id": "ALL"}]):
            out.append(
                {
                    **base,
                    "hypothesis": str(h["id"]),
                    "status": "crash",
                    "verdict": "-",
                    "value": "",
                    "rule": "",
                    "detail": "; ".join(why)[:2000],
                }
            )
    else:
        decide_fn = _load_decide_fn(root_path, poc)
        for d in decide_fn(prereg, new):
            v = d["verdict"]
            if v not in ("PASS", "FAIL", "REPORT"):
                raise ValueError(f"decide() returned invalid verdict {v!r}")
            out.append(
                {
                    **base,
                    "hypothesis": str(d["hypothesis"]),
                    "status": "discard" if v == "FAIL" else "keep",
                    "verdict": v,
                    "value": str(d.get("value", "")),
                    "rule": str(d.get("rule", "")),
                    "detail": str(d.get("detail", "")),
                }
            )

    tsv.parent.mkdir(parents=True, exist_ok=True)
    fresh = not tsv.is_file()
    with tsv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS, delimiter="\t", lineterminator="\n")
        if fresh:
            w.writeheader()
        for r in out:
            w.writerow({k: str(r.get(k, "")).replace("\t", " ").replace("\n", " ") for k in LEDGER_COLUMNS})

    return 1 if any(r["status"] != "keep" for r in out) else 0


def ci_student_t(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float, float, float]:
    """Compute (mean, half_width, ci_low, ci_high) using a two-sided Student-t interval."""
    xs = [float(x) for x in values]
    n = len(xs)
    if n == 0:
        raise ValueError("ci_student_t requires at least 1 observation")
    mean = sum(xs) / n
    if n < 2:
        return mean, float("inf"), float("-inf"), float("inf")
    sd = math.sqrt(sum((x - mean) ** 2 for x in xs) / (n - 1))
    alpha = 1.0 - confidence
    hw = float(stats.t.ppf(1.0 - alpha / 2.0, n - 1)) * sd / math.sqrt(n)
    return mean, hw, mean - hw, mean + hw


def ci_bound_guard(
    gains: Sequence[float],
    theoretical_ceiling: float,
    *,
    min_seeds: int = 5,
    rate_gap: float = 0.0,
    rate_tol: float = 0.01,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """CI-tolerant theoretical bound guard (OptimalEnergyAI Issue #32 / PoC3Pass fix).

    On an ideal source where the true gain equals `theoretical_ceiling` (e.g. Fejes Tóth
    1 - G(A2)/G(Z2) = 3.775%), a raw `mean <= theoretical_ceiling` guard is a 50/50 coin flip.
    Applying the artefact guard to `ci_low <= theoretical_ceiling` while requiring `ci_low > 0`
    for positive gain ensures:
      1. Genuine improvements with CI excluding 0 pass.
      2. Ideal-source runs at the theoretical limit pass reliably.
      3. Rate-mismatched or buggy runs whose entire CI sits above the theoretical ceiling
         (`ci_low > theoretical_ceiling`) are caught as artefacts and rejected.
    """
    n = len(gains)
    mean, hw, ci_low, ci_high = ci_student_t(gains, confidence=confidence)
    seeds_ok = n >= min_seeds
    rate_ok = rate_gap <= rate_tol
    positive_gain_ok = ci_low > 0.0
    artefact_guard_ok = ci_low <= theoretical_ceiling
    passed = seeds_ok and rate_ok and positive_gain_ok and artefact_guard_ok
    return {
        "passed": passed,
        "n_seeds": n,
        "mean_gain": mean,
        "half_width": hw,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "theoretical_ceiling": theoretical_ceiling,
        "rate_gap": rate_gap,
        "checks": {
            "seeds_ok": seeds_ok,
            "rate_ok": rate_ok,
            "positive_gain_ok": positive_gain_ok,
            "artefact_guard_ok": artefact_guard_ok,
        },
    }


def two_sided_oracle_check(
    candidate_points: np.ndarray,
    query_points: np.ndarray,
    oracle_sq_dists: np.ndarray,
    is_valid_member_fn: Callable[[np.ndarray], np.ndarray],
    tol: float = 1e-9,
) -> dict[str, Any]:
    """Two-sided oracle distance & lattice-membership cross-check (OptimalEnergyAI H0 Finding 1).

    A one-sided check (`d_cand <= d_oracle + tol`) fails to detect a buggy decoder that returns
    a non-lattice point *closer* to the query than any true lattice point. This check verifies:
      1. Two-sided squared-distance agreement: `|d_cand - d_oracle| <= tol`.
      2. Explicit lattice/set membership: `is_valid_member_fn(candidate_points)` is True for every row.
    """
    cand = np.atleast_2d(np.asarray(candidate_points, dtype=float))
    queries = np.atleast_2d(np.asarray(query_points, dtype=float))
    oracle_d = np.asarray(oracle_sq_dists, dtype=float)

    cand_d = np.einsum("ij,ij->i", queries - cand, queries - cand)
    signed_diff = cand_d - oracle_d
    abs_err = np.abs(signed_diff)

    dist_mismatches = int((abs_err > tol).sum())
    closer_than_oracle = int((signed_diff < -tol).sum())
    farther_than_oracle = int((signed_diff > tol).sum())

    member_mask = np.asarray(is_valid_member_fn(cand), dtype=bool)
    non_member_count = int((~member_mask).sum())
    total_mismatches = int(((abs_err > tol) | (~member_mask)).sum())

    return {
        "queries": int(len(queries)),
        "mismatches": total_mismatches,
        "distance_mismatches": dist_mismatches,
        "closer_than_oracle_violations": closer_than_oracle,
        "farther_than_oracle_violations": farther_than_oracle,
        "non_member_violations": non_member_count,
        "max_abs_sq_dist_error": float(abs_err.max()) if len(abs_err) else 0.0,
        "passed": total_mismatches == 0,
    }


@dataclass
class AutoresearchStageRecord:
    candidate_id: str
    stage: str
    metric: float
    status: str
    detail: str = ""


@dataclass
class HardenedAutoresearchLoop:
    """Hardened Autoresearch Loop (OptimalEnergyAI `docs/research/autoresearch_hypotheses.md` §1).

    Fixes the four 2026 autoresearch failure modes (metric gaming, seed-dependent dead ends,
    replay overfitting, missing controls) via:
      - Pre-batch positive and negative controls (any failure -> `crash`, halts batch).
      - Stage 1: search split improves over `best_search_metric`.
      - Stage 2: held-out split improves over `best_heldout_metric`.
      - Stage 3: median across >= 3 fresh replicates/seeds improves over `best_replicate_median`.
      - Preregistered batch cap and kill criterion.
    """

    best_search_metric: float
    best_heldout_metric: float
    best_replicate_median: float
    lower_is_better: bool = True
    batch_cap: int = 10
    min_replicates: int = 3
    history: list[AutoresearchStageRecord] = field(default_factory=list)
    kept_candidates: list[str] = field(default_factory=list)
    crashed: bool = False

    def _improves(self, candidate_val: float, current_best: float) -> bool:
        if not math.isfinite(candidate_val):
            return False
        return candidate_val < current_best if self.lower_is_better else candidate_val > current_best

    def evaluate_candidate(
        self,
        candidate_id: str,
        *,
        positive_control_ok: bool,
        negative_control_ok: bool,
        search_fn: Callable[[], float],
        heldout_fn: Callable[[], float],
        replicates_fn: Callable[[], Sequence[float]],
        invariant_ok_fn: Callable[[], tuple[bool, str]] | None = None,
    ) -> dict[str, Any]:
        """Run a candidate through the 3-stage hardened autoresearch funnel."""
        if len(self.kept_candidates) + sum(1 for r in self.history if r.stage == "search") >= self.batch_cap:
            return {"candidate_id": candidate_id, "status": "stopped_batch_cap", "kept": False}

        if not positive_control_ok or not negative_control_ok:
            self.crashed = True
            rec = AutoresearchStageRecord(
                candidate_id=candidate_id,
                stage="controls",
                metric=float("nan"),
                status="crash",
                detail=f"positive={positive_control_ok}, negative={negative_control_ok}",
            )
            self.history.append(rec)
            return {"candidate_id": candidate_id, "status": "crash", "kept": False, "reason": rec.detail}

        if invariant_ok_fn is not None:
            inv_ok, inv_detail = invariant_ok_fn()
            if not inv_ok:
                self.crashed = True
                rec = AutoresearchStageRecord(
                    candidate_id=candidate_id,
                    stage="invariant",
                    metric=float("nan"),
                    status="crash",
                    detail=inv_detail,
                )
                self.history.append(rec)
                return {"candidate_id": candidate_id, "status": "crash", "kept": False, "reason": inv_detail}

        # Stage 1: Search split
        s_val = float(search_fn())
        if not self._improves(s_val, self.best_search_metric):
            self.history.append(
                AutoresearchStageRecord(candidate_id, "search", s_val, "discard", "no search improvement")
            )
            return {"candidate_id": candidate_id, "status": "discard", "stage": "search", "search_metric": s_val, "kept": False}

        # Stage 2: Held-out split
        h_val = float(heldout_fn())
        if not self._improves(h_val, self.best_heldout_metric):
            self.history.append(
                AutoresearchStageRecord(
                    candidate_id, "heldout", h_val, "discard", "search improved but held-out did not"
                )
            )
            return {
                "candidate_id": candidate_id,
                "status": "discard",
                "stage": "heldout",
                "search_metric": s_val,
                "heldout_metric": h_val,
                "kept": False,
            }

        # Stage 3: Multi-seed / multi-chunk replicates
        reps = [float(x) for x in replicates_fn()]
        if len(reps) < self.min_replicates:
            raise ValueError(f"Expected >= {self.min_replicates} replicates, got {len(reps)}")
        rep_med = float(statistics.median(reps))
        if not self._improves(rep_med, self.best_replicate_median):
            self.history.append(
                AutoresearchStageRecord(
                    candidate_id, "replicates", rep_med, "discard", "held-out improved but replicate median did not"
                )
            )
            return {
                "candidate_id": candidate_id,
                "status": "discard",
                "stage": "replicates",
                "search_metric": s_val,
                "heldout_metric": h_val,
                "replicate_median": rep_med,
                "kept": False,
            }

        # All 3 stages improved -> KEEP
        self.best_search_metric = s_val
        self.best_heldout_metric = h_val
        self.best_replicate_median = rep_med
        self.kept_candidates.append(candidate_id)
        self.history.append(
            AutoresearchStageRecord(candidate_id, "replicates", rep_med, "keep", "passed search + heldout + replicates")
        )
        return {
            "candidate_id": candidate_id,
            "status": "keep",
            "stage": "replicates",
            "search_metric": s_val,
            "heldout_metric": h_val,
            "replicate_median": rep_med,
            "kept": True,
        }
