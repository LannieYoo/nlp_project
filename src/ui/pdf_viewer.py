"""
PDF Viewer: Renders PDF pages with bounding box highlights for source tracing.
Uses PyMuPDF to render page images and draw yellow rectangles on source regions.

IMPORTANT: MinerU outputs bbox coordinates in image pixel space (~1000px range),
while PyMuPDF uses PDF point coordinates (~500pt range). This module handles
the coordinate conversion automatically.
"""

import os
import json
from typing import List, Optional

import pymupdf  # PyMuPDF


class PDFViewer:
    """Renders PDF pages with highlighted source regions."""

    # Highlight color: yellow with transparency
    HIGHLIGHT_COLOR = (1, 1, 0)  # RGB yellow
    HIGHLIGHT_OPACITY = 0.3

    # MinerU default image DPI used for bbox coordinates
    # MinerU renders pages at 72 DPI * scale_factor
    # The content_list.json bbox values are in the image coordinate system
    MINERU_IMAGE_SIZE = 1000  # approximate max dimension in MinerU output

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

    def _get_mineru_page_size(self, book_id: str, page_idx: int) -> Optional[tuple]:
        """
        Get the image dimensions MinerU used for this page by checking
        the model.json or inferring from content_list.json bbox values.
        """
        # Try to read the model.json which has page_size info
        model_path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto",
            f"{book_id}_model.json"
        )
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model = json.load(f)
                # model.json contains page_info with width/height
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
        """
        Convert MinerU image-space bbox to PDF point-space rect.

        MinerU bbox is in image pixel coordinates.
        PDF rect is in PDF point coordinates.
        """
        if not bbox or len(bbox) != 4:
            return pymupdf.Rect(0, 0, 0, 0)

        pdf_width = page.rect.width
        pdf_height = page.rect.height

        # Try to get MinerU's image dimensions for this page
        mineru_size = self._get_mineru_page_size(book_id, page_idx)

        if mineru_size and mineru_size[0] > 0 and mineru_size[1] > 0:
            img_width, img_height = mineru_size
        else:
            # Fallback: estimate from bbox values
            # MinerU typically uses ~1000px width
            # Use the max bbox coordinate to estimate scale
            max_coord = max(bbox[2], bbox[3])
            if max_coord > pdf_width * 1.5:
                # Bbox coords are likely in image pixel space
                # Estimate image dimensions from PDF aspect ratio
                scale = max_coord / max(pdf_width, pdf_height)
                img_width = pdf_width * scale
                img_height = pdf_height * scale
            else:
                # Bbox coords seem to be already in PDF space
                return pymupdf.Rect(bbox[0], bbox[1], bbox[2], bbox[3])

        # Scale factors
        sx = pdf_width / img_width
        sy = pdf_height / img_height

        # Convert coordinates
        x1 = bbox[0] * sx
        y1 = bbox[1] * sy
        x2 = bbox[2] * sx
        y2 = bbox[3] * sy

        return pymupdf.Rect(x1, y1, x2, y2)

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
            bbox: [x1, y1, x2, y2] bounding box in MinerU image coordinates
            zoom: Zoom factor for rendering quality

        Returns:
            PNG image bytes, or None if rendering fails
        """
        pdf_path = self.get_pdf_path(book_id)
        if not pdf_path:
            return None

        try:
            # Always open fresh copy since we add temporary annotations
            doc = pymupdf.open(pdf_path)
            if page_idx >= len(doc):
                doc.close()
                return None

            page = doc[page_idx]
            mat = pymupdf.Matrix(zoom, zoom)

            # Add highlight annotation if bbox provided
            if bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
                # Convert MinerU coords to PDF coords
                rect = self._convert_bbox_to_pdf(bbox, page, book_id, page_idx)

                if rect.width > 0 and rect.height > 0:
                    annot = page.add_rect_annot(rect)
                    annot.set_colors(stroke=(1, 0.8, 0),
                                    fill=self.HIGHLIGHT_COLOR)
                    annot.set_opacity(self.HIGHLIGHT_OPACITY)
                    annot.set_border(width=2)
                    annot.update()

            # Render to pixmap
            pix = page.get_pixmap(matrix=mat)
            png_data = pix.tobytes("png")
            doc.close()

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
            doc = pymupdf.open(pdf_path)
            if page_idx >= len(doc):
                doc.close()
                return None

            page = doc[page_idx]
            mat = pymupdf.Matrix(zoom, zoom)

            for bbox in bboxes:
                if len(bbox) == 4 and any(b > 0 for b in bbox):
                    rect = self._convert_bbox_to_pdf(bbox, page, book_id, page_idx)
                    if rect.width > 0 and rect.height > 0:
                        annot = page.add_rect_annot(rect)
                        annot.set_colors(stroke=(1, 0.8, 0),
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

    def close(self):
        """No-op since we no longer cache documents."""
        pass
