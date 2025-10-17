from datetime import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status
from app.schemas.volunteer import VolunteerCreate, VolunteerResponse, DiscussionMessageCreate, DiscussionMessageResponse 

class VolunteerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.volunteers_collection = db.volunteers
        self.issues_collection = db.issues
        self.users_collection = db.users
        # New collection for discussions
        self.discussions_collection = db.volunteer_discussions

    # ------------------------------------------------------------------
    # CORE VOLUNTEER METHODS (from original code)
    # ------------------------------------------------------------------
    
    async def volunteer_for_issue(
        self, 
        issue_id: str, 
        username: str, 
        volunteer_data: VolunteerCreate
    ) -> VolunteerResponse:
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if issue exists and is open
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        if issue["status"] == "resolved":
            raise HTTPException(status_code=400, detail="Issue already resolved")
        
        # Check if already volunteered
        existing = await self.volunteers_collection.find_one({
            "issue_id": ObjectId(issue_id),
            "user_id": user["_id"],
            "status": "active"
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Already volunteered for this issue")
        
        # Create volunteer record
        volunteer_dict = {
            "issue_id": ObjectId(issue_id),
            "user_id": user["_id"],
            "username": user["username"],
            "volunteered_at": datetime.utcnow(),
            "status": "active",
            "contribution": volunteer_data.contribution
        }
        
        result = await self.volunteers_collection.insert_one(volunteer_dict)
        
        # Award points for volunteering
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$inc": {"points": 5}}  # +5 points for volunteering
        )
        
        # Update issue status to "in_progress" if first volunteer
        volunteer_count = await self.volunteers_collection.count_documents({
            "issue_id": ObjectId(issue_id),
            "status": "active"
        })
        
        if volunteer_count == 1 and issue["status"] == "open":
            await self.issues_collection.update_one(
                {"_id": ObjectId(issue_id)},
                {"$set": {"status": "in_progress", "updated_at": datetime.utcnow()}}
            )
        
        # Return volunteer record
        volunteer = await self.volunteers_collection.find_one({"_id": result.inserted_id})
        return self._format_volunteer_response(volunteer)
    
    async def withdraw_volunteer(self, issue_id: str, username: str):
        user = await self.users_collection.find_one({"username": username})
        
        result = await self.volunteers_collection.update_one(
            {
                "issue_id": ObjectId(issue_id),
                "user_id": user["_id"],
                "status": "active"
            },
            {
                "$set": {
                    "status": "withdrawn",
                    "withdrawn_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Volunteer record not found")
        
        return {"message": "Volunteer withdrawn successfully"}
    
    async def get_volunteers_for_issue(self, issue_id: str) -> List[VolunteerResponse]:
        volunteers = await self.volunteers_collection.find({
            "issue_id": ObjectId(issue_id),
            "status": "active"
        }).to_list(100)
        
        return [self._format_volunteer_response(v) for v in volunteers]
    
    def _format_volunteer_response(self, volunteer: dict) -> VolunteerResponse:
        return VolunteerResponse(
            id=str(volunteer["_id"]),
            issue_id=str(volunteer["issue_id"]),
            user_id=str(volunteer["user_id"]),
            username=volunteer["username"],
            volunteered_at=volunteer["volunteered_at"],
            status=volunteer["status"],
            contribution=volunteer.get("contribution")
        )

    # ------------------------------------------------------------------
    # DISCUSSION METHODS (from new code)
    # ------------------------------------------------------------------

    async def post_discussion_message(
        self,
        issue_id: str,
        username: str,
        message_data: DiscussionMessageCreate
    ) -> DiscussionMessageResponse:
        """Post a message in the volunteer discussion"""
        
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if issue exists
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Check if user is a volunteer for this issue (Authorization)
        is_volunteer = await self.volunteers_collection.find_one({
            "issue_id": ObjectId(issue_id),
            "user_id": user["_id"],
            "status": "active"
        })
        
        if not is_volunteer:
            raise HTTPException(
                status_code=403, 
                detail="Only active volunteers can post in discussion"
            )
        
        # Create discussion message
        message_dict = {
            "issue_id": ObjectId(issue_id),
            "user_id": user["_id"],
            "username": user["username"],
            "avatar": user.get("avatar"),
            "message": message_data.message,
            "created_at": datetime.utcnow()
        }
        
        result = await self.discussions_collection.insert_one(message_dict)
        
        # Return the message
        message = await self.discussions_collection.find_one({"_id": result.inserted_id})
        return self._format_discussion_message(message)

    async def get_discussion_messages(
        self,
        issue_id: str,
        username: str
    ) -> List[DiscussionMessageResponse]:
        """Get all discussion messages for an issue"""
        
        # Check if user is a volunteer (Authorization)
        user = await self.users_collection.find_one({"username": username})
        if not user:
             # User check is performed implicitly by the check below, but explicit is better
             raise HTTPException(status_code=404, detail="User not found")

        is_volunteer = await self.volunteers_collection.find_one({
            "issue_id": ObjectId(issue_id),
            "user_id": user["_id"],
            "status": "active"
        })
        
        if not is_volunteer:
            raise HTTPException(
                status_code=403,
                detail="Only volunteers can view discussion"
            )
        
        # Get messages
        messages = await self.discussions_collection.find({
            "issue_id": ObjectId(issue_id)
        }).sort("created_at", 1).to_list(1000)
        
        return [self._format_discussion_message(m) for m in messages]

    def _format_discussion_message(self, message: dict) -> DiscussionMessageResponse:
        return DiscussionMessageResponse(
            id=str(message["_id"]),
            issue_id=str(message["issue_id"]),
            user_id=str(message["user_id"]),
            username=message["username"],
            avatar=message.get("avatar"),
            message=message["message"],
            created_at=message["created_at"]
        )