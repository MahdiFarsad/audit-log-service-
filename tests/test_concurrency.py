import time
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def make_payload(i: int) -> dict:
    return {
        "iD_OrgPerson": i,
        "logType": 1,
        "computerIP": "192.168.1.77",
        "userAgent": "Mozilla/5.0",
        "areaName": "",
        "controllerName": "LoadTest",
        "actionName": "Concurrent",
        "methodParameters": "{}",
        "httpmethod": "POST",
        "displayName": f"load-test-{i}",
        "impersonatorId": None,
        "occurredAt": "2026-08-16T14:30:12.345",
        "succeeded": True,
        "statusCode": 200,
        "errorMessage": None,
        "durationMs": 10,
        "apiKey": settings.api_key,
    }

def test_100_concurrent_requests_all_succeed(client):
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda i: client.post("/Logger", json=make_payload(i)), range(100)))
    statuses = [r.status_code for r in results]
    assert all(s == 204 for s in statuses), f"Some requests failed: {statuses}"

def test_response_time_under_100ms(client):
    start = time.perf_counter()
    response = client.post("/Logger", json=make_payload(999))
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert response.status_code == 204
    assert elapsed_ms < 100, f"Response took {elapsed_ms:.1f}ms, expected under 100ms"