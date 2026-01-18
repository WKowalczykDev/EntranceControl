import os
import pickle
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine

# --- KONFIGURACJA ---
DB_FOLDER = "reference_faces"
DB_FILE = "face_db.pkl"
TEST_IMG = "test.jpg"

# Ustawienia modelu (ArcFace + RetinaFace dla najlepszej jakości)
MODEL = "ArcFace"
BACKEND = "retinaface"
THRESHOLD = 0.50  # Dystans < 0.50 oznacza zgodność


def load_db():
    if os.path.exists(DB_FILE):
        print(f"--- Ładowanie bazy z pliku: {DB_FILE} ---")
        with open(DB_FILE, 'rb') as f:
            return pickle.load(f)
    return {}


def save_db(database):
    with open(DB_FILE, 'wb') as f:
        pickle.dump(database, f)
    print("-> Zapisano zmiany w bazie danych.")


def get_embedding(img_path):
    # Funkcja pomocnicza do wyciągania wektora twarzy
    try:
        objs = DeepFace.represent(
            img_path=img_path,
            model_name=MODEL,
            enforce_detection=True,
            detector_backend=BACKEND,
            align=True
        )
        return objs[0]["embedding"]
    except:
        return None


# --- 1. INTELIGENTNA AKTUALIZACJA BAZY ---
database = load_db()
db_changed = False

# Pobieramy listę folderów
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

people_dirs = [d for d in os.listdir(DB_FOLDER) if os.path.isdir(os.path.join(DB_FOLDER, d))]

print(f"--- Sprawdzanie folderów ({len(people_dirs)} osób)... ---")

for person in people_dirs:
    # KLUCZOWE: Jeśli osoba już jest w bazie, pomijamy ją (nie tracimy czasu)
    if person in database:
        continue

    print(f"-> NOWA OSOBA: Generowanie wektora dla {person}...")
    person_path = os.path.join(DB_FOLDER, person)
    images = [os.path.join(person_path, f) for f in os.listdir(person_path) if f.lower().endswith(('.jpg', '.png'))]

    embeddings = []
    for img in images:
        emb = get_embedding(img)
        if emb: embeddings.append(emb)

    if embeddings:
        database[person] = np.mean(embeddings, axis=0)
        db_changed = True
    else:
        print(f"   [!] Ostrzeżenie: Nie udało się wykryć twarzy w folderze {person}")

# Zapisujemy tylko, jeśli dodano kogoś nowego
if db_changed:
    save_db(database)
else:
    print("-> Baza jest aktualna. Brak nowych twarzy do przetworzenia.")

# --- 2. PORÓWNANIE I TABELA WYNIKÓW ---
print(f"\n--- Analiza zdjęcia: {TEST_IMG} ---")
target_embedding = get_embedding(TEST_IMG)

if target_embedding is not None:
    results = []

    for person, vector in database.items():
        dist = cosine(target_embedding, vector)

        # Przeliczanie na procenty (Liniowe: 0 dystans = 100%, 1 dystans = 0%)
        similarity_percent = max(0, (1.0 - dist) * 100)

        results.append((person, similarity_percent, dist))

    # Sortowanie: Największe podobieństwo na górze
    results.sort(key=lambda x: x[1], reverse=True)

    # Rysowanie tabeli
    print("\n" + "=" * 70)
    print(f"{'OSOBA':<25} | {'PODOBIEŃSTWO':<15} | {'DECYZJA (Dystans)'}")
    print("=" * 70)

    best_person = None

    for person, score, dist in results:
        is_match = dist < THRESHOLD

        # Ustalanie ikony i koloru
        if is_match:
            icon = "✅ TAK"
            color = "\033[92m"  # Zielony
            if best_person is None: best_person = person
        else:
            icon = "❌ NIE"
            color = "\033[91m"  # Czerwony
            # Jeśli blisko, ale nie wystarczająco (np. 40-50%), dajmy na żółto
            if score > 40: color = "\033[93m"

        reset = "\033[0m"

        print(f"{color}{person:<25} | {score:6.2f}%         | {icon} ({dist:.4f}){reset}")

    print("=" * 70)

    if best_person:
        print(f"👉 ZIDENTYFIKOWANO: {best_person}")
    else:
        print("👉 BRAK ZGODNOŚCI (Nie rozpoznano nikogo z bazy)")

else:
    print("❌ BŁĄD: Nie wykryto twarzy na zdjęciu testowym (sprawdź oświetlenie lub kąt).")