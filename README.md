# AI Textbook Q&A System

A RAG-based Educational Question Answering System with Deep Source Tracing.

## Overview

This system answers questions about AI, Machine Learning, and NLP concepts using a curated collection of **46 canonical textbooks** as the knowledge base. It features **deep source tracing** — not just citing a book title, but pinpointing the exact page and region where the answer was found.

## Architecture

### 4-Method Hybrid Retrieval + RRF Fusion

| # | Method | Description |
|---|--------|-------------|
| 1 | **SQLite FTS5 (BM25)** | Full-text keyword search with BM25 ranking |
| 2 | **ChromaDB (Semantic)** | Vector search using sentence-transformers embeddings |
| 3 | **TOC Tree Search** | Hierarchical table-of-contents navigation |
| 4 | **Metadata Filter** | Structured filtering by book, chapter, page, content type |

Results from all methods are combined using **Reciprocal Rank Fusion (RRF)**.

### Key Features

- **Deep Source Tracing**: Click any source reference to see the original PDF page with the source region highlighted
- **Layout-Aware Parsing**: MinerU (DocLayout-YOLO) preserves tables, formulas, and figures
- **85,356 chunks** indexed from 46 textbooks
- **Streamlit UI** for interactive querying
- **Low Resource**: Runs locally with Ollama `qwen2.5:0.5b` (~0.4GB)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Batch Processing (if needed)

```bash
python -m src.pipeline.batch_process
```

### 3. Start Ollama

```bash
ollama serve
ollama pull qwen2.5:0.5b
```

### 4. Launch Streamlit UI

```bash
streamlit run src/app.py
```

## Project Structure

```
nlp/
├── src/
│   ├── pipeline/         # Data pipeline (chunking, indexing, TOC)
│   ├── retrieval/        # 4 search methods + RRF fusion
│   ├── rag/              # Ollama RAG engine (OOP)
│   ├── ui/               # PDF viewer with bbox highlight
│   ├── evaluation/       # 20-question evaluation
│   └── app.py            # Streamlit main app
├── ros2/                 # ROS2 node (Part 2)
├── evaluation/           # Test questions
├── data/                 # Generated indexes (gitignored)
└── mineru_output/        # MinerU processed textbooks (gitignored)
```

## Team

- **Wang, Peng**
- **Yoo, Hye Ran**

## Course

CST8507: Natural Language Processing — Assignment 2
