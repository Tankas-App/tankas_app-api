from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from typing import List, Optional
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, CommentCreate
from app.services.issue_service import IssueService
from app.api.dependencies import get_current_user
from app.core.database import get_database

router = APIRouter(prefix="/api/issues", tags=["Issues"])

@router.get("", response_model=List[IssueResponse])
async def get_all_issues(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.get_all_issues(status=status, limit=limit, skip=skip)

@router.post("", response_model=IssueResponse)
async def create_issue(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    priority: str = Form("medium"),
    difficulty: str = Form("medium"),
    picture: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    issue_data = IssueCreate(
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        priority=priority,
        difficulty=difficulty
    )
    issue_service = IssueService(db)
    return await issue_service.create_issue(issue_data, current_user, picture)

@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: str,
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.get_issue_by_id(issue_id)

@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    update_data: IssueUpdate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.update_issue(issue_id, update_data, current_user)

@router.post("/{issue_id}/resolve", response_model=IssueResponse)
async def resolve_issue(
    issue_id: str,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.resolve_issue(issue_id, current_user)

@router.post("/{issue_id}/comments", response_model=IssueResponse)
async def add_comment(
    issue_id: str,
    comment_data: CommentCreate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.add_comment(issue_id, comment_data, current_user)