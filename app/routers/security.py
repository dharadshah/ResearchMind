from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.security_service import SecurityService
from app.schemas.security import (
    SecurityScanRequest,
    SecurityScanResponse,
    GuardrailCheckResponse,
    SecurityLogResponse,
)
from app.constants.messages import SECURITY_SCAN_FAILED
from app.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/scan", response_model=SecurityScanResponse)
def scan(request: SecurityScanRequest, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        result = service.scan(request.text)
        return SecurityScanResponse(**result)
    except Exception as e:
        logger.error("security scan failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=503, detail=SECURITY_SCAN_FAILED)


@router.post("/guardrail/input", response_model=GuardrailCheckResponse)
def check_input_guardrail(request: SecurityScanRequest, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        result = service.check_input_guardrail(request.text)
        return GuardrailCheckResponse(**result)
    except Exception as e:
        logger.error(
            "input guardrail check failed | error: %s", str(e), exc_info=True
        )
        raise HTTPException(status_code=503, detail=SECURITY_SCAN_FAILED)


@router.post("/guardrail/output", response_model=GuardrailCheckResponse)
def check_output_guardrail(request: SecurityScanRequest, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        result = service.check_output_guardrail(request.text)
        return GuardrailCheckResponse(**result)
    except Exception as e:
        logger.error(
            "output guardrail check failed | error: %s", str(e), exc_info=True
        )
        raise HTTPException(status_code=503, detail=SECURITY_SCAN_FAILED)


@router.get("/logs", response_model=list[SecurityLogResponse])
def list_logs(blocked_only: bool = False, db: Session = Depends(get_db)):
    service = SecurityService(db)
    return service.list_logs(blocked_only=blocked_only)


@router.get("/logs/{log_id}", response_model=SecurityLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        return service.get_log(log_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))