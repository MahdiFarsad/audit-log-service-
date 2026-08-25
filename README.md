# Audit Log Service

FastAPI service that ingests audit/activity log events from MEAS II via `POST /Logger`,
writes them to MongoDB (fast write layer), and periodically syncs them to SQL Server
(`dbo.tblLogUserActivity`) for reporting via an ETL script.

## Architecture

```
MEAS II (.NET client) --POST /Logger--> FastAPI --> MongoDB (activity_logs)
                                                          |
                                                    etl/sync_to_sql.py
                                                          |
                                                          v
                                                SQL Server (dbo.tblLogUserActivity)
```

MongoDB is the primary write path (optimized for the <100ms response requirement).
SQL Server is the reporting layer, kept in sync by a scheduled ETL job — not written
to directly on each request.

## Prerequisites

- Python 3.10+
- MongoDB (running and reachable)
- SQL Server (running and reachable), with the `MEAS_Log` database created
- ODBC Driver 17 for SQL Server (for the SQL Server connection) — download from
  Microsoft if not already installed
- Access to the target SQL Server instance (credentials or Windows Auth)

## Setup

1. Clone the repo and enter the project folder.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in real values (see table below).
5. Create the SQL Server database and table — run `sql/create_database.sql` in SSMS
   against your target server, if not already created.

## Environment variables (`.env`)

| Variable | Description | Example |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB` | MongoDB database name | `audit_log` |
| `SQL_SERVER` | SQL Server address/instance | `192.168.1.31` or `localhost\SQLEXPRESS` |
| `SQL_DATABASE` | SQL Server database name | `MEAS_Log` |
| `SQL_USER` | SQL auth username (leave blank if using Windows Auth) | `sa` |
| `SQL_PASSWORD` | SQL auth password (leave blank if using Windows Auth) | — |
| `API_KEY` | The apiKey MEAS II will send in each request body | (get real value from manager, do not use the dev placeholder) |

**Note on Windows Authentication:** if the target SQL Server uses Windows Auth instead
of a SQL login, `app/database/sqlserver.py`'s connection string needs
`trusted_connection=yes` instead of a username/password — see the version used during
local dev testing if needed.

## Running the service

```
uvicorn app.main:app --host 0.0.0.0 --port 80
```

Port 80 matches the spec's target URL (`http://<server>/Logger`, no port in the URL).
Use `sudo`/admin privileges or a reverse proxy if binding to port 80 requires elevated
permissions on your OS.

## Running the ETL sync

Manually:
```
python etl/sync_to_sql.py
```

Scheduled (recommended — every 1-2 minutes):
- **Windows:** Task Scheduler → New Task → run `python etl/sync_to_sql.py` from the
  project directory on a recurring trigger.
- **Linux:** cron — `*/2 * * * * /path/to/venv/bin/python /path/to/etl/sync_to_sql.py`

## Running tests

```
pytest tests/ -v
```
Covers: auth (valid/invalid key), payload validation (nulls, long strings, Persian
text, missing fields), concurrency (100 simultaneous requests), and response latency
(<100ms).

## Acceptance checklist (run before flipping `Audit:Enabled` to `true` on MEAS II)

- [ ] Sample payload → `204` → record appears in MongoDB
- [ ] ETL run → same record appears in SQL Server, `synced` flag flips to `true`
- [ ] Wrong `apiKey` → `401`, nothing written
- [ ] Malformed body → `400`/`422`
- [ ] Null optional fields don't error
- [ ] Truncated/4001-char `methodParameters` doesn't error
- [ ] Persian `displayName` stored correctly (UTF-8)
- [ ] Response time consistently under 100ms
- [ ] 100 concurrent requests — no dropped records
- [ ] `apiKey` never appears in logs or responses

## Deployment notes

- Confirm target hosting environment (OS, port, process manager) with the team before
  deploying — see open items below.
- Keep `Audit:Enabled: false` on the MEAS II side until the full checklist above passes
  in the production environment, then flip it to `true`.

## Open items / needs from manager

- [ ] Real production `API_KEY` (currently using a dev-only placeholder)
- [ ] Confirmed production `SQL_SERVER` address and auth method
- [ ] Confirmed production `MONGO_URI` (local to the service host, or separate DB server)
- [ ] Deployment target OS and port
- [ ] Firewall/network access confirmation for the service host to reach both databases

## Project structure

```
app/
  main.py              FastAPI app entrypoint
  config.py            Settings loaded from .env
  api/logger.py         POST /Logger route
  schemas/audit_log.py  Request validation model
  models/audit_log.py   SQLAlchemy model for SQL Server table
  database/mongodb.py   Mongo connection + indexes
  database/sqlserver.py SQL Server connection
  services/             Auth, queueing, and log-processing logic
  workers/audit_worker.py  Background worker writing queued logs to Mongo
etl/
  sync_to_sql.py       Syncs unsynced Mongo docs into SQL Server
sql/
  create_database.sql  DDL for MEAS_Log database and table
tests/
  test_auth.py, test_logger.py, test_concurrency.py
```
