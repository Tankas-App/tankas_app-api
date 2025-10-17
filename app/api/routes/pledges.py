from fastapi import APIRouter, Depends
from typing import List
from app.schemas.pledge import PledgeCreate, PledgeResponse
from app.services.pledge_service import PledgeService
from app.api.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter(prefix="/api/issues", tags=["Pledges"])

@router.post("/{issue_id}/pledge", response_model=PledgeResponse)
async def create_pledge(
    issue_id: str,
    pledge_data: PledgeCreate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Pledge a reward for an issue"""
    service = PledgeService(db)
    return await service.create_pledge(issue_id, current_user, pledge_data)

@router.get("/{issue_id}/pledges", response_model=List[PledgeResponse])
async def get_pledges(
    issue_id: str,
    db = Depends(get_database)
):
    """Get all pledges for an issue"""
    service = PledgeService(db)
    return await service.get_pledges_for_issue(issue_id)