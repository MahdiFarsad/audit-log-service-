from app.services.auth_service import is_valid_key
from app.config import settings

def test_valid_key_accepted():
    assert is_valid_key(settings.api_key) is True

def test_invalid_key_rejected():
    assert is_valid_key("wrong-key-12345") is False

def test_empty_key_rejected():
    assert is_valid_key("") is False