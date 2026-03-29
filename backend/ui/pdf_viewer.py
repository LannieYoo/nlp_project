"""
PDF Viewer: Renders PDF pages with bounding box highlights for source tracing.

Strategy for finding the highlight region (in priority order):
  1. TEXT SEARCH — Use PyMuPDF's page.search_for() to find the chunk's text
     on the PDF page. This is the most accurate method.
  2. BBOX CONVERSION — Convert MinerU image-space bbox to PDF points as fallback.

This avoids bbox coordinate mismatches entirely by locating text directly.
"""

import os
import json
import re
from typing import List, Optional

import pymupdf  # PyMuPDF


class PDFViewer:
    """Renders PDF pages with highlighted source regions."""

    # Highlight color: yellow with transparency
    HIGHLIGHT_COLOR = (1, 1, 0)  # RGB yellow
    HIGHLIGHT_OPACITY = 0.3

    def __init__(self, pdf_base_dir: str = "mineru_output/textbooks"):
        self.pdf_base_dir = pdf_base_dir

    def get_pdf_path(self, book_id: str) -> Optional[str]:
        """Find the origin PDF for a book."""
        path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto", f"{book_id}_origin.pdf"
        )
        if os.path.exists(path):
            return path
        return None

    # ------------------------------------------------------------------
    # TEXT-BASED highlight (preferred)
    # ------------------------------------------------------------------

    def _find_text_rects(
        self, page, text_preview: str
    ) -> List[pymupdf.Rect]:
        """
        Search for the chunk's text on the PDF page.
        Uses multiple strategies to find the best match:
          1. Try the longest plain-text segments (between LaTeX blocks)
          2. Try progressively shorter substrings
          3. Try individual sentences
        """
        if not text_preview or len(text_preview.strip()) < 10:
            return []

        # Strategy 1: Extract plain text segments between LaTeX blocks
        # and try the longest ones first (most distinctive)
        segments = self._extract_plain_segments(text_preview)
        for seg in segments:
            if len(seg) < 15:
                continue
            # Try the segment, progressively shorter
            for length in [min(len(seg), 80), min(len(seg), 60),
                           min(len(seg), 40)]:
                snippet = seg[:length].strip()
                if len(snippet) < 12:
                    continue
                rects = page.search_for(snippet)
                if rects:
                    return rects

        # Strategy 2: Try cleaned full text (fallback)
        clean = self._clean_text_for_search(text_preview)
        if clean and len(clean) >= 15:
            for length in [80, 60, 40, 25]:
                snippet = clean[:length].strip()
                if len(snippet) < 10:
                    continue
                rects = page.search_for(snippet)
                if rects:
                    return rects

        return []

    @staticmethod
    def _extract_plain_segments(text: str) -> List[str]:
        """
        Extract continuous runs of plain English text from LaTeX-heavy content.
        Instead of splitting on $ (which has pairing issues), we find
        sequences of 3+ consecutive English words as searchable segments.
        """
        # First: remove all $...$ math blocks by replacing $ and content
        # between matched $ pairs with spaces
        clean = text
        # Remove $$...$$ blocks
        clean = re.sub(r'\$\$[^$]+\$\$', ' ', clean)
        # Remove inline $...$ — but handle carefully by tokenizing
        # Instead of regex on $, just remove everything that looks like math
        # Remove LaTeX commands first
        clean = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+', ' ', clean)
        # Remove $ signs and math symbols
        clean = re.sub(r'[${}_\\^~|]', ' ', clean)
        # Remove standalone math-like tokens: single letters/numbers
        # between operators
        clean = re.sub(r'\s[<>=+\-*/]\s', ' ', clean)

        # Now find continuous runs of English words (3+ words)
        # A "word" is 2+ lowercase/uppercase letters (not just single chars)
        words = clean.split()
        segments = []
        current = []

        for w in words:
            # Check if this looks like an English word (not math notation)
            if re.match(r'^[A-Za-z][A-Za-z,.\-;:()\']{1,}$', w):
                current.append(w)
            else:
                if len(current) >= 3:
                    segments.append(' '.join(current))
                current = []

        if len(current) >= 3:
            segments.append(' '.join(current))

        # Sort by length descending — longest segments are most distinctive
        segments.sort(key=len, reverse=True)
        return segments

    @staticmethod
    def _clean_text_for_search(text: str) -> str:
        """
        Remove LaTeX, markdown formatting, and special chars
        to produce plain text suitable for PDF text search.
        """
        clean = text
        clean = re.sub(r'\$\$[^$]+\$\$', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+', ' ', clean)
        clean = re.sub(r'[*_`#${}|\\^~]', ' ', clean)
        clean = ' '.join(clean.split())
        return clean.strip()

    def _merge_rects(self, rects: List[pymupdf.Rect], page) -> pymupdf.Rect:
        """
        Merge multiple text search rects into one bounding rectangle.
        Add a small padding for visibility.
        """
        if not rects:
            return pymupdf.Rect(0, 0, 0, 0)

        x0 = min(r.x0 for r in rects)
        y0 = min(r.y0 for r in rects)
        x1 = max(r.x1 for r in rects)
        y1 = max(r.y1 for r in rects)

        # Add padding (5 points)
        pad = 5
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(page.rect.width, x1 + pad)
        y1 = min(page.rect.height, y1 + pad)

        return pymupdf.Rect(x0, y0, x1, y1)

    # ------------------------------------------------------------------
    # BBOX CONVERSION fallback
    # ------------------------------------------------------------------

    def _get_mineru_page_size(self, book_id: str, page_idx: int) -> Optional[tuple]:
        """Get MinerU's image dimensions for coordinate conversion."""
        model_path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto",
            f"{book_id}_model.json"
        )
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model = json.load(f)
                if isinstance(model, list) and len(model) > page_idx:
                    page_info = model[page_idx]
                    if "page_info" in page_info:
                        pi = page_info["page_info"]
                        return (pi.get("width", 0), pi.get("height", 0))
            except Exception:
                pass
        return None

    def _convert_bbox_to_pdf(
        self, bbox: List[int], page, book_id: str, page_idx: int
    ) -> pymupdf.Rect:
        """Convert MinerU image-space bbox to PDF point-space rect."""
        if not bbox or len(bbox) != 4:
            return pymupdf.Rect(0, 0, 0, 0)

        pdf_width = page.rect.width
        pdf_height = page.rect.height

        mineru_size = self._get_mineru_page_size(book_id, page_idx)

        if mineru_size and mineru_size[0] > 0 and mineru_size[1] > 0:
            img_width, img_height = mineru_size
        else:
            max_coord = max(bbox[2], bbox[3])
            if max_coord > pdf_width * 1.5:
                scale = max_coord / max(pdf_width, pdf_height)
                img_width = pdf_width * scale
                img_height = pdf_height * scale
            else:
                return pymupdf.Rect(bbox[0], bbox[1], bbox[2], bbox[3])

        sx = pdf_width / img_width
        sy = pdf_height / img_height

        x1 = bbox[0] * sx
        y1 = bbox[1] * sy
        x2 = bbox[2] * sx
        y2 = bbox[3] * sy

        return pymupdf.Rect(x1, y1, x2, y2)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------

    def render_page(
        self,
        book_id: str,
        page_idx: int,
        bbox: Optional[List[int]] = None,
        text_preview: str = "",
        zoom: float = 2.0,
    ) -> Optional[bytes]:
        """
        Render a PDF page as PNG image with highlighted source region.

        Highlight strategy:
          1. Search for text_preview on the page (most accurate)
          2. Fall back to bbox coordinate conversion if text search fails

        Args:
            book_id: Book identifier
            page_idx: 0-based page number
            bbox: [x1, y1, x2, y2] bounding box in MinerU image coordinates
            text_preview: The chunk's text content for text-based search
            zoom: Zoom factor for rendering quality

        Returns:
            PNG image bytes, or None if rendering fails
        """
        pdf_path = self.get_pdf_path(book_id)
        if not pdf_path:
            return None

        try:
            doc = pymupdf.open(pdf_path)
            if page_idx >= len(doc):
                doc.close()
                return None

            page = doc[page_idx]
            mat = pymupdf.Matrix(zoom, zoom)

            highlight_rect = None

            # Strategy 1: Text search (most accurate)
            if text_preview:
                rects = self._find_text_rects(page, text_preview)
                if rects:
                    highlight_rect = self._merge_rects(rects, page)

            # Strategy 2: Bbox conversion (fallback)
            if highlight_rect is None and bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
                highlight_rect = self._convert_bbox_to_pdf(
                    bbox, page, book_id, page_idx
                )

            # Draw the highlight
            if highlight_rect and highlight_rect.width > 0 and highlight_rect.height > 0:
                annot = page.add_rect_annot(highlight_rect)
                annot.set_colors(stroke=(1, 0.8, 0), fill=self.HIGHLIGHT_COLOR)
                annot.set_opacity(self.HIGHLIGHT_OPACITY)
                annot.set_border(width=2)
                annot.update()

            pix = page.get_pixmap(matrix=mat)
            png_data = pix.tobytes("png")
            doc.close()

            return png_data

        except Exception as e:
            print(f"PDF render error: {e}")
            return None

    def close(self):
        """No-op since we no longer cache documents."""
        pass
