from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.dashboard import DashboardStats

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users
        self.issues_collection = db.issues
    
    async def get_user_by_username(self, username: str) -> UserResponse:
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            display_name=user.get("display_name"),
            avatar=user.get("avatar"),
            points=user["points"],
            tasks_completed=user["tasks_completed"],
            tasks_reported=user["tasks_reported"],
            areas_cleaned=user["areas_cleaned"],
            created_at=user["created_at"]
        )
    
    async def update_user(self, username: str, update_data: UserUpdate) -> UserResponse:
        """Update username and other user fields"""
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now()
        
        result = await self.users_collection.update_one(
            {"username": username},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return await self.get_user_by_username(username)
    
    async def update_avatar(self, username: str, avatar_url: str) -> UserResponse:
        """Update only the avatar URL"""
        result = await self.users_collection.update_one(
            {"username": username},
            {
                "$set": {
                    "avatar": avatar_url,
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return await self.get_user_by_username(username)
    
    async def get_user_by_username(self, username: str) -> UserResponse:
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if "_id" in user:
            user["id"] = user.pop("_id")
            
        return UserResponse(**user)
    
    async def get_dashboard(self, username: str) -> DashboardStats:
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get recent issues
        recent_issues = await self.issues_collection.find(
            {"user_id": user["_id"]}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        recent_issues_formatted = [
            {
                "id": str(issue["_id"]),
                "title": issue["title"],
                "status": issue["status"],
                "created_at": issue["created_at"]
            }
            for issue in recent_issues
        ]
        
        return DashboardStats(
            username=user["username"],
            display_name=user.get("display_name"),
            avatar=user.get("avatar"),
            points=user["points"],
            tasks_completed=user["tasks_completed"],
            tasks_reported=user["tasks_reported"],
            areas_cleaned=user["areas_cleaned"],
            recent_issues=recent_issues_formatted
        )