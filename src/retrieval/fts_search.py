"""
FTS Search: SQLite FTS5 BM25 keyword-based retrieval.
Method ① in the 4-method hybrid retrieval architecture.
"""

from typing import List, Optional
from src.pipeline.indexer import SQLiteIndexer


class FTSSearcher:
    """BM25 keyword search using SQLite FTS5."""

    def __init__(self, db_path: str):
        self.indexer = SQLiteIndexer(db_path)

    def search(self, query: str, top_k: int = 10,
               book_filter: Optional[str] = None) -> List[dict]:
        """
        Search using BM25.
        Returns list of {chunk_id, text, book_id, page_idx, bbox, score, ...}
        """
        # Escape FTS5 special characters
        safe_query = self._sanitize_query(query)
        if not safe_query:
            return []

        results = self.indexer.search_fts(safe_query, top_k=top_k,
                                          book_filter=book_filter)

        # Normalize scores: BM25 returns negative values (lower = better)
        # Convert to positive scores where higher = better
        if results:
            min_score = min(r["score"] for r in results)
            max_score = max(r["score"] for r in results)
            score_range = max_score - min_score if max_score != min_score else 1
            for r in results:
                r["normalized_score"] = 1 - (r["score"] - min_score) / score_range
                r["method"] = "fts_bm25"

        return results

    @staticmethod
    def _sanitize_query(query: str) -> str:
        """Remove FTS5 special syntax characters for safe query."""
        # Remove operators that could cause FTS5 syntax errors
        special = ['"', "'", '*', '-', '+', '(', ')', '{', '}', '^', '~', ':']
        clean = query
        for ch in special:
            clean = clean.replace(ch, ' ')
        # Remove extra spaces
        clean = ' '.join(clean.split())
        return clean.strip()

    def close(self):
        self.indexer.close()
