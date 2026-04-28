from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.research_tools import (
    search_documents,
    search_wikipedia,
    search_arxiv,
    web_search,
)
from app.constants.app_constants import ToolName
from app.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])


class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None


class ToolRequest(BaseModel):
    query: str


@router.post("/vector-search")
def tool_vector_search(request: VectorSearchRequest):
    try:
        result = search_documents.invoke({
            "query": request.query,
            "top_k": request.top_k,
            "source_filter": request.source_filter,
        })
        return {"tool": ToolName.VECTOR_SEARCH, "result": result}
    except Exception as e:
        logger.error("tool vector search failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wikipedia")
def tool_wikipedia(request: ToolRequest):
    try:
        result = search_wikipedia.invoke(request.query)
        return {"tool": ToolName.WIKIPEDIA, "result": result}
    except Exception as e:
        logger.error("tool wikipedia failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/arxiv")
def tool_arxiv(request: ToolRequest):
    try:
        result = search_arxiv.invoke(request.query)
        return {"tool": ToolName.ARXIV, "result": result}
    except Exception as e:
        logger.error("tool arxiv failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web-search")
def tool_web_search(request: ToolRequest):
    try:
        result = web_search.invoke(request.query)
        return {"tool": ToolName.WEB_SEARCH, "result": result}
    except Exception as e:
        logger.error("tool web search failed | error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))