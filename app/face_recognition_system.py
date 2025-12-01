from deepface import DeepFace
import os

db_path = "reference_faces"  # katalog z folderami osób
test_img = "test_image.jpg"

# Ustawienie progu – zależy od modelu, domyślnie DeepFace go stosuje,
# ale można wymusić swoje kryterium.
threshold = 0.4

results = DeepFace.find(
    img_path=test_img,
    db_path=db_path,
    model_name="Facenet",
    enforce_detection=False
)

# Jeśli nic nie znaleziono → osoba nie istnieje
if len(results[0]) == 0:
    print("Osoba nie istnieje w bazie.")
else:
    # Wynik to DataFrame ze ścieżkami do dopasowanych zdjęć i odległością
    best_match = results[0].iloc[0]
    identity = best_match["identity"]
    distance = best_match["distance"]

    if distance < threshold:
        # katalog to imię osoby
        person = identity.split(os.sep)[-2]
        probability = max(0.0,distance / threshold)
        print(f"Rozpoznano osobę: {person}")
        print(f"Probability: {probability * 100:.2f}%")
    else:
        print("Osoba nie istnieje w bazie.")
