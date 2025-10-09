from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    points: int
    tasks_completed: int
    tasks_reported: int
    areas_cleaned: int
    created_at: datetime

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar: Optional[str] = None

class WarriorResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    points: int
    tasks_completed: int