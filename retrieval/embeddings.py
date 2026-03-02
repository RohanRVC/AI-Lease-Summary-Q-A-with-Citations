from typing import List

from config import EMBEDDING_MODEL

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = _get_embedder()
    return model.encode(texts, convert_to_numpy=True).tolist()
