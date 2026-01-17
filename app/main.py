from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
import shutil
import os
import qrcode
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

# Importy z Twojego projektu
from database import engine, get_db
from models import Base, Administrator, Pracownik, Przepustka, Bramka, ProbaWejscia, ZdjecieReferencyjne
from schemas import PracownikCreate, PracownikResponse, PrzepustkaCreate, VerificationResponse, BramkaCreate

# Zakładam, że ten plik masz i działa (zwraca is_matched, confidence)
from face_recognition_system import verify_face

# Tworzenie tabel (jeśli nie istnieją)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="QR + Face Recognition System")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfiguracja folderów
UPLOAD_DIR = "uploads"
REF_DIR = "reference_faces"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)

# ============== 1. KONFIGURACJA (ADMIN, BRAMKA, PRACOWNIK) ==============

@app.post("/setup/bramka")
async def stworz_bramke(bramka: BramkaCreate, db: Session = Depends(get_db)):
    """Tworzy bramkę (konieczne, aby rejestrować wejścia)"""
    nowa_bramka = Bramka(nazwa=bramka.nazwa, lokalizacja=bramka.lokalizacja)
    db.add(nowa_bramka)
    db.commit()
    return {"msg": "Bramka utworzona", "id": nowa_bramka.id}

@app.post("/setup/admin")
async def stworz_admina(db: Session = Depends(get_db)):
    """Tworzy domyślnego administratora (potrzebny do tworzenia pracowników)"""
    if db.query(Administrator).first():
        return {"msg": "Admin już istnieje"}

    admin = Administrator(
        email="admin@firma.pl", haslo_hash="secret",
        imie="Jan", nazwisko="Admin"
    )
    db.add(admin)
    db.commit()
    return {"msg": "Administrator utworzony", "id": admin.id}

@app.post("/pracownik", response_model=PracownikResponse)
async def dodaj_pracownika(pracownik: PracownikCreate, db: Session = Depends(get_db)):
    """Tworzy pracownika i folder na jego zdjęcia"""

    # Sprawdź unikalność ID
    if db.query(Pracownik).filter(Pracownik.id_pracownika == pracownik.id_pracownika).first():
        raise HTTPException(status_code=400, detail="Pracownik o tym ID już istnieje")

    # Sprawdź czy admin istnieje (wymagane przez klucz obcy)
    if not db.query(Administrator).filter(Administrator.id == pracownik.administrator_id).first():
        # Fallback: jeśli admina nie ma, stwórzmy go 'w locie' lub rzućmy błąd
        raise HTTPException(status_code=400, detail="Administrator o podanym ID nie istnieje. Użyj /setup/admin")

    nowy_pracownik = Pracownik(
        administrator_id=pracownik.administrator_id,
        id_pracownika=pracownik.id_pracownika,
        imie=pracownik.imie,
        nazwisko=pracownik.nazwisko,
        email=pracownik.email,
        stanowisko=pracownik.stanowisko,
        data_zatrudnienia=pracownik.data_zatrudnienia
    )
    db.add(nowy_pracownik)
    db.commit()
    db.refresh(nowy_pracownik)

    # Utwórz folder dla pracownika (ważne dla face_recognition!)
    os.makedirs(os.path.join(REF_DIR, pracownik.id_pracownika), exist_ok=True)

    return nowy_pracownik

@app.post("/pracownik/zdjecie")
async def dodaj_zdjecie_referencyjne(
    pracownik_id: int = Form(...),
    plik: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Wgrywa zdjęcie twarzy do folderu pracownika"""
    pracownik = db.query(Pracownik).filter(Pracownik.id == pracownik_id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    sciezka = os.path.join(REF_DIR, pracownik.id_pracownika, plik.filename)

    with open(sciezka, "wb") as buffer:
        shutil.copyfileobj(plik.file, buffer)

    # Zapisz w bazie informację o zdjęciu
    db_zdjecie = ZdjecieReferencyjne(pracownik_id=pracownik.id, sciezka_pliku=sciezka)
    db.add(db_zdjecie)
    db.commit()

    return {"msg": "Zdjęcie dodane", "path": sciezka}

# ============== 2. GENEROWANIE QR (Przepustka) ==============

@app.post("/przepustka/generuj")
async def generuj_przepustke_qr(dane: PrzepustkaCreate, db: Session = Depends(get_db)):
    """Generuje przepustkę, zapisuje w bazie i zwraca obrazek QR"""

    pracownik = db.query(Pracownik).filter(Pracownik.id == dane.pracownik_id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    # Logika generowania treści QR (np. ID pracownika + unikalny znacznik)
    qr_content = f"UID:{pracownik.id_pracownika}"

    # Sprawdź czy pracownik ma już przepustkę
    if db.query(Przepustka).filter(Przepustka.pracownik_id == pracownik.id).first():
        raise HTTPException(status_code=400, detail="Ten pracownik ma już aktywną przepustkę")

    # Zapisz w bazie
    nowa_przepustka = Przepustka(
        pracownik_id=pracownik.id,
        kod_qr=qr_content,
        data_waznosci=dane.data_waznosci
    )
    db.add(nowa_przepustka)
    db.commit()

    # Wygeneruj obraz QR (Twoja logika)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

# ============== 3. WERYFIKACJA (ProbaWejscia) ==============

@app.post("/verify", response_model=VerificationResponse)
async def verify_entry(
        bramka_id: int = Form(...), # Nowe pole!
        qr_data: str = Form(...),
        face_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """Logika weryfikacji zgodna z nowym diagramem"""

    # 1. Sprawdź bramkę
    bramka = db.query(Bramka).filter(Bramka.id == bramka_id).first()
    if not bramka:
        raise HTTPException(status_code=404, detail="Bramka nie istnieje")

    # 2. Sprawdź QR w tabeli Przepustka
    przepustka = db.query(Przepustka).filter(
        Przepustka.kod_qr == qr_data,
        Przepustka.aktywna == True
    ).first()

    status_finalny = "DENIED"
    wynik_qr = "INVALID"
    pracownik_imie = None
    confidence = 0.0
    is_matched = False

    # Zapisz zdjęcie z bramki
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_image_path = os.path.join(UPLOAD_DIR, f"entry_{bramka_id}_{timestamp}.jpg")
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(face_image.file, buffer)

    pracownik_id_log = None # Do logów

    # --- Logika biznesowa ---
    if przepustka:
        # Sprawdź datę
        if przepustka.data_waznosci >= date.today():
            wynik_qr = "OK"
            pracownik = przepustka.pracownik
            pracownik_id_log = pracownik.id
            pracownik_imie = f"{pracownik.imie} {pracownik.nazwisko}"

            # Weryfikacja twarzy
            # folder referencyjny to id_pracownika (np. "jan_kowalski_01")
            folder_ref = pracownik.id_pracownika

            try:
                # Twoja funkcja z face_recognition_system.py
                is_matched, conf_val = verify_face(
                    test_img=temp_image_path,
                    expected_person=folder_ref
                )
                confidence = conf_val

                if is_matched:
                    status_finalny = "GRANTED"
            except Exception as e:
                print(f"Błąd face recognition: {e}")
        else:
            wynik_qr = "EXPIRED"

    # --- Zapisz Raport (ProbaWejscia) ---
    log = ProbaWejscia(
        bramka_id=bramka.id,
        pracownik_id=pracownik_id_log,
        wynik_qr=wynik_qr,
        wynik_biometryczny="MATCH" if is_matched else "NO_MATCH",
        procent_podobienstwa=confidence,
        status_finalny=status_finalny,
        sciezka_zdjecia=temp_image_path
    )
    db.add(log)
    db.commit()

    # --- Odpowiedź ---
    if status_finalny == "GRANTED":
        return VerificationResponse(
            success=True,
            message=f"Wstęp przyznany. Witaj {pracownik_imie}",
            person_name=pracownik_imie,
            confidence=confidence
        )
    else:
        return VerificationResponse(
            success=False,
            message=f"Odmowa dostępu. QR: {wynik_qr}, Twarz: {'OK' if is_matched else 'Mismatch'}"
        )

@app.get("/pracownicy")
async def pobierz_pracownikow(db: Session = Depends(get_db)):
    """Pobiera listę wszystkich pracowników do tabeli"""
    return db.query(Pracownik).all()

@app.delete("/pracownik/{id}")
async def usun_pracownika(id: int, db: Session = Depends(get_db)):
    """Usuwa pracownika"""
    pracownik = db.query(Pracownik).filter(Pracownik.id == id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    db.delete(pracownik)
    db.commit()
    return {"msg": "Usunięto"}

@app.get("/logi/")
async def pobierz_logi(pracownik_id: int, db: Session = Depends(get_db)):
    """Pobiera historię wejść dla konkretnego pracownika (do raportów)"""
    # Zwracamy logi posortowane od najnowszych
    logi = db.query(ProbaWejscia).filter(ProbaWejscia.pracownik_id == pracownik_id)\
             .order_by(ProbaWejscia.data_czas.desc()).all()
    return logi