from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    qr_data = Column(String, unique=True, nullable=False, index=True)
    person_name = Column(String, nullable=False)  # Musi odpowiadać nazwie folderu w reference_faces
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_verified = Column(DateTime, nullable=True)


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    qr_data = Column(String, nullable=False)
    person_name = Column(String, nullable=True)
    face_matched = Column(Boolean, nullable=True)
    verification_time = Column(DateTime, default=datetime.utcnow)
    confidence = Column(String, nullable=True)