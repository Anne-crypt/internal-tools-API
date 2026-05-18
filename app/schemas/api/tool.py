from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import DepartmentType, ToolStatusType


class ToolBase(BaseModel):
    name: str
    description: str | None = None
    vendor: str | None = None
    website_url: str | None = None
    category_id: int
    monthly_cost: Decimal = Field(ge=0, description="Le coût doit être positif")
    owner_department: DepartmentType
    status: ToolStatusType = ToolStatusType.ACTIVE


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    vendor: str | None = None
    website_url: str | None = None
    category_id: int | None = None
    monthly_cost: Decimal | None = Field(None, ge=0)
    owner_department: DepartmentType | None = None
    status: ToolStatusType | None = None


# Sortie brute (miroir du modèle)
class ToolOut(ToolBase):
    id: int
    active_users_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Sortie enrichie pour le filtre de Sarah
class ToolWithCategoryNameOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    vendor: str | None = None
    category: str  # Le nom de la catégorie via le JOIN
    monthly_cost: float
    owner_department: str
    status: str
    website_url: str | None = None
    active_users_count: int
    created_at: datetime


class ToolPaginatedResponse(BaseModel):
    data: list[ToolWithCategoryNameOut]
    total: int
    filtered: int
    filters_applied: dict[str, str | float | None]


class UsageMetricsDetail(BaseModel):
    total_sessions: int
    avg_session_minutes: int


class UsageMetrics(BaseModel):
    last_30_days: UsageMetricsDetail


class ToolDetailOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    vendor: str | None = None
    website_url: str | None = None
    category: str
    monthly_cost: float
    owner_department: str
    status: str
    active_users_count: int
    total_monthly_cost: float  # Le champ calculé par le Controller
    created_at: datetime
    updated_at: datetime
    usage_metrics: UsageMetrics

    model_config = ConfigDict(from_attributes=True)