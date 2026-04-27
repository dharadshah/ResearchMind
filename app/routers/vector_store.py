from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.vector_store import VectorStoreGateway
from app.constants.messages import EMBEDDING_FAILED

router = APIRouter(prefix="/vector-store", tags=["vector-store"])


class AddRequest(BaseModel):
    texts: list[str]
    metadatas: list[dict] = []


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/add")
def add_texts(request: AddRequest):
    try:
        store = VectorStoreGateway.get_store()
        metadatas = request.metadatas or [{} for _ in request.texts]
        store.add(request.texts, metadatas)
        return {"added": len(request.texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=EMBEDDING_FAILED)


@router.post("/search")
def search(request: SearchRequest):
    try:
        store = VectorStoreGateway.get_store()
        results = store.search(request.query, top_k=request.top_k)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-and-rerank")
def search_and_rerank(request: SearchRequest):
    try:
        results = VectorStoreGateway.search_and_rerank(
            request.query, top_k=request.top_k
        )
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))