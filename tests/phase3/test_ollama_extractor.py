"""Hermetic tests for the Ollama-backed extractor and live active inference.

No GPU, no server, no network: the HTTP client is injected. Live-hardware runs live in
``run_llm_phase1.py`` / ``run_llm_phase3.py``, not in the unit suite.
"""

from __future__ import annotations

from typing import Any

import pytest
import torch

from anse.autopoiesis.neuro_surgeon import ActiveInferenceLoop
from anse.core.ollama_extractor import (
    OllamaConfig,
    OllamaExtractor,
    strip_think,
)

# ─── Fake HTTP plumbing ──────────────────────────────────────────────────────


class _FakeResponse:
    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
        self._payload = payload
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeClient:
    """Records requests and replays queued responses per endpoint."""

    def __init__(self, gen: list[dict] | None = None, embed: list[dict] | None = None) -> None:
        self.gen = list(gen or [])
        self.embed = list(embed or [])
        self.requests: list[tuple[str, dict, float]] = []

    def post(self, url: str, json: dict, timeout: float) -> _FakeResponse:
        self.requests.append((url, json, timeout))
        queue = self.gen if url.endswith("/api/generate") else self.embed
        return _FakeResponse(queue.pop(0))


def _gen_body(text: str = "```python\nx = 1\n```", **over: Any) -> dict:
    body = {
        "response": text,
        "eval_count": 20,
        "eval_duration": 1_000_000_000,
        "total_duration": 2_000_000_000,
    }
    body.update(over)
    return body


def _embed_body(dim: int = 1024) -> dict:
    return {"embeddings": [[0.01 * i for i in range(dim)]]}


def _extractor(client: _FakeClient, **cfg: Any) -> OllamaExtractor:
    return OllamaExtractor(OllamaConfig(**cfg), client=client)


# ─── strip_think ─────────────────────────────────────────────────────────────


def test_strip_think_removes_reasoning_spans() -> None:
    assert strip_think("<think>pondering\nmore</think>\ndef f(): ...") == "def f(): ..."
    assert strip_think("no think block") == "no think block"
    assert strip_think("<think>a</think>x<think>b</think>y") == "xy"


# ─── generate ────────────────────────────────────────────────────────────────


def test_generate_sends_think_false_keep_alive_and_options() -> None:
    client = _FakeClient(gen=[_gen_body()])
    text, telemetry = _extractor(client).generate("prompt", system_prompt="sys")
    url, payload, timeout = client.requests[0]
    assert url == "http://localhost:11434/api/generate"
    assert payload["think"] is False
    assert payload["keep_alive"] == "30m"
    assert payload["system"] == "sys"
    assert payload["stream"] is False
    assert payload["options"] == {"num_predict": 512, "temperature": 0.2}
    assert timeout == 600.0
    assert text == "```python\nx = 1\n```"
    assert telemetry == {"eval_count": 20, "tokens_per_second": 20.0, "total_duration_ms": 2000.0}


def test_generate_omits_system_when_absent_and_honours_overrides() -> None:
    client = _FakeClient(gen=[_gen_body()])
    _extractor(client).generate("p", max_new_tokens=64, temperature=0.0)
    payload = client.requests[0][1]
    assert "system" not in payload
    assert payload["options"] == {"num_predict": 64, "temperature": 0.0}


def test_generate_strips_think_block_and_counts_tokens() -> None:
    client = _FakeClient(gen=[_gen_body("<think>hmm</think>\ncode"), _gen_body("more")])
    ex = _extractor(client)
    assert ex.generate("a")[0] == "code"
    ex.generate("b")
    assert ex.calls == 2 and ex.total_eval_tokens == 40


def test_generate_handles_missing_and_zero_telemetry() -> None:
    client = _FakeClient(gen=[{"response": "x"}])
    text, telemetry = _extractor(client).generate("p")
    assert text == "x"
    assert telemetry == {"eval_count": 0, "tokens_per_second": 0.0, "total_duration_ms": 0.0}


# ─── error surfaces ──────────────────────────────────────────────────────────


def test_ollama_error_payload_raises() -> None:
    client = _FakeClient(gen=[{"error": "model not found"}])
    with pytest.raises(RuntimeError, match="model not found"):
        _extractor(client).generate("p")


def test_http_status_error_propagates() -> None:
    class _Bad(_FakeClient):
        def post(self, url: str, json: dict, timeout: float) -> _FakeResponse:
            return _FakeResponse({}, status=500)

    with pytest.raises(RuntimeError, match="HTTP 500"):
        _extractor(_Bad()).generate("p")


# ─── embed ───────────────────────────────────────────────────────────────────


def test_embed_returns_vector_and_sends_keep_alive() -> None:
    client = _FakeClient(embed=[_embed_body()])
    vector = _extractor(client).embed("code")
    assert len(vector) == 1024
    url, payload, _ = client.requests[0]
    assert url.endswith("/api/embed")
    assert payload["model"] == "qwen3-embedding:0.6b"
    assert payload["keep_alive"] == "30m"


def test_embed_rejects_dim_mismatch_instead_of_padding() -> None:
    """Regression guard: a 1024-d vector silently zero-padded to 4096 corrupts JEPA."""
    client = _FakeClient(embed=[_embed_body(dim=768)])
    with pytest.raises(ValueError, match="JEPA would train on padding"):
        _extractor(client).embed("code")


def test_embed_rejects_empty_response() -> None:
    client = _FakeClient(embed=[{"embeddings": []}])
    with pytest.raises(RuntimeError, match="no embeddings"):
        _extractor(client).embed("code")


# ─── extract: the AgentLoop contract ─────────────────────────────────────────


def test_extract_returns_record_matching_hidden_state_contract() -> None:
    client = _FakeClient(gen=[_gen_body()], embed=[_embed_body()])
    text, record = _extractor(client).extract("prompt", system_prompt="sys")
    assert text == "```python\nx = 1\n```"
    assert record.hidden_state.shape == (1, 1024)
    assert record.hidden_state.dtype == torch.float32
    assert len(record.to_embedding()) == 1024
    assert record.model_id == "qwen3:8b"
    assert record.device == "ollama-cuda"
    assert record.token_count == 20
    assert record.metadata["embed_model"] == "qwen3-embedding:0.6b"
    assert record.metadata["tokens_per_second"] == 20.0


def test_extract_embeds_prompt_when_generation_is_empty() -> None:
    client = _FakeClient(gen=[_gen_body("")], embed=[_embed_body()])
    text, record = _extractor(client).extract("fallback prompt")
    assert text == ""
    assert client.requests[1][1]["input"] == "fallback prompt"
    assert record.hidden_state.shape == (1, 1024)


def test_config_is_overridable() -> None:
    client = _FakeClient(gen=[_gen_body()])
    ex = _extractor(client, gen_model="m", keep_alive="1h", think=True, timeout_s=5.0)
    ex.generate("p")
    _, payload, timeout = client.requests[0]
    assert payload["model"] == "m" and payload["keep_alive"] == "1h"
    assert payload["think"] is True and timeout == 5.0


def test_lazy_client_is_built_once(monkeypatch) -> None:
    import httpx

    built: list[int] = []

    class _Sentinel:
        def __init__(self) -> None:
            built.append(1)

    monkeypatch.setattr(httpx, "Client", _Sentinel)
    ex = OllamaExtractor()
    assert isinstance(ex.client, _Sentinel)
    assert ex.client is ex.client
    assert len(built) == 1


# ─── Phase 3: live active inference ──────────────────────────────────────────


GOOD_NET = """```python
import torch
import torch.nn as nn

class CustomNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.head = nn.Linear(3 * 4 * 4, 10)

    def forward(self, x):
        return self.head(self.pool(x).reshape(x.size(0), -1))
```"""

BAD_NET = """```python
import torch
import torch.nn as nn

class CustomNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.head = nn.Linear(3 * 4 * 4, 32)

    def forward(self, x):
        return self.head(self.pool(x).reshape(x.size(0), -1))
```"""


def test_run_live_requires_a_generator() -> None:
    with pytest.raises(ValueError, match="requires a generator"):
        ActiveInferenceLoop().run_live()


def test_run_live_stops_immediately_on_first_turn_success() -> None:
    prompts: list[str] = []

    def gen(prompt: str) -> str:
        prompts.append(prompt)
        return GOOD_NET

    steps = ActiveInferenceLoop(generator=gen).run_live(max_turns=3)
    assert len(steps) == 1
    assert steps[0].energy == 0.0 and steps[0].is_valid
    assert steps[0].proof_token is not None
    assert steps[0].feedback_prompt is None
    assert len(prompts) == 1 and "CustomNet" in prompts[0]


def test_run_live_feeds_real_error_trace_into_next_prompt() -> None:
    prompts: list[str] = []
    replies = iter([BAD_NET, GOOD_NET])

    def gen(prompt: str) -> str:
        prompts.append(prompt)
        return next(replies)

    steps = ActiveInferenceLoop(generator=gen).run_live(max_turns=3)
    assert [s.energy for s in steps] == [100.0, 0.0]
    assert steps[0].is_valid is False and steps[1].is_valid is True
    # The second prompt is the deterministic pain signal, not a canned string.
    assert "Shape mismatch" in prompts[1]
    assert "(16, 32)" in prompts[1]
    assert "failed the laws of physics" in prompts[1]
    assert "50,000" in prompts[1]  # constraints restated with the real trace
    assert steps[1].proof_token is not None


def test_run_live_gives_up_after_max_turns_without_token() -> None:
    steps = ActiveInferenceLoop(generator=lambda p: BAD_NET).run_live(max_turns=2)
    assert len(steps) == 2
    assert all(s.energy == 100.0 and not s.is_valid for s in steps)
    assert all(s.proof_token is None for s in steps)
    assert steps[-1].feedback_prompt is not None


def test_run_live_rejects_stub_candidates_via_ast_auditor() -> None:
    stub = "```python\nimport torch.nn as nn\n\nclass CustomNet(nn.Module):\n    def forward(self, x):\n        pass\n```"
    steps = ActiveInferenceLoop(generator=lambda p: stub).run_live(max_turns=1)
    assert steps[0].energy == 100.0
    assert "AST Whistleblower rejection" in str(steps[0].error_trace)
