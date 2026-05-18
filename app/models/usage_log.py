from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.tool import Tool


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tool_id: Mapped[int] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), nullable=False
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    usage_minutes: Mapped[int] = mapped_column(Integer, default=0)
    actions_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tool: Mapped["Tool"] = relationship(back_populates="usage_logs")
