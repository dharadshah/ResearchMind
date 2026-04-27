from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./researchmind.db"
    llm_provider: str = "groq"

    model_config = {"env_file": ".env"}


settings = Settings()