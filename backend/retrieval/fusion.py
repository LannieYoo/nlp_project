"""
Reciprocal Rank Fusion (RRF): Combines results from all four retrieval methods
into a single ranked list.

RRF_score(d) = SUM( 1 / (k + rank_i(d)) ) for each method i

This method is simple, parameter-free (except k), and works well for
combining results from heterogeneous retrieval systems.
"""

from typing import List, Dict, Optional
from collections import defaultdict


class RRFFusion:
    """Reciprocal Rank Fusion for combining multiple retrieval results."""

    # Weights for each method — higher = more influence on ranking
    METHOD_WEIGHTS = {
        "fts_bm25": 2.0,       # keyword match is strong signal
        "vector_semantic": 2.0, # semantic similarity is strong signal
        "tree_search": 1.0,     # TOC-based, supplementary
        "metadata_filter": 1.0, # structured filter, supplementary
    }

    def __init__(self, k: int = 60):
        """
        Args:
            k: RRF constant. Higher k reduces the influence of high-rank items.
               Standard value is 60 (from Cormack et al., 2009).
        """
        self.k = k

    def fuse(self, result_lists: List[List[dict]], top_k: int = 10) -> List[dict]:
        """
        Fuse multiple ranked lists using weighted RRF.

        Args:
            result_lists: List of result lists from different methods.
                Each result must have 'chunk_id' and optionally other fields.
            top_k: Number of results to return.

        Returns:
            Combined ranked list with RRF scores.
        """
        # Accumulate weighted RRF scores per chunk_id
        scores: Dict[str, float] = defaultdict(float)
        chunk_data: Dict[str, dict] = {}
        method_ranks: Dict[str, Dict[str, int]] = defaultdict(dict)

        for method_idx, results in enumerate(result_lists):
            method_name = results[0].get("method", f"method_{method_idx}") if results else ""
            weight = self.METHOD_WEIGHTS.get(method_name, 1.0)
            for rank, result in enumerate(results):
                chunk_id = result["chunk_id"]
                rrf_score = weight * (1.0 / (self.k + rank + 1))
                scores[chunk_id] += rrf_score

                # Keep the richest metadata
                if chunk_id not in chunk_data:
                    chunk_data[chunk_id] = result.copy()

                method_ranks[chunk_id][method_name] = rank + 1

        # Sort by RRF score descending
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Build final results
        fused = []
        for chunk_id in sorted_ids[:top_k]:
            item = chunk_data[chunk_id].copy()
            item["rrf_score"] = scores[chunk_id]
            item["method_ranks"] = dict(method_ranks[chunk_id])
            item["method"] = "rrf_fusion"
            fused.append(item)

        return fused


class HybridRetriever:
    """
    Orchestrates all four retrieval methods and fuses with RRF.
    Main entry point for the retrieval engine.
    """

    def __init__(self, db_path: str, chroma_dir: str, toc_dir: str, k: int = 60):
        self.db_path = db_path
        self.chroma_dir = chroma_dir
        self.toc_dir = toc_dir
        self.fusion = RRFFusion(k=k)

        # Lazy init searchers
        self._fts = None
        self._vector = None
        self._tree = None
        self._metadata = None

    @property
    def fts_searcher(self):
        if self._fts is None:
            from backend.retrieval.fts_search import FTSSearcher
            self._fts = FTSSearcher(self.db_path)
        return self._fts

    @property
    def vector_searcher(self):
        if self._vector is None:
            from backend.retrieval.vector_search import VectorSearcher
            self._vector = VectorSearcher(self.chroma_dir)
        return self._vector

    @property
    def tree_searcher(self):
        if self._tree is None:
            from backend.retrieval.tree_search import TreeSearcher
            self._tree = TreeSearcher(self.toc_dir, self.db_path)
        return self._tree

    @property
    def metadata_searcher(self):
        if self._metadata is None:
            from backend.retrieval.metadata_search import MetadataSearcher
            self._metadata = MetadataSearcher(self.db_path)
        return self._metadata

    def search(
        self,
        query: str,
        top_k: int = 10,
        book_filter: Optional[str] = None,
        methods: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Run hybrid retrieval with RRF fusion.

        Args:
            query: User's natural language question.
            top_k: Number of final results.
            book_filter: Optional book_id to restrict search.
            methods: List of methods to use. Default: all four.
                Options: 'fts', 'vector', 'tree', 'metadata'
        """
        if methods is None:
            methods = ['fts', 'vector', 'tree', 'metadata']

        per_method_k = top_k * 3  # retrieve more per method, then fuse
        result_lists = []

        if 'fts' in methods:
            try:
                fts_results = self.fts_searcher.search(
                    query, top_k=per_method_k, book_filter=book_filter)
                if fts_results:
                    result_lists.append(fts_results)
            except Exception as e:
                print(f"FTS search error: {e}")

        if 'vector' in methods:
            try:
                vec_results = self.vector_searcher.search(
                    query, top_k=per_method_k, book_filter=book_filter)
                if vec_results:
                    result_lists.append(vec_results)
            except Exception as e:
                print(f"Vector search error: {e}")

        if 'tree' in methods:
            try:
                tree_results = self.tree_searcher.search(
                    query, top_k=per_method_k, book_filter=book_filter)
                if tree_results:
                    result_lists.append(tree_results)
            except Exception as e:
                print(f"Tree search error: {e}")

        if 'metadata' in methods:
            try:
                meta_results = self.metadata_searcher.search(
                    query, top_k=per_method_k, book_filter=book_filter)
                if meta_results:
                    result_lists.append(meta_results)
            except Exception as e:
                print(f"Metadata search error: {e}")

        if not result_lists:
            return []

        # If only one method returned results, skip fusion
        if len(result_lists) == 1:
            return result_lists[0][:top_k]

        fused = self.fusion.fuse(result_lists, top_k=top_k * 2)

        # Post-filter: prioritize results confirmed by multiple methods
        multi_method = [r for r in fused if len(r.get("method_ranks", {})) >= 2]
        single_method = [r for r in fused if len(r.get("method_ranks", {})) < 2]

        # If we have enough multi-method results, use them first
        if len(multi_method) >= top_k:
            return multi_method[:top_k]

        # Otherwise fill with single-method results
        combined = multi_method + single_method
        return combined[:top_k]

    def close(self):
        if self._fts:
            self._fts.close()
