"""
FastAPI Backend Server for AI Textbook Q&A System.

Wraps the existing RAG engine as REST API.
PDF pages rendered as images via pypdfium2 (no PyMuPDF).
"""

import os
import sys
import sqlite3
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from backend.rag.engine import RAGEngine
from backend.api.page_renderer import PageRenderer

# --------------- Globals ---------------
_engine: Optional[RAGEngine] = None
_renderer: Optional[PageRenderer] = None

PDF_BASE_DIR = os.path.join(PROJECT_ROOT, "mineru_output", "textbooks")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "chunks.db")


def get_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine(
            db_path=DB_PATH,
            chroma_dir=os.path.join(PROJECT_ROOT, "data", "chroma"),
            toc_dir=os.path.join(PROJECT_ROOT, "data", "toc_trees"),
        )
    return _engine


def get_renderer() -> PageRenderer:
    global _renderer
    if _renderer is None:
        _renderer = PageRenderer(pdf_base_dir=PDF_BASE_DIR)
    return _renderer


# --------------- Pydantic Models ---------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    model: str = "qwen2.5:0.5b"
    book_filter: Optional[str] = None
    methods: List[str] = ["fts", "vector", "tree", "metadata"]


class HighlightInfo(BaseModel):
    """PDF-space coordinates for highlight overlay."""
    x: float
    y: float
    width: float
    height: float
    page_width: float
    page_height: float


class SourceItem(BaseModel):
    chunk_id: str = ""
    book_id: str = ""
    page_idx: int = 0
    chapter: str = ""
    section: str = ""
    text_preview: str = ""
    score: float = 0.0
    method: str = ""
    highlight: Optional[HighlightInfo] = None


class SearchResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    query: str
    model: str


class StatsResponse(BaseModel):
    total_books: int
    total_chunks: int


class BookInfo(BaseModel):
    book_id: str
    title: str
    has_pdf: bool
    page_count: int = 0


# --------------- Highlight Computation ---------------
def compute_highlight(source: dict) -> Optional[HighlightInfo]:
    """
    Compute PDF-space highlight coordinates using pypdfium2.
    """
    renderer = get_renderer()
    book_id = source.get("book_id", "")
    page_idx = source.get("page_idx", 0)
    text_preview = source.get("text_preview", "")
    bbox = source.get("bbox", [0, 0, 0, 0])

    result = renderer.compute_highlight_coords(book_id, page_idx, text_preview, bbox)
    if result:
        return HighlightInfo(**result)
    return None


# --------------- App ---------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if _engine:
        _engine.close()
    if _renderer:
        _renderer.close()


app = FastAPI(title="AI Textbook Q&A API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------- Routes ---------------
@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT book_id) FROM chunks")
        total_books = cur.fetchone()[0]
        conn.close()
        return StatsResponse(total_books=total_books, total_chunks=total_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/books", response_model=List[BookInfo])
def get_books():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT book_id FROM chunks ORDER BY book_id")
        rows = cur.fetchall()
        conn.close()

        renderer = get_renderer()
        books = []
        for (bid,) in rows:
            title = bid.replace("_", " ").title()
            has_pdf = renderer.get_pdf_path(bid) is not None
            page_count = 0
            if has_pdf:
                try:
                    page_count = renderer.get_page_count(bid)
                except Exception:
                    pass
            books.append(BookInfo(book_id=bid, title=title, has_pdf=has_pdf, page_count=page_count))
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    try:
        engine = get_engine()
        engine.model = req.model
        engine.top_k = req.top_k

        response = engine.ask(
            query=req.query,
            book_filter=req.book_filter if req.book_filter else None,
            methods=req.methods,
        )

        sources = []
        for src in response.sources:
            highlight = compute_highlight(src)
            sources.append(SourceItem(
                chunk_id=src.get("chunk_id", ""),
                book_id=src.get("book_id", ""),
                page_idx=src.get("page_idx", 0),
                chapter=src.get("chapter", ""),
                section=src.get("section", ""),
                text_preview=src.get("text_preview", ""),
                score=round(src.get("score", 0), 4),
                method=src.get("method", ""),
                highlight=highlight,
            ))

        return SearchResponse(
            answer=response.answer,
            sources=sources,
            query=response.query,
            model=response.model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/page-image/{book_id}/{page_idx}")
def get_page_image(
    book_id: str,
    page_idx: int,
    scale: float = Query(default=2.0, ge=0.1, le=4.0),
    hl_x: Optional[float] = Query(default=None),
    hl_y: Optional[float] = Query(default=None),
    hl_w: Optional[float] = Query(default=None),
    hl_h: Optional[float] = Query(default=None),
    sq: Optional[str] = Query(default=None),
):
    """
    Render a PDF page as a PNG image.
    Optionally draws a highlight rectangle (in PDF point coordinates).
    """
    renderer = get_renderer()

    highlight_rect = None
    if all(v is not None for v in [hl_x, hl_y, hl_w, hl_h]):
        highlight_rect = (hl_x, hl_y, hl_w, hl_h)

    png_data = renderer.render_page(
        book_id=book_id,
        page_idx=page_idx,
        scale=scale,
        highlight_rect=highlight_rect,
        search_query=sq,
    )

    if png_data is None:
        # Generate a placeholder image instead of 404
        from PIL import Image, ImageDraw, ImageFont
        w, h = int(612 * scale), int(792 * scale)
        img = Image.new("RGB", (w, h), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        msg = f"Page {page_idx + 1} could not be rendered"
        try:
            font = ImageFont.truetype("arial.ttf", int(16 * scale))
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), msg, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((w - tw) / 2, (h - th) / 2), msg, fill=(150, 150, 150), font=font)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_data = buf.getvalue()

    return Response(
        content=png_data,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",
        },
    )


@app.get("/api/page-count/{book_id}")
def get_page_count(book_id: str):
    renderer = get_renderer()
    count = renderer.get_page_count(book_id)
    if count == 0:
        raise HTTPException(status_code=404, detail=f"PDF not found: {book_id}")
    return {"book_id": book_id, "page_count": count}


@app.get("/api/search-in-book/{book_id}")
def search_in_book(book_id: str, q: str = Query(..., min_length=1)):
    """Search for text in a specific book's PDF and return matching pages with snippets."""
    renderer = get_renderer()
    pdf_path = renderer.get_pdf_path(book_id)
    if not pdf_path:
        raise HTTPException(status_code=404, detail=f"PDF not found: {book_id}")

    import pypdfium2 as pdfium
    results = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        for page_idx in range(len(pdf)):
            try:
                page = pdf[page_idx]
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                if q.lower() in text.lower():
                    pos = text.lower().find(q.lower())
                    start = max(0, pos - 40)
                    end = min(len(text), pos + len(q) + 60)
                    snippet = ('…' if start > 0 else '') + text[start:end].strip() + ('…' if end < len(text) else '')
                    results.append({"page_idx": page_idx, "snippet": snippet})
                textpage.close()
                page.close()
            except Exception:
                # Skip pages that can't be read (corrupted, access violation, etc.)
                continue
            if len(results) >= 50:
                break
        pdf.close()
    except Exception as e:
        # Return partial results if we got some before the error
        if results:
            return {"book_id": book_id, "query": q, "total": len(results), "results": results}
        raise HTTPException(status_code=500, detail=str(e))

    return {"book_id": book_id, "query": q, "total": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
