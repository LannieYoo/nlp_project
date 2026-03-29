"""
Indexer module: Dual indexing — SQLite FTS5 (BM25) + ChromaDB (semantic vectors).
Stores chunks with full metadata for retrieval and source tracing.
"""

import os
import sqlite3
from typing import List, Optional

from src.pipeline.chunker import Chunk


# ---------------------------------------------------------------------------
# SQLite + FTS5 Indexer
# ---------------------------------------------------------------------------

class SQLiteIndexer:
    """
    Stores chunks in SQLite with FTS5 virtual table for BM25 full-text search.
    Main table holds chunk data + metadata; FTS5 table mirrors text for search.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        # Main chunks table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id    TEXT PRIMARY KEY,
                book_id     TEXT NOT NULL,
                text        TEXT NOT NULL,
                page_idx    INTEGER NOT NULL,
                bbox_x1     INTEGER,
                bbox_y1     INTEGER,
                bbox_x2     INTEGER,
                bbox_y2     INTEGER,
                content_type TEXT,
                chapter     TEXT,
                section     TEXT,
                text_level  INTEGER
            )
        """)
        # FTS5 virtual table for full-text search with BM25
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(
                chunk_id,
                text,
                book_id,
                chapter,
                section,
                content='chunks',
                content_rowid='rowid'
            )
        """)
        # Triggers to keep FTS in sync
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, chunk_id, text, book_id, chapter, section)
                VALUES (new.rowid, new.chunk_id, new.text, new.book_id, new.chapter, new.section);
            END
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, text, book_id, chapter, section)
                VALUES ('delete', old.rowid, old.chunk_id, old.text, old.book_id, old.chapter, old.section);
            END
        """)
        # Books metadata table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id     TEXT PRIMARY KEY,
                title       TEXT,
                pdf_path    TEXT,
                total_chunks INTEGER DEFAULT 0,
                total_pages  INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def insert_chunks(self, chunks: List[Chunk]):
        """Insert a batch of chunks into SQLite + FTS5."""
        cur = self.conn.cursor()
        for chunk in chunks:
            try:
                cur.execute("""
                    INSERT OR REPLACE INTO chunks
                    (chunk_id, book_id, text, page_idx, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                     content_type, chapter, section, text_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.book_id, chunk.text, chunk.page_idx,
                    chunk.bbox[0], chunk.bbox[1], chunk.bbox[2], chunk.bbox[3],
                    chunk.content_type, chunk.chapter, chunk.section, chunk.text_level,
                ))
            except sqlite3.IntegrityError:
                pass  # skip duplicates
        self.conn.commit()

    def register_book(self, book_id: str, title: str = "", pdf_path: str = "",
                      total_chunks: int = 0, total_pages: int = 0):
        """Register a book in the books metadata table."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO books (book_id, title, pdf_path, total_chunks, total_pages)
            VALUES (?, ?, ?, ?, ?)
        """, (book_id, title or book_id, pdf_path, total_chunks, total_pages))
        self.conn.commit()

    def search_fts(self, query: str, top_k: int = 10,
                   book_filter: Optional[str] = None) -> List[dict]:
        """
        Full-text search using FTS5 BM25 ranking.
        Returns list of dicts with chunk data + bm25 score.
        """
        cur = self.conn.cursor()
        if book_filter:
            cur.execute("""
                SELECT c.*, bm25(chunks_fts) AS score
                FROM chunks_fts f
                JOIN chunks c ON c.chunk_id = f.chunk_id
                WHERE chunks_fts MATCH ?
                AND c.book_id = ?
                ORDER BY bm25(chunks_fts)
                LIMIT ?
            """, (query, book_filter, top_k))
        else:
            cur.execute("""
                SELECT c.*, bm25(chunks_fts) AS score
                FROM chunks_fts f
                JOIN chunks c ON c.chunk_id = f.chunk_id
                WHERE chunks_fts MATCH ?
                ORDER BY bm25(chunks_fts)
                LIMIT ?
            """, (query, top_k))

        results = []
        for row in cur.fetchall():
            results.append({
                "chunk_id": row["chunk_id"],
                "book_id": row["book_id"],
                "text": row["text"],
                "page_idx": row["page_idx"],
                "bbox": [row["bbox_x1"], row["bbox_y1"], row["bbox_x2"], row["bbox_y2"]],
                "content_type": row["content_type"],
                "chapter": row["chapter"],
                "section": row["section"],
                "score": row["score"],
            })
        return results

    def get_chunk(self, chunk_id: str) -> Optional[dict]:
        """Get a single chunk by ID."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

    def get_book_list(self) -> List[dict]:
        """Return list of all registered books."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM books ORDER BY book_id")
        return [dict(row) for row in cur.fetchall()]

    def get_stats(self) -> dict:
        """Return database statistics."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT book_id) FROM chunks")
        total_books = cur.fetchone()[0]
        return {"total_chunks": total_chunks, "total_books": total_books}

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# ChromaDB Vector Indexer
# ---------------------------------------------------------------------------

class ChromaIndexer:
    """
    Stores chunk embeddings in ChromaDB for semantic (vector) search.
    Uses sentence-transformers all-MiniLM-L6-v2 for embedding.
    """

    COLLECTION_NAME = "textbook_chunks"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    BATCH_SIZE = 256  # ChromaDB batch limit

    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self._client = None
        self._collection = None
        self._embedding_fn = None

    @property
    def client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    @property
    def embedding_fn(self):
        if self._embedding_fn is None:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            self._embedding_fn = SentenceTransformerEmbeddingFunction(
                model_name=self.EMBEDDING_MODEL
            )
        return self._embedding_fn

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def insert_chunks(self, chunks: List[Chunk]):
        """Insert chunks into ChromaDB in batches."""
        for i in range(0, len(chunks), self.BATCH_SIZE):
            batch = chunks[i : i + self.BATCH_SIZE]
            ids = [c.chunk_id for c in batch]
            documents = [c.text for c in batch]
            metadatas = [
                {
                    "book_id": c.book_id,
                    "page_idx": c.page_idx,
                    "bbox": str(c.bbox),
                    "content_type": c.content_type,
                    "chapter": c.chapter,
                    "section": c.section,
                }
                for c in batch
            ]
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

    def search(self, query: str, top_k: int = 10,
               book_filter: Optional[str] = None) -> List[dict]:
        """Semantic search using vector similarity."""
        where_filter = None
        if book_filter:
            where_filter = {"book_id": book_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        items = []
        if results and results["ids"]:
            for i, cid in enumerate(results["ids"][0]):
                items.append({
                    "chunk_id": cid,
                    "text": results["documents"][0][i],
                    "book_id": results["metadatas"][0][i].get("book_id", ""),
                    "page_idx": results["metadatas"][0][i].get("page_idx", 0),
                    "bbox": results["metadatas"][0][i].get("bbox", "[0,0,0,0]"),
                    "content_type": results["metadatas"][0][i].get("content_type", "text"),
                    "chapter": results["metadatas"][0][i].get("chapter", ""),
                    "section": results["metadatas"][0][i].get("section", ""),
                    "distance": results["distances"][0][i],
                    "score": 1 - results["distances"][0][i],  # cosine similarity
                })
        return items

    def get_count(self) -> int:
        """Return total number of chunks in the collection."""
        return self.collection.count()
