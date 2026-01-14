from pydantic import BaseModel
from datetime import date
from typing import Optional

# --- BRAMKA ---
# Używane przy tworzeniu nowej bramki (POST /setup/bramka)
class BramkaCreate(BaseModel):
    nazwa: str
    lokalizacja: str

# --- PRACOWNIK ---
# Dane potrzebne do rejestracji pracownika
class PracownikCreate(BaseModel):
    imie: str
    nazwisko: str
    id_pracownika: str  # Np. "jan_kowalski" - to będzie też nazwa folderu zdjęć
    email: str
    stanowisko: str
    administrator_id: int = 1  # Domyślne ID admina
    data_zatrudnienia: date

# Dane zwracane przez API po utworzeniu pracownika
class PracownikResponse(BaseModel):
    id: int
    imie: str
    nazwisko: str
    id_pracownika: str
    stanowisko: str
    aktywny: bool

    class Config:
        orm_mode = True  # Pozwala Pydantic czytać dane bezpośrednio z obiektów SQLAlchemy

# --- PRZEPUSTKA ---
# Dane potrzebne do wygenerowania przepustki
class PrzepustkaCreate(BaseModel):
    pracownik_id: int
    data_waznosci: date

# --- WERYFIKACJA ---
# Odpowiedź wysyłana do bramki po weryfikacji
class VerificationResponse(BaseModel):
    success: bool
    message: str
    person_name: Optional[str] = None
    confidence: Optional[float] = None