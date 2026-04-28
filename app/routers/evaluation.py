from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.evaluation_service import EvaluationService
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.constants.messages import EVALUATION_FAILED
from app.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/run", response_model=EvaluationResponse)
def run_evaluation(request: EvaluationRequest, db: Session = Depends(get_db)):
    try:
        service = EvaluationService(db)
        result = service.evaluate(
            question=request.question,
            context=request.context,
            response=request.response,
            conversation_id=request.conversation_id,
        )
        return result
    except Exception as e:
        logger.error(
            "evaluation failed | error: %s", str(e), exc_info=True
        )
        raise HTTPException(status_code=503, detail=EVALUATION_FAILED)


@router.get("/", response_model=list[EvaluationResponse])
def list_evaluations(
    conversation_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = EvaluationService(db)
    return service.list_evaluations(conversation_id=conversation_id)


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    try:
        service = EvaluationService(db)
        return service.get_evaluation(evaluation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))