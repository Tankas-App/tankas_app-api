from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.user import WarriorResponse
from app.services.warrior_service import WarriorService
from app.core.database import get_database

router = APIRouter(prefix="/api/warriors", tags=["Clean Up Warriors"])

@router.get("", response_model=List[WarriorResponse])
async def get_all_warriors(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    db = Depends(get_database)
):
    """Get all cleanup warriors sorted by points"""
    warrior_service = WarriorService(db)
    return await warrior_service.get_all_warriors(limit=limit, skip=skip)

@router.get("/{user_id}", response_model=WarriorResponse)
async def get_warrior_by_id(
    user_id: str,
    db = Depends(get_database)
):
    """Get specific warrior details"""
    warrior_service = WarriorService(db)
    return await warrior_service.get_warrior_by_id(user_id)