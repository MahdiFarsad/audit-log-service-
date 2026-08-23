import asyncio
import logging

logger = logging.getLogger("audit_queue")

class BoundedAuditQueue:
    def __init__(self, maxsize: int = 1000):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, item: dict):
        if self._queue.full():
            try:
                dropped = self._queue.get_nowait()
                logger.warning("Queue full — dropped oldest record occurredAt=%s", dropped.get("occurredAt"))
            except asyncio.QueueEmpty:
                pass
        await self._queue.put(item)

    async def get(self):
        return await self._queue.get()

    def task_done(self):
        self._queue.task_done()

audit_queue = BoundedAuditQueue(maxsize=1000)
