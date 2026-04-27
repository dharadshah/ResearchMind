from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.document_indexer import DocumentIndexer
from app.schemas.document import DocumentResponse, URLIngestRequest, TextIngestRequest

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    indexer = DocumentIndexer(db)
    return indexer.list_documents()


@router.post("/ingest/pdf", response_model=DocumentResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    indexer = DocumentIndexer(db)
    return indexer.ingest_pdf(contents, file.filename)


@router.post("/ingest/text", response_model=DocumentResponse)
def ingest_text(request: TextIngestRequest, db: Session = Depends(get_db)):
    indexer = DocumentIndexer(db)
    return indexer.ingest_text(request.text, request.name)


@router.post("/ingest/url", response_model=DocumentResponse)
def ingest_url(request: URLIngestRequest, db: Session = Depends(get_db)):
    indexer = DocumentIndexer(db)
    return indexer.ingest_url(request.url, request.name)