from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CategoryInDB(BaseModel):
    id: int
    name: str
    description: str | None = None
    color_hex: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)