from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.research_tools import (
    search_documents,
    search_wikipedia,
    search_arxiv,
    web_search,
)
from app.constants.messages import TOOL_EXECUTION_FAILED
from app.constants.app_constants import ToolName

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolRequest(BaseModel):
    query: str


@router.post("/vector-search")
def tool_vector_search(request: ToolRequest):
    try:
        result = search_documents.invoke(request.query)
        return {"tool": ToolName.VECTOR_SEARCH, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wikipedia")
def tool_wikipedia(request: ToolRequest):
    try:
        result = search_wikipedia.invoke(request.query)
        return {"tool": ToolName.WIKIPEDIA, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/arxiv")
def tool_arxiv(request: ToolRequest):
    try:
        result = search_arxiv.invoke(request.query)
        return {"tool": ToolName.ARXIV, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web-search")
def tool_web_search(request: ToolRequest):
    try:
        result = web_search.invoke(request.query)
        return {"tool": ToolName.WEB_SEARCH, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))