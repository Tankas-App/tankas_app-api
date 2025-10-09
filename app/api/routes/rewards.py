from fastapi import APIRouter, Depends, Query
from typing import List
from app.core.database import get_database

router = APIRouter(prefix="/api/rewards", tags=["Rewards"])

@router.get("")
async def get_all_rewards(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db = Depends(get_database)
):
    """Get all available rewards"""
    rewards = await db.rewards.find({"available": True}).skip(skip).limit(limit).to_list(limit)
    
    return [
        {
            "id": str(reward["_id"]),
            "name": reward["name"],
            "description": reward["description"],
            "points_required": reward["points_required"],
            "image_url": reward.get("image_url")
        }
        for reward in rewards
    ]

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_database)
):
    """Get top users by points (leaderboard)"""
    users = await db.users.find().sort("points", -1).limit(limit).to_list(limit)
    
    return [
        {
            "rank": idx + 1,
            "username": user["username"],
            "display_name": user.get("display_name"),
            "avatar": user.get("avatar"),
            "points": user["points"],
            "tasks_completed": user["tasks_completed"]
        }
        for idx, user in enumerate(users)
    ]