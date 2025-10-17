from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.routes import auth, users, warriors, issues, events, rewards, volunteers, pledges

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
   # Only create uploads directory if using local storage
    if not settings.use_cloudinary:
        os.makedirs(settings.upload_dir, exist_ok=True)
    
    yield
    
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Tankas App API",
    description="Backend API for Tankas application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (uploads)
# app.mount(f"/{settings.upload_dir}", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(warriors.router)
app.include_router(issues.router)
app.include_router(events.router)
app.include_router(rewards.router)
app.include_router(volunteers.router)
app.include_router(pledges.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Tankas App API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}