from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import RequestStatusType


class AccessRequestBase(BaseModel):
    tool_id: int
    business_justification: str


# Quand un employé demande un accès
class AccessRequestCreate(AccessRequestBase):
    pass


# Quand un admin/manager approuve ou refuse
class AccessRequestReview(BaseModel):
    status: RequestStatusType  # approved ou rejected
    processing_notes: str | None = None


class AccessRequestOut(AccessRequestBase):
    id: int
    user_id: int
    status: RequestStatusType
    requested_at: datetime
    processed_at: datetime | None = None
    processed_by: int | None = None
    processing_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)