from collections import OrderedDict
from typing import Optional, Tuple

from rag.embeddings import EmbeddingClient
from rag.retriever import search
from rag.store import VectorStore


class _EmbeddingCache:
    """极简 LRU 缓存：同一句话在短时间内不需要重复调用 embedding API。"""

    def __init__(self, maxsize: int = 256):
        self.maxsize = maxsize
        self._data: OrderedDict[str, object] = OrderedDict()

    def get(self, key: str):
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: str, value) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.maxsize:
            self._data.popitem(last=False)


class KnowledgeRetriever:
    """Encapsulate RAG retrieval for agent scripts and user-facing treatments."""

    def __init__(
        self,
        store: Optional[VectorStore],
        embedding_client: Optional[EmbeddingClient],
        tags,
        severities,
        top_k: int = 3,
    ):
        self.store = store
        self.embedding_client = embedding_client
        self.tags = tags
        self.severities = severities
        self.top_k = top_k
        self._embedding_cache = _EmbeddingCache()

    def _embed_query(self, user_text: str):
        cached = self._embedding_cache.get(user_text)
        if cached is not None:
            return cached
        emb = self.embedding_client.embed([user_text])[0]
        self._embedding_cache.put(user_text, emb)
        return emb

    def retrieve(self, user_text: str, *, include_treatment: bool = True) -> Tuple[str, str]:
        """Return (script_text, treatment_text) retrieved for the current turn."""
        if not self.store or not self.store.documents:
            return "", ""

        query_emb = None
        if self.embedding_client is not None:
            try:
                query_emb = self._embed_query(user_text)
            except Exception:
                query_emb = None

        kwargs = {"tags": self.tags, "severities": self.severities}
        scripts = search(self.store, query_emb, target="agent", top_k=self.top_k, **kwargs)
        script_text = "\n\n".join(d.text for d, _ in scripts)

        treatment_text = ""
        if include_treatment:
            treats = search(self.store, query_emb, target="user", top_k=self.top_k, **kwargs)
            treatment_text = "\n\n".join(d.text for d, _ in treats)

        return script_text, treatment_text
