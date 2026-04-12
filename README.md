# AI Textbook Q&A System

A RAG-based Educational Question Answering System with Deep Source Tracing, built with a FastAPI backend and a modern React/Vite frontend.

## Overview

This system answers questions about AI, Machine Learning, and NLP concepts using a curated collection of **46 canonical textbooks** as the knowledge base. It features **deep source tracing** — not just citing a book title, but pinpointing the exact page and region where the answer was found, along with a built-in PDF viewer.

## System Architecture

```
+--------------------------------------------------------------------------+
|                          USER (Browser)                                   |
|                     http://localhost:5173                                  |
+-----------------------------------+--------------------------------------+
                                    |  HTTP / JSON
                                    v
+--------------------------------------------------------------------------+
|                     React / Vite Frontend                                 |
|  +----------------+  +------------------+  +---------------------------+  |
|  |  SearchPanel   |  |   SourceCard     |  |   PDF Document Viewer     |  |
|  |  (query input, |  |   (grouped by    |  |   (page rendering,       |  |
|  |   autocomplete,|  |    book, scores, |  |    bbox highlighting,    |  |
|  |   related tags)|  |    View PDF btn) |  |    zoom, fullscreen)     |  |
|  +----------------+  +------------------+  +---------------------------+  |
+-----------------------------------+--------------------------------------+
                                    |  REST API (port 8000)
                                    v
+--------------------------------------------------------------------------+
|                     FastAPI Backend                                        |
|  +------------------------------------------------------------------+    |
|  |  /api/ask  (POST)    ->  RAG Engine                               |    |
|  |  /api/search (POST)  ->  Hybrid Retriever                        |    |
|  |  /api/page-image     ->  PDF Page Renderer                       |    |
|  |  /api/books          ->  Book Metadata                            |    |
|  +------------------------------------------------------------------+    |
|                                                                           |
|  +----------------------------------------------------+                  |
|  |              RAG Engine (engine.py)                  |                  |
|  |  1. Retrieve relevant chunks (HybridRetriever)      |                  |
|  |  2. Build context from top chunks                   |                  |
|  |  3. Generate answer via Ollama LLM                  |                  |
|  |  4. Return answer + sources (0-1 normalized scores) |                  |
|  +------------+-----------------------+----------------+                  |
|               |                       |                                   |
|               v                       v                                   |
|  +------------------+  +--------------------+                             |
|  |  Ollama LLM      |  |  Hybrid Retriever  |                             |
|  |  qwen2.5:0.5b    |  |  (4-Method + RRF)  |                             |
|  |  (~0.4GB)        |  |                    |                             |
|  +------------------+  +--------+-----------+                             |
|                                 |                                         |
|          +----------------------+----------------------+                  |
|          |              |              |               |                  |
|          v              v              v               v                  |
|  +-------------+ +------------+ +--------------+ +------------+          |
|  | 1. FTS5     | | 2. Chroma  | | 3. TOC Tree  | | 4. Meta    |          |
|  |    BM25     | |    DB      | |    Search    | |    Filter   |          |
|  | (keyword +  | | (semantic  | | (section     | | (book/ch/  |          |
|  |  expansion) | |  vectors)  | |  hierarchy)  | |  page/type)|          |
|  +------+------+ +-----+------+ +------+-------+ +-----+------+          |
|         |               |              |               |                  |
|         +-------+-------+-------+------+-------+------+                   |
|                 |                                                          |
|                 v                                                          |
|         +------------------+                                              |
|         |  RRF Fusion      |                                              |
|         |  Reciprocal Rank |                                              |
|         |  k=60, weighted  |                                              |
|         |  + multi-method  |                                              |
|         |  prioritization  |                                              |
|         +------------------+                                              |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                     Data Layer                                             |
|  +----------------+  +----------------+  +----------------------------+   |
|  | SQLite DB      |  | ChromaDB       |  | TOC JSON Trees             |   |
|  | (chunks.db)    |  | (vector store) |  | (per-book TOC hierarchy)   |   |
|  | 85,356 chunks  |  | embeddings     |  | extracted from textbooks   |   |
|  +----------------+  +----------------+  +----------------------------+   |
|                                                                           |
|  +-------------------------------------------------------------------+   |
|  |  MinerU Pipeline (DocLayout-YOLO)                                  |   |
|  |  46 PDF textbooks -> layout detection -> chunking -> indexing      |   |
|  +-------------------------------------------------------------------+   |
+--------------------------------------------------------------------------+
```

### 4-Method Hybrid Retrieval + RRF Fusion

| # | Method | Technology | Description |
|---|--------|------------|-------------|
| 1 | **FTS5 BM25** | SQLite FTS5 | Full-text keyword search with BM25 ranking and abbreviation expansion (e.g., SVM -> "support vector machine") |
| 2 | **Semantic Search** | ChromaDB + sentence-transformers | Vector similarity search using dense embeddings for semantic understanding |
| 3 | **TOC Tree Search** | JSON Tree + SQLite | Hierarchical table-of-contents navigation with keyword overlap scoring |
| 4 | **Metadata Filter** | SQLite | Structured filtering by book, chapter, page range, and content type |

All results are combined using **Reciprocal Rank Fusion (RRF)** with weighted scoring (BM25 and Vector have 2x weight). Final scores are **normalized to 0-1 range** using the theoretical maximum for intuitive display.

## Features

- **Deep Source Tracing and PDF Rendering**: Click any source reference to instantly open the built-in PDF viewer, jumping directly to the exact page and highlighting the source region with bounding boxes.
- **4-Method Hybrid Retrieval**: Combines semantic understanding (ChromaDB) with lexical precision (BM25), structural awareness (TOC), and metadata filtering for highly accurate retrieval.
- **Reciprocal Rank Fusion (RRF)**: Merges results from all retrieval methods into a single ranked list with normalized 0-1 confidence scores.
- **Layout-Aware Parsing**: Textbooks are processed using MinerU (DocLayout-YOLO) to accurately preserve tables, formulas, and figures during the chunking phase.
- **Smart Autocomplete**: Over 370 AI/ML/NLP topics with auto-generated question suggestions and dynamic related topic chips.
- **Interactive PDF Viewer**: Full-featured viewer with zoom (up to 3x), fullscreen mode, page navigation, and responsive bounding box highlights.
- **85,356 Indexed Chunks**: From 46 canonical AI/ML/NLP textbooks including Eisenstein, Bishop, Goodfellow, Jurafsky, and more.
- **Offline and Local-First**: Runs entirely locally using Ollama (qwen2.5:0.5b ~0.4GB), ensuring data privacy with minimal resource usage.
- **ROS 2 Integration**: Designed with decoupled OOP architecture for integration into a multi-node ROS 2 robotics pipeline (voice input to RAG to voice output).

## Quick Start

### 1. Start Ollama and Pull Model

```bash
ollama serve
ollama pull qwen2.5:0.5b
```

### 2. Start the FastAPI Backend

```bash
pip install -r requirements.txt
python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000
```

### 3. Start the React Frontend

```bash
cd frontend
npm install
npm run dev
```

### Or Use the Launcher Script (Windows)

```bash
run.bat
```

This automatically kills existing processes, starts both servers, and opens the browser.

## Project Structure

```
nlp/
├── backend/
│   ├── api/              # FastAPI REST endpoints (server.py)
│   ├── pipeline/         # Data pipeline (chunking, indexing, TOC building)
│   ├── retrieval/        # 4 search methods + RRF fusion engine
│   └── rag/              # Ollama RAG engine (OOP, ROS2-ready)
├── frontend/
│   ├── src/
│   │   ├── components/   # SearchPanel, SourceCard, PdfViewer, Sidebar
│   │   ├── utils/        # Book metadata, API helpers
│   │   └── App.jsx       # Main application shell
│   └── public/           # Static assets
├── ros2/                 # ROS 2 node integration (Part 2)
├── evaluation/           # 20-question evaluation test set
├── guide/                # Project report, presentation, documentation
├── data/                 # SQLite DB, ChromaDB, TOC trees (generated)
└── mineru_output/        # MinerU processed textbook extractions
```

## Team

- **Wang, Peng**
- **Yoo, Hye Ran**

## Course

CST8507: Natural Language Processing - Assignment 2
