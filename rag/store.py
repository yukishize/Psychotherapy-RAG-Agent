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
        self._embedding_matrix: Optional[np.ndarray] = None
        self._normalized_matrix: Optional[np.ndarray] = None

    def add(self, doc: Document) -> None:
        self.documents.append(doc)
        # 文档变化后使缓存失效，避免使用旧矩阵
        self._embedding_matrix = None
        self._normalized_matrix = None

    def embedding_matrix(self) -> Optional[np.ndarray]:
        if self._embedding_matrix is not None:
            return self._embedding_matrix
        if not self.documents:
            return None
        if any(d.embedding is None for d in self.documents):
            return None
        self._embedding_matrix = np.vstack([d.embedding for d in self.documents]).astype("float32")
        return self._embedding_matrix

    def normalized_embedding_matrix(self) -> Optional[np.ndarray]:
        """返回按行归一化后的向量矩阵，并缓存结果。

        每轮检索会调用多次，归一化结果复用后可以省去重复的 np.linalg.norm。
        """
        if self._normalized_matrix is not None:
            return self._normalized_matrix
        mat = self.embedding_matrix()
        if mat is None:
            return None
        norms = np.linalg.norm(mat, axis=-1, keepdims=True)
        self._normalized_matrix = mat / np.clip(norms, 1e-9, None)
        return self._normalized_matrix

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
