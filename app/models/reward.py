from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import PyObjectId
from bson import ObjectId


class RewardModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    points_required: int
    image_url: Optional[str] = None
    available: bool = None
    created_at: datetime = Field(default_factory= lambda: datetime.now())

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}