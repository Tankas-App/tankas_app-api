from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VolunteerCreate(BaseModel):
    contribution: Optional[str] = None  # Optional message when volunteering

class VolunteerResponse(BaseModel):
    id: str
    issue_id: str
    user_id: str
    username: str
    avatar: Optional[str] = None
    volunteered_at: datetime
    status: str
    contribution: Optional[str] = None

class DiscussionMessage(BaseModel):
    message: str

class DiscussionResponse(BaseModel):
    id: str
    user_id: str
    username: str
    avatar: Optional[str] = None
    message: str
    created_at: datetime

class DiscussionMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class DiscussionMessageResponse(BaseModel):
    id: str
    issue_id: str
    user_id: str
    username: str
    avatar: Optional[str] = None
    message: str
    created_at: datetime