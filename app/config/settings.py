from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    groq_model: str = "llama-3.1-8b-instant"
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./researchmind.db"
    llm_provider: str = "groq"
    vector_store_provider: str = "faiss"
    vector_store_path: str = "./vector_store"
    embedding_model: str = "all-MiniLM-L6-v2"
    qdrant_url: str = "http://localhost:6333"
    chroma_path: str = "./chroma_store"
    default_chunk_size: int = 512
    default_chunk_overlap: int = 50
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "researchmind"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 3
    enable_reranking: bool = True
    
    model_config = {"env_file": ".env"}


settings = Settings()