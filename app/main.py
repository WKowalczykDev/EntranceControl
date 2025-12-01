from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

from database import engine, get_db
from models import Base, QRCode, VerificationLog
from schemas import QRCodeCreate, QRCodeResponse, VerificationResponse
from face_recognition_system import verify_face

# Tworzenie tabel
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QR + Face Recognition System")


# ============== ENDPOINTY QR ==============

@app.post("/qr/generate")
async def generate_qr(qr_create: QRCodeCreate, db: Session = Depends(get_db)):
    """Generuje kod QR i zapisuje w bazie"""

    # Sprawdź czy QR już istnieje
    existing = db.query(QRCode).filter(QRCode.qr_data == qr_create.qr_data).first()
    if existing:
        raise HTTPException(status_code=400, detail="QR code już istnieje")

    # Zapisz w bazie
    new_qr = QRCode(
        qr_data=qr_create.qr_data,
        person_name=qr_create.person_name
    )
    db.add(new_qr)
    db.commit()
    db.refresh(new_qr)

    # Wygeneruj obraz QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_create.qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Zwróć jako PNG
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@app.get("/qr/list")
async def list_qr_codes(db: Session = Depends(get_db)):
    """Lista wszystkich QR kodów"""
    qr_codes = db.query(QRCode).filter(QRCode.is_active == True).all()
    return qr_codes


# ============== ENDPOINT WERYFIKACJI ==============

@app.post("/verify", response_model=VerificationResponse)
async def verify_qr_and_face(
        qr_data: str = Form(...),
        face_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    KROK 1: Sprawdza QR w bazie
    KROK 2: Jeśli OK → weryfikuje twarz
    """

    # KROK 1: Weryfikacja QR
    qr_record = db.query(QRCode).filter(
        QRCode.qr_data == qr_data,
        QRCode.is_active == True
    ).first()

    if not qr_record:
        # Loguj nieudaną próbę
        log = VerificationLog(qr_data=qr_data, face_matched=False)
        db.add(log)
        db.commit()

        return VerificationResponse(
            success=False,
            message="Kod QR nie istnieje w bazie lub jest nieaktywny"
        )

    # KROK 2: Weryfikacja twarzy
    # Zapisz przesłane zdjęcie tymczasowo
    temp_image_path = f"uploads/temp_{qr_data}_{datetime.now().timestamp()}.jpg"
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(face_image.file, buffer)

    try:
        # Wywołaj funkcję rozpoznawania twarzy
        person_folder = qr_record.person_name
        is_matched, confidence = verify_face(
            test_img=temp_image_path,
            expected_person=person_folder
        )

        # Aktualizuj rekord QR
        qr_record.last_verified = datetime.utcnow()

        # Loguj weryfikację
        log = VerificationLog(
            qr_data=qr_data,
            person_name=person_folder if is_matched else None,
            face_matched=is_matched,
            confidence=f"{confidence:.2f}%" if is_matched else None
        )
        db.add(log)
        db.commit()

        # Usuń tymczasowy plik
        os.remove(temp_image_path)

        if is_matched:
            return VerificationResponse(
                success=True,
                message=f"Weryfikacja udana! Witaj {person_folder}",
                person_name=person_folder,
                confidence=confidence
            )
        else:
            return VerificationResponse(
                success=False,
                message="Twarz nie pasuje do osoby przypisanej do QR"
            )

    except Exception as e:
        # Usuń plik w razie błędu
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        raise HTTPException(status_code=500, detail=f"Błąd weryfikacji: {str(e)}")


@app.get("/")
async def root():
    return {"message": "QR + Face Recognition System API"}