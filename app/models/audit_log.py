from sqlalchemy import Column, BigInteger, SmallInteger, String, Boolean, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "tblLogUserActivity"

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    ID_OrgPerson = Column(BigInteger, nullable=True)
    LogType = Column(SmallInteger, nullable=False)
    ComputerIP = Column(String(64), nullable=True)
    UserAgent = Column(String(512), nullable=True)
    AreaName = Column(String(64), nullable=True)
    ControllerName = Column(String(128), nullable=True)
    ActionName = Column(String(128), nullable=True)
    MethodParameters = Column(String, nullable=True)  # NVARCHAR(MAX)
    HttpMethod = Column(String(16), nullable=True)
    DisplayName = Column(String(256), nullable=True)
    ImpersonatorId = Column(BigInteger, nullable=True)
    OccurredAt = Column(DateTime, nullable=False)
    ReceivedAt = Column(DateTime, nullable=False)
    Succeeded = Column(Boolean, nullable=False)
    StatusCode = Column(Integer, nullable=False)
    ErrorMessage = Column(String(2000), nullable=True)
    DurationMs = Column(BigInteger, nullable=False)
