# System kontroli wejść na teren zakładu pracy

System weryfikacji tożsamości pracowników wykorzystujący kody QR oraz rozpoznawanie twarzy do kontroli dostępu na teren zakładu pracy.

## Opis projektu

System eliminuje nadużycia związane z przekazywaniem kart dostępu poprzez dwuetapową weryfikację:
1. **Skanowanie kodu QR** - identyfikacja pracownika
2. **Rozpoznawanie twarzy** - weryfikacja biometryczna (min. 90% dokładności)

Każda próba wejścia jest rejestrowana z pełnymi danymi (data, godzina, wynik weryfikacji, procent podobieństwa), a system automatycznie wykrywa podejrzane próby dostępu.

## Funkcjonalności

### Panel administratora (aplikacja webowa)
- Zarządzanie profilami pracowników (imię, nazwisko, stanowisko)
- Przypisywanie zdjęć referencyjnych (min. 3 na osobę)
- Generowanie kodów QR
- Przeglądanie logów wejść
- Generowanie raportów (wejścia, nadużycia, efektywność)
- Konfiguracja systemu

### System przy bramkach
- Automatyczne skanowanie QR
- Przechwytywanie zdjęcia twarzy
- Weryfikacja biometryczna w czasie rzeczywistym
- Rejestracja wszystkich prób dostępu
- Sterowanie bramką (otwarcie/odmowa)

## Technologie

### Backend
- **Python 3.11** - język programowania
- **FastAPI** - framework REST API
- **PostgreSQL** - baza danych
- **SQLAlchemy** - ORM
- **DeepFace** - rozpoznawanie twarzy (model Facenet)
- **OpenCV** - przetwarzanie obrazu
- **qrcode/pyzbar** - obsługa kodów QR

### Frontend (planowany)
- **React** - biblioteka UI
- **Vite** - build tool
- **Chart.js/Recharts** - wizualizacja danych

### Infrastruktura
- **Docker** - konteneryzacja
- **docker-compose** - orkiestracja
- **pgAdmin** - zarządzanie bazą danych

## Instalacja i uruchomienie

### Wymagania
- Docker
- Docker Compose
- Kamera 1080p (dla systemu przy bramkach)
- Czytnik QR

### Uruchomienie

1. Sklonuj repozytorium
2. Utwórz katalog `reference_faces` z folderami dla każdego pracownika:
```
reference_faces/
├── jan_kowalski/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.jpg
└── anna_nowak/
    ├── foto1.jpg
    ├── foto2.jpg
    └── foto3.jpg
```

3. Uruchom kontenerzy:
```bash
docker-compose up -d
```

4. API dostępne pod adresem: `http://localhost:8000`
5. pgAdmin: `http://localhost:5050` (login: admin@admin.com / hasło: admin)

## API Endpoints

### Generowanie QR
```http
POST /qr/generate
Content-Type: application/json

{
  "qr_data": "EMP001",
  "person_name": "jan_kowalski"
}
```

### Lista kodów QR
```http
GET /qr/list
```

### Weryfikacja QR + Twarz
```http
POST /verify
Content-Type: multipart/form-data

qr_data: "EMP001"
face_image: [plik jpg/png]
```

## Struktura projektu

```
.
├── app/
│   ├── main.py                      # Główna aplikacja FastAPI
│   ├── models.py                    # Modele SQLAlchemy
│   ├── schemas.py                   # Schematy Pydantic
│   ├── database.py                  # Konfiguracja bazy danych
│   ├── face_recognition_system.py   # Moduł rozpoznawania twarzy
│   ├── requirements.txt             # Zależności Python
│   └── Dockerfile                   # Obraz Docker
├── reference_faces/                 # Zdjęcia referencyjne pracowników
├── uploads/                         # Tymczasowe zdjęcia z weryfikacji
├── docker-compose.yml               # Konfiguracja kontenerów
└── README.md
```

## Bezpieczeństwo

- Hasła administratorów szyfrowane SHA256
- Połączenie z bazą danych przez zmienne środowiskowe
- Automatyczne usuwanie tymczasowych zdjęć po weryfikacji
- Logowanie wszystkich prób dostępu

## Ograniczenia

- System zaprojektowany dla max. 100 aktywnych pracowników
- Wymaga dobrego oświetlenia przy bramkach
- Aplikacja webowa wymaga połączenia internetowego
- Interfejs w języku polskim