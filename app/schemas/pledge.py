from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PledgeCreate(BaseModel):
    reward_type: str = Field(..., pattern="^(points|money|item)$")
    reward_amount: Optional[float] = Field(None, ge=0)
    reward_description: Optional[str] = None

class PledgeResponse(BaseModel):
    id: str
    issue_id: str
    pledger_id: str
    pledger_username: str
    reward_type: str
    reward_amount: Optional[float] = None
    reward_description: Optional[str] = None
    status: str
    created_at: datetime
    distributed_at: Optional[datetime] = None