import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.agents.hitl_supervisor import hitl_supervisor
from app.services.conversation_service import ConversationService
from app.constants.messages import (
    HITL_AWAITING_APPROVAL,
    HITL_RESUMED,
    HITL_THREAD_NOT_FOUND,
    HITL_REJECTED,
    AGENT_RUN_FAILED,
)
from app.constants.app_constants import QueryIntent
from app.config.logging_config import get_logger
from app.services.security_service import SecurityService
from app.constants.messages import PROMPT_INJECTION_DETECTED, INPUT_GUARDRAIL_BLOCKED
from app.routers.research_agent import run_security_checks

logger = get_logger(__name__)

router = APIRouter(prefix="/research/hitl", tags=["human-in-the-loop"])


class HITLStartRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class HITLStartResponse(BaseModel):
    thread_id: str
    question: str
    intent: str
    message: str
    conversation_id: int


class HITLResumeRequest(BaseModel):
    thread_id: str
    approved: bool
    override_intent: str | None = None
    conversation_id: int


class HITLResumeResponse(BaseModel):
    thread_id: str
    question: str
    response: str
    decision: str
    tools_used: list[str]
    agent_used: str
    intent: str
    conversation_id: int


@router.post("/start", response_model=HITLStartResponse)
def start(request: HITLStartRequest, db: Session = Depends(get_db)):
    try:
        safe_question, security_service = run_security_checks(
            request.question, db
        )

        service = ConversationService(db)

        if request.conversation_id:
            conversation = service.get_conversation(request.conversation_id)
            history = service.get_history(request.conversation_id)
        else:
            conversation = service.create_conversation()
            history = []

        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "question": safe_question,
            "history": history,
            "intent": "",
            "response": "",
            "decision": "",
            "tools_used": [],
            "agent_used": "",
        }

        hitl_supervisor.invoke(initial_state, config=config)

        current_state = hitl_supervisor.get_state(config)
        intent = current_state.values.get("intent", "research")

        logger.info("hitl | start | thread_id: %s | intent: %s", thread_id, intent)

        return HITLStartResponse(
            thread_id=thread_id,
            question=safe_question,
            intent=intent,
            message=HITL_AWAITING_APPROVAL,
            conversation_id=conversation.id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("hitl start failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=503, detail=AGENT_RUN_FAILED)


@router.post("/resume", response_model=HITLResumeResponse)
def resume(request: HITLResumeRequest, db: Session = Depends(get_db)):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        if not request.approved:
            logger.info("hitl | resume | rejected | thread_id: %s", request.thread_id)
            raise HTTPException(status_code=400, detail=HITL_REJECTED)

        current_state = hitl_supervisor.get_state(config)
        if not current_state:
            raise HTTPException(
                status_code=404,
                detail=HITL_THREAD_NOT_FOUND.format(thread_id=request.thread_id),
            )

        if request.override_intent:
            if request.override_intent not in QueryIntent.ALL:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid intent. Must be one of: {QueryIntent.ALL}",
                )
            logger.info(
                "hitl | resume | override intent to: %s | thread_id: %s",
                request.override_intent,
                request.thread_id,
            )
            hitl_supervisor.update_state(
                config,
                {"intent": request.override_intent},
            )

        final_state = hitl_supervisor.invoke(None, config=config)

        service = ConversationService(db)
        service.add_turn(
            conversation_id=request.conversation_id,
            question=final_state["question"],
            response=final_state["response"],
            decision=final_state["decision"],
            tools_used=final_state["tools_used"],
            sources=[],
        )

        logger.info(
            "hitl | resume | complete | agent: %s | thread_id: %s",
            final_state["agent_used"],
            request.thread_id,
        )

        return HITLResumeResponse(
            thread_id=request.thread_id,
            question=final_state["question"],
            response=final_state["response"],
            decision=final_state["decision"],
            tools_used=final_state["tools_used"],
            agent_used=final_state["agent_used"],
            intent=final_state["intent"],
            conversation_id=request.conversation_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("hitl resume failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=503, detail=AGENT_RUN_FAILED)