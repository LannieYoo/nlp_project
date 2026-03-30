"""
PDF Page Image Renderer using pypdfium2 + Pillow.
Renders PDF pages as PNG images with highlight overlays.
No PyMuPDF dependency.
"""

import os
import io
import re
import json
import threading
from typing import Optional, List, Tuple

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


class PageRenderer:
    """Renders PDF pages as images with optional highlight overlay."""

    HIGHLIGHT_COLOR = (255, 220, 50, 70)  # RGBA yellow with transparency

    def __init__(self, pdf_base_dir: str = "mineru_output/textbooks"):
        self.pdf_base_dir = pdf_base_dir
        self._doc_cache: dict = {}  # book_id -> pdfium.PdfDocument
        self._lock = threading.Lock()

    def get_pdf_path(self, book_id: str) -> Optional[str]:
        path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto", f"{book_id}_origin.pdf"
        )
        return path if os.path.exists(path) else None

    def _get_doc(self, book_id: str) -> Optional[pdfium.PdfDocument]:
        if book_id not in self._doc_cache:
            pdf_path = self.get_pdf_path(book_id)
            if not pdf_path:
                return None
            self._doc_cache[book_id] = pdfium.PdfDocument(pdf_path)
        return self._doc_cache[book_id]

    def get_page_count(self, book_id: str) -> int:
        doc = self._get_doc(book_id)
        return len(doc) if doc else 0

    def render_page(
        self,
        book_id: str,
        page_idx: int,
        scale: float = 2.0,
        highlight_rect: Optional[Tuple[float, float, float, float]] = None,
        search_query: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Render a PDF page as a PNG image.

        Args:
            book_id: Book identifier
            page_idx: 0-based page number
            scale: Render scale (2.0 = 144 DPI)
            highlight_rect: (x, y, w, h) in PDF points to highlight

        Returns:
            PNG image bytes
        """
        with self._lock:
            doc = self._get_doc(book_id)
            if not doc or page_idx >= len(doc):
                return None

            try:
                page = doc[page_idx]
                # Render to PIL Image
                bitmap = page.render(scale=scale)
                pil_image = bitmap.to_pil()

                # Create overlay image for highlights
                draw_img = None
                draw = None
                sx = pil_image.width / page.get_width()
                sy = pil_image.height / page.get_height()

                def _init_draw():
                    nonlocal draw_img, draw
                    if not draw_img:
                        draw_img = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
                        draw = ImageDraw.Draw(draw_img)

                def _draw_rect(x, y, w, h):
                    _init_draw()
                    px, py = int(x * sx), int(y * sy)
                    pw, ph = int(w * sx), int(h * sy)
                    draw.rectangle(
                        [px, py, px + pw, py + ph],
                        fill=self.HIGHLIGHT_COLOR,
                        outline=(255, 180, 0, 200),
                        width=3,
                    )

                # 1. Draw single highlight_rect if given
                if highlight_rect:
                    x, y, w, h = highlight_rect
                    _draw_rect(x, y, w, h)

                # 2. Draw search_query occurrences if given
                if search_query:
                    try:
                        textpage = page.get_textpage()
                        searcher = textpage.search(search_query)
                        while True:
                            try:
                                res = searcher.get_next()
                                if not res:
                                    break
                                count = textpage.count_rects(res[0], res[1])
                                for i in range(count):
                                    r = textpage.get_rect(i)
                                    page_height = page.get_height()
                                    x = r[0]
                                    w = r[2] - r[0]
                                    y = page_height - r[3]
                                    h = r[3] - r[1]
                                    _draw_rect(x, y, w, h)
                            except Exception as ex:
                                print(f"pdf search rects error: {ex}")
                                break
                        textpage.close()
                    except Exception as ex:
                        print(f"pdf search_query error (skipped): {ex}")

                # Composite if any highlights were drawn
                if draw_img:
                    pil_image = pil_image.convert("RGBA")
                    pil_image = Image.alpha_composite(pil_image, draw_img)
                    pil_image = pil_image.convert("RGB")

                # Encode as PNG
                buf = io.BytesIO()
                pil_image.save(buf, format="PNG", optimize=True)
                return buf.getvalue()

            except Exception as e:
                print(f"Page render error: {e}")
                # Clear corrupted doc cache and retry once with lower scale
                if book_id in self._doc_cache:
                    try:
                        self._doc_cache[book_id].close()
                    except Exception:
                        pass
                    del self._doc_cache[book_id]
                try:
                    doc2 = self._get_doc(book_id)
                    if doc2 and page_idx < len(doc2):
                        page2 = doc2[page_idx]
                        bitmap2 = page2.render(scale=min(scale, 1.0))
                        pil2 = bitmap2.to_pil()
                        buf2 = io.BytesIO()
                        pil2.save(buf2, format="PNG", optimize=True)
                        return buf2.getvalue()
                except Exception as e2:
                    print(f"Page render retry also failed: {e2}")
                return None

    def compute_highlight_coords(
        self, book_id: str, page_idx: int, text_preview: str, bbox: Optional[List] = None
    ) -> Optional[dict]:
        """
        Compute highlight rectangle in PDF point coordinates.

        Strategy:
          1. Text search on the page using pypdfium2
          2. Bbox conversion fallback (MinerU coords -> PDF points)

        Returns: dict with x, y, width, height, page_width, page_height
        """
        doc = self._get_doc(book_id)
        if not doc or page_idx >= len(doc):
            return None

        try:
            page = doc[page_idx]
            page_w = page.get_width()
            page_h = page.get_height()
            rect = None

            # Strategy 1: Text search
            if text_preview and len(text_preview.strip()) >= 10:
                rect = self._text_search(page, text_preview, page_w, page_h)

            # Strategy 2: Bbox fallback
            if rect is None and bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
                rect = self._bbox_convert(bbox, page_w, page_h, book_id, page_idx)

            if rect and rect[2] > 0 and rect[3] > 0:
                return {
                    "x": rect[0],
                    "y": rect[1],
                    "width": rect[2],
                    "height": rect[3],
                    "page_width": page_w,
                    "page_height": page_h,
                }

        except Exception as e:
            print(f"Highlight compute error: {e}")

        return None

    def _text_search(
        self, page, text_preview: str, page_w: float, page_h: float
    ) -> Optional[Tuple[float, float, float, float]]:
        """Search for text on the page using pypdfium2 textpage."""
        try:
            textpage = page.get_textpage()

            # Try progressively shorter snippets of clean text
            segments = self._extract_plain_segments(text_preview)

            for seg in segments:
                if len(seg) < 12:
                    continue
                for length in [min(len(seg), 80), min(len(seg), 50), min(len(seg), 30)]:
                    snippet = seg[:length].strip()
                    if len(snippet) < 10:
                        continue
                    result = self._search_snippet(textpage, snippet, page_h)
                    if result:
                        return result

            # Fallback: clean text approach
            clean = self._clean_text(text_preview)
            if clean and len(clean) >= 15:
                for length in [80, 50, 30, 20]:
                    snippet = clean[:length].strip()
                    if len(snippet) < 10:
                        continue
                    result = self._search_snippet(textpage, snippet, page_h)
                    if result:
                        return result

        except Exception as e:
            print(f"Text search error: {e}")

        return None

    def _search_snippet(
        self, textpage, snippet: str, page_h: float
    ) -> Optional[Tuple[float, float, float, float]]:
        """Search for a text snippet and return (x, y, w, h) in top-left coords."""
        searcher = textpage.search(snippet)
        if not searcher:
            return None

        result = searcher.get_next()
        if not result:
            return None

        char_idx, char_count = result

        # Get bounding boxes for each character
        boxes = []
        for i in range(char_idx, char_idx + char_count):
            try:
                box = textpage.get_charbox(i)
                if box:
                    boxes.append(box)
            except Exception:
                pass

        if not boxes:
            return None

        # boxes are (left, bottom, right, top) in PDF coordinates (origin bottom-left)
        left = min(b[0] for b in boxes)
        bottom = min(b[1] for b in boxes)
        right = max(b[2] for b in boxes)
        top = max(b[3] for b in boxes)

        # Convert to top-left origin and add padding
        pad = 5
        x = max(0, left - pad)
        y = max(0, page_h - top - pad)
        w = (right - left) + pad * 2
        h = (top - bottom) + pad * 2

        if w > 0 and h > 0:
            return (x, y, w, h)

        return None

    def _bbox_convert(
        self, bbox: list, page_w: float, page_h: float, book_id: str, page_idx: int
    ) -> Optional[Tuple[float, float, float, float]]:
        """Convert MinerU image-space bbox to PDF point-space (x, y, w, h)."""
        mineru_size = self._get_mineru_page_size(book_id, page_idx)

        if mineru_size and mineru_size[0] > 0 and mineru_size[1] > 0:
            img_w, img_h = mineru_size
        else:
            max_coord = max(bbox[2], bbox[3])
            if max_coord > page_w * 1.5:
                ratio = max_coord / max(page_w, page_h)
                img_w = page_w * ratio
                img_h = page_h * ratio
            else:
                # Assume bbox is already in PDF points
                x, y = bbox[0], bbox[1]
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                return (x, y, w, h)

        sx = page_w / img_w
        sy = page_h / img_h

        x = bbox[0] * sx
        y = bbox[1] * sy
        w = (bbox[2] - bbox[0]) * sx
        h = (bbox[3] - bbox[1]) * sy

        return (x, y, w, h)

    def _get_mineru_page_size(self, book_id: str, page_idx: int) -> Optional[tuple]:
        model_path = os.path.join(
            self.pdf_base_dir, book_id, book_id, "auto", f"{book_id}_model.json"
        )
        if os.path.exists(model_path):
            try:
                with open(model_path, "r", encoding="utf-8") as f:
                    model = json.load(f)
                if isinstance(model, list) and len(model) > page_idx:
                    pi = model[page_idx].get("page_info", {})
                    return (pi.get("width", 0), pi.get("height", 0))
            except Exception:
                pass
        return None

    @staticmethod
    def _extract_plain_segments(text: str) -> List[str]:
        clean = text
        clean = re.sub(r'\$\$[^$]+\$\$', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+', ' ', clean)
        clean = re.sub(r'[${}_\\^~|]', ' ', clean)
        clean = re.sub(r'\s[<>=+\-*/]\s', ' ', clean)

        words = clean.split()
        segments = []
        current = []

        for w in words:
            if re.match(r"^[A-Za-z][A-Za-z,.\-;:()']{1,}$", w):
                current.append(w)
            else:
                if len(current) >= 3:
                    segments.append(" ".join(current))
                current = []

        if len(current) >= 3:
            segments.append(" ".join(current))

        segments.sort(key=len, reverse=True)
        return segments

    @staticmethod
    def _clean_text(text: str) -> str:
        clean = text
        clean = re.sub(r'\$\$[^$]+\$\$', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', ' ', clean)
        clean = re.sub(r'\\[a-zA-Z]+', ' ', clean)
        clean = re.sub(r'[*_`#${}|\\^~]', ' ', clean)
        return " ".join(clean.split()).strip()

    def close(self):
        for doc in self._doc_cache.values():
            doc.close()
        self._doc_cache.clear()
