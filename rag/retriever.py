from typing import Iterable, List, Optional, Tuple

import numpy as np

from .store import Document, VectorStore


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec, axis=-1, keepdims=True)
    return vec / np.clip(norm, 1e-9, None)


def search(
    store: VectorStore,
    query_embedding: Optional[np.ndarray],
    *,
    target: Optional[str] = None,
    categories: Optional[Iterable[str]] = None,
    tags: Optional[Iterable[str]] = None,
    severities: Optional[Iterable[str]] = None,
    top_k: int = 5,
) -> List[Tuple[Document, float]]:
    if not store.documents:
        return []

    categories = set(categories) if categories else None
    tags = set(tags) if tags else None
    severities = set(severities) if severities else None

    candidates = [
        i
        for i, d in enumerate(store.documents)
        if (target is None or d.target == target)
        and (categories is None or d.category in categories)
        and (tags is None or (set(d.tags) & tags))
        and (severities is None or (set(d.severity) & severities))
    ]
    if not candidates:
        return []

    if query_embedding is None:
        return [(store.documents[i], 0.0) for i in candidates[:top_k]]

    docs_mat = store.normalized_embedding_matrix()
    if docs_mat is None:
        return [(store.documents[i], 0.0) for i in candidates[:top_k]]

    query = _normalize(query_embedding.reshape(1, -1))
    docs_mat = docs_mat[candidates]
    scores = (docs_mat @ query.T).ravel()

    order = np.argsort(-scores)[:top_k]
    return [(store.documents[candidates[i]], float(scores[i])) for i in order]
