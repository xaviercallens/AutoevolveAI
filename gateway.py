#!/usr/bin/env python3
"""
Antigravity Multi-Tier Routing & Circuit-Breaker Gateway.
Routes:
  - Planning     -> Gemini 3.1 Pro
  - Execution    -> Gemini 3.8 Flash
  - Verification -> Gemini 3.1 Pro
  - Fallback     -> Local LoRA / Junior Model (vLLM / Ollama)
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Header, Request, Response
from fastapi.responses import StreamingResponse

# Upstream Frontier Models
MODEL_PLANNING = os.getenv("MODEL_PLANNING", "gemini-3.1-pro")
MODEL_EXECUTION = os.getenv("MODEL_EXECUTION", "gemini-3.8-flash")
MODEL_VERIFICATION = os.getenv("MODEL_VERIFICATION", "gemini-3.1-pro")

# Local Model Configuration
LOCAL_INFERENCE_URL = os.getenv("LOCAL_INFERENCE_URL", "http://localhost:8000/v1/chat/completions")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "antigravity-local")
ROUTE_TO_LOCAL = os.getenv("ROUTE_TO_LOCAL", "true").lower() == "true"

# Infrastructure
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
UPSTREAM_GEMINI = os.getenv("UPSTREAM_GEMINI_URL", "https://generativelanguage.googleapis.com")

client_pool = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=8.0, read=180.0, write=30.0, pool=50.0),
    limits=httpx.Limits(max_keepalive_connections=100, max_connections=200),
)

redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    global redis_client
    redis_client = aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=False,
    )
    yield
    await client_pool.aclose()
    if redis_client is not None:
        await redis_client.aclose()


app = FastAPI(title="Antigravity Multi-Tier Resilient Gateway", lifespan=lifespan)


def _safe_decode_payload(payload: bytes) -> Any:
    """Safely decode JSON payload or fall back to unicode string."""
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return payload.decode("utf-8", errors="replace")


def _classify_phase_by_text(text: str) -> tuple[str, str]:
    """Classify phase by inspecting semantic tokens in request text."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["decompose", "subtask", "architecture", "plan"]):
        return MODEL_PLANNING, "PLANNING"
    if any(k in text_lower for k in ["verify", "inspect", "audit", "run test", "assert"]):
        return MODEL_VERIFICATION, "VERIFICATION"
    return MODEL_EXECUTION, "EXECUTION"


def resolve_target_model(
    phase: str | None, body: dict[str, Any], path: str = ""
) -> tuple[str, str]:
    """Resolves target model based on explicit phase header or content semantics."""
    normalized = (phase or "").strip().lower()
    if normalized in ("plan", "planning", "architect"):
        return MODEL_PLANNING, "PLANNING"
    if normalized in ("verify", "verification", "audit", "review"):
        return MODEL_VERIFICATION, "VERIFICATION"
    if normalized in ("exec", "execute", "implementation", "diff"):
        return MODEL_EXECUTION, "EXECUTION"

    if "3.8-flash" in path:
        return MODEL_EXECUTION, "EXECUTION"
    if "3.1-pro" in path:
        return MODEL_PLANNING, "PLANNING"

    text_parts: list[str] = []
    for turn in body.get("contents", [])[-2:]:
        for part in turn.get("parts", []):
            if "text" in part:
                text_parts.append(part["text"])
    return _classify_phase_by_text(" ".join(text_parts))


def _extract_system_messages(gemini_req: dict[str, Any]) -> list[dict[str, str]]:
    """Extract system instruction parts into OpenAI system message."""
    sys_parts = gemini_req.get("system_instruction", {}).get("parts", [])
    if not sys_parts:
        return []
    sys_text = "\n".join(p.get("text", "") for p in sys_parts if "text" in p).strip()
    return [{"role": "system", "content": sys_text}] if sys_text else []


def _extract_content_messages(gemini_req: dict[str, Any]) -> list[dict[str, str]]:
    """Extract multi-turn contents into OpenAI user and assistant messages."""
    messages: list[dict[str, str]] = []
    for turn in gemini_req.get("contents", []):
        role = "user" if turn.get("role") == "user" else "assistant"
        text_content: list[str] = []
        for p in turn.get("parts", []):
            if "text" in p:
                text_content.append(p["text"])
            elif "functionCall" in p:
                text_content.append(f"<tool_call>{json.dumps(p['functionCall'])}</tool_call>")
        if text_content:
            messages.append({"role": role, "content": "\n".join(text_content)})
    return messages


def gemini_to_openai_payload(
    gemini_req: dict[str, Any], model_name: str = LOCAL_MODEL_NAME
) -> dict[str, Any]:
    """Translate Gemini generateContent payload to OpenAI chat/completions schema."""
    messages = _extract_system_messages(gemini_req)
    messages.extend(_extract_content_messages(gemini_req))

    gen_config = gemini_req.get("generationConfig", {})
    return {
        "model": model_name,
        "messages": messages,
        "temperature": gen_config.get("temperature", 0.1),
        "top_p": gen_config.get("topP", 0.95),
        "max_tokens": gen_config.get("maxOutputTokens", 4096),
    }


def _extract_tool_calls_from_text(content_text: str) -> list[dict[str, Any]]:
    """Extract functionCall objects from text with <tool_call> tags or return raw text."""
    if "<tool_call>" not in content_text or "</tool_call>" not in content_text:
        return [{"text": content_text}]

    raw_tool = content_text.split("<tool_call>")[1].split("</tool_call>")[0].strip()
    try:
        fn_call = json.loads(raw_tool)
        return [{"functionCall": fn_call}]
    except Exception:
        return [{"text": content_text}]


def openai_to_gemini_response(openai_resp: dict[str, Any]) -> dict[str, Any]:
    """Translate OpenAI completion JSON to Gemini Candidate JSON."""
    choices = openai_resp.get("choices", [])
    if not choices:
        return {"candidates": []}

    choice = choices[0]
    message = choice.get("message", {})
    content_text = message.get("content", "") or ""
    parts = _extract_tool_calls_from_text(content_text)

    for tc in message.get("tool_calls", []):
        fn = tc.get("function", {})
        fn_name = fn.get("name", "")
        fn_args_raw = fn.get("arguments", "{}")
        try:
            fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
        except Exception:
            fn_args = {"raw": fn_args_raw}
        parts.append({"functionCall": {"name": fn_name, "args": fn_args}})

    finish_reason = "STOP" if choice.get("finish_reason") == "stop" else "MAX_TOKENS"
    usage = openai_resp.get("usage", {})

    return {
        "candidates": [
            {
                "content": {"parts": parts, "role": "model"},
                "finishReason": finish_reason,
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": usage.get("prompt_tokens", 0),
            "candidatesTokenCount": usage.get("completion_tokens", 0),
            "totalTokenCount": usage.get("total_tokens", 0),
        },
    }


async def log_interaction_to_redis(
    session_id: str,
    endpoint: str,
    request_headers: dict[str, str],
    request_body: bytes,
    response_body: bytes,
    status_code: int,
    latency_ms: float,
    event_id: str | None = None,
    subtask_id: str = "",
    phase: str = "EXECUTION",
    model_used: str = "gemini",
    is_fallback: bool = False,
) -> None:
    """Asynchronously append unified audit event to Redis Streams."""
    if redis_client is None:
        return

    event_id = event_id or str(uuid.uuid4())
    record = {
        "event_id": event_id,
        "trace_id": event_id,
        "session_id": session_id,
        "subtask_id": subtask_id,
        "timestamp": str(time.time()),
        "phase": phase,
        "model_used": model_used,
        "is_fallback": str(int(is_fallback)),
        "endpoint": endpoint,
        "status_code": str(status_code),
        "latency_ms": str(latency_ms),
        "headers_json": json.dumps(request_headers),
        "request_json": json.dumps(_safe_decode_payload(request_body)),
        "response_json": json.dumps(_safe_decode_payload(response_body)),
    }

    try:
        pipe = redis_client.pipeline()
        pipe.xadd("antigravity:stream:audit", record)  # type: ignore[arg-type]
        pipe.rpush(f"antigravity:session:{session_id}:traces", event_id)
        if subtask_id:
            pipe.rpush(f"antigravity:subtask:{subtask_id}:traces", event_id)

        pipe.set(f"antigravity:trace:{event_id}", json.dumps(record))
        await pipe.execute()
    except Exception as err:
        print(f"Warning: Failed to log interaction to Redis: {err}")


async def handle_local_inference(
    gemini_json: dict[str, Any],
    raw_req_body: bytes,
    session_id: str,
    subtask_id: str,
    trace_id: str,
    phase: str,
    path: str,
    start: float,
    is_fallback: bool,
) -> Response | None:
    """Executes inference on local vLLM / Ollama with schema translation."""
    try:
        openai_payload = gemini_to_openai_payload(gemini_json)
        local_resp = await client_pool.post(
            LOCAL_INFERENCE_URL,
            json=openai_payload,
            headers={"Content-Type": "application/json"},
        )
        if local_resp.status_code != 200:
            return None

        local_data = local_resp.json()
        if not isinstance(local_data, dict) or not local_data.get("choices"):
            return None

        translated_resp = openai_to_gemini_response(local_data)
        resp_bytes = json.dumps(translated_resp).encode("utf-8")
        latency = (time.perf_counter() - start) * 1000.0

        asyncio.create_task(
            log_interaction_to_redis(
                session_id=session_id,
                endpoint=path,
                request_headers={"x-backend-routed": "local-lora"},
                request_body=raw_req_body,
                response_body=resp_bytes,
                status_code=200,
                latency_ms=latency,
                event_id=trace_id,
                subtask_id=subtask_id,
                phase=phase,
                model_used=LOCAL_MODEL_NAME,
                is_fallback=is_fallback,
            )
        )

        served_by = f"{LOCAL_MODEL_NAME} ({'FALLBACK' if is_fallback else 'LOCAL'})"
        resp_headers = {
            "content-type": "application/json",
            "x-trace-id": trace_id,
            "x-served-by": served_by,
            "x-backend-routed": "local-lora",
        }
        return Response(content=resp_bytes, status_code=200, headers=resp_headers)
    except Exception as err:
        print(f"Warning: Local inference failed ({err}). Falling back.")
        return None


async def _dispatch_upstream(
    request: Request,
    url: str,
    headers: dict[str, str],
    req_body: bytes,
    target_model: str,
    trace_id: str,
    session_id: str,
    subtask_id: str,
    phase: str,
    path: str,
    start: float,
) -> Response:
    """Dispatches request to upstream Gemini endpoint with audit recording."""
    upstream_resp = await client_pool.request(
        method=request.method,
        url=url,
        headers=headers,
        content=req_body,
    )
    latency = (time.perf_counter() - start) * 1000.0

    asyncio.create_task(
        log_interaction_to_redis(
            session_id=session_id,
            endpoint=path,
            request_headers=headers,
            request_body=req_body,
            response_body=upstream_resp.content,
            status_code=upstream_resp.status_code,
            latency_ms=latency,
            event_id=trace_id,
            subtask_id=subtask_id,
            phase=phase,
            model_used=target_model,
            is_fallback=False,
        )
    )

    excluded = {"content-encoding", "content-length", "transfer-encoding"}
    resp_headers = {k: v for k, v in upstream_resp.headers.items() if k.lower() not in excluded}
    resp_headers["x-trace-id"] = trace_id
    resp_headers["x-served-by"] = target_model
    resp_headers["x-backend-routed"] = "upstream-gemini"
    return Response(
        content=upstream_resp.content, status_code=upstream_resp.status_code, headers=resp_headers
    )


async def _handle_streaming_request(
    request: Request,
    url: str,
    headers: dict[str, str],
    req_body: bytes,
    session_id: str,
    subtask_id: str,
    path: str,
    start_time: float,
) -> StreamingResponse:
    """Handles Server-Sent Events (SSE) streaming relays with chunk reassembly."""
    trace_id = str(uuid.uuid4())
    req = client_pool.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=req_body,
    )
    upstream_resp = await client_pool.send(req, stream=True)

    async def stream_iterator() -> AsyncGenerator[bytes, None]:
        response_chunks: list[bytes] = []
        try:
            async for chunk in upstream_resp.aiter_bytes():
                response_chunks.append(chunk)
                yield chunk
        finally:
            await upstream_resp.aclose()
            latency = (time.perf_counter() - start_time) * 1000.0
            full_response = b"".join(response_chunks)
            asyncio.create_task(
                log_interaction_to_redis(
                    session_id=session_id,
                    endpoint=path,
                    request_headers=headers,
                    request_body=req_body,
                    response_body=full_response,
                    status_code=upstream_resp.status_code,
                    latency_ms=latency,
                    event_id=trace_id,
                    subtask_id=subtask_id,
                    phase="EXECUTION",
                    model_used=MODEL_EXECUTION,
                    is_fallback=False,
                )
            )

    resp_headers = dict(upstream_resp.headers)
    resp_headers["x-trace-id"] = trace_id
    resp_headers["x-served-by"] = MODEL_EXECUTION
    resp_headers["x-backend-routed"] = "upstream-gemini"
    return StreamingResponse(
        stream_iterator(),
        status_code=upstream_resp.status_code,
        headers=resp_headers,
    )


async def _passthrough_non_generation(request: Request, path: str, req_body: bytes) -> Response:
    """Direct passthrough for non-generation requests (models list, embeddings, etc)."""
    upstream_url = f"{UPSTREAM_GEMINI}/{path}"
    if request.url.query:
        upstream_url = f"{upstream_url}?{request.url.query}"
    headers = dict(request.headers)
    headers.pop("host", None)
    res = await client_pool.request(request.method, upstream_url, headers=headers, content=req_body)
    return Response(content=res.content, status_code=res.status_code)


async def _route_with_circuit_breaker(
    request: Request,
    upstream_url: str,
    headers: dict[str, str],
    req_body: bytes,
    gemini_json: dict[str, Any],
    session_id: str,
    subtask_id: str,
    trace_id: str,
    phase: str,
    target_model: str,
    path: str,
    start_time: float,
) -> Response:
    """Dispatches to upstream with automatic failover to local model on 429/5xx or timeout."""
    try:
        upstream_res = await client_pool.request(
            request.method, upstream_url, headers=headers, content=req_body
        )
        if upstream_res.status_code in (429, 500, 502, 503, 504):
            print(
                f"Warning: Upstream returned {upstream_res.status_code}. Circuit breaker engaged."
            )
            local_fallback = await handle_local_inference(
                gemini_json,
                req_body,
                session_id,
                subtask_id,
                trace_id,
                phase,
                path,
                start_time,
                True,
            )
            if local_fallback is not None:
                return local_fallback

        return await _dispatch_upstream(
            request,
            upstream_url,
            headers,
            req_body,
            target_model,
            trace_id,
            session_id,
            subtask_id,
            phase,
            path,
            start_time,
        )
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as err:
        print(f"Warning: Upstream network error ({err}). Circuit breaker engaged.")
        local_fallback = await handle_local_inference(
            gemini_json, req_body, session_id, subtask_id, trace_id, phase, path, start_time, True
        )
        if local_fallback is not None:
            return local_fallback
        return Response(
            content=b'{"error": "Upstream and local fallback failed."}', status_code=503
        )


def _build_upstream_url(base_path: str, query: str | None) -> str:
    """Build full upstream URL appending query string if present."""
    url = f"{UPSTREAM_GEMINI}/{base_path}"
    return f"{url}?{query}" if query else url


def _should_force_local(x_force_local: str, x_route_target: str) -> bool:
    """Determine if client explicitly forced local model routing."""
    return x_force_local.lower() == "true" or x_route_target.lower() == "local"


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reverse_proxy(
    request: Request,
    path: str,
    x_task_phase: str | None = Header(default=None),
    x_antigravity_session_id: str = Header(default="default_session"),
    x_subtask_id: str = Header(default=""),
    x_route_target: str = Header(default="auto"),
    x_force_local: str = Header(default="false"),
) -> Response:
    start_time = time.perf_counter()
    req_body = await request.body()
    trace_id = str(uuid.uuid4())
    is_gen = "generatecontent" in path.lower() and request.method == "POST"

    if not is_gen:
        return await _passthrough_non_generation(request, path, req_body)

    gemini_json = _safe_decode_payload(req_body)
    gemini_dict = gemini_json if isinstance(gemini_json, dict) else {}

    target_model, phase = resolve_target_model(x_task_phase, gemini_dict, path=path)

    if _should_force_local(x_force_local, x_route_target):
        local_res = await handle_local_inference(
            gemini_dict,
            req_body,
            x_antigravity_session_id,
            x_subtask_id,
            trace_id,
            phase,
            path,
            start_time,
            False,
        )
        if local_res is not None:
            return local_res

    query_str = str(request.url.query) if request.url.query else ""
    if "stream" in path or "alt=sse" in query_str:
        stream_url = _build_upstream_url(path, query_str)
        stream_headers = dict(request.headers)
        stream_headers.pop("host", None)
        return await _handle_streaming_request(
            request,
            stream_url,
            stream_headers,
            req_body,
            x_antigravity_session_id,
            x_subtask_id,
            path,
            start_time,
        )

    target_path = re.sub(r"models/[^:]+", f"models/{target_model}", path)
    upstream_url = _build_upstream_url(target_path, query_str)
    headers = dict(request.headers)
    headers.pop("host", None)

    return await _route_with_circuit_breaker(
        request,
        upstream_url,
        headers,
        req_body,
        gemini_dict,
        x_antigravity_session_id,
        x_subtask_id,
        trace_id,
        phase,
        target_model,
        path,
        start_time,
    )


if __name__ == "__main__":
    import uvicorn

    bind_host = os.getenv("GATEWAY_HOST", "127.0.0.1")
    bind_port = int(os.getenv("GATEWAY_PORT", "8080"))
    uvicorn.run(app, host=bind_host, port=bind_port)  # nosec B104
