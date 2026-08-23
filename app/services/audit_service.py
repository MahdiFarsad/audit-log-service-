from datetime import datetime, timezone
from app.schemas.audit_log import LogEntry
from app.services.queue_service import audit_queue

async def enqueue_log(entry: LogEntry):
    doc = entry.model_dump(exclude={"apiKey"})
    doc["receivedAt"] = datetime.now(timezone.utc)
    doc["synced"] = False
    await audit_queue.put(doc)
