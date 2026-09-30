# tests/test_conversation.py

from conversation import ConversationMemory


def test_trim_keeps_last_pairs():
    memory = ConversationMemory(max_turns=2)
    memory.add_user("q1")
    memory.add_assistant("a1")
    memory.add_user("q2")
    memory.add_assistant("a2")
    memory.add_user("q3")
    memory.add_assistant("a3")
    contents = [m.content for m in memory.messages]
    assert "q1" not in contents
    assert "q2" in contents
    assert "q3" in contents


def test_roundtrip_dicts():
    memory = ConversationMemory()
    memory.add_user("list buckets")
    memory.add_assistant("here they are", source="hybrid", follow_ups=["next?"])
    restored = ConversationMemory.from_dicts(memory.to_dicts())
    assert restored.messages[0].content == "list buckets"
    assert restored.messages[1].source == "hybrid"
    assert restored.messages[1].follow_ups == ["next?"]
