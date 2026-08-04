import datetime
import re
from typing import Optional

import motor.motor_asyncio

from info import DATABASE_NAME, DATABASE_URI


class MovieRequestDatabase:
    """MongoDB storage for user movie requests."""

    def __init__(self, uri: str, database_name: str):
        client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.collection = client[database_name].movie_requests

    @staticmethod
    def normalize_title(title: str) -> str:
        title = re.sub(r"\s+", " ", title or "").strip()
        return title[:200]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [("user_id", 1), ("normalized_title", 1), ("status", 1)]
        )
        await self.collection.create_index([("created_at", -1)])

    async def create_request(
        self,
        *,
        user_id: int,
        user_name: str,
        title: str,
        chat_id: int,
        message_id: int,
    ) -> tuple[bool, dict]:
        clean_title = self.normalize_title(title)
        normalized = clean_title.casefold()
        existing = await self.collection.find_one(
            {
                "user_id": int(user_id),
                "normalized_title": normalized,
                "status": "pending",
            }
        )
        if existing:
            return False, existing

        document = {
            "user_id": int(user_id),
            "user_name": user_name or "User",
            "title": clean_title,
            "normalized_title": normalized,
            "chat_id": int(chat_id),
            "message_id": int(message_id),
            "status": "pending",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        }
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return True, document

    async def get_request(self, request_id: str) -> Optional[dict]:
        from bson import ObjectId

        try:
            return await self.collection.find_one({"_id": ObjectId(request_id)})
        except Exception:
            return None

    async def list_pending(self, limit: int = 10) -> list[dict]:
        cursor = self.collection.find({"status": "pending"}).sort("created_at", -1).limit(limit)
        return [item async for item in cursor]

    async def set_status(self, request_id: str, status: str, admin_id: int) -> Optional[dict]:
        from bson import ObjectId

        if status not in {"approved", "rejected"}:
            raise ValueError("Invalid request status")
        try:
            query = {"_id": ObjectId(request_id), "status": "pending"}
        except Exception:
            return None

        updated_at = datetime.datetime.now(datetime.timezone.utc)
        document = await self.collection.find_one_and_update(
            query,
            {
                "$set": {
                    "status": status,
                    "admin_id": int(admin_id),
                    "updated_at": updated_at,
                }
            },
            return_document=True,
        )
        return document

    async def pending_count(self) -> int:
        return await self.collection.count_documents({"status": "pending"})


request_db = MovieRequestDatabase(DATABASE_URI, DATABASE_NAME)
