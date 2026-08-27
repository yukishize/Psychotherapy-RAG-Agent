from typing import Iterator, List, Optional

from qengine.models import AssessmentProfile
from rag.embeddings import EmbeddingClient
from rag.store import VectorStore

from .llm import LLMClient
from .memory import ConversationHistory
from .profile import (
    DIM_TAGS,
    NORMAL_LEVELS,
    profile_summary_text,
    profile_to_query,
    severity_from_level,
)
from .prompts import build_system_prompt
from .retriever import KnowledgeRetriever
from .safety import SafetyChecker


class Session:
    def __init__(
        self,
        llm: LLMClient,
        store: Optional[VectorStore],
        embedding_client: Optional[EmbeddingClient],
        profiles: List[AssessmentProfile],
        max_history: int = 16,
        top_k: int = 3,
    ):
        self.llm = llm
        self.store = store
        self.embedding_client = embedding_client
        self.profiles = profiles
        self.max_history = max_history
        self.top_k = top_k
        self.self_harm = any("self_harm_risk" in p.flags for p in profiles)
        self.tags, self.severities = profile_to_query(profiles)
        self.history = ConversationHistory(max_messages=max_history)
        self.retriever = KnowledgeRetriever(
            store, embedding_client, self.tags, self.severities, top_k=top_k
        )
        self.safety = SafetyChecker()

    @property
    def messages(self) -> List[dict]:
        """Backward-compatible read-only view of non-system chat history."""
        return self.history.messages

    def update_profiles(self, profiles: List[AssessmentProfile]) -> None:
        self.profiles = profiles
        self.self_harm = any("self_harm_risk" in p.flags for p in profiles)
        self.tags, self.severities = profile_to_query(profiles)
        self.retriever = KnowledgeRetriever(
            self.store,
            self.embedding_client,
            self.tags,
            self.severities,
            top_k=self.top_k,
        )
        self.history.clear()

    def _stream_and_record(self, stream) -> Iterator[str]:
        """Yield LLM chunks and persist the complete assistant reply in history."""
        if stream is None:
            return
        if isinstance(stream, str):
            if stream:
                self.history.add_assistant(stream)
            yield stream
            return

        parts = []
        try:
            for chunk in stream:
                parts.append(chunk)
                yield chunk
        finally:
            if parts:
                self.history.add_assistant("".join(parts))

    def reply(self, user_text: str) -> Iterator[str]:
        crisis = self.safety.check(user_text) or self.self_harm
        script_text, treatment_text = self.retriever.retrieve(
            user_text, include_treatment=not crisis
        )
        system = build_system_prompt(
            profile_summary_text(self.profiles),
            script_text,
            treatment_text,
            crisis,
        )
        self.history.add_user(user_text)
        try:
            stream = self.llm.chat(self.history.with_system(system))
        except Exception:
            # Don't leave an unanswered user turn behind when the API call fails.
            if self.history.messages and self.history.messages[-1]["role"] == "user":
                self.history.messages.pop()
            raise
        return self._stream_and_record(stream)
