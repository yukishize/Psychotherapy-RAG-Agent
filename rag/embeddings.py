from typing import List, Optional

import numpy as np
from openai import OpenAI


class EmbeddingClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.model = model
        self._client = OpenAI(base_url=base_url or None, api_key=api_key)

    def embed(self, texts: List[str]) -> Optional[np.ndarray]:
        if not texts:
            return None
        resp = self._client.embeddings.create(model=self.model, input=texts)
        return np.array([d.embedding for d in resp.data], dtype="float32")
