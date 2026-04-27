from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.prompt_studio import PromptStudioService
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptRunRequest,
    PromptRunResponse,
)
from app.constants.messages import PROMPT_RUN_FAILED

router = APIRouter(prefix="/prompt-studio", tags=["prompt-studio"])


@router.post("/templates", response_model=PromptTemplateResponse)
def create_template(data: PromptTemplateCreate, db: Session = Depends(get_db)):
    try:
        service = PromptStudioService(db)
        return service.create_template(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=list[PromptTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    service = PromptStudioService(db)
    return service.get_all_templates()


@router.get("/templates/{template_id}", response_model=PromptTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    try:
        service = PromptStudioService(db)
        return service.get_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/run", response_model=PromptRunResponse)
def run_prompt(request: PromptRunRequest, db: Session = Depends(get_db)):
    try:
        service = PromptStudioService(db)
        result = service.run_prompt(request)
        return PromptRunResponse(
            template_id=result.template_id,
            provider=result.provider,
            filled_prompt=result.filled_prompt,
            response=result.response,
            latency_ms=result.latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=PROMPT_RUN_FAILED)