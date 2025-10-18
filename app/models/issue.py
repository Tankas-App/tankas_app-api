from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class CommentModel(BaseModel):
    user_id: PyObjectId
    username: str
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class LocationModel(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class IssueModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    title: str
    description: str
    location: LocationModel
    picture_url: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    difficulty: str = "medium"  # easy, medium, hard
    status: str = "open"  # open, in_progress, resolved
    points_assigned: int = 0
    reward_listing: Optional[str] = None
    comments: List[CommentModel] = []
    resolved_by: Optional[PyObjectId] = None
    resolved_at: Optional[datetime] = None
    resolution_picture_url: Optional[str] = None
    resolution_location: Optional[dict] = None  # GeoJSON format
    verification_distance_meters: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}