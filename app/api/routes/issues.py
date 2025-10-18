from fastapi import APIRouter, Depends, File, UploadFile, Form, Query, HTTPException, UploadFile, File, Form
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
    latitude: str = Form(""),
    longitude: str = Form(""),
    priority: str = Form("medium"),
    difficulty: str = Form("medium"),
    picture: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    
    # Convert empty strings to None, otherwise parse as float
    lat = None
    lng = None
    
    # Parse latitude
    if latitude and latitude.strip():
        try:
            lat = float(latitude)
            if not (-90 <= lat <= 90):
                raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid latitude value: {latitude}")
    
    # Parse longitude
    if longitude and longitude.strip():
        try:
            lng = float(longitude)
            if not (-180 <= lng <= 180):
                raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid longitude value: {longitude}")

    issue_data = IssueCreate(
        title=title,
        description=description,
        latitude=lat,
        longitude=lng,
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
    resolution_picture: UploadFile = File(..., description="Picture taken at the resolved location with GPS data"),
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Resolve an issue with GPS verification
    
    - **issue_id**: The ID of the issue to resolve
    - **resolution_picture**: Picture with GPS metadata showing the resolved issue
    
    The system will:
    1. Extract GPS coordinates from the uploaded picture
    2. Compare with the original issue's GPS location
    3. Only allow resolution if within 100 meters
    4. Award points to the resolver
    5. Distribute any pledges
    
    **Note**: Location services must be enabled when taking the photo.
    """
    issue_service = IssueService(db)
    
    return await issue_service.resolve_issue(
        issue_id=issue_id,
        username=current_user,
        resolution_picture=resolution_picture
    )

# # If you want to make it optional (for backward compatibility during migration)
# @router.post("/{issue_id}/resolve-without-verification", response_model=IssueResponse)
# async def resolve_issue_without_verification(
#     issue_id: str,
#     current_user: dict = Depends(get_current_user),
#     db = Depends(get_database)
# ):
#     """
#     Resolve an issue WITHOUT GPS verification (legacy endpoint)
    
#     This endpoint is for backward compatibility. 
#     The main /resolve endpoint should be used for new resolutions.
#     """
#     issue_service = IssueService(db)
    
#     return await issue_service.resolve_issue(
#         issue_id=issue_id,
#         username=current_user["username"],
#         resolution_picture=None  # No verification
#     )

@router.post("/{issue_id}/comments", response_model=IssueResponse)
async def add_comment(
    issue_id: str,
    comment_data: CommentCreate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    issue_service = IssueService(db)
    return await issue_service.add_comment(issue_id, comment_data, current_user)