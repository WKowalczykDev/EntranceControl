from deepface import DeepFace
import os

def verify_face(test_img: str, expected_person: str, threshold: float = 0.4):
    db_path = "../reference_faces"  # katalog z folderami osób

    expected_folder = os.path.join(db_path, expected_person)

    if not os.path.exists(expected_folder):
        raise ValueError(f"Folder {expected_person} nie istnieje w reference_faces")


    try:
        results = DeepFace.find(
            img_path=test_img,
            db_path=db_path,
            model_name="Facenet",
            enforce_detection=False,
            silent=True
        )

        # Jeśli nic nie znaleziono
        if len(results[0]) == 0:
            return False, 0.0

        # Sprawdź najlepsze dopasowanie
        best_match = results[0].iloc[0]
        identity = best_match["identity"]
        distance = best_match["distance"]

        # Wyciągnij nazwę osoby z ścieżki
        matched_person = identity.split(os.sep)[-2]

        # Sprawdź czy zgadza się z oczekiwaną osobą
        if matched_person == expected_person and distance < threshold:
            probability = max(0.0, (1 - distance / threshold) * 100)
            return True, probability
        else:
            return False, 0.0

    except Exception as e:
        print(f"Błąd rozpoznawania: {e}")
        return False, 0.0