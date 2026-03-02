from typing import List

from config import TOP_K_RETRIEVAL
from .store import VectorStore

    #     Retrieve relevant chunks for a query from the vector store.....   
def retrieve_context(store: VectorStore, query: str, top_k: int | None = None) -> List[dict]:
   
    if top_k is None:
        top_k = TOP_K_RETRIEVAL
    return store.search(query, top_k=top_k)
