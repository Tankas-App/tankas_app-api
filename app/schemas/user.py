from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    points: int
    tasks_completed: int
    tasks_reported: int
    areas_cleaned: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

    @field_validator('id', mode='before')
    @classmethod
    def convert_id(cls, v):
        if v is not None:
            return str(v)
        return v

class UserUpdate(BaseModel):
    display_name: Optional[str] = None

class WarriorResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    points: int
    tasks_completed: int