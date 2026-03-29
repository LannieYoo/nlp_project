"""
Chunker module: Parses MinerU content_list.json files and creates
intelligent text chunks with full source metadata (book, page, bbox, section).
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Chunk:
    """A single text chunk with source tracing metadata."""
    chunk_id: str                # unique id: "{book_id}_p{page}_c{idx}"
    book_id: str                 # e.g. "jurafsky_slp3"
    text: str                    # chunk text content
    page_idx: int                # 0-based page number
    bbox: List[int]              # [x1, y1, x2, y2] bounding box on page
    content_type: str            # "text", "table", "formula", "image_caption"
    chapter: str = ""            # chapter title (from text_level hierarchy)
    section: str = ""            # section title
    text_level: Optional[int] = None  # heading level if this is a heading

    def to_dict(self) -> dict:
        return asdict(self)


class ContentListChunker:
    """
    Parse content_list.json from MinerU output and produce chunks.

    Strategy:
    - Use text_level fields to detect section boundaries (headings)
    - Accumulate consecutive text blocks into chunks
    - Keep tables and formulas as individual chunks (don't split them)
    - Max chunk size ~500 tokens (~2000 chars), overlap handled at retrieval
    - Each chunk carries full metadata for source tracing
    """

    MAX_CHUNK_CHARS = 2000  # ~500 tokens
    MIN_CHUNK_CHARS = 100   # don't create tiny chunks

    def __init__(self, book_id: str, content_list_path: str):
        self.book_id = book_id
        self.content_list_path = content_list_path
        self._current_chapter = ""
        self._current_section = ""

    def load_content_list(self) -> list:
        """Load and return the content_list.json entries."""
        with open(self.content_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def chunk(self) -> List[Chunk]:
        """Main entry: parse content_list and return list of Chunks."""
        entries = self.load_content_list()
        chunks: List[Chunk] = []
        buffer_text = ""
        buffer_pages = []
        buffer_bboxes = []
        chunk_counter = 0

        for entry in entries:
            entry_type = entry.get("type", "text")
            text = entry.get("text", "").strip()
            page_idx = entry.get("page_idx", 0)
            bbox = entry.get("bbox", [0, 0, 0, 0])
            text_level = entry.get("text_level", None)

            # Skip discarded entries and empty text
            if entry_type == "discarded" or not text:
                continue

            # Update chapter/section tracking from headings
            if text_level is not None:
                # Flush buffer before heading
                if buffer_text.strip():
                    chunks.extend(
                        self._create_chunks(
                            buffer_text.strip(), buffer_pages, buffer_bboxes,
                            chunk_counter, "text"
                        )
                    )
                    chunk_counter += len(chunks) - chunk_counter

                if text_level == 1:
                    self._current_chapter = text
                    self._current_section = ""
                elif text_level in (2, 3):
                    self._current_section = text

                # Create a heading chunk
                chunks.append(Chunk(
                    chunk_id=f"{self.book_id}_p{page_idx}_c{chunk_counter}",
                    book_id=self.book_id,
                    text=text,
                    page_idx=page_idx,
                    bbox=bbox,
                    content_type="heading",
                    chapter=self._current_chapter,
                    section=self._current_section,
                    text_level=text_level,
                ))
                chunk_counter += 1
                buffer_text = ""
                buffer_pages = []
                buffer_bboxes = []
                continue

            # Detect content type
            content_type = "text"
            if "<table" in text.lower() or "</table>" in text.lower():
                content_type = "table"
            elif "$$" in text or "\\begin{" in text:
                content_type = "formula"

            # Tables and formulas: flush buffer, emit as single chunk
            if content_type in ("table", "formula"):
                if buffer_text.strip():
                    chunks.extend(
                        self._create_chunks(
                            buffer_text.strip(), buffer_pages, buffer_bboxes,
                            chunk_counter, "text"
                        )
                    )
                    chunk_counter = len(chunks)
                    buffer_text = ""
                    buffer_pages = []
                    buffer_bboxes = []

                chunks.append(Chunk(
                    chunk_id=f"{self.book_id}_p{page_idx}_c{chunk_counter}",
                    book_id=self.book_id,
                    text=text,
                    page_idx=page_idx,
                    bbox=bbox,
                    content_type=content_type,
                    chapter=self._current_chapter,
                    section=self._current_section,
                ))
                chunk_counter += 1
                continue

            # Regular text: accumulate in buffer
            buffer_text += " " + text
            buffer_pages.append(page_idx)
            buffer_bboxes.append(bbox)

            # If buffer exceeds max size, flush
            if len(buffer_text) >= self.MAX_CHUNK_CHARS:
                chunks.extend(
                    self._create_chunks(
                        buffer_text.strip(), buffer_pages, buffer_bboxes,
                        chunk_counter, "text"
                    )
                )
                chunk_counter = len(chunks)
                buffer_text = ""
                buffer_pages = []
                buffer_bboxes = []

        # Flush remaining buffer
        if buffer_text.strip():
            chunks.extend(
                self._create_chunks(
                    buffer_text.strip(), buffer_pages, buffer_bboxes,
                    chunk_counter, "text"
                )
            )

        return chunks

    def _create_chunks(
        self, text: str, pages: list, bboxes: list,
        start_idx: int, content_type: str
    ) -> List[Chunk]:
        """Split text into chunks of MAX_CHUNK_CHARS, preserving sentence boundaries."""
        if len(text) <= self.MAX_CHUNK_CHARS:
            # Merge bboxes: take the union
            merged_bbox = self._merge_bboxes(bboxes) if bboxes else [0, 0, 0, 0]
            primary_page = pages[0] if pages else 0
            return [Chunk(
                chunk_id=f"{self.book_id}_p{primary_page}_c{start_idx}",
                book_id=self.book_id,
                text=text,
                page_idx=primary_page,
                bbox=merged_bbox,
                content_type=content_type,
                chapter=self._current_chapter,
                section=self._current_section,
            )]

        # Split at sentence boundaries
        result = []
        sentences = self._split_sentences(text)
        current = ""
        idx = start_idx

        for sentence in sentences:
            if len(current) + len(sentence) > self.MAX_CHUNK_CHARS and current:
                primary_page = pages[0] if pages else 0
                merged_bbox = self._merge_bboxes(bboxes) if bboxes else [0, 0, 0, 0]
                result.append(Chunk(
                    chunk_id=f"{self.book_id}_p{primary_page}_c{idx}",
                    book_id=self.book_id,
                    text=current.strip(),
                    page_idx=primary_page,
                    bbox=merged_bbox,
                    content_type=content_type,
                    chapter=self._current_chapter,
                    section=self._current_section,
                ))
                idx += 1
                current = sentence
            else:
                current += " " + sentence

        if current.strip():
            primary_page = pages[-1] if pages else 0
            merged_bbox = self._merge_bboxes(bboxes) if bboxes else [0, 0, 0, 0]
            result.append(Chunk(
                chunk_id=f"{self.book_id}_p{primary_page}_c{idx}",
                book_id=self.book_id,
                text=current.strip(),
                page_idx=primary_page,
                bbox=merged_bbox,
                content_type=content_type,
                chapter=self._current_chapter,
                section=self._current_section,
            ))

        return result

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Simple sentence splitting on period/question/exclamation followed by space."""
        import re
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p for p in parts if p.strip()]

    @staticmethod
    def _merge_bboxes(bboxes: list) -> List[int]:
        """Compute union of multiple bounding boxes."""
        if not bboxes:
            return [0, 0, 0, 0]
        x1 = min(b[0] for b in bboxes if len(b) == 4)
        y1 = min(b[1] for b in bboxes if len(b) == 4)
        x2 = max(b[2] for b in bboxes if len(b) == 4)
        y2 = max(b[3] for b in bboxes if len(b) == 4)
        return [x1, y1, x2, y2]


def find_content_list(book_dir: str) -> Optional[str]:
    """Find the content_list.json for a given book directory."""
    book_name = os.path.basename(book_dir)
    # Standard MinerU output path: {book_name}/{book_name}/auto/{book_name}_content_list.json
    path = os.path.join(book_dir, book_name, "auto", f"{book_name}_content_list.json")
    if os.path.exists(path):
        return path
    return None


def find_origin_pdf(book_dir: str) -> Optional[str]:
    """Find the origin PDF for a given book directory."""
    book_name = os.path.basename(book_dir)
    path = os.path.join(book_dir, book_name, "auto", f"{book_name}_origin.pdf")
    if os.path.exists(path):
        return path
    return None
