from fastapi import APIRouter, Response, HTTPException
from app.schemas.audit_log import LogEntry
from app.services.auth_service import is_valid_key
from app.services.audit_service import enqueue_log

router = APIRouter()

@router.post("/Logger", status_code=204)
async def create_log(entry: LogEntry):
    if not is_valid_key(entry.apiKey):
        raise HTTPException(status_code=401, detail="Invalid API key")

    await enqueue_log(entry)
    return Response(status_code=204)
