from datetime import timedelta
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import verify_password, get_password_hash, create_access_token
from app.config import settings
from app.schemas.auth import SignupRequest, LoginRequest, Token
from app.models.user import UserModel

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users
    
    async def signup(self, signup_data: SignupRequest) -> Token:
        # Check if user exists
        existing_user = await self.users_collection.find_one({
            "$or": [
                {"username": signup_data.username},
                {"email": signup_data.email}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create user
        user_dict = {
            "username": signup_data.username,
            "email": signup_data.email,
            "hashed_password": get_password_hash(signup_data.password),
            "display_name": signup_data.display_name or signup_data.username,
            "points": 0,
            "tasks_completed": 0,
            "tasks_reported": 0,
            "areas_cleaned": 0
        }
        
        user = UserModel(**user_dict)
        result = await self.users_collection.insert_one(user.model_dump(by_alias=True, exclude={"id"}))
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": signup_data.username},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token)
    
    async def login(self, login_data: LoginRequest) -> Token:
        # Find user
        user = await self.users_collection.find_one({"username": login_data.username})
        
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": login_data.username},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token)