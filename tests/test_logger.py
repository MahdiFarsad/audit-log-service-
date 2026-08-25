from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

VALID_PAYLOAD = {
    "iD_OrgPerson": 23864,
    "logType": 1,
    "computerIP": "192.168.1.77",
    "userAgent": "Mozilla/5.0",
    "areaName": "",
    "controllerName": "RawConfirmsApi",
    "actionName": "Save",
    "methodParameters": "{}",
    "httpmethod": "POST",
    "displayName": "test",
    "impersonatorId": None,
    "occurredAt": "2026-08-16T14:30:12.345",
    "succeeded": True,
    "statusCode": 200,
    "errorMessage": None,
    "durationMs": 137,
    "apiKey": settings.api_key,
}

def test_valid_payload_returns_204():
    response = client.post("/Logger", json=VALID_PAYLOAD)
    assert response.status_code == 204

def test_wrong_api_key_returns_401():
    payload = {**VALID_PAYLOAD, "apiKey": "wrong-key"}
    response = client.post("/Logger", json=payload)
    assert response.status_code == 401

def test_missing_required_field_returns_400():
    payload = {**VALID_PAYLOAD}
    del payload["logType"]  # required field
    response = client.post("/Logger", json=payload)
    assert response.status_code == 422  # FastAPI/Pydantic validation error code

def test_null_optional_fields_accepted():
    payload = {**VALID_PAYLOAD, "computerIP": None, "userAgent": None, "errorMessage": None}
    response = client.post("/Logger", json=payload)
    assert response.status_code == 204

def test_long_method_parameters_accepted():
    payload = {**VALID_PAYLOAD, "methodParameters": "x" * 4001}
    response = client.post("/Logger", json=payload)
    assert response.status_code == 204

def test_persian_display_name_accepted():
    payload = {**VALID_PAYLOAD, "displayName": "ثبت سند"}
    response = client.post("/Logger", json=payload)
    assert response.status_code == 204