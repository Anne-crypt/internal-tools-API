from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.tool import Tool


class UserToolAccess(Base):
    __tablename__ = "user_tool_access"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tool_id",
            "status",
            name="user_tool_access_user_id_tool_id_status_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tool_id: Mapped[int] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), nullable=False
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    granted_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String, default="active")

    # Relations
    user: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="tool_accesses"
    )
    tool: Mapped["Tool"] = relationship(back_populates="accesses")
    granter: Mapped["User"] = relationship(
        foreign_keys=[granted_by], back_populates="granted_accesses"
    )
