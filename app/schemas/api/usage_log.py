from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class UsageLogBase(BaseModel):
    tool_id: int
    session_date: date
    usage_minutes: int = Field(ge=0)
    actions_count: int = Field(ge=0)


class UsageLogCreate(UsageLogBase):
    user_id: int  # Transmis dans le body ou extrait du token


class UsageLogOut(UsageLogBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
