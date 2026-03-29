"""
AI Textbook Q&A System — Streamlit Application

A RAG-based educational question answering system with deep source tracing.
Users can ask questions about AI/ML concepts and receive answers grounded
in a collection of 46 canonical textbooks, with clickable references
that highlight the exact source region on the original PDF page.
"""

import os
import sys
import ast
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.engine import RAGEngine
from src.ui.pdf_viewer import PDFViewer


# ---------- Page Config ----------
st.set_page_config(
    page_title="AI Textbook Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .answer-box {
        background: #0e1117;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Initialize Session State ----------
if "engine" not in st.session_state:
    st.session_state.engine = None
if "viewer" not in st.session_state:
    st.session_state.viewer = PDFViewer()
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "pdf_views" not in st.session_state:
    st.session_state.pdf_views = {}  # {source_idx: png_bytes}


def get_engine():
    """Lazy-load the RAG engine."""
    if st.session_state.engine is None:
        st.session_state.engine = RAGEngine()
    return st.session_state.engine


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## Settings")

    model_name = st.text_input("Ollama Model", value="qwen2.5:0.5b")
    top_k = st.slider("Number of sources", min_value=1, max_value=20, value=5)

    st.markdown("---")
    st.markdown("## Retrieval Methods")
    use_fts = st.checkbox("BM25 Keyword Search", value=True)
    use_vector = st.checkbox("Semantic Vector Search", value=True)
    use_tree = st.checkbox("TOC Tree Search", value=True)
    use_metadata = st.checkbox("Metadata Filter", value=True)

    st.markdown("---")
    st.markdown("## Book Filter")
    book_filter = st.text_input("Filter by book ID (optional)",
                                placeholder="e.g. jurafsky_slp3")

    st.markdown("---")

    # Show stats
    try:
        engine = get_engine()
        stats = engine.retriever.fts_searcher.indexer.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Books", stats["total_books"])
        with col2:
            st.metric("Chunks", f"{stats['total_chunks']:,}")
    except Exception:
        st.info("Index not loaded yet. Run batch_process first.")


# ---------- Main Content ----------
st.markdown('<p class="main-header">AI Textbook Q&A System</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">'
    'RAG-based educational Q&A with deep source tracing across 46 AI/ML textbooks'
    '</p>',
    unsafe_allow_html=True,
)

# Query input
query = st.text_input(
    "Ask a question about AI, ML, or NLP:",
    placeholder="e.g., What is the transformer attention mechanism?",
    key="query_input",
)

# Build methods list
methods = []
if use_fts:
    methods.append("fts")
if use_vector:
    methods.append("vector")
if use_tree:
    methods.append("tree")
if use_metadata:
    methods.append("metadata")

# Search button
if st.button("Search", type="primary", use_container_width=True) and query:
    if not methods:
        st.warning("Please select at least one retrieval method.")
    else:
        with st.spinner("Searching textbooks and generating answer..."):
            engine = get_engine()
            engine.model = model_name
            engine.top_k = top_k

            response = engine.ask(
                query=query,
                book_filter=book_filter if book_filter else None,
                methods=methods,
            )

        # Store in session state (persists across re-runs)
        st.session_state.last_response = response
        st.session_state.last_query = query
        st.session_state.pdf_views = {}  # reset PDF views for new search


# ---------- Display Results (from session state) ----------
response = st.session_state.last_response
if response:
    # Display answer
    st.markdown("### Answer")
    st.markdown(
        f'<div class="answer-box">{response.answer}</div>',
        unsafe_allow_html=True,
    )

    # Display sources
    if response.sources:
        st.markdown(f"### Source Documents ({len(response.sources)} references)")

        for i, src in enumerate(response.sources):
            book_name = src["book_id"].replace("_", " ").title()
            page = src["page_idx"]
            chapter = src.get("chapter", "")
            section = src.get("section", "")
            preview = src.get("text_preview", "")
            score = src.get("score", 0)
            method = src.get("method", "")

            with st.expander(
                f"[{i+1}] {book_name} - p.{page} | {chapter[:50]}",
                expanded=(i == 0),
            ):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Book:** {book_name}")
                    if chapter:
                        st.markdown(f"**Chapter:** {chapter[:80]}")
                    if section:
                        st.markdown(f"**Section:** {section[:80]}")
                with col2:
                    st.markdown(f"**Page:** {page}")
                    st.markdown(f"**Score:** {score:.3f}")
                with col3:
                    st.markdown(f"**Method:** {method}")

                st.markdown("**Preview:**")
                st.text(preview)

                # PDF View button — uses session_state to persist image
                bbox = src.get("bbox", [0, 0, 0, 0])
                if isinstance(bbox, str):
                    try:
                        bbox = ast.literal_eval(bbox)
                    except Exception:
                        bbox = [0, 0, 0, 0]

                btn_key = f"pdf_{i}"
                if st.button(
                    f"View PDF Page (p.{page})",
                    key=btn_key,
                ):
                    with st.spinner("Rendering PDF page..."):
                        viewer = st.session_state.viewer
                        img_data = viewer.render_page(
                            book_id=src["book_id"],
                            page_idx=page,
                            bbox=bbox,
                            zoom=1.5,
                        )
                        if img_data:
                            st.session_state.pdf_views[i] = img_data
                        else:
                            st.session_state.pdf_views[i] = None

                # Display PDF image if already rendered (persists across re-runs)
                if i in st.session_state.pdf_views:
                    img_data = st.session_state.pdf_views[i]
                    if img_data:
                        st.image(
                            img_data,
                            caption=f"{book_name} - Page {page} (highlighted region)",
                            use_container_width=True,
                        )
                    else:
                        st.warning(
                            "Could not render PDF page. "
                            "Ensure the PDF exists at the expected path."
                        )
