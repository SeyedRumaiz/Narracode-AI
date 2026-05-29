"""Optional vector storage integration for code search and similarity history."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except ImportError:  # pragma: no cover
    chromadb = None
    Settings = None
    embedding_functions = None


class CodeVectorStore:
    """Lightweight Chromadb wrapper for code snippet indexing."""

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or os.getenv("VECTOR_PERSIST_DIR", "./backend/.vectors")
        self.client = self._build_client()
        self.collection = self._ensure_collection()

    def _build_client(self):
        if chromadb is None:
            return None
        return chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.persist_directory))

    def _ensure_collection(self):
        if self.client is None:
            return None
        return self.client.get_or_create_collection("code_analysis", embedding_function=embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-3-small"))

    def add_snippet(self, code: str, metadata: Dict[str, Any]) -> None:
        if self.collection is None:
            return
        self.collection.add(documents=[code], metadatas=[metadata], ids=[metadata.get("id", "")])
        self.client.persist()

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        if self.collection is None:
            return []
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results.get("documents", [])
