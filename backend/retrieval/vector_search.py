"""
Vector Search: ChromaDB semantic retrieval using sentence-transformer embeddings.
Method ② in the 4-method hybrid retrieval architecture.
"""

from typing import List, Optional
from backend.pipeline.indexer import ChromaIndexer


class VectorSearcher:
    """Semantic search using ChromaDB + sentence-transformers."""

    def __init__(self, chroma_dir: str):
        self.indexer = ChromaIndexer(chroma_dir)

    def search(self, query: str, top_k: int = 10,
               book_filter: Optional[str] = None) -> List[dict]:
        """
        Semantic search using cosine similarity.
        Returns list of {chunk_id, text, book_id, page_idx, bbox, score, ...}
        """
        results = self.indexer.search(query, top_k=top_k,
                                       book_filter=book_filter)
        for r in results:
            r["normalized_score"] = r.get("score", 0)
            r["method"] = "vector_semantic"

        return results
