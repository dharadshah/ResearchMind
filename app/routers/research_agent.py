from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.agents.supervisor_agent import run_supervisor
from app.services.conversation_service import ConversationService
from app.schemas.conversation import ConversationResponse
from app.constants.messages import AGENT_RUN_FAILED
from app.config.logging_config import get_logger
from app.services.memory_service import MemoryService


logger = get_logger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class ResearchResponse(BaseModel):
    question: str
    response: str
    decision: str
    tools_used: list[str]
    agent_used: str
    intent: str
    sources: list[str]
    chunk_count: int
    conversation_id: int


@router.post("/query", response_model=ResearchResponse)
def query(request: ResearchRequest, db: Session = Depends(get_db)):
    try:
        conv_service = ConversationService(db)
        memory_service = MemoryService(db)

        if request.conversation_id:
            conversation = conv_service.get_conversation(request.conversation_id)
            memory_context = memory_service.get_full_memory_context(
                request.conversation_id, request.question
            )
            history = memory_context["window_history"]
        else:
            conversation = conv_service.create_conversation()
            memory_context = {}
            history = []

        result = run_supervisor(
            request.question,
            history=history,
            memory_context=memory_context,
        )

        conv_service.add_turn(
            conversation_id=conversation.id,
            question=result["question"],
            response=result["response"],
            decision=result["decision"],
            tools_used=result["tools_used"],
            sources=result["sources"],
        )

        memory_service.store_turn_in_vector_memory(
            conversation_id=conversation.id,
            question=result["question"],
            response=result["response"],
        )

        return ResearchResponse(
            **result,
            conversation_id=conversation.id,
        )
    except Exception as e:
        logger.error(
            "research query failed | question: %s | error: %s",
            request.question,
            str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=503, detail=AGENT_RUN_FAILED)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.list_conversations()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    try:
        service = ConversationService(db)
        return service.get_conversation(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))