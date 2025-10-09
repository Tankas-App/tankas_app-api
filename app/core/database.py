from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, GEOSPHERE
from app.config import settings


class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)

    # Creating Indexes
    database = db.client[settings.database_name]
    await database.users.create_index([("username", ASCENDING)], unique=True)
    await database.users.create_index([("email", ASCENDING)], unique=True)
    await database.issues.create_index([("location", GEOSPHERE)])
    await database.issues.create_index([("status", ASCENDING)])
    print("Connected to MongoDB")

async def close_mongo_connection():
    db.client.close()
    print("Closed Mongo Connection")

def get_database():
    return db.client[settings.database_name]