from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LocationCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class IssueCreate(BaseModel):
    title: str
    description: str
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    priority: str = "medium"
    difficulty: str = "medium"

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None

class CommentCreate(BaseModel):
    comment: str

class CommentResponse(BaseModel):
    user_id: str
    username: str
    comment: str
    created_at: datetime

class IssueResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    latitude: float
    longitude: float
    picture_url: Optional[str] = None
    priority: str
    difficulty: str
    status: str
    points_assigned: int
    reward_listing: Optional[str] = None
    comments: List[CommentResponse] = []
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime