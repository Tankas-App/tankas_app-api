from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.issue import IssueResponse
from app.services.issue_service import IssueService
from app.core.database import get_database

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[IssueResponse])
async def get_all_events(
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db = Depends(get_database)
):
    """Public endpoint - Get all events/issues for landing page"""
    issue_service = IssueService(db)
    return await issue_service.get_all_issues(limit=limit, skip=skip)