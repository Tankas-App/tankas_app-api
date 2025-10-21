from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status, UploadFile
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, CommentCreate, CommentResponse
from app.services.location_service import LocationService
from app.services.storage_service import StorageService
from app.utils.points_calculator import calculate_points
from app.models.issue import IssueModel
from app.utils.exif_helper import extract_gps_from_image
from math import radians, sin, cos, sqrt, atan2

class IssueService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.issues_collection = db.issues
        self.users_collection = db.users
        self.location_service = LocationService()
        self.storage_service = StorageService()
        # Maximum distance in meters for GPS verification
        self.MAX_VERIFICATION_DISTANCE = 100
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in meters using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    async def create_issue(
        self, 
        issue_data: IssueCreate, 
        username: str,
        picture: Optional[UploadFile] = None
    ) -> IssueResponse:
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Variables for location
        latitude = issue_data.latitude
        longitude = issue_data.longitude

        # Read picture once if provided
        picture_bytes = None
        if picture:
            picture_bytes = await picture.read()

        # If picture is provided and no coordinates given, try to extract from EXIF
        if picture_bytes and (latitude is None or longitude is None):
            print(f"No coordinates provided. Attempting to extract GPS from image EXIF...")
            
            # Try to extract GPS from EXIF
            gps_coords = extract_gps_from_image(picture_bytes)
            
            if gps_coords:
                latitude, longitude = gps_coords
                print(f"GPS extracted from EXIF: Lat={latitude}, Lng={longitude}")
            else:
                print(f"No GPS data found in image EXIF")
            
        # Validate that we have coordinates (either from form or EXIF)
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Location required: Either provide coordinates or upload an image with GPS data"
            )

        # Validate coordinates
        if not self.location_service.validate_coordinates(latitude, longitude):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Invalid coordinates: Lat={latitude}, Lng={longitude}"
            )
        
        # Upload picture if provided (we already have the bytes)
        picture_url = None
        if picture_bytes:
            picture_url = await self.storage_service.save_upload_file_bytes(picture_bytes, picture.filename)
        
        # Calculate points
        points = calculate_points(issue_data.difficulty, issue_data.priority)
        
        # Create issue
        issue_dict = {
            "user_id": str(user["_id"]),
            "title": issue_data.title,
            "description": issue_data.description,
            "location": self.location_service.create_geojson(latitude, longitude),
            "picture_url": picture_url,
            "priority": issue_data.priority,
            "difficulty": issue_data.difficulty,
            "status": "open",
            "points_assigned": points,
            "comments": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        issue = IssueModel(**issue_dict)
        result = await self.issues_collection.insert_one(issue.model_dump(by_alias=True, exclude={"id"}))
        
        # Update user's tasks_reported
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$inc": {"tasks_reported": 1}}
        )
        
        # Fetch and return created issue
        return await self.get_issue_by_id(str(result.inserted_id))
    
    async def get_all_issues(
        self, 
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[IssueResponse]:
        query = {}
        if status:
            query["status"] = status
        
        issues = await self.issues_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [self._format_issue_response(issue) for issue in issues]
    
    async def get_issue_by_id(self, issue_id: str) -> IssueResponse:
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        
        return self._format_issue_response(issue)
    
    async def update_issue(self, issue_id: str, update_data: IssueUpdate, username: str) -> IssueResponse:
        # Get issue
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        
        # Get user
        user = await self.users_collection.find_one({"username": username})
        
        # Check ownership
        if issue["user_id"] != user["_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this issue")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now()
        
        await self.issues_collection.update_one(
            {"_id": ObjectId(issue_id)},
            {"$set": update_dict}
        )
        
        return await self.get_issue_by_id(issue_id)
    
    async def resolve_issue(
        self, 
        issue_id: str, 
        username: str,
        resolution_picture: Optional[UploadFile] = None
    ) -> IssueResponse:
        """
        Resolve an issue with GPS verification
        - Requires a picture with GPS data
        - Verifies user is within MAX_VERIFICATION_DISTANCE of original issue location
        """
        # Get issue
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        
        if issue["status"] == "resolved":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Issue already resolved")
        
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Require resolution picture
        if not resolution_picture:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolution picture is required to verify you are at the location"
            )
        
        # Validate file type
        if not resolution_picture.content_type or not resolution_picture.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read picture bytes
        picture_bytes = await resolution_picture.read()
        
        # Extract GPS from resolution picture
        resolution_gps = extract_gps_from_image(picture_bytes)
        
        if not resolution_gps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract GPS data from image. Please ensure location services are enabled when taking the photo."
            )
        
        resolution_lat, resolution_lng = resolution_gps
        
        # Get original issue location
        original_lat, original_lng = self.location_service.extract_coordinates(issue["location"])
        
        # Calculate distance between locations
        distance = self.calculate_distance(
            original_lat,
            original_lng,
            resolution_lat,
            resolution_lng
        )
        
        print(f"GPS Verification: Distance between locations = {distance:.2f}m (max: {self.MAX_VERIFICATION_DISTANCE}m)")
        
        # Verify user is within acceptable range
        if distance > self.MAX_VERIFICATION_DISTANCE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You must be at the issue location to resolve it. You are {distance:.0f}m away (maximum allowed: {self.MAX_VERIFICATION_DISTANCE}m)"
            )
        
        # Upload resolution picture to Cloudinary
        resolution_picture_url = await self.storage_service.save_upload_file_bytes(
            picture_bytes, 
            resolution_picture.filename,
            folder="resolutions"
        )
        
        # Update issue with resolution data
        await self.issues_collection.update_one(
            {"_id": ObjectId(issue_id)},
            {
                "$set": {
                    "status": "resolved",
                    "resolved_by": user["_id"],
                    "resolved_at": datetime.now(),
                    "resolution_picture_url": resolution_picture_url,
                    "resolution_location": self.location_service.create_geojson(resolution_lat, resolution_lng),
                    "verification_distance_meters": round(distance, 2),
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Award points to resolver
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$inc": {
                    "points": issue["points_assigned"],
                    "tasks_completed": 1,
                    "areas_cleaned": 1
                }
            }
        )
        
        # Distribute pledges to resolver
        from app.services.pledge_service import PledgeService
        pledge_service = PledgeService(self.db)
        pledge_distribution = await pledge_service.distribute_pledges(issue_id, user["_id"])
        
        print(f"✅ Distributed pledges: {pledge_distribution}")
        print(f"✅ Issue resolved with GPS verification (distance: {distance:.2f}m)")
            
        return await self.get_issue_by_id(issue_id)
    
    async def add_comment(self, issue_id: str, comment_data: CommentCreate, username: str) -> IssueResponse:
        # Get user
        user = await self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Check if issue exists
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        
        # Create comment
        comment = {
            "user_id": user["_id"],
            "username": user["username"],
            "avatar": user["avatar"],
            "comment": comment_data.comment,
            "created_at": datetime.now()
        }
        
        # Add comment to issue
        await self.issues_collection.update_one(
            {"_id": ObjectId(issue_id)},
            {
                "$push": {"comments": comment},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return await self.get_issue_by_id(issue_id)
    
    def _format_issue_response(self, issue: dict) -> IssueResponse:
        lat, lng = self.location_service.extract_coordinates(issue["location"])
        
        # Handle resolution location if exists
        resolution_lat, resolution_lng = None, None
        if issue.get("resolution_location"):
            resolution_lat, resolution_lng = self.location_service.extract_coordinates(issue["resolution_location"])
        
        comments = [
            CommentResponse(
                user_id=str(comment["user_id"]),
                username=comment["username"],
                comment=comment["comment"],
                created_at=comment["created_at"]
            )
            for comment in issue.get("comments", [])
        ]
        
        return IssueResponse(
            id=str(issue["_id"]),
            user_id=str(issue["user_id"]),
            title=issue["title"],
            description=issue["description"],
            latitude=lat,
            longitude=lng,
            picture_url=issue.get("picture_url"),
            priority=issue["priority"],
            difficulty=issue["difficulty"],
            status=issue["status"],
            points_assigned=issue["points_assigned"],
            reward_listing=issue.get("reward_listing"),
            comments=comments,
            resolved_by=str(issue["resolved_by"]) if issue.get("resolved_by") else None,
            resolved_at=issue.get("resolved_at"),
            resolution_picture_url=issue.get("resolution_picture_url"),
            resolution_latitude=resolution_lat,
            resolution_longitude=resolution_lng,
            verification_distance_meters=issue.get("verification_distance_meters"),
            created_at=issue["created_at"],
            updated_at=issue["updated_at"]
        )
    
    async def get_comments(self, issue_id: str):
        issue = await self.issues_collection.find_one({"_id": ObjectId(issue_id)})
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        comments = issue.get("comments", [])
        formatted_comments = []
        
        for comment in comments:
            formatted_comment = {
                "_id": str(comment.get("_id", "")),
                "user": {
                    "id": str(comment.get("user_id", "")),
                    "username": comment.get("username", ""),
                    "avatar": comment.get("avatar", "")
                },
                "content": comment.get("comment", ""),
                "created_at": comment.get("created_at", "")
            }
            formatted_comments.append(formatted_comment)
        
        return formatted_comments