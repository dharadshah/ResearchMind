from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    database_url: str = "sqlite:///./researchmind.db"
    llm_provider: str = "groq"

    model_config = {"env_file": ".env"}


settings = Settings()