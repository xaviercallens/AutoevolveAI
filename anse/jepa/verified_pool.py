"""Append-only pool of verifier-labelled episodes that feeds the dream-phase predictor.

Every row is a verdict from a real check: a Lean gate, a pytest run, a pipeline assertion, or a
sandbox execution. Conversations never enter this pool; they stay retrieval-only. A row is
refused at write time unless it carries the fields the trainer needs to trust its label:

- ``task``: a non-empty string used to group folds, so held-out tasks never leak into training.
- ``hidden_state``: finite floats whose length equals the embedder dimension recorded on the row.
- ``energy``: exactly 0.0 (the check held) or 1.0 (the check failed). Partial scores are refused
  because a binary verdict is what the trainer's scoring rule is defined on.
- ``metadata``: ``tests_total >= 1``, a non-empty ``verifier``, a non-empty ``evidence_path``,
  and the ``embedding_model`` that produced ``hidden_state``.

Rows are validated again on read, so a hand-edited line cannot slip into training.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

REQUIRED_META_STR: tuple[str, ...] = ("verifier", "evidence_path", "embedding_model")


class EpisodeContractError(ValueError):
    """Raised when a candidate episode does not satisfy the verified-pool contract."""


def validate_episode(episode: dict[str, Any], embedding_dim: int) -> None:
    """Raise ``EpisodeContractError`` unless ``episode`` is a valid verified row."""
    task = episode.get("task")
    if not isinstance(task, str) or not task.strip():
        raise EpisodeContractError("task must be a non-empty string")

    hidden = episode.get("hidden_state")
    if not isinstance(hidden, list) or len(hidden) != embedding_dim:
        raise EpisodeContractError(f"hidden_state must be a list of length {embedding_dim}")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in hidden):
        raise EpisodeContractError("hidden_state contains a non-finite value")

    energy = episode.get("energy")
    if energy not in (0.0, 1.0) or isinstance(energy, bool):
        raise EpisodeContractError("energy must be exactly 0.0 (held) or 1.0 (failed)")

    meta = episode.get("metadata")
    if not isinstance(meta, dict):
        raise EpisodeContractError("metadata must be an object")
    tests_total = meta.get("tests_total")
    if not isinstance(tests_total, int) or isinstance(tests_total, bool) or tests_total < 1:
        raise EpisodeContractError("metadata.tests_total must be an integer >= 1")
    for key in REQUIRED_META_STR:
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            raise EpisodeContractError(f"metadata.{key} must be a non-empty string")


def append_verified_episode(pool_path: Path, episode: dict[str, Any], embedding_dim: int) -> None:
    """Validate ``episode`` and append it as one JSON line. Invalid rows are never written."""
    validate_episode(episode, embedding_dim)
    pool_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pool_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(episode, sort_keys=True) + "\n")


def load_verified_pool(
    pool_path: Path, embedding_dim: int
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Read the pool, keeping only rows that pass validation.

    Returns the accepted rows and a count of refused rows by reason, so the caller can report
    how much of the pool was usable instead of silently dropping data.
    """
    accepted: list[dict[str, Any]] = []
    refused: dict[str, int] = {"malformed_json": 0, "contract": 0}
    if not pool_path.exists():
        return accepted, refused
    with open(pool_path, encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                episode = json.loads(line)
            except json.JSONDecodeError:
                refused["malformed_json"] += 1
                continue
            try:
                validate_episode(episode, embedding_dim)
            except EpisodeContractError:
                refused["contract"] += 1
                continue
            accepted.append(episode)
    return accepted, refused
