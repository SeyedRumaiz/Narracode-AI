"""Session history persistence for AI code analysis results."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from pymongo import MongoClient
except ImportError:  # pragma: no cover
    MongoClient = None


MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGODB_DB", "ai_code_explainer")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION", "analysis_history")

memory_store: Dict[str, List[Dict[str, Any]]] = {}


def _mongo_client() -> Optional[MongoClient]:
    if MongoClient is None:
        return None
    return MongoClient(MONGO_URI)


def save_history(session_id: str, record: Dict[str, Any]) -> None:
    """Save a history record in-memory and optionally persist to MongoDB."""
    memory_store.setdefault(session_id, []).append(record)
    client = _mongo_client()
    if client:
        try:
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            collection.insert_one({"session_id": session_id, "record": record})
        except Exception:
            # MongoDB is optional; keep in-memory history and continue.
            return


def get_history(session_id: str) -> List[Dict[str, Any]]:
    """Return saved history records for a session."""
    if session_id in memory_store:
        return memory_store[session_id]

    client = _mongo_client()
    if not client:
        return []

    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        cursor = collection.find({"session_id": session_id}).sort([("_id", 1)])
        return [item["record"] for item in cursor]
    except Exception:
        return []
