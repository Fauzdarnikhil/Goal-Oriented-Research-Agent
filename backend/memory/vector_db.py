import os
from typing import List, Dict, Any, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PERSIST_DIR = os.path.join(DATA_DIR, "chroma_store")

os.makedirs(PERSIST_DIR, exist_ok=True)


class ResearchMemory:
    """
    Simple wrapper around Chroma + HuggingFaceEmbeddings for agent memory.
    Stores arbitrary text + metadata and supports similarity search.
    """

    def __init__(self, collection_name: str = "research_memory"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=PERSIST_DIR,
        )

    def add_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        metadata = metadata or {}
    
        clean_metadata = {}
        for k, v in metadata.items():
            if isinstance(v, list):
                clean_metadata[k] = ", ".join(str(x) for x in v)
            else:
                clean_metadata[k] = v
    
        doc = Document(page_content=content, metadata=clean_metadata)
        self.vector_store.add_documents([doc])
    
        try:
            if hasattr(self.vector_store, "persist"):
                self.vector_store.persist()
        except:
            pass

    def search_memory(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        results = self.vector_store.similarity_search(query, k=k)
        out = []
        for r in results:
            out.append(
                {
                    "content": r.page_content,
                    "metadata": r.metadata,
                }
            )
        return out

    def all_memory(self, k: int = 50) -> List[Dict[str, Any]]:
        results = self.vector_store.similarity_search("", k=k)
        out = []
        for r in results:
            out.append(
                {
                    "content": r.page_content,
                    "metadata": r.metadata,
                }
            )
        return out


# Global singleton instance for app-wide use
global_memory = ResearchMemory()
