from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class UsageLogInDB(BaseModel):
    id: int
    user_id: int
    tool_id: int
    session_date: date
    usage_minutes: int
    actions_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
