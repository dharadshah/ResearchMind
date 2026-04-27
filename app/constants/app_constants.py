# app/constants/app_constants.py

MAX_QUERY_LENGTH = 2000
MAX_DOCUMENT_SIZE_MB = 20
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 5


class LLMProvider:
    GROQ = "groq"
    OLLAMA = "ollama"

    ALL = [GROQ, OLLAMA]


class DocumentStatus:
    PENDING = "pending"
    INGESTED = "ingested"
    FAILED = "failed"


class QueryIntent:
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    SUMMARISE = "summarise"
    COMPARE = "compare"

    ALL = [FACTUAL, ANALYTICAL, SUMMARISE, COMPARE]

class VectorStoreProvider:
    FAISS = "faiss"
    CHROMA = "chroma"
    QDRANT = "qdrant"

    ALL = [FAISS, CHROMA, QDRANT]

class DocumentType:
    PDF = "pdf"
    TEXT = "text"
    URL = "url"

    ALL = [PDF, TEXT, URL]