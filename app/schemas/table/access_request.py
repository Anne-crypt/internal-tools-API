from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import RequestStatusType


class AccessRequestInDB(BaseModel):
    id: int
    user_id: int
    tool_id: int
    business_justification: str
    status: RequestStatusType
    requested_at: datetime
    processed_at: datetime | None = None
    processed_by: int | None = None
    processing_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
