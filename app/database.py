from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# POPRAWIONY connection string - użytkownik@host/nazwa_bazy
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qruser:qrpass123@postgres:5432/qr_database"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()