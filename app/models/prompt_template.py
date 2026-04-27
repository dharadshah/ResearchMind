from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    system_prompt: Mapped[str] = mapped_column(nullable=True)
    user_prompt: Mapped[str] = mapped_column(nullable=False)
    variables: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)