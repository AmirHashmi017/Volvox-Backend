from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.MONGODB_DB]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGO_DB_URI)
    print("Connected to MongoDB!")

async def close_mongo_connection():
    db.client.close()
    print("MongoDB connection closed!")

async def get_collection(collection_name: str):
    database = await get_database()
    return database[collection_name]