import hmac
from app.config import settings

def is_valid_key(provided_key: str) -> bool:
    return hmac.compare_digest(provided_key, settings.api_key)
