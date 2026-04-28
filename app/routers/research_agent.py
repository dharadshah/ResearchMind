from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.agents.supervisor_agent import run_supervisor
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.security_service import SecurityService
from app.schemas.conversation import ConversationResponse
from app.constants.messages import (
    AGENT_RUN_FAILED,
    PROMPT_INJECTION_DETECTED,
    INPUT_GUARDRAIL_BLOCKED,
    OUTPUT_GUARDRAIL_BLOCKED,
)
from app.constants.app_constants import GuardrailStatus
from app.config.logging_config import get_logger

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


def run_security_checks(
    question: str,
    db: Session,
) -> tuple[str, SecurityService]:
    security_service = SecurityService(db)

    scan_result = security_service.scan(question)
    if scan_result["blocked"]:
        raise HTTPException(
            status_code=400,
            detail=PROMPT_INJECTION_DETECTED,
        )
    safe_question = scan_result["sanitised_input"]

    input_guardrail = security_service.check_input_guardrail(safe_question)
    if not input_guardrail["is_safe"]:
        logger.warning(
            "research | input guardrail blocked | reason: %s",
            input_guardrail["reason"],
        )
        raise HTTPException(
            status_code=400,
            detail=INPUT_GUARDRAIL_BLOCKED,
        )

    return safe_question, security_service


def run_output_check(
    response: str,
    security_service: SecurityService,
) -> str:
    output_guardrail = security_service.check_output_guardrail(response)
    if not output_guardrail["is_safe"]:
        logger.warning(
            "research | output guardrail blocked | reason: %s",
            output_guardrail["reason"],
        )
        raise HTTPException(
            status_code=400,
            detail=OUTPUT_GUARDRAIL_BLOCKED,
        )
    return response


@router.post("/query", response_model=ResearchResponse)
def query(request: ResearchRequest, db: Session = Depends(get_db)):
    try:
        safe_question, security_service = run_security_checks(
            request.question, db
        )

        conv_service = ConversationService(db)
        memory_service = MemoryService(db)

        if request.conversation_id:
            conversation = conv_service.get_conversation(request.conversation_id)
            memory_context = memory_service.get_full_memory_context(
                request.conversation_id, safe_question
            )
            history = memory_context["window_history"]
        else:
            conversation = conv_service.create_conversation()
            memory_context = {}
            history = []

        result = run_supervisor(
            safe_question,
            history=history,
            memory_context=memory_context,
        )

        run_output_check(result["response"], security_service)

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
    except HTTPException:
        raise
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