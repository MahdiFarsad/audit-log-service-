"""
ETL job: reads unsynced audit log documents from MongoDB and inserts them
into SQL Server (dbo.tblLogUserActivity), then marks them as synced.

Run manually:
    python etl/sync_to_sql.py

Or schedule via Windows Task Scheduler / cron to run every 1-2 minutes.
"""

import logging
from datetime import datetime
from sqlalchemy import text
from app.database.mongodb import logs_collection
from app.database.sqlserver import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("etl_sync")

INSERT_SQL = text("""
    INSERT INTO dbo.tblLogUserActivity
    (ID_OrgPerson, LogType, ComputerIP, UserAgent, AreaName, ControllerName,
     ActionName, MethodParameters, HttpMethod, DisplayName, ImpersonatorId,
     OccurredAt, ReceivedAt, Succeeded, StatusCode, ErrorMessage, DurationMs)
    VALUES
    (:id_org_person, :log_type, :computer_ip, :user_agent, :area_name, :controller_name,
     :action_name, :method_parameters, :http_method, :display_name, :impersonator_id,
     :occurred_at, :received_at, :succeeded, :status_code, :error_message, :duration_ms)
""")


def sync_batch(batch_size: int = 500) -> int:
    docs = list(logs_collection.find({"synced": False}).limit(batch_size))
    if not docs:
        return 0

    synced_count = 0
    failed_count = 0

    with engine.begin() as conn:
        for doc in docs:
            try:
                conn.execute(INSERT_SQL, {
                    "id_org_person": doc.get("iD_OrgPerson"),
                    "log_type": doc["logType"],
                    "computer_ip": doc.get("computerIP"),
                    "user_agent": doc.get("userAgent"),
                    "area_name": doc.get("areaName", ""),
                    "controller_name": doc.get("controllerName"),
                    "action_name": doc.get("actionName"),
                    "method_parameters": doc.get("methodParameters"),
                    "http_method": doc.get("httpmethod"),
                    "display_name": doc.get("displayName"),
                    "impersonator_id": doc.get("impersonatorId"),
                    "occurred_at": doc["occurredAt"],
                    "received_at": doc["receivedAt"],
                    "succeeded": doc["succeeded"],
                    "status_code": doc["statusCode"],
                    "error_message": doc.get("errorMessage"),
                    "duration_ms": doc["durationMs"],
                })
                logs_collection.update_one({"_id": doc["_id"]}, {"$set": {"synced": True}})
                synced_count += 1
            except Exception as e:
                failed_count += 1
                logger.error("Failed to sync doc _id=%s: %s", doc.get("_id"), e)
                # Leave synced=False so it's retried next run.
                logs_collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"syncError": str(e), "syncErrorAt": datetime.utcnow()}}
                )

    logger.info("Synced %d record(s), %d failed", synced_count, failed_count)
    return synced_count


if __name__ == "__main__":
    total = sync_batch()
    print(f"Done. Synced {total} record(s).")