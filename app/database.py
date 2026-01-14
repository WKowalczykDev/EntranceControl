from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base # <--- TEGO BRAKOWAŁO
from sqlalchemy.orm import sessionmaker
import os

# Konfiguracja połączenia
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qruser:qrpass123@postgres:5432/qr_database"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# To jest ta linijka, która powodowała błąd (teraz zadziała, bo dodaliśmy import wyżej)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()