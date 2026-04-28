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

class ToolName:
    VECTOR_SEARCH = "search_documents"
    WIKIPEDIA = "search_wikipedia"
    ARXIV = "search_arxiv"
    WEB_SEARCH = "web_search"

    ALL = [VECTOR_SEARCH, WIKIPEDIA, ARXIV, WEB_SEARCH]

class AgentDecision:
    RELEVANT = "relevant"
    NOT_RELEVANT = "not_relevant"
    GENERATE = "generate"
    FALLBACK = "fallback"

class AgentNode:
    TOOL_SELECTOR = "tool_selector"
    EXECUTE_TOOL = "execute_tool"
    GRADE = "grade"
    GENERATE = "generate"
    FALLBACK = "fallback"

class AgentName:
    SUPERVISOR = "supervisor"
    RESEARCH = "research"
    SUMMARISATION = "summarisation"
    FACT_CHECK = "fact_check"


class QueryIntent:
    RESEARCH = "research"
    SUMMARISE = "summarise"
    FACT_CHECK = "fact_check"

    ALL = [RESEARCH, SUMMARISE, FACT_CHECK]

class EvaluationMetric:
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_RELEVANCE = "context_relevance"
    GROUNDEDNESS = "groundedness"

    ALL = [ANSWER_RELEVANCE, CONTEXT_RELEVANCE, GROUNDEDNESS]

class SecurityFlag:
    PROMPT_INJECTION = "prompt_injection"
    PII_DETECTED = "pii_detected"
    CLEAN = "clean"

    ALL = [PROMPT_INJECTION, PII_DETECTED, CLEAN]


PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard your instructions",
    "forget your instructions",
    "you are now",
    "act as if",
    "pretend you are",
    "override instructions",
    "system prompt",
    "jailbreak",
    "do anything now",
    "dan mode",
    "bypass",
    "ignore your training",
    "new persona",
    "simulate",
]

class GuardrailStatus:
    PASSED = "passed"
    BLOCKED = "blocked"
    ERROR = "error"

TECHNICAL_TERMS_ALLOWLIST = {
    "faiss", "bert", "gpt", "llm", "rag", "api", "sql", "nosql",
    "langchain", "langgraph", "llamaindex", "docker", "python",
    "fastapi", "gradio", "openai", "groq", "ollama", "chroma",
    "qdrant", "pinecone", "huggingface", "pytorch", "tensorflow",
    "researchmind", "spacy", "presidio", "uvicorn", "sqlalchemy",
    "pydantic", "arxiv", "wikipedia", "duckduckgo",
}