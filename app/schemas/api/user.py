from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.enums import DepartmentType, UserRoleType, UserStatusType


# Champs communs pour la manipulation d'un User via l'API
class UserBase(BaseModel):
    name: str
    email: EmailStr
    department: DepartmentType
    role: UserRoleType = UserRoleType.EMPLOYEE
    status: UserStatusType = UserStatusType.ACTIVE
    hire_date: date | None = None


# Ce que l'API reçoit à la création
class UserCreate(UserBase):
    pass


# Ce que l'API reçoit pour une mise à jour (tous les champs deviennent optionnels)
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    department: DepartmentType | None = None
    role: UserRoleType | None = None
    status: UserStatusType | None = None
    hire_date: date | None = None


# Ce que l'API renvoie (Contrat de sortie)
class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)