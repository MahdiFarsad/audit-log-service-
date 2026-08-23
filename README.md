# Audit Log Service

FastAPI service that ingests audit/activity log events from MEAS II via POST /Logger,
writes them to MongoDB, and syncs them to SQL Server for reporting.

## Setup
1. python -m venv venv && venv\Scripts\activate
2. pip install -r requirements.txt
3. Copy .env.example to .env and fill in real values
4. uvicorn app.main:app --reload --port 8000
