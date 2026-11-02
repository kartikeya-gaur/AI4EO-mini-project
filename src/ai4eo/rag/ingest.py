"""Glue to LangChain's splitter.

NOT RUN YET: written without network access and without langchain installed.
Install with `pip install -e ".[rag]"`, then check the current LangChain text-splitter
docs for the import path and arguments before relying on this.

Indexing into Qdrant is the next step and is not written yet: it needs the embedding
model choice first. Embeddings from different models are not comparable, so record the
embedding model name and dimension in docs/decisions.md and in the collection name.
"""

from __future__ import annotations

from ai4eo.rag.chunks import SplitFn


def recursive_splitter(chunk_size: int, chunk_overlap: int) -> SplitFn:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text
