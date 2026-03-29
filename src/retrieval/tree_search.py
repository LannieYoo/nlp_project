"""
Tree Search: LLM-guided hierarchical TOC tree navigation.
Method ③ in the 4-method hybrid retrieval architecture.

The LLM reads the TOC outline and selects the most relevant sections,
then retrieves chunks from those sections.
"""

import os
import json
import sqlite3
from typing import List, Optional, Dict

from src.pipeline.toc_builder import TOCBuilder


class TreeSearcher:
    """
    Tree-based retrieval: uses pre-built TOC trees to find relevant sections.
    For now, uses keyword matching on TOC titles (no LLM needed).
    Can be upgraded to LLM-guided navigation later.
    """

    def __init__(self, toc_dir: str, db_path: str):
        self.toc_dir = toc_dir
        self.db_path = db_path
        self._toc_cache: Dict[str, dict] = {}

    def _load_toc(self, book_id: str) -> Optional[dict]:
        """Load TOC tree for a book, with caching."""
        if book_id in self._toc_cache:
            return self._toc_cache[book_id]

        path = os.path.join(self.toc_dir, f"{book_id}_toc.json")
        if not os.path.exists(path):
            return None

        data = TOCBuilder.load_tree(path)
        self._toc_cache[book_id] = data
        return data

    def _load_all_tocs(self) -> Dict[str, dict]:
        """Load all TOC trees."""
        tocs = {}
        if not os.path.exists(self.toc_dir):
            return tocs
        for fname in os.listdir(self.toc_dir):
            if fname.endswith("_toc.json"):
                book_id = fname.replace("_toc.json", "")
                toc = self._load_toc(book_id)
                if toc:
                    tocs[book_id] = toc
        return tocs

    def search(self, query: str, top_k: int = 10,
               book_filter: Optional[str] = None) -> List[dict]:
        """
        Search by matching query keywords against TOC section titles,
        then retrieving chunks from matching sections.
        """
        query_words = set(query.lower().split())

        # Score each TOC node by keyword overlap
        scored_sections = []

        if book_filter:
            toc = self._load_toc(book_filter)
            if toc:
                self._score_nodes(toc.get("toc", []), query_words,
                                  book_filter, scored_sections)
        else:
            all_tocs = self._load_all_tocs()
            for book_id, toc in all_tocs.items():
                self._score_nodes(toc.get("toc", []), query_words,
                                  book_id, scored_sections)

        # Sort by score descending
        scored_sections.sort(key=lambda x: x["score"], reverse=True)

        # Take top sections and retrieve their chunks
        results = []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        for section in scored_sections[:top_k]:
            book_id = section["book_id"]
            page_idx = section["page_idx"]
            title = section["title"]

            # Find chunks near this section's page
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM chunks
                WHERE book_id = ? AND page_idx BETWEEN ? AND ?
                AND content_type != 'heading'
                ORDER BY page_idx, chunk_id
                LIMIT 3
            """, (book_id, page_idx, page_idx + 2))

            for row in cur.fetchall():
                results.append({
                    "chunk_id": row["chunk_id"],
                    "book_id": row["book_id"],
                    "text": row["text"],
                    "page_idx": row["page_idx"],
                    "bbox": [row["bbox_x1"], row["bbox_y1"],
                             row["bbox_x2"], row["bbox_y2"]],
                    "content_type": row["content_type"],
                    "chapter": row["chapter"],
                    "section": title,
                    "score": section["score"],
                    "normalized_score": section["score"],
                    "method": "tree_search",
                })

            if len(results) >= top_k:
                break

        conn.close()
        return results[:top_k]

    def _score_nodes(self, nodes: list, query_words: set,
                     book_id: str, results: list):
        """Recursively score TOC nodes by keyword overlap with query."""
        for node in nodes:
            title_words = set(node.get("title", "").lower().split())
            overlap = len(query_words & title_words)
            if overlap > 0:
                score = overlap / max(len(query_words), 1)
                results.append({
                    "title": node["title"],
                    "page_idx": node.get("page_idx", 0),
                    "book_id": book_id,
                    "score": score,
                })
            # Recurse into children
            self._score_nodes(node.get("children", []), query_words,
                              book_id, results)

    def get_book_outline(self, book_id: str) -> str:
        """Get the TOC outline for a book (for LLM consumption)."""
        toc = self._load_toc(book_id)
        if not toc:
            return f"No TOC available for {book_id}"
        return TOCBuilder.tree_to_outline(toc)
