from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str

    sql_server: str
    sql_database: str
    sql_user: Optional[str] = None
    sql_password: Optional[str] = None

    api_key: str

    model_config = {"env_file": ".env"}

settings = Settings()