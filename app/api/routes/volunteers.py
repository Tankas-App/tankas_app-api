from fastapi import APIRouter, Depends
from typing import List
from app.schemas.volunteer import (
    VolunteerCreate, 
    VolunteerResponse, 
    DiscussionMessageCreate,
    DiscussionMessageResponse
)
from app.services.volunteer_service import VolunteerService
from app.api.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter(prefix="/api/issues", tags=["Volunteers"])

# ------------------------------------------------------------------
# CORE VOLUNTEER ENDPOINTS
# ------------------------------------------------------------------

@router.post("/{issue_id}/volunteer", response_model=VolunteerResponse)
async def volunteer_for_issue(
    issue_id: str,
    volunteer_data: VolunteerCreate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Volunteer to solve an issue"""
    service = VolunteerService(db)
    return await service.volunteer_for_issue(issue_id, current_user, volunteer_data)

@router.delete("/{issue_id}/volunteer")
async def withdraw_volunteer(
    issue_id: str,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Withdraw from volunteering"""
    service = VolunteerService(db)
    return await service.withdraw_volunteer(issue_id, current_user)

@router.get("/{issue_id}/volunteers", response_model=List[VolunteerResponse])
async def get_volunteers(
    issue_id: str,
    db = Depends(get_database)
):
    """Get all volunteers for an issue"""
    service = VolunteerService(db)
    return await service.get_volunteers_for_issue(issue_id)

# ------------------------------------------------------------------
# DISCUSSION ENDPOINTS
# ------------------------------------------------------------------

@router.post("/{issue_id}/discussion", response_model=DiscussionMessageResponse)
async def post_discussion_message(
    issue_id: str,
    message_data: DiscussionMessageCreate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Post a message in volunteer discussion (volunteers only)"""
    service = VolunteerService(db)
    return await service.post_discussion_message(issue_id, current_user, message_data)

@router.get("/{issue_id}/discussion", response_model=List[DiscussionMessageResponse])
async def get_discussion_messages(
    issue_id: str,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all discussion messages (volunteers only)"""
    service = VolunteerService(db)
    return await service.get_discussion_messages(issue_id, current_user)