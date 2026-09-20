from __future__ import annotations

from gateway import (
    MODEL_EXECUTION,
    MODEL_PLANNING,
    MODEL_VERIFICATION,
    _extract_tool_calls_from_text,
    gemini_to_openai_payload,
    resolve_target_model,
)


class TestGatewayRouting:
    """Validates multi-tier semantic routing (Lean: StrongGravity axioms)."""

    def test_planning_phase_resolves_to_pro(self):
        model, phase = resolve_target_model("planning", {}, "")
        assert model == MODEL_PLANNING
        assert phase == "PLANNING"

    def test_execution_phase_resolves_to_flash(self):
        model, phase = resolve_target_model("execution", {}, "")
        assert model == MODEL_EXECUTION
        assert phase == "EXECUTION"

    def test_verification_phase_resolves_to_pro(self):
        model, phase = resolve_target_model("verification", {}, "")
        assert model == MODEL_VERIFICATION
        assert phase == "VERIFICATION"

    def test_semantic_classification_planning(self):
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "decompose subtask architecture"}
                    ],
                }
            ]
        }
        model, phase = resolve_target_model(None, body, "")
        assert model == MODEL_PLANNING
        assert phase == "PLANNING"

    def test_semantic_classification_verification(self):
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "verify audit inspect the code"}
                    ],
                }
            ]
        }
        model, phase = resolve_target_model(None, body, "")
        assert model == MODEL_VERIFICATION
        assert phase == "VERIFICATION"

    def test_default_fallback_is_execution(self):
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Just do some stuff"}],
                }
            ]
        }
        model, phase = resolve_target_model(None, body, "")
        assert model == MODEL_EXECUTION
        assert phase == "EXECUTION"

    def test_path_based_routing_flash(self):
        path = "/v1/models/gemini-3.8-flash:generateContent"
        model, phase = resolve_target_model(None, {}, path)
        assert model == MODEL_EXECUTION
        assert phase == "EXECUTION"

    def test_path_based_routing_pro(self):
        path = "/v1/models/gemini-3.1-pro:generateContent"
        model, phase = resolve_target_model(None, {}, path)
        assert model == MODEL_PLANNING
        assert phase == "PLANNING"

    def test_gemini_to_openai_translation(self):
        gemini_req = {
            "contents": [
                {"role": "user", "parts": [{"text": "Hello"}]}
            ],
        }
        res = gemini_to_openai_payload(gemini_req, "gpt-4")
        assert res["model"] == "gpt-4"
        assert "messages" in res
        assert any(m["content"] == "Hello" for m in res["messages"])

    def test_tool_call_extraction_with_tags(self):
        text = (
            '<tool_call>'
            '{"name": "func", "arguments": {}}'
            '</tool_call>'
        )
        res = _extract_tool_calls_from_text(text)
        assert len(res) == 1
        assert "functionCall" in res[0]

    def test_tool_call_extraction_without_tags(self):
        text = "Just a plain text response"
        res = _extract_tool_calls_from_text(text)
        assert len(res) == 1
        assert "text" in res[0]
        assert res[0]["text"] == text
