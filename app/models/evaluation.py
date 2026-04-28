from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(nullable=False)
    context: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
    answer_relevance: Mapped[float] = mapped_column(nullable=True)
    context_relevance: Mapped[float] = mapped_column(nullable=True)
    groundedness: Mapped[float] = mapped_column(nullable=True)
    overall_score: Mapped[float] = mapped_column(nullable=True)
    conversation_id: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)