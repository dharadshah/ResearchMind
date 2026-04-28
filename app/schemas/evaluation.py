from pydantic import BaseModel
from datetime import datetime


class EvaluationRequest(BaseModel):
    question: str
    context: str
    response: str
    conversation_id: int | None = None


class EvaluationResponse(BaseModel):
    id: int
    question: str
    context: str
    response: str
    answer_relevance: float | None
    context_relevance: float | None
    groundedness: float | None
    overall_score: float | None
    conversation_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}