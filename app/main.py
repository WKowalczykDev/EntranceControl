from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
import shutil
import os
import qrcode
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

# Importy modułów projektu
from database import engine, get_db
from models import Base, Administrator, Pracownik, Przepustka, Bramka, ProbaWejscia, ZdjecieReferencyjne
from schemas import PracownikCreate, PracownikResponse, PrzepustkaCreate, VerificationResponse, BramkaCreate

# System rozpoznawania twarzy
from face_recognition_system import verify_face

# Inicjalizacja bazy danych
Base.metadata.create_all(bind=engine)

app = FastAPI(title="System Kontroli Wejść - Zgodny z Inżynierią Wymagań")

# Konfiguracja CORS
origins = ["*"]  # W produkcji warto ograniczyć do konkretnych domen
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


# ==========================================
# 1. SETUP I KONFIGURACJA (Admin, Bramki)
# ==========================================

@app.post("/setup/bramka")
async def stworz_bramke(bramka: BramkaCreate, db: Session = Depends(get_db)):
    """Tworzy punkt kontrolny (bramkę)."""
    nowa_bramka = Bramka(nazwa=bramka.nazwa, lokalizacja=bramka.lokalizacja)
    db.add(nowa_bramka)
    db.commit()
    db.refresh(nowa_bramka)
    return {"msg": "Bramka utworzona", "id": nowa_bramka.id}


@app.post("/setup/admin")
async def stworz_admina(db: Session = Depends(get_db)):
    """Tworzy domyślnego administratora wymaganego do relacji."""
    if db.query(Administrator).first():
        return {"msg": "Admin już istnieje"}

    admin = Administrator(
        email="admin@firma.pl", haslo_hash="secret",
        imie="Jan", nazwisko="Admin"
    )
    db.add(admin)
    db.commit()
    return {"msg": "Administrator utworzony", "id": admin.id}


# ==========================================
# 2. ZARZĄDZANIE PRACOWNIKAMI
# ==========================================

@app.post("/pracownik", response_model=PracownikResponse)
async def dodaj_pracownika(pracownik: PracownikCreate, db: Session = Depends(get_db)):
    """Rejestruje pracownika i tworzy folder na zdjęcia referencyjne."""

    # Sprawdzenie unikalności ID pracownika (folderu)
    if db.query(Pracownik).filter(Pracownik.id_pracownika == pracownik.id_pracownika).first():
        raise HTTPException(status_code=400, detail="Pracownik o tym ID już istnieje")

    # Sprawdzenie czy istnieje administrator (Foreign Key)
    if not db.query(Administrator).filter(Administrator.id == pracownik.administrator_id).first():
        raise HTTPException(status_code=400, detail="Brak administratora. Użyj /setup/admin")

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

    # Tworzenie fizycznego folderu dla DeepFace
    os.makedirs(os.path.join(REF_DIR, pracownik.id_pracownika), exist_ok=True)

    return nowy_pracownik


@app.post("/pracownik/zdjecie")
async def dodaj_zdjecie_referencyjne(
        pracownik_id: int = Form(...),
        plik: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """Wgrywa zdjęcie 'wzorca' do folderu pracownika."""
    pracownik = db.query(Pracownik).filter(Pracownik.id == pracownik_id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    sciezka = os.path.join(REF_DIR, pracownik.id_pracownika, plik.filename)

    with open(sciezka, "wb") as buffer:
        shutil.copyfileobj(plik.file, buffer)

    db_zdjecie = ZdjecieReferencyjne(pracownik_id=pracownik.id, sciezka_pliku=sciezka)
    db.add(db_zdjecie)
    db.commit()

    return {"msg": "Zdjęcie dodane", "path": sciezka}


@app.delete("/pracownik/{id}")
async def usun_pracownika(id: int, db: Session = Depends(get_db)):
    pracownik = db.query(Pracownik).filter(Pracownik.id == id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    # Opcjonalnie: usuwanie folderu z dysku
    folder_path = os.path.join(REF_DIR, pracownik.id_pracownika)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    db.delete(pracownik)
    db.commit()
    return {"msg": "Pracownik usunięty"}


@app.get("/pracownicy")
async def pobierz_pracownikow(db: Session = Depends(get_db)):
    return db.query(Pracownik).all()


# ==========================================
# 3. GENEROWANIE PRZEPUSTKI QR
# ==========================================

@app.post("/przepustka/generuj")
async def generuj_przepustke_qr(dane: PrzepustkaCreate, db: Session = Depends(get_db)):
    """Generuje kod QR: UID:{id_pracownika}."""
    pracownik = db.query(Pracownik).filter(Pracownik.id == dane.pracownik_id).first()
    if not pracownik:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")

    # Format danych w QR: UID:jan_kowalski_01
    qr_content = f"UID:{pracownik.id_pracownika}"

    # Sprawdzenie czy już ma aktywną
    if db.query(Przepustka).filter(Przepustka.pracownik_id == pracownik.id, Przepustka.aktywna == True).first():
        # Dla celów testowych można tu pozwolić na nadpisanie lub rzucić błąd
        pass

    nowa_przepustka = Przepustka(
        pracownik_id=pracownik.id,
        kod_qr=qr_content,
        data_waznosci=dane.data_waznosci
    )
    db.add(nowa_przepustka)
    db.commit()

    # Generowanie obrazka PNG
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


# ==========================================
# 4. WERYFIKACJA (CORE SYSTEMU)
# ==========================================

@app.post("/verify", response_model=VerificationResponse)
async def verify_entry(
        bramka_id: int = Form(...),
        qr_data: str = Form(...),
        face_image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Implementacja logiki z Diagramu Aktywności (Dokumentacja, str. 6).
    1. Sprawdź ważność QR.
    2. Jeśli QR OK -> Wykonaj porównanie twarzy.
    3. Jeśli podobieństwo >= 90% -> SUKCES.
    4. W przeciwnym razie -> ODMOWA.
    """

    # --- KROK 0: Kontekst Bramki ---
    bramka = db.query(Bramka).filter(Bramka.id == bramka_id).first()
    if not bramka:
        raise HTTPException(status_code=404, detail="Bramka nie istnieje")

    # Przygotowanie obiektu logu
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_image_path = os.path.join(UPLOAD_DIR, f"entry_{bramka_id}_{timestamp}.jpg")

    # Zapisz zdjęcie z kamery (wymagane do analizy i dowodów)
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(face_image.file, buffer)

    log_entry = ProbaWejscia(
        bramka_id=bramka.id,
        sciezka_zdjecia=temp_image_path,
        procent_podobienstwa=0.0,
        podejrzana=False
    )

    # --- KROK 1: Weryfikacja QR ---
    przepustka = db.query(Przepustka).filter(
        Przepustka.kod_qr == qr_data,
        Przepustka.aktywna == True
    ).first()

    # Przypadek: Błędny QR lub przeterminowany
    if not przepustka or przepustka.data_waznosci < date.today():
        log_entry.wynik_qr = "INVALID"
        log_entry.status_finalny = "ODMOWA - nieprawidłowy QR"  # Zgodne z diagramem
        log_entry.wynik_biometryczny = "N/A"

        db.add(log_entry)
        db.commit()

        return VerificationResponse(
            success=False,
            message="Nieprawidłowa przepustka",
            confidence=0.0
        )

    # --- KROK 2: QR Poprawny -> Weryfikacja Biometryczna ---
    log_entry.wynik_qr = "OK"
    pracownik = przepustka.pracownik
    log_entry.pracownik_id = pracownik.id

    # Wyciągamy identyfikator folderu ze zdjęciami tego pracownika
    folder_ref = pracownik.id_pracownika

    try:
        # Wywołanie zewnętrznego modułu rozpoznawania
        is_matched_deepface, conf_val = verify_face(
            test_img=temp_image_path,
            expected_person=folder_ref
        )

        # Zapisz wynik liczbowy
        log_entry.procent_podobienstwa = conf_val

        # --- KROK 3: Decyzja (Próg 90%) ---
        THRESHOLD = 90.0  # Wymaganie z dokumentacji (str. 3 i 6)

        if conf_val >= THRESHOLD:
            # SUKCES
            log_entry.wynik_biometryczny = "MATCH"
            log_entry.status_finalny = "SUKCES"
            komunikat = f"Wejście dozwolone. Witaj {pracownik.imie} {pracownik.nazwisko}"
            db_success = True
        else:
            # ODMOWA BIOMETRYCZNA
            log_entry.wynik_biometryczny = "NO_MATCH"
            log_entry.status_finalny = "ODMOWA - niska zgodność"  # Zgodne z diagramem
            log_entry.podejrzana = True  # Oznacz jako potencjalne nadużycie
            komunikat = "Odmowa wejścia - weryfikacja nieudana"
            db_success = False

    except Exception as e:
        print(f"Błąd krytyczny DeepFace: {e}")
        log_entry.status_finalny = "BŁĄD SYSTEMU"
        komunikat = "Błąd wewnętrzny serwera przetwarzania obrazu"
        db_success = False
        log_entry.procent_podobienstwa = 0.0

    # Zapisz log w bazie
    db.add(log_entry)
    db.commit()

    return VerificationResponse(
        success=db_success,
        message=komunikat,
        person_name=f"{pracownik.imie} {pracownik.nazwisko}" if db_success else None,
        confidence=log_entry.procent_podobienstwa
    )


# ==========================================
# 5. RAPORTY I LOGI
# ==========================================

@app.get("/logi/")
async def pobierz_logi(pracownik_id: int, db: Session = Depends(get_db)):
    """Pobiera historię wejść pracownika."""
    logi = db.query(ProbaWejscia).filter(ProbaWejscia.pracownik_id == pracownik_id) \
        .order_by(ProbaWejscia.data_czas.desc()).all()
    return logi


