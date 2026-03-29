"""
FastAPI Backend Server for AI Textbook Q&A System.

Wraps the existing RAG engine as REST API and serves PDFs statically.
"""

import os
import sys
import sqlite3
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from backend.rag.engine import RAGEngine
from backend.ui.pdf_viewer import PDFViewer

# --------------- Globals ---------------
_engine: Optional[RAGEngine] = None
_viewer: Optional[PDFViewer] = None

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


def get_viewer() -> PDFViewer:
    global _viewer
    if _viewer is None:
        _viewer = PDFViewer(pdf_base_dir=PDF_BASE_DIR)
    return _viewer


# --------------- Pydantic Models ---------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    model: str = "qwen2.5:0.5b"
    book_filter: Optional[str] = None
    methods: List[str] = ["fts", "vector", "tree", "metadata"]


class HighlightInfo(BaseModel):
    """PDF-space coordinates for bbox highlight overlay."""
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


# --------------- Highlight Computation ---------------
def compute_highlight(source: dict) -> Optional[HighlightInfo]:
    """
    Compute PDF-space highlight coordinates for a source.
    Uses PyMuPDF text search (most accurate) with bbox fallback.
    """
    viewer = get_viewer()
    book_id = source.get("book_id", "")
    page_idx = source.get("page_idx", 0)
    text_preview = source.get("text_preview", "")
    bbox = source.get("bbox", [0, 0, 0, 0])

    pdf_path = viewer.get_pdf_path(book_id)
    if not pdf_path:
        return None

    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        if page_idx >= len(doc):
            doc.close()
            return None

        page = doc[page_idx]
        page_w = page.rect.width
        page_h = page.rect.height
        rect = None

        # Strategy 1: Text search
        if text_preview:
            rects = viewer._find_text_rects(page, text_preview)
            if rects:
                rect = viewer._merge_rects(rects, page)

        # Strategy 2: Bbox conversion fallback
        if rect is None and bbox and len(bbox) == 4 and any(b > 0 for b in bbox):
            rect = viewer._convert_bbox_to_pdf(bbox, page, book_id, page_idx)

        doc.close()

        if rect and rect.width > 0 and rect.height > 0:
            return HighlightInfo(
                x=rect.x0,
                y=rect.y0,
                width=rect.width,
                height=rect.height,
                page_width=page_w,
                page_height=page_h,
            )
    except Exception as e:
        print(f"Highlight computation error: {e}")

    return None


# --------------- App ---------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if _engine:
        _engine.close()


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

        viewer = get_viewer()
        books = []
        for (bid,) in rows:
            title = bid.replace("_", " ").title()
            has_pdf = viewer.get_pdf_path(bid) is not None
            books.append(BookInfo(book_id=bid, title=title, has_pdf=has_pdf))
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


@app.get("/pdf/{book_id}")
def serve_pdf(book_id: str):
    """Serve the original PDF file for a given book."""
    viewer = get_viewer()
    pdf_path = viewer.get_pdf_path(book_id)
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF not found: {book_id}")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={"Accept-Ranges": "bytes"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
