from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


@dataclass
class Document:
    id: str
    category: str
    target: str
    tags: List[str] = field(default_factory=list)
    severity: List[str] = field(default_factory=list)
    title: str = ""
    text: str = ""
    embedding: Optional[np.ndarray] = None


class VectorStore:
    def __init__(self):
        self.documents: List[Document] = []

    def add(self, doc: Document) -> None:
        self.documents.append(doc)

    def embedding_matrix(self) -> Optional[np.ndarray]:
        if not self.documents:
            return None
        if any(d.embedding is None for d in self.documents):
            return None
        return np.vstack([d.embedding for d in self.documents]).astype("float32")

    def save(self, index_path, npz_path) -> None:
        import json

        meta = {
            "version": 1,
            "documents": [
                {
                    "id": d.id,
                    "category": d.category,
                    "target": d.target,
                    "tags": d.tags,
                    "severity": d.severity,
                    "title": d.title,
                    "text": d.text,
                }
                for d in self.documents
            ],
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        mat = self.embedding_matrix()
        if mat is not None:
            np.savez(npz_path, embeddings=mat)

    @classmethod
    def load(cls, index_path, npz_path) -> "VectorStore":
        import json

        with open(index_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        store = cls()
        mat = None
        try:
            arr = np.load(npz_path)
            mat = arr["embeddings"]
        except Exception:
            mat = None
        for i, m in enumerate(meta["documents"]):
            emb = mat[i] if mat is not None and i < len(mat) else None
            store.add(
                Document(
                    id=m["id"],
                    category=m["category"],
                    target=m["target"],
                    tags=m.get("tags", []),
                    severity=m.get("severity", []),
                    title=m.get("title", ""),
                    text=m.get("text", ""),
                    embedding=emb,
                )
            )
        return store
