from datetime import datetime
from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
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
    owner_department: DepartmentType
    status: ToolStatusType
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
    owner_department: DepartmentType
    status: ToolStatusType
    active_users_count: int
    total_monthly_cost: float  # Le champ calculé par le Controller
    created_at: datetime
    updated_at: datetime
    usage_metrics: UsageMetrics


class ToolCreateIn(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nom obligatoire de 2 à 100 caractères",
    )
    description: str | None = None
    vendor: str = Field(
        ..., max_length=100, description="Fournisseur obligatoire, max 100 caractères"
    )
    website_url: HttpUrl | None = Field(
        None, description="Doit être une URL valide si fournie"
    )
    category_id: int = Field(..., description="L'ID de la catégorie doit exister")
    monthly_cost: Decimal = Field(
        ..., ge=0, description="Le coût doit être supérieur ou égal à 0"
    )
    owner_department: DepartmentType

    @field_validator("monthly_cost")
    @classmethod
    def validate_decimal_places(cls, v: Decimal) -> Decimal:
        # Vérification des 2 décimales maximum requis
        exponent = v.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("Le coût mensuel ne peut pas avoir plus de 2 décimales")
        return v


class ToolCreateOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    vendor: str
    website_url: str | None = None
    category: str  # Lisa veut le nom de la catégorie, pas l'ID !
    monthly_cost: float
    owner_department: DepartmentType
    status: ToolStatusType
    active_users_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolUpdateIn(BaseModel):
    name: Annotated[str | None, Field(min_length=2, max_length=100)] = None
    description: str | None = None
    vendor: Annotated[str | None, Field(max_length=100)] = None
    website_url: HttpUrl | None = None
    category_id: int | None = None
    monthly_cost: Decimal | None = Field(None, ge=0)
    owner_department: DepartmentType | None = None
    status: ToolStatusType | None = None  # Validation via l'Enum demandé

    @field_validator("monthly_cost")
    @classmethod
    def validate_decimal_places(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and len(str(v).partition(".")[2].rstrip("0")) > 2:
            raise ValueError("Le coût mensuel ne peut pas avoir plus de 2 décimales")
        return v
