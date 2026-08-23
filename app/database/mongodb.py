from pymongo import MongoClient, ASCENDING, DESCENDING
from app.config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db]
logs_collection = db["activity_logs"]

def ensure_indexes():
    logs_collection.create_index([("occurredAt", DESCENDING)])
    logs_collection.create_index([("iD_OrgPerson", ASCENDING), ("occurredAt", DESCENDING)])
    logs_collection.create_index([("controllerName", ASCENDING), ("actionName", ASCENDING)])
    logs_collection.create_index([("synced", ASCENDING)])
