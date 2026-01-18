import os
import pickle
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine

# --- KONFIGURACJA ---
# Używamy katalogu reference_faces, który jest już w Twojej strukturze
DB_FOLDER = "reference_faces"
DB_FILE = os.path.join(DB_FOLDER, "face_db.pkl")

# Ustawienia modelu (z Twojego kodu)
MODEL = "ArcFace"
BACKEND = "retinaface"
THRESHOLD = 0.50  # Dystans < 0.50 oznacza zgodność dla ArcFace

# Globalna zmienna na bazę w pamięci RAM
_face_database = None


def load_db():
    """Ładuje bazę wektorów z pliku pickle do pamięci."""
    global _face_database
    if os.path.exists(DB_FILE):
        print(f"--- [AI] Ładowanie bazy wektorów z: {DB_FILE} ---")
        with open(DB_FILE, 'rb') as f:
            _face_database = pickle.load(f)
    else:
        print("--- [AI] Brak pliku bazy wektorów, tworzę nową. ---")
        _face_database = {}
    return _face_database


def save_db():
    """Zapisuje aktualny stan bazy wektorów na dysk."""
    global _face_database
    if _face_database is not None:
        with open(DB_FILE, 'wb') as f:
            pickle.dump(_face_database, f)
        print("-> [AI] Zapisano zmiany w bazie wektorów.")


def get_embedding(img_path):
    """Generuje wektor cech dla podanego obrazu."""
    try:
        objs = DeepFace.represent(
            img_path=img_path,
            model_name=MODEL,
            enforce_detection=True,
            detector_backend=BACKEND,
            align=True
        )
        # DeepFace.represent zwraca listę, bierzemy pierwszą twarz
        return objs[0]["embedding"]
    except Exception as e:
        # print(f"Błąd generowania embeddingu: {e}")
        return None


def update_person_embedding(person_id: str):
    """
    Wymusza aktualizację wektora dla konkretnej osoby (np. po dodaniu zdjęcia).
    Skanuje folder danej osoby i uśrednia wektory.
    """
    global _face_database
    if _face_database is None:
        load_db()

    person_path = os.path.join(DB_FOLDER, person_id)
    if not os.path.exists(person_path):
        return False

    images = [os.path.join(person_path, f) for f in os.listdir(person_path)
              if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    embeddings = []
    print(f"-> [AI] Przetwarzanie osoby: {person_id} ({len(images)} zdjęć)...")

    for img in images:
        emb = get_embedding(img)
        if emb:
            embeddings.append(emb)

    if embeddings:
        # Uśredniamy wektory wszystkich zdjęć tej osoby
        _face_database[person_id] = np.mean(embeddings, axis=0)
        save_db()
        return True
    return False


def verify_face(test_img: str, expected_person: str, threshold: float = THRESHOLD):
    """
    Główna funkcja wywoływana przez main.py.
    Sprawdza, czy twarz na zdjęciu test_img należy do expected_person.
    """
    global _face_database

    # 1. Upewnij się, że baza jest załadowana
    if _face_database is None:
        load_db()

    # 2. Jeśli osoby nie ma w cache (np. dopiero dodana), spróbuj ją przetworzyć
    if expected_person not in _face_database:
        print(f"-> [AI] Osoby {expected_person} brak w cache, próba generowania...")
        found = update_person_embedding(expected_person)
        if not found:
            print(f"-> [AI] Nie znaleziono zdjęć referencyjnych dla {expected_person}")
            return False, 0.0

    # 3. Pobierz wektor wzorcowy
    target_vector = _face_database[expected_person]

    # 4. Wygeneruj wektor dla zdjęcia z bramki
    current_vector = get_embedding(test_img)

    if current_vector is None:
        print("-> [AI] Nie wykryto twarzy na zdjęciu z bramki.")
        return False, 0.0

    # 5. Oblicz dystans
    dist = cosine(current_vector, target_vector)

    # 6. Interpretacja wyniku
    is_match = dist < threshold

    # Konwersja dystansu na procenty dla main.py (który wymaga > 90% dla sukcesu)
    # ArcFace: 0.0 to identyczne, >0.5 to różne.
    # Musimy to przeskalować tak, aby próg 0.5 odpowiadał np. 90% pewności w logice biznesowej.

    if is_match:
        # Skalowanie: 0.0 -> 100%, threshold -> 90%
        # Wzór: 100 - (dist / threshold) * 10
        probability = max(90.0, 100.0 - (dist / threshold) * 10.0)
    else:
        # Skalowanie reszty: threshold -> 89%, 1.0 -> 0%
        probability = max(0.0, (1.0 - dist) * 100)

    print(
        f"-> [AI] Wynik weryfikacji: {expected_person} | Dystans: {dist:.4f} | Prob: {probability:.2f}% | Match: {is_match}")

    return is_match, probability

# Inicjalizacja przy starcie (opcjonalna, main.py i tak wywoła verify)
# load_db()