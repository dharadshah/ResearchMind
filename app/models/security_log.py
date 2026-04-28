from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_input: Mapped[str] = mapped_column(nullable=False)
    sanitised_input: Mapped[str] = mapped_column(nullable=True)
    flag: Mapped[str] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(nullable=True)
    pii_entities: Mapped[str] = mapped_column(nullable=True)
    blocked: Mapped[bool] = mapped_column(default=False)
    input_guardrail_status: Mapped[str] = mapped_column(nullable=True)
    input_guardrail_reason: Mapped[str] = mapped_column(nullable=True)
    output_guardrail_status: Mapped[str] = mapped_column(nullable=True)
    output_guardrail_reason: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)