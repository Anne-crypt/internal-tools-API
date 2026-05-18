from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.schemas.enums import DepartmentType, ToolStatusType

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user_tool_access import UserToolAccess
    from app.models.access_request import AccessRequest
    from app.models.usage_log import UsageLog
    from app.models.cost_tracking import CostTracking


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    monthly_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    active_users_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    owner_department: Mapped[DepartmentType] = mapped_column(
        SQLEnum(
            DepartmentType,
            name="department_type",
            inherit_schema=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )  # Type énuméré géré par String/Enum côté API
    status: Mapped[ToolStatusType] = mapped_column(
        SQLEnum(
            ToolStatusType,
            name="tool_status_type",
            inherit_schema=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=ToolStatusType.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relations
    category: Mapped["Category"] = relationship(back_populates="tools")
    accesses: Mapped[list["UserToolAccess"]] = relationship(back_populates="tool")
    requests: Mapped[list["AccessRequest"]] = relationship(back_populates="tool")
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="tool")
    costs: Mapped[list["CostTracking"]] = relationship(back_populates="tool")
