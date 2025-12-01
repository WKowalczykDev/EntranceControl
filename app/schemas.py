from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QRCodeCreate(BaseModel):
    qr_data: str
    person_name: str

class QRCodeResponse(BaseModel):
    id: int
    qr_data: str
    person_name: str
    is_active: bool
    created_at: datetime

class VerificationRequest(BaseModel):
    qr_data: str

class VerificationResponse(BaseModel):
    success: bool
    message: str
    person_name: Optional[str] = None
    confidence: Optional[float] = None