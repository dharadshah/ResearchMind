from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.database import Base, engine, _checkpointer_cm
from app.config.logging_config import setup_logging
from app.routers import (
    llm,
    prompt_studio,
    vector_store,
    document_indexer,
    tools,
    research_agent,
    hitl,
    evaluation,
    security,
)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    _checkpointer_cm.__exit__(None, None, None)


app = FastAPI(
    title="ResearchMind",
    description="AI-powered research assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(llm.router)
app.include_router(prompt_studio.router)
app.include_router(vector_store.router)
app.include_router(document_indexer.router)
app.include_router(tools.router)
app.include_router(research_agent.router)
app.include_router(hitl.router)
app.include_router(evaluation.router)
app.include_router(security.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "app": "ResearchMind"}