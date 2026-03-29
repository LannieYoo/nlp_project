"""
RAG Engine: Core question-answering pipeline.
Integrates retrieval (HybridRetriever) with Ollama LLM generation.

OOP design for easy conversion to ROS2 node in Part 2.
"""

import os
from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class RAGResponse:
    """Structured response from the RAG engine."""
    answer: str
    sources: List[dict] = field(default_factory=list)  # retrieved chunks used
    query: str = ""
    model: str = ""


class RAGEngine:
    """
    Main RAG engine. Accepts a query, retrieves relevant chunks,
    constructs a prompt with context, and generates a grounded answer.

    OOP structure for ROS2 conversion.
    """

    DEFAULT_MODEL = "qwen2.5:0.5b"
    DEFAULT_DB_PATH = os.path.join("data", "chunks.db")
    DEFAULT_CHROMA_DIR = os.path.join("data", "chroma")
    DEFAULT_TOC_DIR = os.path.join("data", "toc_trees")

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        db_path: str = DEFAULT_DB_PATH,
        chroma_dir: str = DEFAULT_CHROMA_DIR,
        toc_dir: str = DEFAULT_TOC_DIR,
        ollama_host: str = "http://localhost:11434",
        top_k: int = 5,
    ):
        self.model = model
        self.db_path = db_path
        self.chroma_dir = chroma_dir
        self.toc_dir = toc_dir
        self.ollama_host = ollama_host
        self.top_k = top_k

        self._retriever = None
        self._client = None

    @property
    def retriever(self):
        if self._retriever is None:
            from src.retrieval.fusion import HybridRetriever
            self._retriever = HybridRetriever(
                db_path=self.db_path,
                chroma_dir=self.chroma_dir,
                toc_dir=self.toc_dir,
            )
        return self._retriever

    @property
    def client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(host=self.ollama_host)
        return self._client

    def ask(
        self,
        query: str,
        book_filter: Optional[str] = None,
        methods: Optional[List[str]] = None,
    ) -> RAGResponse:
        """
        Main entry: ask a question, get grounded answer with sources.

        Args:
            query: Natural language question.
            book_filter: Optional book_id to restrict search.
            methods: Retrieval methods to use. Default: all four.

        Returns:
            RAGResponse with answer and source references.
        """
        # 1. Retrieve relevant chunks
        chunks = self.retriever.search(
            query=query,
            top_k=self.top_k,
            book_filter=book_filter,
            methods=methods,
        )

        if not chunks:
            return RAGResponse(
                answer="I couldn't find relevant information in the textbooks for this question.",
                sources=[],
                query=query,
                model=self.model,
            )

        # 2. Build context from retrieved chunks
        context = self._build_context(chunks)

        # 3. Build prompt
        system_prompt = self._build_system_prompt(context)

        # 4. Generate answer via Ollama
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
            )
            answer = response["message"]["content"]
        except Exception as e:
            answer = f"Error generating answer: {e}"

        # 5. Format sources for tracing
        sources = []
        for c in chunks:
            sources.append({
                "chunk_id": c.get("chunk_id", ""),
                "book_id": c.get("book_id", ""),
                "page_idx": c.get("page_idx", 0),
                "bbox": c.get("bbox", [0, 0, 0, 0]),
                "chapter": c.get("chapter", ""),
                "section": c.get("section", ""),
                "text_preview": c.get("text", "")[:200],
                "score": c.get("rrf_score", c.get("normalized_score", 0)),
                "method": c.get("method", ""),
            })

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=query,
            model=self.model,
        )

    def _build_context(self, chunks: List[dict]) -> str:
        """Format retrieved chunks into context text for the LLM."""
        parts = []
        for i, c in enumerate(chunks, 1):
            book = c.get("book_id", "unknown").replace("_", " ").title()
            page = c.get("page_idx", 0)
            chapter = c.get("chapter", "")
            text = c.get("text", "")

            ref = f"[Source {i}: {book}, p.{page}"
            if chapter:
                ref += f", {chapter}"
            ref += "]"

            parts.append(f"{ref}\n{text}")

        return "\n\n".join(parts)

    def _build_system_prompt(self, context: str) -> str:
        """Build the system prompt with context."""
        return (
            "You are an AI textbook assistant that answers questions about "
            "AI, machine learning, and NLP concepts. You MUST answer based "
            "ONLY on the provided source documents below. Do NOT use any "
            "external knowledge.\n\n"
            "When answering:\n"
            "1. Provide accurate, detailed explanations from the sources.\n"
            "2. Always cite sources using [Source N] format.\n"
            "3. If the sources don't contain enough information, say so.\n"
            "4. Be concise but thorough.\n\n"
            "--- SOURCE DOCUMENTS ---\n\n"
            f"{context}\n\n"
            "--- END OF SOURCES ---\n\n"
            "Answer the user's question based ONLY on the sources above."
        )

    def ask_simple(self, query: str) -> str:
        """Simple interface: returns just the answer text (for ROS2 node)."""
        response = self.ask(query)
        return response.answer

    def close(self):
        """Cleanup resources."""
        if self._retriever:
            self._retriever.close()
