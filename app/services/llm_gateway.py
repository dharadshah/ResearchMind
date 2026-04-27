from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from app.config.settings import settings
from app.constants.app_constants import LLMProvider
from app.constants.messages import PROVIDER_NOT_SUPPORTED


class LLMProviderBase(ABC):

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        pass


class GroqProvider(LLMProviderBase):

    def get_model(self) -> BaseChatModel:
        return ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )


class LLMGateway:

    _providers: dict[str, LLMProviderBase] = {
        LLMProvider.GROQ: GroqProvider(),
    }

    @classmethod
    def get_model(cls, provider: str | None = None) -> BaseChatModel:
        selected = provider or settings.llm_provider
        if selected not in cls._providers:
            raise ValueError(
                PROVIDER_NOT_SUPPORTED.format(provider=selected)
            )
        return cls._providers[selected].get_model()