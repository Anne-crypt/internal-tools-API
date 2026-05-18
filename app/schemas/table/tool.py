from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import DepartmentType, ToolStatusType


class ToolInDB(BaseModel):
    id: int
    name: str
    description: str | None = None
    vendor: str | None = None
    website_url: str | None = None
    category_id: int
    monthly_cost: Decimal
    active_users_count: int
    owner_department: DepartmentType
    status: ToolStatusType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)