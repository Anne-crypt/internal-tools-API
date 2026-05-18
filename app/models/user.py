from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user_tool_access import UserToolAccess
    from app.models.access_request import AccessRequest


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    department: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="employee")
    status: Mapped[str] = mapped_column(String, default="active")
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tool_accesses: Mapped[list["UserToolAccess"]] = relationship(
        foreign_keys="[UserToolAccess.user_id]", back_populates="user"
    )
    granted_accesses: Mapped[list["UserToolAccess"]] = relationship(
        foreign_keys="[UserToolAccess.granted_by]", back_populates="granter"
    )
    requests: Mapped[list["AccessRequest"]] = relationship(
        foreign_keys="[AccessRequest.user_id]", back_populates="user"
    )
