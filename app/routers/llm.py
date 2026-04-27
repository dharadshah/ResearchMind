from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_gateway import LLMGateway
from app.constants.messages import LLM_UNAVAILABLE
from app.constants.app_constants import LLMProvider


router = APIRouter(prefix="/llm", tags=["llm"])


class ChatRequest(BaseModel):
    message: str
    provider: str = LLMProvider.GROQ


class ChatResponse(BaseModel):
    response: str
    provider: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        model = LLMGateway.get_model(provider=request.provider)
        result = model.invoke(request.message)
        return ChatResponse(
            response=result.content,
            provider=request.provider,
        )
    except Exception as e:
        print(f"LLM error: {e}")
        raise HTTPException(status_code=503, detail=LLM_UNAVAILABLE)