from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str

    sql_server: str
    sql_database: str
    sql_user: str
    sql_password: str

    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
