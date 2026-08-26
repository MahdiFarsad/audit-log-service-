from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

connection_string = (
    f"mssql+pyodbc://@{settings.sql_server}/{settings.sql_database}"
    f"?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

engine = create_engine(connection_string, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
