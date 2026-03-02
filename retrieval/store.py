from typing import List

import faiss
import numpy as np

from .embeddings import get_embeddings


class VectorStore:

    def __init__(self):
        self.index: faiss.IndexFlatL2 | None = None
        self.metadata: List[dict] = []

    def add_chunks(self, chunks: List[dict]) -> None:
        if not chunks:
            return
        texts = [c["text"] for c in chunks]
        vectors = get_embeddings(texts)
        dim = len(vectors[0])
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        arr = np.array(vectors, dtype=np.float32)
        self.index.add(arr)
        self.metadata.extend(chunks)

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        if self.index is None or not self.metadata:
            return []
        from .embeddings import get_embeddings
        qv = get_embeddings([query])
        distances, indices = self.index.search(np.array(qv, dtype=np.float32), min(top_k, len(self.metadata)))
        result = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx].copy()
            meta["score"] = float(-distances[0][i])  # negative L2 as similarity proxy
            result.append(meta)
        return result

    def clear(self) -> None:
        self.index = None
        self.metadata = []
