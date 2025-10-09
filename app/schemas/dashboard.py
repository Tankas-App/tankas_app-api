from pydantic import BaseModel
from typing import List, Optional

class DashboardStats(BaseModel):
    username: str
    display_name: Optional[str]
    avatar: Optional[str]
    points: int
    tasks_completed: int
    tasks_reported: int
    areas_cleaned: int
    recent_issues: List[dict] = []