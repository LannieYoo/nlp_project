"""
Cross-Encoder Reranker: Quality-based relevance scoring.
Uses a Cross-Encoder model to compute true relevance between (query, document) pairs.

This supplements the rank-based RRF scoring with actual quality scores.
"""

from typing import List, Optional
from functools import lru_cache


class CrossEncoderReranker:
    """
    Reranks retrieval results using a Cross-Encoder model.
    
    Unlike Bi-Encoders (all-MiniLM-L6-v2) which encode query and document
    independently, Cross-Encoders process the (query, document) pair together,
    producing more accurate relevance scores at the cost of speed.
    
    Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (~80MB, CPU-friendly)
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self):
        self._model = None

    @property
    def model(self):
        """Lazy-load the Cross-Encoder model."""
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.MODEL_NAME)
        return self._model

    def rerank(self, query: str, chunks: List[dict],
               score_key: str = "quality_score") -> List[dict]:
        """
        Add quality scores to chunks without changing their order.
        
        The existing rank-based scores and ordering are PRESERVED.
        A new 'quality_score' field is added to each chunk.
        
        Args:
            query: The user's question.
            chunks: List of retrieved chunks (will NOT be reordered).
            score_key: Key name for the quality score field.
            
        Returns:
            Same chunks list with added quality_score field (0~1 range).
        """
        if not chunks or not query.strip():
            for c in chunks:
                c[score_key] = 0.0
            return chunks

        # Build (query, document) pairs — use text_preview for sources
        pairs = []
        for c in chunks:
            text = c.get("text", c.get("text_preview", ""))
            pairs.append((query, text if text else ""))

        # Get raw scores from Cross-Encoder (logits, not bounded)
        raw_scores = self.model.predict(pairs)

        # Min-max normalize within this batch to get 0~1 spread
        # This shows relative quality differences between results
        scores_list = [float(s) for s in raw_scores]
        min_s = min(scores_list)
        max_s = max(scores_list)
        score_range = max_s - min_s if max_s != min_s else 1.0

        for i, c in enumerate(chunks):
            c[score_key] = round((scores_list[i] - min_s) / score_range, 4)

        return chunks
