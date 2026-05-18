from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.enums import DepartmentType, UserRoleType, UserStatusType


class UserInDB(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: DepartmentType
    role: UserRoleType
    status: UserStatusType
    hire_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
