import asyncio
from fastapi import FastAPI
from app.api.logger import router as logger_router
from app.database.mongodb import ensure_indexes
from app.workers.audit_worker import run_worker

app = FastAPI()
app.include_router(logger_router)

@app.on_event("startup")
async def startup():
    ensure_indexes()
    asyncio.create_task(run_worker())
