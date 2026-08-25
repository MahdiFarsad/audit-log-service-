CREATE DATABASE MEAS_AuditLog;
GO
USE MEAS_AuditLog;
GO

CREATE TABLE dbo.tblLogUserActivity
(
    ID                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    ID_OrgPerson        BIGINT           NULL,
    LogType             TINYINT      NOT NULL,
    ComputerIP          NVARCHAR(64)     NULL,
    UserAgent           NVARCHAR(512)    NULL,
    AreaName            NVARCHAR(64)     NULL,
    ControllerName      NVARCHAR(128)    NULL,
    ActionName          NVARCHAR(128)    NULL,
    MethodParameters    NVARCHAR(MAX)    NULL,
    HttpMethod          NVARCHAR(16)     NULL,
    DisplayName         NVARCHAR(256)    NULL,
    ImpersonatorId      BIGINT           NULL,
    OccurredAt          DATETIME2(3) NOT NULL,
    ReceivedAt          DATETIME2(3) NOT NULL DEFAULT (SYSDATETIME()),
    Succeeded           BIT          NOT NULL,
    StatusCode          INT          NOT NULL,
    ErrorMessage        NVARCHAR(2000)   NULL,
    DurationMs          BIGINT       NOT NULL
);

CREATE INDEX IX_LogUserActivity_OccurredAt ON dbo.tblLogUserActivity (OccurredAt DESC) INCLUDE (ID_OrgPerson, LogType);
CREATE INDEX IX_LogUserActivity_Person ON dbo.tblLogUserActivity (ID_OrgPerson, OccurredAt DESC);
CREATE INDEX IX_LogUserActivity_Action ON dbo.tblLogUserActivity (ControllerName, ActionName, OccurredAt DESC);
CREATE INDEX IX_LogUserActivity_Failed ON dbo.tblLogUserActivity (OccurredAt DESC) WHERE Succeeded = 0;
