"""
Batch Processor: Processes all 46 textbooks through the full pipeline:
  1. Parse content_list.json → Chunks
  2. Index into SQLite FTS5
  3. Index into ChromaDB
  4. Build TOC tree

Supports resuming (skips already-processed books).
"""

import os
import sys
import json
import time
from typing import Optional

from tqdm import tqdm

from src.pipeline.chunker import ContentListChunker, find_content_list, find_origin_pdf
from src.pipeline.indexer import SQLiteIndexer, ChromaIndexer
from src.pipeline.toc_builder import TOCBuilder


# Default paths
DEFAULT_TEXTBOOKS_DIR = os.path.join("mineru_output", "textbooks")
DEFAULT_DATA_DIR = os.path.join("data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DATA_DIR, "chunks.db")
DEFAULT_CHROMA_DIR = os.path.join(DEFAULT_DATA_DIR, "chroma")
DEFAULT_TOC_DIR = os.path.join(DEFAULT_DATA_DIR, "toc_trees")


class BatchProcessor:
    """Process all textbooks through the chunking + indexing pipeline."""

    def __init__(
        self,
        textbooks_dir: str = DEFAULT_TEXTBOOKS_DIR,
        db_path: str = DEFAULT_DB_PATH,
        chroma_dir: str = DEFAULT_CHROMA_DIR,
        toc_dir: str = DEFAULT_TOC_DIR,
    ):
        self.textbooks_dir = textbooks_dir
        self.db_path = db_path
        self.chroma_dir = chroma_dir
        self.toc_dir = toc_dir

        # Ensure output dirs
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(chroma_dir, exist_ok=True)
        os.makedirs(toc_dir, exist_ok=True)

    def discover_books(self):
        """Discover all book directories in textbooks_dir."""
        books = []
        for name in sorted(os.listdir(self.textbooks_dir)):
            book_dir = os.path.join(self.textbooks_dir, name)
            if os.path.isdir(book_dir):
                content_list = find_content_list(book_dir)
                if content_list:
                    books.append({
                        "book_id": name,
                        "book_dir": book_dir,
                        "content_list": content_list,
                        "pdf_path": find_origin_pdf(book_dir) or "",
                    })
        return books

    def process_all(self, skip_existing: bool = True):
        """
        Process all discovered books.
        If skip_existing=True, skip books already in SQLite.
        """
        books = self.discover_books()
        print(f"\n{'='*60}")
        print(f"  Batch Processing: {len(books)} textbooks")
        print(f"  DB: {self.db_path}")
        print(f"  ChromaDB: {self.chroma_dir}")
        print(f"  TOC: {self.toc_dir}")
        print(f"{'='*60}\n")

        sqlite_idx = SQLiteIndexer(self.db_path)
        chroma_idx = ChromaIndexer(self.chroma_dir)

        # Check which books already processed
        existing_books = set()
        if skip_existing:
            for b in sqlite_idx.get_book_list():
                existing_books.add(b["book_id"])

        total_chunks = 0
        errors = []

        for book in tqdm(books, desc="Processing books"):
            book_id = book["book_id"]

            if book_id in existing_books:
                tqdm.write(f"  [SKIP] {book_id} (already indexed)")
                continue

            try:
                n_chunks = self._process_single_book(
                    book, sqlite_idx, chroma_idx
                )
                total_chunks += n_chunks
                tqdm.write(f"  [OK] {book_id}: {n_chunks} chunks")
            except Exception as e:
                errors.append((book_id, str(e)))
                tqdm.write(f"  [ERR] {book_id}: {e}")

        sqlite_idx.close()

        # Summary
        print(f"\n{'='*60}")
        print(f"  Processing Complete!")
        print(f"  Books processed: {len(books) - len(existing_books)}")
        print(f"  Total new chunks: {total_chunks}")
        if errors:
            print(f"  Errors: {len(errors)}")
            for bid, err in errors:
                print(f"    [ERR] {bid}: {err}")
        print(f"{'='*60}\n")

        return {"total_chunks": total_chunks, "errors": errors}

    def _process_single_book(
        self,
        book: dict,
        sqlite_idx: SQLiteIndexer,
        chroma_idx: ChromaIndexer,
    ) -> int:
        """Process a single book: chunk → index → TOC."""
        book_id = book["book_id"]
        content_list_path = book["content_list"]
        pdf_path = book.get("pdf_path", "")

        # 1. Chunk
        chunker = ContentListChunker(book_id, content_list_path)
        chunks = chunker.chunk()

        if not chunks:
            return 0

        # Filter out very short chunks (noise)
        chunks = [c for c in chunks if len(c.text.strip()) >= 20]

        # 2. Index into SQLite
        sqlite_idx.insert_chunks(chunks)
        sqlite_idx.register_book(
            book_id=book_id,
            title=book_id.replace("_", " ").title(),
            pdf_path=pdf_path,
            total_chunks=len(chunks),
        )

        # 3. Index into ChromaDB (skip headings-only chunks for vector search)
        indexable_chunks = [c for c in chunks if c.content_type != "heading"]
        if indexable_chunks:
            chroma_idx.insert_chunks(indexable_chunks)

        # 4. Build TOC tree
        toc_builder = TOCBuilder(book_id)
        toc_tree = toc_builder.build_from_chunks(chunks)
        if toc_tree:
            toc_path = os.path.join(self.toc_dir, f"{book_id}_toc.json")
            toc_builder.save_tree(toc_tree, toc_path)

        return len(chunks)


def main():
    """CLI entry point for batch processing."""
    import argparse

    parser = argparse.ArgumentParser(description="Batch process textbooks for RAG indexing")
    parser.add_argument("--textbooks-dir", default=DEFAULT_TEXTBOOKS_DIR,
                        help="Path to MinerU textbooks output directory")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR,
                        help="Output directory for indexes")
    parser.add_argument("--no-skip", action="store_true",
                        help="Re-process already indexed books")
    args = parser.parse_args()

    processor = BatchProcessor(
        textbooks_dir=args.textbooks_dir,
        db_path=os.path.join(args.data_dir, "chunks.db"),
        chroma_dir=os.path.join(args.data_dir, "chroma"),
        toc_dir=os.path.join(args.data_dir, "toc_trees"),
    )
    processor.process_all(skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
