from pydantic import BaseModel, Field
from typing import Optional

class RewardCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    points_required: int = Field(..., ge=1)
    image_url: Optional[str] = None

class RewardResponse(RewardCreate):
    id: str
    available: bool