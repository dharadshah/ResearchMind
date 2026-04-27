from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    name: str
    source: str
    document_type: str
    chunk_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class URLIngestRequest(BaseModel):
    url: str
    name: str


class TextIngestRequest(BaseModel):
    text: str
    name: str