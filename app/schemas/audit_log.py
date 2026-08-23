from pydantic import BaseModel, Field
from typing import Optional

class LogEntry(BaseModel):
    iD_OrgPerson: Optional[int] = None
    logType: int
    computerIP: Optional[str] = None
    userAgent: Optional[str] = None
    areaName: str = ""
    controllerName: Optional[str] = None
    actionName: Optional[str] = None
    methodParameters: Optional[str] = None
    httpmethod: Optional[str] = Field(default=None, alias="httpmethod")
    displayName: Optional[str] = None
    impersonatorId: Optional[int] = None
    occurredAt: str
    succeeded: bool
    statusCode: int
    errorMessage: Optional[str] = None
    durationMs: int
    apiKey: str

    class Config:
        populate_by_name = True
