from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.research_agent import run_agent
from app.constants.messages import AGENT_RUN_FAILED

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    question: str


class ResearchResponse(BaseModel):
    question: str
    response: str
    decision: str
    tools_used: list[str]
    sources: list[str]
    chunk_count: int


@router.post("/query", response_model=ResearchResponse)
def query(request: ResearchRequest):
    try:
        result = run_agent(request.question)
        return ResearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=503, detail=AGENT_RUN_FAILED)