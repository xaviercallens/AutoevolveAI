"""Contract tests for the verified episode pool: only verifier-labelled rows may enter training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anse.jepa.verified_pool import (
    EpisodeContractError,
    append_verified_episode,
    load_verified_pool,
    validate_episode,
)

DIM = 4


def _episode(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "task": "desi_dr2_bao:controls.py",
        "iteration": 0,
        "hidden_state": [0.1, -0.2, 0.3, 0.4],
        "energy": 0.0,
        "converged": True,
        "metadata": {
            "tests_total": 1,
            "tests_passed": 1,
            "verifier": "pytest",
            "evidence_path": "results/x.json",
            "embedding_model": "qwen3-embedding:0.6b",
        },
    }
    base.update(overrides)
    return base


def test_valid_episode_round_trips_through_append_and_load(tmp_path: Path) -> None:
    pool = tmp_path / "pool.jsonl"
    episode = _episode()

    append_verified_episode(pool, episode, DIM)
    accepted, refused = load_verified_pool(pool, DIM)

    assert accepted == [episode]
    assert refused == {"malformed_json": 0, "contract": 0}


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"energy": 0.5}, "energy must be exactly"),
        ({"energy": True}, "energy must be exactly"),
        ({"hidden_state": [0.1, 0.2, 0.3]}, "hidden_state must be a list"),
        ({"hidden_state": [0.1, float("nan"), 0.3, 0.4]}, "non-finite"),
        ({"task": "   "}, "task must be"),
        (
            {
                "metadata": {
                    "tests_total": 0,
                    "verifier": "p",
                    "evidence_path": "e",
                    "embedding_model": "m",
                }
            },
            "tests_total",
        ),
        (
            {
                "metadata": {
                    "tests_total": 1,
                    "verifier": "",
                    "evidence_path": "e",
                    "embedding_model": "m",
                }
            },
            "verifier",
        ),
        (
            {"metadata": {"tests_total": 1, "verifier": "p", "evidence_path": "e"}},
            "embedding_model",
        ),
    ],
)
def test_contract_refuses_unverified_or_malformed_rows(
    overrides: dict[str, Any], message: str
) -> None:
    with pytest.raises(EpisodeContractError, match=message):
        validate_episode(_episode(**overrides), DIM)


def test_append_never_writes_a_refused_row(tmp_path: Path) -> None:
    pool = tmp_path / "pool.jsonl"

    with pytest.raises(EpisodeContractError):
        append_verified_episode(pool, _episode(energy=0.25), DIM)

    assert not pool.exists()


def test_load_counts_malformed_and_contract_violations_separately(tmp_path: Path) -> None:
    pool = tmp_path / "pool.jsonl"
    good = _episode()
    bad_contract = _episode(energy=0.5)
    lines = [json.dumps(good), "{not json", json.dumps(bad_contract), ""]
    pool.write_text("\n".join(lines) + "\n", encoding="utf-8")

    accepted, refused = load_verified_pool(pool, DIM)

    assert accepted == [good]
    assert refused == {"malformed_json": 1, "contract": 1}


@given(
    energy=st.sampled_from([0.0, 1.0]),
    task=st.text(min_size=1, max_size=40).filter(lambda s: s.strip() != ""),
    values=st.lists(
        st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
        min_size=DIM,
        max_size=DIM,
    ),
)
def test_any_well_formed_binary_episode_is_accepted(
    energy: float, task: str, values: list[float]
) -> None:
    episode = _episode(energy=energy, task=task, hidden_state=values)

    validate_episode(episode, DIM)

    assert episode["energy"] in (0.0, 1.0)
