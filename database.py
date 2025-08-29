from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# --- 1. Data Model ---
class ImageLog(BaseModel):
    original_filename: str
    processed_filename: str
    filter_applied: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# --- 2. Database Connection ---
class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.client.admin.command("ping")
            print("✅ MongoDB connection successful.")
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
        
        if self.client:
            self.db = self.client[DB_NAME]
            self.logs_collection: Collection = self.db["image_processing_logs"]

    def close(self):
        if self.client:
            self.client.close()


# --- 3. CRUD ---
def create_log_entry(collection: Collection, log_data: ImageLog) -> str:
    try:
        result = collection.insert_one(log_data.model_dump())
        print(f"📄 Log saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ Error logging: {e}")
        return None
