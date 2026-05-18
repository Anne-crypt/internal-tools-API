from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CostTrackingInDB(BaseModel):
    id: int
    tool_id: int
    month_year: date
    total_monthly_cost: Decimal
    active_users_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
