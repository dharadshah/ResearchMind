from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.config.database import Base


class PromptResult(Base):
    __tablename__ = "prompt_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("prompt_templates.id"), nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    filled_prompt: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
    latency_ms: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)