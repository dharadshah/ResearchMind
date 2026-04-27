from pydantic import BaseModel
from datetime import datetime


class ConversationTurnResponse(BaseModel):
    id: int
    conversation_id: int
    question: str
    response: str
    decision: str | None
    tools_used: str | None
    sources: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    updated_at: datetime
    turns: list[ConversationTurnResponse] = []

    model_config = {"from_attributes": True}


class ConversationCreateRequest(BaseModel):
    title: str | None = None