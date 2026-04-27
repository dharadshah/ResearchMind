from abc import ABC, abstractmethod
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config.settings import settings
from app.constants.app_constants import VectorStoreProvider
from app.constants.messages import (
    VECTOR_STORE_NOT_INITIALIZED,
    VECTOR_STORE_PROVIDER_NOT_SUPPORTED,
)
from app.services.reranker import Reranker



class VectorStoreBase(ABC):

    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.embedding_model.encode(texts, convert_to_numpy=True)

    @abstractmethod
    def add(self, texts: list[str], metadatas: list[dict]) -> None:
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class FAISSVectorStore(VectorStoreBase):

    def __init__(self):
        super().__init__()
        self.index = None
        self.metadata_store: list[dict] = []
        self.store_path = settings.vector_store_path
        os.makedirs(self.store_path, exist_ok=True)

    def add(self, texts: list[str], metadatas: list[dict]) -> None:
        embeddings = self.embed(texts)
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype(np.float32))
        for i, meta in enumerate(metadatas):
            meta["text"] = texts[i]
            self.metadata_store.append(meta)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if self.index is None:
            raise ValueError(VECTOR_STORE_NOT_INITIALIZED)
        query_embedding = self.embed([query]).astype(np.float32)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata_store):
                result = dict(self.metadata_store[idx])
                result["score"] = float(dist)
                results.append(result)
        return results

    def search_and_rerank(self, query: str, top_k: int = 5) -> list[dict]:
        results = self.search(query, top_k=top_k * 2)
        if not results:
            return results
        return Reranker.rerank(query, results, top_k=top_k)

    def clear(self) -> None:
        self.index = None
        self.metadata_store = []


class ChromaVectorStore(VectorStoreBase):

    def add(self, texts: list[str], metadatas: list[dict]) -> None:
        raise NotImplementedError("Chroma support coming in a future step.")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        raise NotImplementedError("Chroma support coming in a future step.")

    def clear(self) -> None:
        raise NotImplementedError("Chroma support coming in a future step.")


class QdrantVectorStore(VectorStoreBase):

    def add(self, texts: list[str], metadatas: list[dict]) -> None:
        raise NotImplementedError("Qdrant support coming in a future step.")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        raise NotImplementedError("Qdrant support coming in a future step.")

    def clear(self) -> None:
        raise NotImplementedError("Qdrant support coming in a future step.")


class VectorStoreGateway:

    _stores: dict[str, VectorStoreBase] = {}

    @classmethod
    def get_store(cls, provider: str | None = None) -> VectorStoreBase:
        selected = provider or settings.vector_store_provider
        if selected not in cls._stores:
            if selected == VectorStoreProvider.FAISS:
                cls._stores[selected] = FAISSVectorStore()
            elif selected == VectorStoreProvider.CHROMA:
                cls._stores[selected] = ChromaVectorStore()
            elif selected == VectorStoreProvider.QDRANT:
                cls._stores[selected] = QdrantVectorStore()
            else:
                raise ValueError(
                    VECTOR_STORE_PROVIDER_NOT_SUPPORTED.format(provider=selected)
                )
        return cls._stores[selected]
    
    @classmethod
    def search_and_rerank(cls, query: str, top_k: int = 5, provider: str | None = None) -> list[dict]:
        store = cls.get_store(provider)
        if hasattr(store, "search_and_rerank"):
            return store.search_and_rerank(query, top_k=top_k)
        return store.search(query, top_k=top_k)