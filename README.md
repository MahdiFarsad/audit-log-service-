# Audit Log Service

> Ingests activity logs from MEAS II, writes them to MongoDB for speed, and syncs them to SQL Server for reporting.

![Status](https://img.shields.io/badge/status-live-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20MongoDB%20%7C%20SQL%20Server-informational)

---

## Overview

This service receives a single type of event — a user activity log — from the MEAS II
application, and makes it available for both real-time storage and long-term reporting.

```
┌─────────────┐      POST /Logger       ┌─────────────┐      queued write      ┌──────────────┐
│   MEAS II   │ ──────────────────────▶│   FastAPI   │─────────────────────▶ │   MongoDB    │
│  (.NET app) │      < 100ms resp.      │   service   │                        │ (fast writes)│
└─────────────┘                         └─────────────┘                        └──────┬───────┘
                                                                                        │
                                                                              every 2 min (ETL)
                                                                                        │
                                                                                        ▼
                                                                                ┌───────────────┐
                                                                                │  SQL Server   │
                                                                                │ (reporting)   │
                                                                                └───────────────┘
```

**Why two databases?** MongoDB absorbs writes fast enough to hit the sub-100ms response
requirement without blocking on a relational write. SQL Server is what the reporting
tools and the rest of the team already know how to query — the ETL job keeps it in
sync every 2 minutes without the client ever waiting on it.

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI (Python) |
| Fast write store | MongoDB |
| Reporting store | SQL Server |
| Background sync | Custom ETL script (SQLAlchemy + pyodbc) |
| Production hosting | Windows Service (via NSSM) + Task Scheduler |
| Tests | pytest, httpx |

---

## Project structure

```
app/
├── main.py                    FastAPI entrypoint
├── config.py                  Settings loaded from .env
├── api/logger.py              POST /Logger route
├── schemas/audit_log.py       Request validation (Pydantic)
├── models/audit_log.py        SQL Server table model (SQLAlchemy)
├── database/
│   ├── mongodb.py             Mongo connection + indexes
│   └── sqlserver.py           SQL Server connection
├── services/
│   ├── auth_service.py        API key verification
│   ├── audit_service.py       Request → storable document
│   └── queue_service.py       In-memory bounded queue (keeps responses fast)
└── workers/audit_worker.py    Background worker draining the queue into MongoDB
etl/
└── sync_to_sql.py             Syncs unsynced Mongo docs into SQL Server
sql/
└── create_database.sql        DDL for MEAS_AuditLog database + table
tests/
├── test_auth.py
├── test_logger.py
└── test_concurrency.py
docs/
├── production-deployment-guide.md
├── environment-checklist.md
└── how-to-test.md
```

---

## Getting started (local development)

```bash
git clone <repo-url>
cd audit-log-service

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
copy .env.example .env         # then fill in real values, see below
```

Create the database:
```bash
# Run sql/create_database.sql in SSMS against your SQL Server instance
```

Run it:
```bash
uvicorn app.main:app --reload --port 8000
```

---

## Environment variables

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DB` | MongoDB database name |
| `SQL_SERVER` | SQL Server address/instance |
| `SQL_DATABASE` | SQL Server database name (`MEAS_AuditLog`) |
| `SQL_USER` / `SQL_PASSWORD` | SQL auth credentials (leave blank for Windows Auth) |
| `API_KEY` | Shared secret MEAS II sends with each request |

Full explanation of each value and where it comes from: see `docs/environment-checklist.md`.

---

## API contract

**`POST /Logger`**

Body includes `apiKey` (not a header), fire-and-forget from the client side, target
response time < 100ms.

| Response | Meaning |
|---|---|
| `204 No Content` | Accepted and queued |
| `401 Unauthorized` | Invalid `apiKey` |
| `422 Unprocessable Entity` | Missing/invalid required field |

Full field list: see `app/schemas/audit_log.py`.

---

## Testing

```bash
pytest tests/ -v
```

Covers: auth, payload validation (nulls, long strings, Persian text), 100 concurrent
requests, and response latency.

Manual smoke test: see `docs/how-to-test.md`.

---

## Deploying to production

Full walkthrough — server requirements, NSSM service setup, Task Scheduler for the
ETL, firewall config: **`docs/production-deployment-guide.md`**

Short version:
1. Clone repo onto the target server, set up venv, install dependencies
2. Fill in `.env` with production values
3. Run `sql/create_database.sql` against the production SQL Server
4. Wrap the app as a Windows Service with **NSSM** (auto-start, auto-restart)
5. Schedule `python -m etl.sync_to_sql` via **Task Scheduler** (every 2 minutes)
6. Open the firewall for the service's port
7. Run the acceptance checklist below before going live

---

## Acceptance checklist

- [ ] Valid payload → `204`, record in MongoDB
- [ ] ETL sync → same record appears in SQL Server
- [ ] Wrong `apiKey` → `401`
- [ ] Malformed body → `422`
- [ ] Null optional fields handled
- [ ] Long `methodParameters` (4000+ chars) handled
- [ ] Persian text stored correctly (UTF-8)
- [ ] Response time consistently under 100ms
- [ ] 100 concurrent requests — no failures, no dropped records
- [ ] `apiKey` never appears in logs or responses

---

## Status

Deployed and verified in production as of Aug 2026 — running as a Windows Service
with an automated ETL sync. Pending: MEAS II pointed at the live endpoint and
`Audit:Enabled` flipped to `true`.
