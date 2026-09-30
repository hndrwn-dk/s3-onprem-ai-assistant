# conversation.py - Sliding-window chat memory

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from config import CHAT_MEMORY_TURNS, RECENT_QUESTIONS_FILE


@dataclass
class ChatMessage:
    role: str
    content: str
    source: str = ""
    citations: list = field(default_factory=list)
    follow_ups: list = field(default_factory=list)


class ConversationMemory:
    """Keep the last N user/assistant turns for grounding later questions."""

    def __init__(self, max_turns: int = CHAT_MEMORY_TURNS):
        self.max_turns = max(1, int(max_turns))
        self.messages: List[ChatMessage] = []

    def add_user(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))
        self._trim()

    def add_assistant(
        self,
        content: str,
        source: str = "",
        citations: Optional[list] = None,
        follow_ups: Optional[list] = None,
    ) -> None:
        self.messages.append(
            ChatMessage(
                role="assistant",
                content=content,
                source=source,
                citations=citations or [],
                follow_ups=follow_ups or [],
            )
        )
        self._trim()

    def _trim(self) -> None:
        # max_turns is user+assistant pairs; keep 2 * max_turns messages
        limit = self.max_turns * 2
        if len(self.messages) > limit:
            self.messages = self.messages[-limit:]

    def history_text(self, exclude_last_user: bool = True) -> str:
        items = self.messages
        if exclude_last_user and items and items[-1].role == "user":
            items = items[:-1]
        if not items:
            return "(none)"
        lines = []
        for msg in items:
            label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{label}: {msg.content}")
        return "\n".join(lines)

    def has_history(self) -> bool:
        return any(m.role == "user" for m in self.messages)

    def persist(self, path: str = RECENT_QUESTIONS_FILE) -> None:
        questions = [m.content for m in self.messages if m.role == "user"]
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(questions[-20:]))
        except OSError:
            pass

    def load_questions(self, path: str = RECENT_QUESTIONS_FILE) -> List[str]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return [line.strip() for line in handle if line.strip()]
        except OSError:
            return []

    def to_dicts(self) -> List[dict]:
        return [asdict(m) for m in self.messages]

    @classmethod
    def from_dicts(
        cls, payload: Optional[List[dict]], max_turns: int = CHAT_MEMORY_TURNS
    ) -> "ConversationMemory":
        memory = cls(max_turns=max_turns)
        for item in payload or []:
            memory.messages.append(
                ChatMessage(
                    role=item.get("role", "user"),
                    content=item.get("content", ""),
                    source=item.get("source", ""),
                    citations=item.get("citations") or [],
                    follow_ups=item.get("follow_ups") or [],
                )
            )
        memory._trim()
        return memory
