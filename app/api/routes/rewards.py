from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from app.core.database import get_database 
from app.api.dependencies import get_current_user 
from app.schemas.reward import RewardCreate, RewardResponse 
from bson import ObjectId 
from datetime import datetime 


router = APIRouter(prefix="/api/rewards", tags=["Rewards"])

# ------------------------------------------------------------------
# READ ENDPOINTS (Listing and Leaderboard)
# ------------------------------------------------------------------

@router.get("", response_model=List[RewardResponse]) # Added List[RewardResponse] for clarity
async def get_all_rewards(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db = Depends(get_database)
):
    """Get all available rewards"""
    rewards = await db.rewards.find({"available": True}).skip(skip).limit(limit).to_list(limit)
    
    # Helper function to format the reward response (recommended, but inline for this example)
    def format_reward(reward):
        return {
            "id": str(reward["_id"]),
            "name": reward["name"],
            "description": reward["description"],
            "points_required": reward["points_required"],
            "image_url": reward.get("image_url"),
            "available": reward["available"] if "available" in reward else True
        }

    return [format_reward(reward) for reward in rewards]

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_database)
):
    """Get top users by points (leaderboard)"""
    # Note: Assuming 'points' field exists on the user document
    users = await db.users.find().sort("points", -1).limit(limit).to_list(limit)
    
    return [
        {
            "rank": idx + 1,
            "username": user["username"],
            "display_name": user.get("display_name"),
            "avatar": user.get("avatar"),
            "points": user.get("points", 0), # Use get with default for safety
            "tasks_completed": user.get("tasks_completed", 0)
        }
        for idx, user in enumerate(users)
    ]

# ------------------------------------------------------------------
# ENDPOINTS (Create and Redeem)
# ------------------------------------------------------------------

@router.post("", response_model=RewardResponse, status_code=201)
async def create_reward(
    reward_data: RewardCreate,
    current_user: str = Depends(get_current_user), 
    db = Depends(get_database)
):
    """
    Creates a new reward available for redemption. 
    (Requires Admin/Staff permissions)
    """
    # 1. (Optional but RECOMMENDED): Authorization Check
    # In a real application, you would check the user's role here:
    # user_data = await db.users.find_one({"username": current_user})
    # if user_data.get("role") != "admin":
    #     raise HTTPException(status_code=403, detail="Not authorized to create rewards")

    # 2. Prepare the data
    reward_dict = {
        "name": reward_data.name,
        "description": reward_data.description,
        "points_required": reward_data.points_required,
        "image_url": reward_data.image_url,
        "available": True, 
        "created_at": datetime.utcnow() # datetime imported from second code block
    }

    # 3. Insert into the collection
    result = await db.rewards.insert_one(reward_dict)
    
    # 4. Fetch the created record and format the response
    new_reward = await db.rewards.find_one({"_id": result.inserted_id})
    
    # Inline formatting for RewardResponse
    return {
        "id": str(new_reward["_id"]),
        "name": new_reward["name"],
        "description": new_reward["description"],
        "points_required": new_reward["points_required"],
        "image_url": new_reward.get("image_url"),
        "available": new_reward["available"],
    }

@router.post("/{reward_id}/redeem", status_code=200)
async def redeem_reward(
    reward_id: str,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Allows a user to redeem an available reward using their points."""
    try:
        reward_obj_id = ObjectId(reward_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reward ID format")

    # 1. Look up the reward and the user
    reward = await db.rewards.find_one({"_id": reward_obj_id, "available": True})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found or unavailable")
    
    user = await db.users.find_one({"username": current_user})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    points_required = reward["points_required"]
    
    # 2. Check if the user has enough points
    if user.get("points", 0) < points_required:
        raise HTTPException(status_code=400, detail="Insufficient points to redeem this reward")
        
    # 3. Atomically deduct points
    result = await db.users.update_one(
        {"_id": user["_id"], "points": {"$gte": points_required}}, 
        {"$inc": {"points": -points_required}} 
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to deduct points. Check point balance.")

    # 4. Record the redemption
    redemption_record = {
        "user_id": user["_id"],
        "username": current_user,
        "reward_id": reward_obj_id,
        "reward_name": reward["name"],
        "points_deducted": points_required,
        "status": "pending_fulfillment",
        "redeemed_at": datetime.utcnow()
    }
    await db.redemptions.insert_one(redemption_record)

    return {"message": f"Successfully redeemed '{reward['name']}' for {points_required} points. Fulfillment is pending."}