"""APIExtractor against a fake HTTP transport (external I/O boundary)."""

import json

import httpx
import pytest

from anse.config import ModelConfig
from anse.core.api_extractor import APIExtractor


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_extract_sends_messages_and_returns_text_with_embedding():
    seen: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append({"path": request.url.path, "body": body})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(200, json={"choices": [{"message": {"content": "```python\nx = 1\n```"}}], "usage": {"completion_tokens": 7}})
        return httpx.Response(200, json={"embedding": [0.5, -1.0, 2.0]})

    cfg = ModelConfig(api_base_url="http://llm.test/v1", api_model_name="tiny", temperature=0.3)
    text, record = APIExtractor(config=cfg, client=_client(handler), seed=11).extract("do it", system_prompt="sys")

    assert text == "```python\nx = 1\n```"
    assert record.to_embedding() == [0.5, -1.0, 2.0]
    assert record.token_count == 7 and record.model_id == "tiny"
    chat = seen[0]["body"]
    assert [m["role"] for m in chat["messages"]] == ["system", "user"]
    assert chat["seed"] == 11 and chat["temperature"] == 0.3
    assert seen[1]["path"] == "/api/embeddings"


def test_missing_embedding_endpoint_yields_empty_vector_not_a_crash():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})
        return httpx.Response(404)

    cfg = ModelConfig(api_base_url="http://llm.test/v1")
    text, record = APIExtractor(config=cfg, client=_client(handler)).extract("p")
    assert text == "hello"
    assert record.to_embedding() == []
    assert record.metadata["has_embedding"] is False


def test_chat_http_error_propagates():
    cfg = ModelConfig(api_base_url="http://llm.test/v1")
    extractor = APIExtractor(config=cfg, client=_client(lambda request: httpx.Response(500)))
    with pytest.raises(httpx.HTTPStatusError, match="500"):
        extractor.extract("p")


def test_native_ollama_mode_sends_seed_and_temperature_in_options():
    seen: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append({"path": request.url.path, "body": json.loads(request.content)})
        if request.url.path == "/api/chat":
            return httpx.Response(200, json={"message": {"content": "native reply"}, "eval_count": 9})
        return httpx.Response(200, json={"embedding": [1.0]})

    cfg = ModelConfig(api_base_url="http://llm.test/v1", api_model_name="tiny")
    extractor = APIExtractor(config=cfg, client=_client(handler), seed=5, ollama_native=True)
    text, record = extractor.extract("p", temperature=0.9)

    assert text == "native reply" and record.token_count == 9
    assert seen[0]["path"] == "/api/chat"
    assert seen[0]["body"]["options"] == {"temperature": 0.9, "num_predict": cfg.max_new_tokens, "seed": 5}
    assert seen[0]["body"]["stream"] is False
