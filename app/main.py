from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.database import Base, engine
from app.routers import llm, prompt_studio


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ResearchMind",
    description="AI-powered research assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(llm.router)
app.include_router(prompt_studio.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "app": "ResearchMind"}