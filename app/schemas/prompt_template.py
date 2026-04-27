from pydantic import BaseModel
from datetime import datetime


class PromptTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    system_prompt: str | None = None
    user_prompt: str
    variables: str | None = None


class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None
    system_prompt: str | None
    user_prompt: str
    variables: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptRunRequest(BaseModel):
    template_id: int
    provider: str = "groq"
    variable_values: dict[str, str] = {}


class PromptRunResponse(BaseModel):
    template_id: int
    provider: str
    filled_prompt: str
    response: str
    latency_ms: int