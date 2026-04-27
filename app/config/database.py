from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from langgraph.checkpoint.memory import MemorySaver
from app.config.settings import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


checkpointer = MemorySaver()