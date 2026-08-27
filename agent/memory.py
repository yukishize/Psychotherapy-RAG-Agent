from typing import List


class ConversationHistory:
    """Manage the non-system chat history passed to the LLM.

    System messages are intentionally not stored here because the system
    prompt is rebuilt on every turn with fresh RAG context and safety state.
    """

    def __init__(self, max_messages: int = 16):
        self.max_messages = max_messages
        self.messages: List[dict] = []

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str) -> None:
        if not content:
            return
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def with_system(self, system: str) -> List[dict]:
        """Return a complete LLM message list: system prompt + recent history."""
        return [{"role": "system", "content": system}] + self.messages[-self.max_messages:]

    def clear(self) -> None:
        self.messages.clear()

    def _trim(self) -> None:
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
