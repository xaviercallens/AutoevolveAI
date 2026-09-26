"""
Tests for P1-8: Silent in-memory fallbacks must announce themselves.

Verifies that when Redis is unavailable:
1. redis_bus logs at ERROR level and marks writes as volatile (is_mock=True)
2. redis_memory.store_turn() logs at ERROR and either raises or returns False
3. Both modules' docstrings qualify their persistence claims
"""

from __future__ import annotations

import logging
import re
from unittest.mock import MagicMock, patch

import pytest

from anse.infrastructure.fabrication import UnverifiedDataError
from anse.memory.redis_memory import ConversationTurn, RedisLongTermMemory
from antigravity_harness.storage.redis_bus import RedisBus, TraceRecord


class TestRedisBusConnectionFailure:
    """Test redis_bus behavior when connection fails."""

    def test_failed_connection_logs_error_with_port(self, caplog: pytest.LogCaptureFixture) -> None:
        """When connection fails, logs at ERROR level with host and port."""
        with patch("redis.Redis.ping", side_effect=ConnectionError("Connection refused")):
            with caplog.at_level(logging.ERROR):
                bus = RedisBus(host="localhost", port=6379)

        # Assert ERROR level was logged
        assert any(record.levelname == "ERROR" for record in caplog.records)

        # Assert port is mentioned in the error message
        error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
        assert any("6379" in msg for msg in error_messages), f"Port 6379 not found in error messages: {error_messages}"

    def test_publish_event_returns_dict_with_is_mock_true_on_fallback(self) -> None:
        """When using in-memory fallback, publish_event returns is_mock=True."""
        with patch("redis.Redis.ping", side_effect=TimeoutError("Connection timeout")):
            bus = RedisBus(host="localhost", port=6379)

        result = bus.publish_event("test-stream", {"key": "value"})

        assert isinstance(result, dict)
        assert "value" in result
        assert "is_mock" in result
        assert result["is_mock"] is True
        assert isinstance(result["value"], str)

    def test_publish_event_returns_dict_with_is_mock_false_on_redis(self) -> None:
        """When connected to Redis, publish_event returns is_mock=False."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.xadd.return_value = "1234567890-0"

        with patch("redis.Redis", return_value=mock_client):
            bus = RedisBus(host="localhost", port=6379)

        result = bus.publish_event("test-stream", {"key": "value"})

        assert isinstance(result, dict)
        assert "value" in result
        assert "is_mock" in result
        assert result["is_mock"] is False
        assert result["value"] == "1234567890-0"

    def test_record_trace_returns_dict_with_is_mock_on_fallback(self) -> None:
        """When using in-memory fallback, record_trace returns is_mock=True."""
        with patch("redis.Redis.ping", side_effect=ConnectionError("Connection refused")):
            bus = RedisBus(host="localhost", port=6379)

        trace = TraceRecord(
            trace_id="trace-001",
            subtask_id="task-001",
            prompt="test prompt",
            completion="test completion",
            verdict="PASSED",
            energy=0.5,
        )
        result = bus.record_trace(trace)

        assert isinstance(result, dict)
        assert "value" in result
        assert "is_mock" in result
        assert result["is_mock"] is True
        assert result["value"] == "trace-001"

    def test_set_with_ttl_returns_dict_with_is_mock_on_fallback(self) -> None:
        """When using in-memory fallback, set_with_ttl returns is_mock=True."""
        with patch("redis.Redis.ping", side_effect=OSError("Socket error")):
            bus = RedisBus(host="localhost", port=6379)

        result = bus.set_with_ttl("test-key", "test-value", ttl_seconds=3600)

        assert isinstance(result, dict)
        assert "value" in result
        assert "is_mock" in result
        assert result["is_mock"] is True
        assert result["value"] is True

    def test_trim_stream_returns_dict_with_is_mock_on_fallback(self) -> None:
        """When using in-memory fallback, trim_stream returns is_mock=True."""
        with patch("redis.Redis.ping", side_effect=TimeoutError("Timeout")):
            bus = RedisBus(host="localhost", port=6379)

        # Add some events first
        for i in range(5):
            bus.publish_event("test-stream", {"msg": f"msg-{i}"})

        result = bus.trim_stream("test-stream", max_len=2)

        assert isinstance(result, dict)
        assert "value" in result
        assert "is_mock" in result
        assert result["is_mock"] is True
        assert isinstance(result["value"], int)


class TestRedisMemoryStrictMode:
    """Test redis_memory.store_turn() strict mode."""

    def test_store_turn_strict_true_raises_unverified_data_error(self) -> None:
        """With strict=True and no connection, store_turn raises UnverifiedDataError."""
        # Patch _connect to prevent any actual connection attempt
        with patch.object(RedisLongTermMemory, "_connect"):
            memory = RedisLongTermMemory(host="localhost", port=6379)
            memory._client = None  # Simulate failed connection

        turn = ConversationTurn(
            step_index=1,
            role="user",
            content="test message",
        )

        with pytest.raises(UnverifiedDataError):
            memory.store_turn("conv-001", turn, strict=True)

    def test_store_turn_strict_false_returns_false_on_no_connection(self) -> None:
        """With strict=False and no connection, store_turn returns False."""
        with patch.object(RedisLongTermMemory, "_connect"):
            memory = RedisLongTermMemory(host="localhost", port=6379)
            memory._client = None  # Simulate failed connection

        turn = ConversationTurn(
            step_index=1,
            role="user",
            content="test message",
        )

        result = memory.store_turn("conv-001", turn, strict=False)
        assert result is False

    def test_store_turn_strict_false_logs_error_on_no_connection(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """With strict=False and no connection, logs at ERROR level."""
        with patch.object(RedisLongTermMemory, "_connect"):
            with caplog.at_level(logging.ERROR):
                memory = RedisLongTermMemory(host="localhost", port=6379)
                memory._client = None

                turn = ConversationTurn(
                    step_index=1,
                    role="user",
                    content="test message",
                )
                memory.store_turn("conv-001", turn, strict=False)

        error_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(error_records) > 0, "No ERROR level logs found"

        # Assert conversation ID is in the error message
        error_messages = [r.message for r in error_records]
        assert any("conv-001" in msg for msg in error_messages), f"Conversation ID not in error messages: {error_messages}"

    def test_store_turn_strict_true_logs_error_before_raising(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """With strict=True and no connection, logs at ERROR level before raising."""
        with patch.object(RedisLongTermMemory, "_connect"):
            with caplog.at_level(logging.ERROR):
                memory = RedisLongTermMemory(host="localhost", port=6379)
                memory._client = None

                turn = ConversationTurn(
                    step_index=1,
                    role="user",
                    content="test message",
                )

                with pytest.raises(UnverifiedDataError):
                    memory.store_turn("conv-002", turn, strict=True)

        error_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(error_records) > 0, "No ERROR level logs found"

        # Assert conversation ID is in the error message
        error_messages = [r.message for r in error_records]
        assert any("conv-002" in msg for msg in error_messages), f"Conversation ID not in error messages: {error_messages}"

    def test_store_turn_strict_defaults_to_false(self) -> None:
        """store_turn strict parameter defaults to False."""
        with patch.object(RedisLongTermMemory, "_connect"):
            memory = RedisLongTermMemory(host="localhost", port=6379)
            memory._client = None

            turn = ConversationTurn(
                step_index=1,
                role="user",
                content="test message",
            )

            # Should not raise, should return False (default strict=False)
            result = memory.store_turn("conv-001", turn)
            assert result is False


class TestDocstringPersistenceClaims:
    """Test that docstrings accurately qualify persistence claims."""

    def test_redis_bus_docstring_qualifies_persistence(self) -> None:
        """redis_bus module docstring should qualify persistence claims."""
        with open("/home/callensxavier_gmail_com/AutoevolveAI/antigravity-harness/storage/redis_bus.py") as f:
            content = f.read()

        # Find the module-level docstring (between the first triple quotes)
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        assert match, "Could not find module docstring in redis_bus.py"

        docstring = match.group(1)

        # Should mention "persistence" or "persistent"
        assert re.search(r"persistence|persistent", docstring, re.IGNORECASE), \
            "redis_bus docstring should mention persistence"

        # Should qualify it (contain words like "when", "available", "connected", "only", "fallback", "volatile")
        qualifier_pattern = r"(when\s+|only\s+|available|connected|fallback|volatile)"
        assert re.search(qualifier_pattern, docstring, re.IGNORECASE), \
            "redis_bus docstring should qualify persistence claim within 200 chars"

    def test_redis_memory_docstring_qualifies_persistence(self) -> None:
        """redis_memory module docstring should qualify persistence claims."""
        with open("/home/callensxavier_gmail_com/AutoevolveAI/anse/memory/redis_memory.py") as f:
            content = f.read()

        # Find the module-level docstring
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        assert match, "Could not find module docstring in redis_memory.py"

        docstring = match.group(1)

        # Should mention "persistence" or "persistent"
        assert re.search(r"persistence|persistent", docstring, re.IGNORECASE), \
            "redis_memory docstring should mention persistence"

        # Should qualify it (contain words that limit the claim)
        qualifier_pattern = r"(when\s+|only\s+|available|connected|fallback|volatile)"
        assert re.search(qualifier_pattern, docstring, re.IGNORECASE), \
            "redis_memory docstring should qualify persistence claim"

    def test_redis_bus_class_docstring_qualifies_persistence(self) -> None:
        """RedisBus class docstring should qualify persistence claims."""
        with open("/home/callensxavier_gmail_com/AutoevolveAI/antigravity-harness/storage/redis_bus.py") as f:
            content = f.read()

        # Find RedisBus class docstring
        match = re.search(
            r'class RedisBus:.*?"""(.*?)"""',
            content,
            re.DOTALL
        )
        assert match, "Could not find RedisBus class docstring"

        docstring = match.group(1)

        # Should mention fallback behavior (looks for "fall" prefix for "fallback", "falls back", etc.)
        assert re.search(r"fall|in-memory|volatile|is_mock|InMemoryBusBackend", docstring, re.IGNORECASE), \
            "RedisBus class docstring should mention fallback or in-memory behavior"

    def test_redis_memory_class_docstring_qualifies_persistence(self) -> None:
        """RedisLongTermMemory class docstring should qualify persistence claims."""
        with open("/home/callensxavier_gmail_com/AutoevolveAI/anse/memory/redis_memory.py") as f:
            content = f.read()

        # Find RedisLongTermMemory class docstring
        match = re.search(
            r'class RedisLongTermMemory:.*?"""(.*?)"""',
            content,
            re.DOTALL
        )
        assert match, "Could not find RedisLongTermMemory class docstring"

        docstring = match.group(1)

        # Should clarify that persistence is conditional on connection
        assert re.search(r"when\s+connected|when\s+available|unavailable|fallback", docstring, re.IGNORECASE), \
            "RedisLongTermMemory class docstring should clarify when persistence happens"


class TestRedisMemoryConnectErrorLogging:
    """Test that _connect logs at ERROR level when connection fails."""

    def test_connect_logs_error_with_host_and_port(self, caplog: pytest.LogCaptureFixture) -> None:
        """_connect should log at ERROR level with host and port when connection fails."""
        with caplog.at_level(logging.ERROR):
            with patch("redis.Redis") as mock_redis:
                mock_redis.return_value.ping.side_effect = ConnectionError("Connection refused")

                memory = RedisLongTermMemory(host="redis.example.com", port=6380)

        error_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(error_records) > 0, "No ERROR level logs found for connection failure"

        error_messages = [r.message for r in error_records]
        # Assert host and port are in error message
        assert any("redis.example.com" in msg and "6380" in msg for msg in error_messages), \
            f"Host and port not found in error messages: {error_messages}"
