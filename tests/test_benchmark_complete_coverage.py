"""
Comprehensive unit & integration test suite targeting >= 95% test coverage across:
- anse/benchmark/dpo_schema.py
- anse/benchmark/tolerances.py
- anse/benchmark/rust_numeric_cases.py
- scripts/export_claude_opus_rl_dataset.py
- gateway.py
- web/server.py (ASCD reset & telemetry endpoints)
"""

import json
import pytest
import os
import time
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from starlette.requests import Request

# Module under test imports
from anse.benchmark.dpo_schema import DPORecord
from anse.benchmark.tolerances import TOLERANCES, get_registry, normalize_error
from anse.benchmark.rust_numeric_cases import (
    compile_and_run_rust,
    RUST_KERNELS,
    RustBenchmarkResult,
)
import scripts.export_claude_opus_rl_dataset as export_script
import gateway
import web.server as web_server


# =========================================================================
# 1. DPORecord Schema & Validation
# =========================================================================

def test_dpo_record_valid_lifecycle():
    data = {
        "case_id": "test_001",
        "domain": "rust_numerical",
        "prompt": "Implement symplectic velocity verlet",
        "chosen": "fn verlet() { /* SIMD */ }",
        "rejected": "fn verlet() { /* slow */ }",
        "reward_chosen": 10.0,
        "reward_rejected": 5.0,
        "reward_delta": 5.0,
        "opt_lat": 1.5,
        "base_lat": 4.5,
        "opt_e": 2.0,
        "base_e": 8.0,
        "opt_lat__provenance": "measured",
        "base_lat__provenance": "measured",
        "opt_e__provenance": "measured",
        "base_e__provenance": "measured",
        "metadata": {"simd": True},
    }
    rec = DPORecord.from_dict(data)
    assert rec.case_id == "test_001"
    assert rec.reward_delta == 5.0
    assert rec.metadata["simd"] is True

    exported = rec.to_dict()
    assert exported["case_id"] == "test_001"
    assert exported["opt_lat"] == 1.5


def test_dpo_record_invalidation_rules():
    # 1. Non-positive reward delta
    with pytest.raises(ValueError, match="reward_delta"):
        DPORecord(
            case_id="bad_delta",
            domain="math",
            prompt="p",
            chosen="c",
            rejected="r",
            reward_chosen=5.0,
            reward_rejected=5.0,
            reward_delta=0.0,
            opt_lat=1.0,
            base_lat=2.0,
            opt_e=1.0,
            base_e=2.0,
        )

    # 2. Non-positive latency
    with pytest.raises(ValueError, match="latency values"):
        DPORecord(
            case_id="bad_lat",
            domain="math",
            prompt="p",
            chosen="c",
            rejected="r",
            reward_chosen=10.0,
            reward_rejected=5.0,
            reward_delta=5.0,
            opt_lat=-1.0,
            base_lat=2.0,
            opt_e=1.0,
            base_e=2.0,
        )

    # 3. Provenance violation (fabrication guard)
    with pytest.raises(ValueError, match="Fabrication violation"):
        DPORecord(
            case_id="bad_prov",
            domain="math",
            prompt="p",
            chosen="c",
            rejected="r",
            reward_chosen=10.0,
            reward_rejected=5.0,
            reward_delta=5.0,
            opt_lat=1.0,
            base_lat=2.0,
            opt_e=1.0,
            base_e=2.0,
            opt_lat__provenance="synthetic",
        )

    # 4. Missing keys in from_dict
    with pytest.raises(KeyError, match="missing required"):
        DPORecord.from_dict({"case_id": "missing_keys"})


# =========================================================================
# 2. Tolerances Registry & Normalization
# =========================================================================

def test_tolerances_lookup_and_normalize():
    assert "RUST-01" in TOLERANCES
    assert "MATH-01" in TOLERANCES
    assert "PHYS-01" in TOLERANCES

    # Zero or negative error
    assert normalize_error("RUST-01", 0.0) == 0.0
    assert normalize_error("RUST-01", -0.5) == 0.0

    # Normalization with default tolerance (clamped to [0, 1])
    tol_val = TOLERANCES["RUST-01"]
    assert normalize_error("RUST-01", tol_val * 0.5) == pytest.approx(0.5, 1e-4)
    assert normalize_error("RUST-01", tol_val * 2.0) == 1.0

    # Registry loading
    reg = get_registry()
    assert isinstance(reg, dict)


def test_tolerances_quadratic_normalization():
    with patch("anse.benchmark.tolerances.get_registry", return_value={"TEST-QUAD": {"tolerance": 1e-3, "normalization": "quadratic"}}):
        # ratio is 0.5, quadratic -> 0.25
        norm_half = normalize_error("TEST-QUAD", 0.5e-3)
        assert norm_half == pytest.approx(0.25, 1e-4)
        # ratio is 2.0, quadratic clamped to 1.0
        norm_clamp = normalize_error("TEST-QUAD", 2e-3)
        assert norm_clamp == 1.0


# =========================================================================
# 3. Rust Numeric Cases Error Handling
# =========================================================================

def test_rust_cases_unknown_id():
    with pytest.raises(ValueError, match="Unknown Rust case ID"):
        compile_and_run_rust("NON_EXISTENT_RUST_CASE")


def test_rust_cases_compilation_failure():
    mock_failed_comp = MagicMock(returncode=1, stderr="syntax error in rust kernel")
    with patch("subprocess.run", return_value=mock_failed_comp):
        result = compile_and_run_rust("RUST-01")
        assert result.verified is False
        assert result.energy == 1e6
        assert "compilation_error" in result.details


def test_rust_cases_execution_failure():
    mock_success_comp = MagicMock(returncode=0)
    mock_failed_run = MagicMock(returncode=1, stderr="panic: index out of bounds", stdout="")
    with patch("subprocess.run", side_effect=[mock_success_comp, mock_failed_run]):
        result = compile_and_run_rust("RUST-01")
        assert result.verified is False
        assert result.energy > 0


# =========================================================================
# 4. Export Claude / Opus RL Dataset Script
# =========================================================================

def test_export_safe_json_dumps():
    data = {
        "np_bool": np.bool_(True),
        "np_int": np.int64(42),
        "np_float": np.float64(3.14159),
        "np_arr": np.array([1, 2, 3]),
        "regular_str": "hello",
    }
    encoded = export_script.safe_json_dumps(data)
    decoded = json.loads(encoded)
    assert decoded["np_bool"] is True
    assert decoded["np_int"] == 42
    assert decoded["np_float"] == pytest.approx(3.14159, 1e-4)
    assert decoded["np_arr"] == [1, 2, 3]


def test_export_harvest_records_empty():
    records = export_script.harvest_claude_opus_records("non_existent_stream")
    assert isinstance(records, list)


def test_export_seed_synthetic():
    records = export_script.seed_synthetic_claude_opus_if_empty([], count=6)
    assert len(records) >= 6
    rec = records[0]
    assert "claude" in rec["model_used"].lower()
    assert rec["status_code"] == 200
    assert "messages_json" in rec

    # Already populated records should pass through
    assert export_script.seed_synthetic_claude_opus_if_empty(records) == records


def test_export_build_datasets(tmp_path):
    records = export_script.seed_synthetic_claude_opus_if_empty([], count=4)
    sft_file = tmp_path / "sft.jsonl"
    dpo_file = tmp_path / "dpo.jsonl"

    sft_count = export_script.build_sft_dataset(records, sft_file)
    dpo_count = export_script.build_dpo_dataset(records, dpo_file)

    assert sft_count == len(records)
    assert dpo_count == len(records)
    assert os.path.exists(sft_file)
    assert os.path.exists(dpo_file)

    # Validate DPO record schema compatibility
    with open(dpo_file, "r") as f:
        for line in f:
            d = json.loads(line)
            dpo_obj = DPORecord.from_dict(d)
            assert dpo_obj.reward_delta > 0


def test_export_main_cli(tmp_path):
    sft_file = tmp_path / "cli_sft.jsonl"
    dpo_file = tmp_path / "cli_dpo.jsonl"
    with patch(
        "sys.argv",
        [
            "export_claude_opus_rl_dataset.py",
            "--output-sft",
            str(sft_file),
            "--output-dpo",
            str(dpo_file),
            "--seed-if-empty",
        ],
    ):
        export_script.main()
        assert os.path.exists(sft_file)
        assert os.path.exists(dpo_file)


# =========================================================================
# 5. Multi-Tier Gateway Coverage
# =========================================================================

def test_gateway_model_and_payload_utilities():
    assert gateway.is_claude_or_opus_model("claude-3-5-sonnet") is True
    assert gateway.is_claude_or_opus_model("claude-3-opus") is True
    assert gateway.is_claude_or_opus_model("gemini-2.0-flash") is False

    # safe decode payload
    assert gateway._safe_decode_payload(b'{"key": "value"}') == {"key": "value"}
    assert gateway._safe_decode_payload(b"plain string") == "plain string"

    # classification by text
    assert gateway._classify_phase_by_text("Please create an architecture plan")[1] == "PLANNING"
    assert gateway._classify_phase_by_text("Run audit and verify tests")[1] == "VERIFICATION"
    assert gateway._classify_phase_by_text("Write python function")[1] == "EXECUTION"

    # resolve target model
    assert gateway.resolve_target_model("plan", {})[1] == "PLANNING"
    assert gateway.resolve_target_model("verify", {})[1] == "VERIFICATION"
    assert gateway.resolve_target_model("exec", {})[1] == "EXECUTION"
    assert gateway.resolve_target_model(None, {}, path="3.8-flash")[1] == "EXECUTION"
    assert gateway.resolve_target_model(None, {}, path="3.1-pro")[1] == "PLANNING"


def test_gateway_gemini_to_openai_translation():
    gemini_req = {
        "system_instruction": {"parts": [{"text": "You are an assistant"}]},
        "contents": [
            {"role": "user", "parts": [{"text": "Hello"}]},
            {"role": "model", "parts": [{"text": "Hi there"}]},
            {"role": "user", "parts": [{"functionCall": {"name": "test_tool", "args": {}}}]},
        ],
        "generationConfig": {"temperature": 0.2, "topP": 0.9, "maxOutputTokens": 1024},
    }
    openai_payload = gateway.gemini_to_openai_payload(gemini_req, "test-model")
    assert openai_payload["model"] == "test-model"
    assert len(openai_payload["messages"]) == 4
    assert openai_payload["messages"][0]["role"] == "system"
    assert openai_payload["messages"][0]["content"] == "You are an assistant"
    assert openai_payload["max_tokens"] == 1024


def test_gateway_openai_to_gemini_translation():
    openai_resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Result with <tool_call>{\"name\": \"run_cmd\", \"args\": {\"c\": \"ls\"}}</tool_call>",
                    "tool_calls": [
                        {"function": {"name": "secondary_tool", "arguments": "{\"flag\": true}"}}
                    ],
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
    }
    gemini_resp = gateway.openai_to_gemini_response(openai_resp)
    assert "candidates" in gemini_resp
    parts = gemini_resp["candidates"][0]["content"]["parts"]
    assert any("functionCall" in p for p in parts)
    assert gemini_resp["usageMetadata"]["totalTokenCount"] == 150

    # Empty choices
    assert gateway.openai_to_gemini_response({"choices": []}) == {"candidates": []}


def test_gateway_routing_helpers():
    assert gateway._build_upstream_url("v1beta/models", "key=123") == "https://generativelanguage.googleapis.com/v1beta/models?key=123"
    assert gateway._build_upstream_url("v1beta/models", None) == "https://generativelanguage.googleapis.com/v1beta/models"
    assert gateway._should_force_local("true", "gemini") is True
    assert gateway._should_force_local("false", "local") is True
    assert gateway._should_force_local("false", "upstream") is False


@pytest.mark.asyncio
async def test_gateway_mcp_endpoints():
    mock_router = MagicMock()
    mock_router.list_servers.return_value = ["antigravity-guard", "lean4-prover"]
    async def mock_list_tools(force_refresh=False):
        return [{"name": "audit_code", "server": "antigravity-guard"}]
    mock_router.list_tools = mock_list_tools

    async def mock_call_tool(server, tool, args):
        return {"result": f"called_{tool}_on_{server}"}
    mock_router.call_tool = mock_call_tool

    with patch("gateway.get_mcp_router", return_value=mock_router):
        servers = await gateway.list_mcp_servers()
        assert "servers" in servers
        assert "antigravity-guard" in servers["servers"]

        tools = await gateway.list_mcp_tools()
        assert tools["count"] == 1
        assert tools["tools"][0]["name"] == "audit_code"


def test_gateway_http_routes():
    client = TestClient(gateway.app)

    # Health check
    resp = client.get("/health")
    assert resp.status_code == 200

    # Anthropic messages fallback route
    with patch("gateway.log_claude_opus_interaction", return_value=None):
        msg_payload = {
            "model": "claude-3-opus-20240229",
            "messages": [{"role": "user", "content": "Compute symplectic invariants"}],
        }
        res = client.post("/v1/messages", json=msg_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["model"] == "claude-3-opus-20240229"
        assert len(data["content"]) > 0


# =========================================================================
# 6. ASCD Control Center Web Server & Reset Endpoint
# =========================================================================

def test_ascd_control_center_state_and_endpoints():
    client = TestClient(web_server.app)

    # Telemetry
    tel = client.get("/api/ascd/telemetry")
    assert tel.status_code == 200
    tel_json = tel.json()
    assert "status" in tel_json

    # Reset endpoint
    reset_resp = client.post("/api/ascd/reset")
    assert reset_resp.status_code == 200
    reset_json = reset_resp.json()
    assert reset_json["status"] == "SUCCESS"
    assert "state" in reset_json

    state = reset_json["state"]
    assert state["metrics"]["active_agents"] == 12
    assert state["metrics"]["tokens_per_sec"] == 4250
    assert len(state["mcp_servers"]) == 4
    assert len(state["agents"]) == 4
    assert state["status"] == "RUNNING"

    # Emergency halt
    halt_resp = client.post("/api/ascd/halt", json={"paused": True})
    assert halt_resp.status_code == 200
    assert halt_resp.json()["status"] == "PAUSED"


# =========================================================================
# 7. Extended Gateway, Rust & Tolerances Edge Coverage
# =========================================================================

def test_tolerances_yaml_exception_handling():
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        # Force cache clearing
        import anse.benchmark.tolerances as tol_module
        tol_module._REGISTRY_CACHE = None
        reg = tol_module.get_registry()
        assert reg == {}


def test_rust_numeric_time_cmd_not_found():
    mock_success_comp = MagicMock(returncode=0)
    mock_run_direct = MagicMock(returncode=0, stdout="INVARIANT_CHECK: PASSED\nINVARIANT_ERROR: 1.2e-5", stderr="")
    with patch("subprocess.run", side_effect=[mock_success_comp, FileNotFoundError("No /usr/bin/time"), mock_run_direct]):
        res = compile_and_run_rust("RUST-01")
        assert res.verified is True
        assert res.invariant_error == pytest.approx(1.2e-5, 1e-6)


def test_rust_numeric_run_all_benchmarks():
    with patch("anse.benchmark.rust_numeric_cases.compile_and_run_rust") as mock_run:
        mock_run.return_value = RustBenchmarkResult(
            case_id="RUST-01",
            name="Mock Kernel",
            description="Mock",
            latency_ms=1.0,
            memory_mb=1.0,
            invariant_error=0.0,
            energy=2.0,
            verified=True,
            details={},
        )
        from anse.benchmark.rust_numeric_cases import run_all_rust_benchmarks
        results = run_all_rust_benchmarks()
        assert len(results) == len(RUST_KERNELS)


def test_export_claude_opus_redis_stream_mock():
    mock_redis = MagicMock()
    mock_redis.is_connected = True
    mock_client = MagicMock()
    mock_client.xrange.return_value = [
        (
            b"1690000000-0",
            {
                b"event_id": b"evt_1",
                b"model_used": b"claude-3-opus",
                b"prompt": b"Write SIMD kernel",
                b"completion": b"fn simd() {}",
                b"latency_ms": b"12.4",
            },
        )
    ]
    mock_redis._client = mock_client
    with patch("scripts.export_claude_opus_rl_dataset.RedisLongTermMemory", return_value=mock_redis):
        recs = export_script.harvest_claude_opus_records("test_stream")
        assert len(recs) == 1
        assert recs[0]["model_used"] == "claude-3-opus"


def test_export_claude_opus_filter_branches(tmp_path):
    # Empty prompt or completion in SFT
    sft_file = tmp_path / "sft_filtered.jsonl"
    dpo_file = tmp_path / "dpo_filtered.jsonl"
    records = [
        {"prompt": "", "completion": "c"},
        {"prompt": "p", "completion": ""},
        {"prompt": "p", "completion": "same", "rejected_completion": "same"},
    ]
    assert export_script.build_sft_dataset(records, sft_file) == 1
    assert export_script.build_dpo_dataset(records, dpo_file) == 0


def test_gateway_critic_and_router_singletons():
    critic = gateway.get_gateway_critic()
    assert critic is not None
    router = gateway.get_mcp_router()
    assert router is not None


def test_gateway_text_classification_branches():
    # Body text inspection in resolve_target_model
    body_plan = {
        "contents": [
            {"parts": [{"text": "Please provide an architecture decomposition plan"}]}
        ]
    }
    assert gateway.resolve_target_model(None, body_plan)[1] == "PLANNING"

    body_verify = {
        "contents": [
            {"parts": [{"text": "Inspect AST invariants and run tests"}]}
        ]
    }
    assert gateway.resolve_target_model(None, body_verify)[1] == "VERIFICATION"


def test_gateway_malformed_tool_call_extract():
    # Invalid JSON in tool call
    parts_malformed = gateway._extract_tool_calls_from_text("<tool_call>{invalid_json</tool_call>")
    assert len(parts_malformed) == 1
    assert "text" in parts_malformed[0]

    # Malformed function call arguments in openai_to_gemini_response
    openai_bad_args = {
        "choices": [
            {
                "message": {
                    "tool_calls": [{"function": {"name": "test", "arguments": "invalid_json"}}]
                },
                "finish_reason": "stop",
            }
        ]
    }
    gemini_resp = gateway.openai_to_gemini_response(openai_bad_args)
    assert "candidates" in gemini_resp


@pytest.mark.asyncio
async def test_gateway_mcp_call_and_rpc():
    mock_router = MagicMock()
    mock_router.call_tool = AsyncMock(return_value={"result": "routed"})
    mock_router.handle_json_rpc = AsyncMock(return_value={"jsonrpc": "2.0", "result": "ok"})

    with patch("gateway.get_mcp_router", return_value=mock_router):
        client = TestClient(gateway.app)
        
        # Test call_mcp_tool_by_server
        resp_call = client.post("/mcp/tools/antigravity-guard/audit", json={"path": "main.py"})
        assert resp_call.status_code == 200

        # Test call_mcp_tool_auto_route
        resp_auto = client.post("/mcp/call", json={"name": "audit", "arguments": {}})
        assert resp_auto.status_code == 200

        # Test mcp_json_rpc_endpoint
        resp_rpc = client.post("/mcp/rpc/antigravity-guard", json={"method": "tools/list"})
        assert resp_rpc.status_code == 200


@pytest.mark.asyncio
async def test_gateway_chat_completions_proxy():
    client = TestClient(gateway.app)
    mock_upstream_resp = MagicMock()
    mock_upstream_resp.status_code = 200
    mock_upstream_resp.content = b'{"choices": [{"message": {"role": "assistant", "content": "Done"}}]}'

    with patch.object(gateway.client_pool, "post", return_value=mock_upstream_resp):
        payload = {
            "model": "claude-3-opus",
            "messages": [{"role": "user", "content": "hello"}],
        }
        resp = client.post("/v1/chat/completions", json=payload, headers={"authorization": "Bearer test"})
        assert resp.status_code == 200
        data = resp.json()
        assert "choices" in data

