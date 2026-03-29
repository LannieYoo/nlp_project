"""
FTS Search: SQLite FTS5 BM25 keyword-based retrieval.
Method ① in the 4-method hybrid retrieval architecture.
"""

from typing import List, Optional
from backend.pipeline.indexer import SQLiteIndexer


class FTSSearcher:
    """BM25 keyword search using SQLite FTS5."""

    # Common abbreviation -> full form mapping for better search
    ABBREVIATIONS = {
        "svm": "support vector machine",
        "svd": "singular value decomposition",
        "pca": "principal component analysis",
        "rnn": "recurrent neural network",
        "cnn": "convolutional neural network",
        "lstm": "long short term memory",
        "gru": "gated recurrent unit",
        "gan": "generative adversarial network",
        "vae": "variational autoencoder",
        "bert": "bidirectional encoder representations from transformers",
        "gpt": "generative pre trained transformer",
        "nlp": "natural language processing",
        "rl": "reinforcement learning",
        "hmm": "hidden markov model",
        "em": "expectation maximization",
        "knn": "k nearest neighbor",
        "mle": "maximum likelihood estimation",
        "map": "maximum a posteriori",
        "sgd": "stochastic gradient descent",
        "adam": "adaptive moment estimation",
        "relu": "rectified linear unit",
        "bpe": "byte pair encoding",
        "tfidf": "term frequency inverse document frequency",
    }

    def __init__(self, db_path: str):
        self.indexer = SQLiteIndexer(db_path)

    def search(self, query: str, top_k: int = 10,
               book_filter: Optional[str] = None) -> List[dict]:
        """
        Search using BM25.
        Returns list of {chunk_id, text, book_id, page_idx, bbox, score, ...}
        """
        # Build enhanced query with abbreviation expansion
        safe_query = self._build_fts_query(query)
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

    def _build_fts_query(self, query: str) -> str:
        """
        Build an FTS5 query with abbreviation expansion and phrase matching.
        e.g. "What is SVM?" -> 'SVM OR "support vector machine"'
        """
        # First sanitize
        clean = self._sanitize_query(query)
        if not clean:
            return ""

        words = clean.lower().split()
        query_parts = []
        expanded = set()

        for word in words:
            # Skip common stop words
            if word in {"what", "is", "the", "a", "an", "of", "in", "for",
                        "how", "does", "do", "are", "was", "were", "been",
                        "be", "to", "and", "or", "it", "this", "that"}:
                continue

            query_parts.append(word)

            # Expand abbreviations
            if word in self.ABBREVIATIONS:
                full_form = self.ABBREVIATIONS[word]
                expanded.add(f'"{full_form}"')

        if not query_parts:
            return clean

        # Build: original terms + expanded phrase forms
        base = " ".join(query_parts)
        if expanded:
            # Use OR to include expanded forms
            return f'{base} OR {" OR ".join(expanded)}'
        return base

    @staticmethod
    def _sanitize_query(query: str) -> str:
        """Remove FTS5 special syntax characters for safe query."""
        # Remove operators that could cause FTS5 syntax errors
        special = ["'", '*', '-', '+', '(', ')', '{', '}', '^', '~', ':']
        clean = query
        for ch in special:
            clean = clean.replace(ch, ' ')
        # Remove extra spaces
        clean = ' '.join(clean.split())
        return clean.strip()

    def close(self):
        self.indexer.close()
