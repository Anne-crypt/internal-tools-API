from datetime import date, datetime
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import ForeignKey, Date, DateTime, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.tool import Tool

class CostTracking(Base):
    __tablename__ = "cost_tracking"
    __table_args__ = (
        UniqueConstraint("tool_id", "month_year", name="cost_tracking_tool_id_month_year_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    month_year: Mapped[date] = mapped_column(Date, nullable=False)
    total_monthly_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    active_users_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tool: Mapped["Tool"] = relationship(back_populates="costs")