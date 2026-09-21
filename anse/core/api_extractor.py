"""
API-backed System 1: drop-in alternative to HiddenStateExtractor for machines
without a GPU. Generates through an OpenAI-compatible endpoint (Ollama / vLLM)
and, when the server is Ollama, fetches the model's embedding of the response as
the hidden-state vector. If no embedding is available the record is empty, and
the harvester skips vector indexing for that trace.

Set ``ollama_native=True`` for Ollama: some Ollama versions (0.1.44 verified)
silently ignore ``seed`` and ``temperature`` on /v1/chat/completions, so every
"seed" returns the same sample. The native /api/chat endpoint honours both.
"""

from __future__ import annotations

import logging

import httpx
import torch

from anse.config import ModelConfig, get_config
from anse.core.encoder import HiddenStateRecord

logger = logging.getLogger(__name__)


class APIExtractor:
    def __init__(
        self,
        config: ModelConfig | None = None,
        client: httpx.Client | None = None,
        seed: int | None = None,
        timeout_s: float = 600.0,
        ollama_native: bool = False,
    ) -> None:
        self.config = config or get_config().model
        self.seed = seed
        self.ollama_native = ollama_native
        self._client = client or httpx.Client(timeout=timeout_s)
        self._base = self.config.api_base_url.rstrip("/")
        self._native_root = self._base[:-3] if self._base.endswith("/v1") else self._base

    def extract(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
    ) -> tuple[str, HiddenStateRecord]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        max_tokens = max_new_tokens or self.config.max_new_tokens
        temp = self.config.temperature if temperature is None else temperature
        if self.ollama_native:
            text, token_count = self._chat_native(messages, max_tokens, temp)
        else:
            text, token_count = self._chat_openai(messages, max_tokens, temp)

        embedding = self._embed(text)
        record = HiddenStateRecord(
            hidden_state=torch.tensor([embedding], dtype=torch.float32),
            layer_indices=[-1],
            token_count=token_count,
            model_id=self.config.api_model_name,
            device="api",
            metadata={"prompt_length": len(prompt), "has_embedding": bool(embedding)},
        )
        return text, record

    def _chat_openai(
        self, messages: list[dict[str, str]], max_tokens: int, temperature: float
    ) -> tuple[str, int]:
        payload: dict[str, object] = {
            "model": self.config.api_model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if self.seed is not None:
            payload["seed"] = self.seed
        response = self._client.post(
            f"{self._base}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.config.api_key}"},
        )
        response.raise_for_status()
        body = response.json()
        text = body["choices"][0]["message"]["content"] or ""
        return text, int(body.get("usage", {}).get("completion_tokens", 0))

    def _chat_native(
        self, messages: list[dict[str, str]], max_tokens: int, temperature: float
    ) -> tuple[str, int]:
        options: dict[str, object] = {"temperature": temperature, "num_predict": max_tokens}
        if self.seed is not None:
            options["seed"] = self.seed
        response = self._client.post(
            f"{self._native_root}/api/chat",
            json={
                "model": self.config.api_model_name,
                "messages": messages,
                "stream": False,
                "options": options,
            },
        )
        response.raise_for_status()
        body = response.json()
        return body["message"]["content"] or "", int(body.get("eval_count", 0))

    def _embed(self, text: str) -> list[float]:
        if not text:
            return []
        try:
            response = self._client.post(
                f"{self._native_root}/api/embeddings",
                json={"model": self.config.api_model_name, "prompt": text},
            )
            response.raise_for_status()
            return [float(x) for x in response.json().get("embedding", [])]
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Embedding unavailable (%s); trace will not be vector-indexed.", exc)
            return []
