"""
TOC Builder: Generates hierarchical Table-of-Contents (PageIndex) trees
from MinerU content_list.json heading entries.

Used by the Tree Search retrieval method — the LLM navigates this tree
top-down to find relevant sections for a given query.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class TOCNode:
    """A node in the Table-of-Contents tree."""
    title: str
    level: int                          # 1 = chapter, 2 = section, 3 = subsection
    page_idx: int                       # page where this heading appears
    children: List["TOCNode"] = field(default_factory=list)
    chunk_ids: List[str] = field(default_factory=list)  # chunks under this section

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "level": self.level,
            "page_idx": self.page_idx,
            "chunk_ids": self.chunk_ids,
            "children": [c.to_dict() for c in self.children],
        }

    def to_outline(self, depth: int = 0) -> str:
        """Return a flat text outline for LLM consumption."""
        indent = "  " * depth
        line = f"{indent}- [{self.level}] {self.title} (p.{self.page_idx})"
        lines = [line]
        for child in self.children:
            lines.append(child.to_outline(depth + 1))
        return "\n".join(lines)


class TOCBuilder:
    """
    Builds a TOC tree from content_list.json by extracting headings
    (entries with text_level field).
    """

    def __init__(self, book_id: str):
        self.book_id = book_id

    def build_from_content_list(self, content_list_path: str) -> List[TOCNode]:
        """Parse content_list.json and build the TOC tree."""
        with open(content_list_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)

        headings = []
        for entry in entries:
            text_level = entry.get("text_level")
            text = entry.get("text", "").strip()
            if text_level is not None and text:
                headings.append({
                    "title": text,
                    "level": text_level,
                    "page_idx": entry.get("page_idx", 0),
                })

        return self._build_tree(headings)

    def build_from_chunks(self, chunks) -> List[TOCNode]:
        """Build TOC tree from a list of Chunk objects (heading chunks)."""
        headings = []
        for chunk in chunks:
            if chunk.text_level is not None:
                headings.append({
                    "title": chunk.text,
                    "level": chunk.text_level,
                    "page_idx": chunk.page_idx,
                    "chunk_id": chunk.chunk_id,
                })
        return self._build_tree(headings)

    def _build_tree(self, headings: list) -> List[TOCNode]:
        """Convert a flat list of headings into a tree structure."""
        if not headings:
            return []

        root_nodes: List[TOCNode] = []
        stack: List[TOCNode] = []  # stack for building hierarchy

        for h in headings:
            node = TOCNode(
                title=h["title"],
                level=h["level"],
                page_idx=h["page_idx"],
                chunk_ids=[h.get("chunk_id", "")],
            )

            # Pop stack until we find parent (lower level)
            while stack and stack[-1].level >= node.level:
                stack.pop()

            if stack:
                stack[-1].children.append(node)
            else:
                root_nodes.append(node)

            stack.append(node)

        return root_nodes

    def save_tree(self, tree: List[TOCNode], output_path: str):
        """Save the TOC tree as JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data = {
            "book_id": self.book_id,
            "toc": [node.to_dict() for node in tree],
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_tree(tree_path: str) -> Dict:
        """Load a TOC tree from JSON file."""
        with open(tree_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def tree_to_outline(tree_data: Dict) -> str:
        """Convert a saved tree dict to a flat text outline for LLM."""
        def _node_to_text(node: dict, depth: int = 0) -> str:
            indent = "  " * depth
            line = f"{indent}- {node['title']} (p.{node['page_idx']})"
            lines = [line]
            for child in node.get("children", []):
                lines.append(_node_to_text(child, depth + 1))
            return "\n".join(lines)

        lines = [f"Book: {tree_data.get('book_id', 'unknown')}"]
        for node in tree_data.get("toc", []):
            lines.append(_node_to_text(node))
        return "\n".join(lines)
