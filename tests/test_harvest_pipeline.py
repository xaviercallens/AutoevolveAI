"""
Unit and Integration Tests for Continuous Data Harvester and Local Training Pipeline.
Verifies extraction of SFT, DPO, and GRPO datasets from Redis, as well as local LoRA / GRPO trainers.  # noqa: E501
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from harvest_training_pipeline import (
    _build_dpo_and_grpo_pairs,
    _classify_subtask_verdicts,
    _harvest_sft_from_passed,
    harvest_datasets,
    parse_trace_message,
)
from train_grpo import (
    check_cyclomatic_complexity_exceeded,
    check_fake_data_leakage,
    check_has_stubs,
    compute_code_hygiene_reward,
    compute_group_advantages,
    compute_grpo_loss_sample,
    evaluate_candidate_reward,
    execute_grpo_run,
)
from train_lora_local import (
    build_training_args,
    execute_training_run,
    get_lora_config,
    prepare_dpo_pairs,
    prepare_sft_prompts,
)


def _make_gemini_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    """Helper creating mock Gemini request and response payloads."""
    req = {
        "system_instruction": {"parts": [{"text": "You are a code optimizer."}]},
        "contents": [{"role": "user", "parts": [{"text": "Optimize matrix_multiply."}]}],
    }
    resp = {
        "candidates": [
            {"content": {"parts": [{"text": "def matrix_multiply(a, b):\n    return [[1]]"}]}}
        ]
    }
    return req, resp


def test_parse_trace_message() -> None:
    """Validate parsing of Gemini payloads into conversational turns and completion."""
    req, resp = _make_gemini_payloads()
    messages, completion = parse_trace_message(req, resp)

    assert messages is not None
    assert completion is not None
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "def matrix_multiply" in completion


def test_classify_subtask_verdicts() -> None:
    """Validate classification of trace IDs into PASSED and FAILED buckets."""
    mock_redis = MagicMock()
    mock_redis.hgetall.side_effect = [
        {"verdict": "FAILED", "reasons": '["Anti-stub gate failed"]'},
        {"verdict": "PASSED", "reasons": "[]"},
    ]

    passed, failed = _classify_subtask_verdicts(["tr-1", "tr-2"], mock_redis)
    assert len(failed) == 1
    assert failed[0][0] == "tr-1"
    assert len(passed) == 1
    assert passed[0][0] == "tr-2"


def test_harvest_sft_from_passed() -> None:
    """Validate extraction of verified passing traces into SFT format."""
    mock_redis = MagicMock()
    req, resp = _make_gemini_payloads()
    mock_record = {
        "request_json": req,
        "response_json": resp,
        "model_used": "gemini-3.8-flash",
        "phase": "EXECUTION",
    }
    mock_redis.get.return_value = json.dumps(mock_record)

    passed_traces = [("tr-pass", {"verdict": "PASSED"})]
    sft = _harvest_sft_from_passed(passed_traces, mock_redis)

    assert len(sft) == 1
    assert len(sft[0]["messages"]) == 3
    assert sft[0]["messages"][-1]["role"] == "assistant"
    assert sft[0]["metadata"]["trace_id"] == "tr-pass"


def test_build_dpo_and_grpo_pairs() -> None:
    """Validate generation of DPO triplets and GRPO candidate reward groups."""
    mock_redis = MagicMock()
    req, resp_pass = _make_gemini_payloads()
    _, resp_fail = _make_gemini_payloads()
    resp_fail["candidates"][0]["content"]["parts"][0]["text"] = (
        "def matrix_multiply(a, b):\n    pass"  # noqa: E501
    )

    record_pass = {"request_json": req, "response_json": resp_pass}
    record_fail = {"request_json": req, "response_json": resp_fail}

    mock_redis.get.side_effect = [json.dumps(record_pass), json.dumps(record_fail)]

    passed = [("tr-pass", {"verdict": "PASSED"})]
    failed = [("tr-fail", {"verdict": "FAILED", "reasons": '["Stub"]'})]

    dpo, grpo = _build_dpo_and_grpo_pairs(passed, failed, mock_redis)

    assert len(dpo) == 1
    assert "return [[1]]" in dpo[0]["chosen"]
    assert "pass" in dpo[0]["rejected"]

    assert len(grpo) == 1
    candidates = grpo[0]["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["reward"] == 1.0
    assert candidates[1]["reward"] == -1.0


def test_harvest_datasets_file_export(tmp_path: Path) -> None:
    """Validate complete harvesting pipeline writing JSONL files."""
    sft_file = tmp_path / "test_sft.jsonl"
    dpo_file = tmp_path / "test_dpo.jsonl"
    grpo_file = tmp_path / "test_grpo.jsonl"

    mock_redis = MagicMock()
    mock_redis.keys.return_value = [b"antigravity:subtask:SUB-01:traces"]
    mock_redis.lrange.return_value = [b"tr-fail", b"tr-pass"]

    # hgetall for tr-fail then tr-pass
    mock_redis.hgetall.side_effect = [
        {b"verdict": b"FAILED", b"reasons": b'["Contains pass"]'},
        {b"verdict": b"PASSED", b"reasons": b"[]"},
    ]

    req, resp_pass = _make_gemini_payloads()
    _, resp_fail = _make_gemini_payloads()
    resp_fail["candidates"][0]["content"]["parts"][0]["text"] = "pass"

    # get for sft passed trace, then dpo pass trace, then dpo fail trace
    mock_redis.get.side_effect = [
        json.dumps({"request_json": req, "response_json": resp_pass, "phase": "EXECUTION"}),
        json.dumps({"request_json": req, "response_json": resp_pass}),
        json.dumps({"request_json": req, "response_json": resp_fail}),
    ]

    sft, dpo, grpo = harvest_datasets(
        sft_out=sft_file,
        dpo_out=dpo_file,
        grpo_out=grpo_file,
        redis_client=mock_redis,
    )

    assert len(sft) == 1
    assert len(dpo) == 1
    assert len(grpo) == 1
    assert sft_file.exists()
    assert dpo_file.exists()
    assert grpo_file.exists()


def test_train_lora_local_config(tmp_path: Path) -> None:
    lora_cfg = get_lora_config(r=16, lora_alpha=32)
    assert lora_cfg is not None

    args = build_training_args(output_dir=str(tmp_path))
    assert args["fp16"] is True
    assert args["per_device_train_batch_size"] == 1
    assert args["gradient_accumulation_steps"] == 8


def test_train_lora_local_prompts() -> None:
    sample_sft = {
        "messages": [
            {"role": "user", "content": "Write quicksort"},
            {"role": "assistant", "content": "def quicksort(a): return sorted(a)"},
        ]
    }
    prompts = prepare_sft_prompts([sample_sft])
    assert len(prompts) == 1
    assert "<|im_start|>user" in prompts[0]

    sample_dpo = {
        "prompt": "Write quicksort",
        "chosen": "def quicksort(a): return sorted(a)",
        "rejected": "def quicksort(a): pass",
    }
    pairs = prepare_dpo_pairs([sample_dpo])
    assert len(pairs) == 1
    assert pairs[0]["chosen"] == sample_dpo["chosen"]


def test_train_lora_local_execution(tmp_path: Path) -> None:
    test_sft_file = tmp_path / "sft.jsonl"
    sample_sft = {
        "messages": [
            {"role": "user", "content": "Write quicksort"},
            {"role": "assistant", "content": "def quicksort(a): return sorted(a)"},
        ]
    }
    test_sft_file.write_text(json.dumps(sample_sft) + "\n", encoding="utf-8")

    summary = execute_training_run(
        mode="sft",
        dataset_path=test_sft_file,
        output_dir=str(tmp_path),
        dry_run=True,
    )
    assert summary["status"] == "COMPLETED_DRY_RUN"
    assert summary["sample_count"] == 1


def test_train_grpo_anti_stub() -> None:
    """Validate GRPO anti-stub checks, fake data, and complexity."""
    assert check_has_stubs("def foo():\n    pass") is True
    assert check_has_stubs("def foo():\n    return 1") is False

    assert check_fake_data_leakage("mock_data = 123") is True
    assert check_fake_data_leakage("real_data = 123") is False

    assert check_cyclomatic_complexity_exceeded("def simple():\n    return 1") is False


def test_train_grpo_rewards() -> None:
    # Negative reward on stubs
    r_stub = compute_code_hygiene_reward("def foo():\n    pass")
    assert r_stub < 0.0

    # Combined candidate evaluation
    cand_pass = {"completion": "def foo():\n    return 42", "verdict": "PASSED"}
    cand_fail = {"completion": "def foo():\n    pass", "verdict": "FAILED"}
    rew_pass = evaluate_candidate_reward(cand_pass)
    rew_fail = evaluate_candidate_reward(cand_fail)
    assert rew_pass > rew_fail

    # Advantage normalization
    advantages = compute_group_advantages([rew_pass, rew_fail])
    assert len(advantages) == 2
    assert advantages[0] > 0.0  # Pass candidate has positive advantage
    assert advantages[1] < 0.0  # Fail candidate has negative advantage

    # Loss calculation
    loss = compute_grpo_loss_sample(logp_policy=-0.5, logp_ref=-0.6, advantage=1.0)
    assert isinstance(loss, float)


def test_train_grpo_execution(tmp_path: Path) -> None:
    # Dry-run execution
    grpo_file = tmp_path / "grpo.jsonl"
    cand_pass = {"completion": "def foo():\n    return 42", "verdict": "PASSED"}
    cand_fail = {"completion": "def foo():\n    pass", "verdict": "FAILED"}
    sample_group = {
        "prompt": [{"role": "user", "content": "Write foo"}],
        "candidates": [cand_pass, cand_fail],
    }
    grpo_file.write_text(json.dumps(sample_group) + "\n", encoding="utf-8")

    grpo_summary = execute_grpo_run(dataset_path=grpo_file, dry_run=True)
    assert grpo_summary["status"] == "COMPLETED_DRY_RUN"
    assert grpo_summary["group_count"] == 1
    assert grpo_summary["total_candidates"] == 2
