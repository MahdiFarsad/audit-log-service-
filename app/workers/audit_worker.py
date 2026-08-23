import asyncio
import logging
from app.services.queue_service import audit_queue
from app.database.mongodb import logs_collection

logger = logging.getLogger("audit_worker")

async def run_worker():
    while True:
        doc = await audit_queue.get()
        try:
            logs_collection.insert_one(doc)
        except Exception as e:
            logger.error("Failed to write log to MongoDB: %s", e)
        finally:
            audit_queue.task_done()
