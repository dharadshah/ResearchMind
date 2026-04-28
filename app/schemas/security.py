from pydantic import BaseModel
from datetime import datetime


class SecurityScanRequest(BaseModel):
    text: str


class SecurityScanResponse(BaseModel):
    original_input: str
    sanitised_input: str
    flag: str
    reason: str | None
    pii_entities: list[str]
    blocked: bool


class GuardrailCheckResponse(BaseModel):
    is_safe: bool
    reason: str | None
    status: str


class SecurityLogResponse(BaseModel):
    id: int
    original_input: str
    sanitised_input: str | None
    flag: str
    reason: str | None
    pii_entities: str | None
    blocked: bool
    input_guardrail_status: str | None
    input_guardrail_reason: str | None
    output_guardrail_status: str | None
    output_guardrail_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}