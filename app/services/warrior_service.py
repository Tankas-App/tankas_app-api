from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.schemas.user import WarriorResponse

class WarriorService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users
    
    async def get_all_warriors(self, limit: int = 100, skip: int = 0) -> List[WarriorResponse]:
        """Get all cleanup warriors sorted by points"""
        warriors = await self.users_collection.find().sort("points", -1).skip(skip).limit(limit).to_list(limit)
        
        return [
            WarriorResponse(
                id=str(warrior["_id"]),
                username=warrior["username"],
                display_name=warrior.get("display_name"),
                avatar=warrior.get("avatar"),
                points=warrior["points"],
                tasks_completed=warrior["tasks_completed"]
            )
            for warrior in warriors
        ]
    
    async def get_warrior_by_id(self, user_id: str) -> WarriorResponse:
        """Get specific warrior details"""
        from bson import ObjectId
        warrior = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not warrior:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warrior not found")
        
        return WarriorResponse(
            id=str(warrior["_id"]),
            username=warrior["username"],
            display_name=warrior.get("display_name"),
            avatar=warrior.get("avatar"),
            points=warrior["points"],
            tasks_completed=warrior["tasks_completed"]
        )