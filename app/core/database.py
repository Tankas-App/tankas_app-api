from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, GEOSPHERE, DESCENDING
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
    await database.volunteers.create_index([("issue_id", ASCENDING), ("user_id", ASCENDING)], unique=True, partialFilterExpression={"status": "active"})
    await database.volunteers.create_index([("issue_id", ASCENDING), ("status", ASCENDING), ("volunteered_at", DESCENDING)])
    await database.pledges.create_index([("issue_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)])
    await database.pledges.create_index([("pledger_id", ASCENDING)])
    await database.rewards.create_index([("available", DESCENDING), ("points_required", ASCENDING)])
    await database.rewards.create_index([("name", ASCENDING)])
    await database.redemptions.create_index([("user_id", ASCENDING), ("redeemed_at", DESCENDING)])
    await database.redemptions.create_index([("reward_id", ASCENDING)])

    print("Connected to MongoDB")

async def close_mongo_connection():
    db.client.close()
    print("Closed Mongo Connection")

def get_database():
    return db.client[settings.database_name]