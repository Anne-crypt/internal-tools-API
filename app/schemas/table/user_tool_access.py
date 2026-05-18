from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import AccessStatusType


class UserToolAccessInDB(BaseModel):
    id: int
    user_id: int
    tool_id: int
    granted_at: datetime
    granted_by: int
    revoked_at: datetime | None = None
    revoked_by: int | None = None
    status: AccessStatusType

    model_config = ConfigDict(from_attributes=True)
