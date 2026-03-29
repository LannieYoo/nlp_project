"""
Metadata Search: Structured filtering by book, chapter, page, content type.
Method ④ in the 4-method hybrid retrieval architecture.
"""

import sqlite3
from typing import List, Optional


class MetadataSearcher:
    """Structured search by metadata fields."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def search(
        self,
        query: str = "",
        top_k: int = 10,
        book_filter: Optional[str] = None,
        chapter_filter: Optional[str] = None,
        content_type_filter: Optional[str] = None,
        page_range: Optional[tuple] = None,
    ) -> List[dict]:
        """
        Filter chunks by metadata fields.
        Optionally also does simple text LIKE matching on query.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        conditions = []
        params = []

        if book_filter:
            conditions.append("book_id = ?")
            params.append(book_filter)

        if chapter_filter:
            conditions.append("chapter LIKE ?")
            params.append(f"%{chapter_filter}%")

        if content_type_filter:
            conditions.append("content_type = ?")
            params.append(content_type_filter)

        if page_range:
            conditions.append("page_idx BETWEEN ? AND ?")
            params.extend(page_range)

        if query:
            conditions.append("text LIKE ?")
            params.append(f"%{query}%")

        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT * FROM chunks
            WHERE {where} AND content_type != 'heading'
            ORDER BY book_id, page_idx
            LIMIT ?
        """
        params.append(top_k)

        cur = conn.cursor()
        cur.execute(sql, params)

        results = []
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
                "section": row["section"],
                "score": 0.5,  # fixed score for metadata matches
                "normalized_score": 0.5,
                "method": "metadata_filter",
            })

        conn.close()
        return results

    def get_books(self) -> List[dict]:
        """List all books."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM books ORDER BY book_id")
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        return results

    def get_chapters(self, book_id: str) -> List[str]:
        """List unique chapters for a book."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT chapter FROM chunks
            WHERE book_id = ? AND chapter != ''
            ORDER BY MIN(page_idx)
        """, (book_id,))
        results = [row[0] for row in cur.fetchall()]
        conn.close()
        return results
