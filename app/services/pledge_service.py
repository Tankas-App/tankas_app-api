from datetime import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException
from app.schemas.pledge import PledgeCreate, PledgeResponse

class PledgeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pledges_collection = db.pledges
        self.issues_collection = db.issues
        self.users_collection = db.users
    
    async def create_pledge(
        self, 
        issue_id: str, 
        username: str, 
        pledge_data: PledgeCreate
    ) -> PledgeResponse:
        # Validate
        if pledge_data.reward_type in ["points", "money"] and not pledge_data.reward_amount:
            raise HTTPException(status_code=400, detail="reward_amount required for points/money")
        
        if pledge_data.reward_type == "item" and not pledge_data.reward_description:
            raise HTTPException(status_code=400, detail="reward_description required for items")
        
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check issue exists
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        if issue["status"] == "resolved":
            raise HTTPException(status_code=400, detail="Cannot pledge for resolved issue")
        
        # Create pledge
        pledge_dict = {
            "issue_id": ObjectId(issue_id),
            "pledger_id": user["_id"],
            "pledger_username": user["username"],
            "reward_type": pledge_data.reward_type,
            "reward_amount": pledge_data.reward_amount,
            "reward_description": pledge_data.reward_description,
            "status": "active",
            "created_at": datetime.utcnow()
        }
        
        result = await self.pledges_collection.insert_one(pledge_dict)
        
        # Award pledger points for generosity
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$inc": {"points": 20}}  # +20 points for pledging
        )
        
        # Update issue priority (more pledges = higher priority)
        pledge_count = await self.pledges_collection.count_documents({
            "issue_id": ObjectId(issue_id),
            "status": "active"
        })
        
        if pledge_count >= 3:
            await self.issues_collection.update_one(
                {"_id": ObjectId(issue_id)},
                {"$set": {"priority": "high"}}
            )
        
        pledge = await self.pledges_collection.find_one({"_id": result.inserted_id})
        return self._format_pledge_response(pledge)
    
    async def get_pledges_for_issue(self, issue_id: str) -> List[PledgeResponse]:
        pledges = await self.pledges_collection.find({
            "issue_id": ObjectId(issue_id),
            "status": "active"
        }).to_list(100)
        
        return [self._format_pledge_response(p) for p in pledges]
    
    async def distribute_pledges(self, issue_id: str, resolver_id: ObjectId):
        """Distribute all pledges to the resolver when issue is completed"""
        pledges = await self.pledges_collection.find({
            "issue_id": ObjectId(issue_id),
            "status": "active"
        }).to_list(100)
        
        total_points = 0
        total_money = 0
        
        for pledge in pledges:
            if pledge["reward_type"] == "points":
                total_points += pledge["reward_amount"]
            elif pledge["reward_type"] == "money":
                total_money += pledge["reward_amount"]
            
            # Mark as distributed
            await self.pledges_collection.update_one(
                {"_id": pledge["_id"]},
                {
                    "$set": {
                        "status": "distributed",
                        "distributed_at": datetime.utcnow(),
                        "distributed_to": resolver_id
                    }
                }
            )
        
        # Award points to resolver
        if total_points > 0:
            await self.users_collection.update_one(
                {"_id": resolver_id},
                {"$inc": {"points": int(total_points)}}
            )
        
        return {
            "total_points": total_points,
            "total_money": total_money,
            "pledge_count": len(pledges)
        }
    
    def _format_pledge_response(self, pledge: dict) -> PledgeResponse:
        return PledgeResponse(
            id=str(pledge["_id"]),
            issue_id=str(pledge["issue_id"]),
            pledger_id=str(pledge["pledger_id"]),
            pledger_username=pledge["pledger_username"],
            reward_type=pledge["reward_type"],
            reward_amount=pledge.get("reward_amount"),
            reward_description=pledge.get("reward_description"),
            status=pledge["status"],
            created_at=pledge["created_at"],
            distributed_at=pledge.get("distributed_at")
        )