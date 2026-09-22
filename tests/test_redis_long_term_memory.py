"""
Unit tests for Redis Long-Term Memory Hub.
"""

from __future__ import annotations

import time

from anse.memory.redis_memory import ConversationTurn, RedisLongTermMemory


def test_redis_long_term_memory_turn_storage() -> None:
    mem = RedisLongTermMemory()
    if not mem.is_connected:
        return

    test_cid = f"test-conv-{int(time.time())}"
    turn1 = ConversationTurn(
        step_index=0,
        role="user",
        content="Test user prompt for long-term memory",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    turn2 = ConversationTurn(
        step_index=1,
        role="assistant",
        content="Test assistant response",
        thinking="Pondering solution...",
        tool_calls=[{"name": "view_file", "path": "foo.py"}],
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    ok1 = mem.store_turn(test_cid, turn1, publish_stream=True)
    ok2 = mem.store_turn(test_cid, turn2, publish_stream=True)

    assert ok1 is True
    assert ok2 is True

    # Retrieve and verify
    turns = mem.get_conversation_turns(test_cid)
    assert len(turns) == 2
    assert turns[0].role == "user"
    assert turns[0].content == "Test user prompt for long-term memory"
    assert turns[1].role == "assistant"
    assert turns[1].thinking == "Pondering solution..."
    assert turns[1].tool_calls == [{"name": "view_file", "path": "foo.py"}]

    meta = mem.get_conversation_metadata(test_cid)
    assert int(meta.get("total_turns", 0)) == 2
    assert int(meta.get("user_turns", 0)) == 1
    assert int(meta.get("assistant_turns", 0)) == 1

    # Cleanup test key
    if mem._client:
        mem._client.delete(f"antigravity:conversation:{test_cid}:turns")
        mem._client.delete(f"antigravity:conversation:{test_cid}:meta")
        mem._client.srem("antigravity:conversations:all", test_cid)


def test_redis_full_conversation_batch_storage() -> None:
    mem = RedisLongTermMemory()
    if not mem.is_connected:
        return

    test_cid = f"test-batch-{int(time.time())}"
    turns = [
        ConversationTurn(step_index=i, role="user" if i % 2 == 0 else "assistant", content=f"Step {i}")
        for i in range(5)
    ]

    count = mem.store_full_conversation(test_cid, turns, metadata={"tag": "unit-test"})
    assert count == 5

    retrieved = mem.get_conversation_turns(test_cid)
    assert len(retrieved) == 5
    assert retrieved[4].content == "Step 4"

    meta = mem.get_conversation_metadata(test_cid)
    assert meta.get("tag") == "unit-test"
    assert int(meta.get("total_turns", 0)) == 5

    # Cleanup
    if mem._client:
        mem._client.delete(f"antigravity:conversation:{test_cid}:turns")
        mem._client.delete(f"antigravity:conversation:{test_cid}:meta")
        mem._client.delete(f"antigravity:memory:long_term:{test_cid}")
        mem._client.srem("antigravity:conversations:all", test_cid)
