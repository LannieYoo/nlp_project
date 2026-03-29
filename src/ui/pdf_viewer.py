"""
PDF Viewer: Renders PDF pages with bounding box highlights for source tracing.
Uses PyMuPDF to render page images and draw yellow rectangles on source regions.
"""

import os
import io
from typing import List, Optional, Tuple

import pymupdf  # PyMuPDF


class PDFViewer:
    """Renders PDF pages with highlighted source regions."""

    # Highlight color: yellow with transparency
    HIGHLIGHT_COLOR = (1, 1, 0)  # RGB yellow
    HIGHLIGHT_OPACITY = 0.3

    def __init__(self, pdf_base_dir: str = "mineru_output/textbooks"):
        self.pdf_base_dir = pdf_base_dir
        self._pdf_cache = {}

    def get_pdf_path(self, book_id: str) -> Optional[str]:
        """Find the origin PDF for a book."""
        path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto", f"{book_id}_origin.pdf"
        )
        if os.path.exists(path):
            return path
        return None

    def render_page(
        self,
        book_id: str,
        page_idx: int,
        bbox: Optional[List[int]] = None,
        zoom: float = 2.0,
    ) -> Optional[bytes]:
        """
        Render a PDF page as PNG image with optional bbox highlight.

        Args:
            book_id: Book identifier
            page_idx: 0-based page number
            bbox: [x1, y1, x2, y2] bounding box to highlight
            zoom: Zoom factor for rendering quality

        Returns:
            PNG image bytes, or None if rendering fails
        """
        pdf_path = self.get_pdf_path(book_id)
        if not pdf_path:
            return None

        try:
            doc = self._get_doc(pdf_path)
            if page_idx >= len(doc):
                return None

            page = doc[page_idx]
            mat = pymupdf.Matrix(zoom, zoom)

            # Add highlight annotation if bbox provided
            if bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
                # Draw highlight rectangle
                rect = pymupdf.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                annot = page.add_rect_annot(rect)
                annot.set_colors(stroke=self.HIGHLIGHT_COLOR,
                                fill=self.HIGHLIGHT_COLOR)
                annot.set_opacity(self.HIGHLIGHT_OPACITY)
                annot.set_border(width=2)
                annot.update()

            # Render to pixmap
            pix = page.get_pixmap(matrix=mat)
            png_data = pix.tobytes("png")

            # Remove annotation after rendering (don't modify the file)
            if bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
                # Reload page to remove temporary annotation
                self._pdf_cache.pop(pdf_path, None)

            return png_data

        except Exception as e:
            print(f"PDF render error: {e}")
            return None

    def render_page_with_multiple_highlights(
        self,
        book_id: str,
        page_idx: int,
        bboxes: List[List[int]],
        zoom: float = 2.0,
    ) -> Optional[bytes]:
        """Render a page with multiple highlighted regions."""
        pdf_path = self.get_pdf_path(book_id)
        if not pdf_path:
            return None

        try:
            # Open fresh copy for annotation
            doc = pymupdf.open(pdf_path)
            if page_idx >= len(doc):
                return None

            page = doc[page_idx]
            mat = pymupdf.Matrix(zoom, zoom)

            for bbox in bboxes:
                if len(bbox) == 4 and any(b > 0 for b in bbox):
                    rect = pymupdf.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                    annot = page.add_rect_annot(rect)
                    annot.set_colors(stroke=self.HIGHLIGHT_COLOR,
                                    fill=self.HIGHLIGHT_COLOR)
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

    def _get_doc(self, pdf_path: str):
        """Open PDF with caching."""
        if pdf_path not in self._pdf_cache:
            self._pdf_cache[pdf_path] = pymupdf.open(pdf_path)
        return self._pdf_cache[pdf_path]

    def close(self):
        """Close all cached PDF documents."""
        for doc in self._pdf_cache.values():
            doc.close()
        self._pdf_cache.clear()
