import cv2
import requests
import time
import sys

# --- KONFIGURACJA ---
# Jeśli odpalasz symulator lokalnie, a backend jest w Dockerze -> localhost:8000
API_URL = "http://localhost:8000"


def get_available_gates():
    """Pobiera listę bramek z API."""
    try:
        response = requests.get(f"{API_URL}/setup/bramki")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Nie można połączyć się z API. Upewnij się, że backend działa.")
        return []
    return []


def create_gate(name, location):
    """Tworzy nową bramkę przez API."""
    payload = {"nazwa": name, "lokalizacja": location}
    try:
        response = requests.post(f"{API_URL}/setup/bramka", json=payload)
        if response.status_code == 200:
            print(f"✅ Utworzono bramkę: {name}")
            return response.json()
    except Exception as e:
        print(f"❌ Błąd tworzenia bramki: {e}")
    return None


def verify_entry_api(frame, qr_data, gate_id):
    """Wysyła ramkę i kod QR do backendu"""
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'face_image': ('capture.jpg', img_encoded.tobytes(), 'image/jpeg')}
        data = {'bramka_id': gate_id, 'qr_data': qr_data}

        print(f"📡 Wysyłanie do weryfikacji (Bramka {gate_id})... QR: {qr_data}")
        response = requests.post(f"{API_URL}/verify", data=data, files=files)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Błąd sieci: {e}", "confidence": 0}


def draw_text(img, text, y_pos, color=(0, 255, 0), scale=0.8):
    cv2.putText(img, text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)


# --- MENU WYBORU BRAMKI ---
def select_gate_menu():
    print("\n--- KONFIGURACJA SYMULATORA ---")
    gates = get_available_gates()

    if not gates:
        print("⚠️ Brak bramek w systemie.")
        choice = input("Czy chcesz utworzyć nową bramkę? (t/n): ")
        if choice.lower() == 't':
            name = input("Nazwa bramki: ")
            loc = input("Lokalizacja: ")
            create_gate(name, loc)
            gates = get_available_gates()
        else:
            print("Koniec programu.")
            sys.exit()

    print("\nDostępne bramki:")
    for idx, g in enumerate(gates):
        print(f"[{idx + 1}] ID: {g['id']} | {g['nazwa']} ({g['lokalizacja']})")

    while True:
        try:
            sel = input("\nWybierz numer bramki z listy (lub 'n' by dodać nową): ")
            if sel.lower() == 'n':
                name = input("Nazwa bramki: ")
                loc = input("Lokalizacja: ")
                create_gate(name, loc)
                gates = get_available_gates()  # odśwież listę
                # Wypisz ponownie
                for idx, g in enumerate(gates):
                    print(f"[{idx + 1}] ID: {g['id']} | {g['nazwa']} ({g['lokalizacja']})")
                continue

            idx = int(sel) - 1
            if 0 <= idx < len(gates):
                return gates[idx]  # Zwracamy obiekt wybranej bramki
        except ValueError:
            pass
        print("Nieprawidłowy wybór.")


# --- GŁÓWNA PĘTLA ---
def main():
    # 1. Wybór bramki na starcie
    current_gate = select_gate_menu()

    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    state = 'SCANNING'
    current_qr = None
    result_data = None
    result_timer = 0

    # Cache listy bramek do szybkiego przełączania
    all_gates = get_available_gates()
    gate_index = 0
    # Ustaw index na aktualnie wybraną
    for i, g in enumerate(all_gates):
        if g['id'] == current_gate['id']:
            gate_index = i
            break

    print(f"🚀 Symulator Uruchomiony na bramce: {current_gate['nazwa']}")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # --- NAGŁÓWEK ---
        # Pasek statusu na górze
        cv2.rectangle(frame, (0, 0), (640, 40), (50, 50, 50), -1)
        draw_text(frame, f"BRAMKA: {current_gate['nazwa']} (ID: {current_gate['id']})", 30, (255, 255, 0), 0.7)

        # --- LOGIKA STANÓW ---
        if state == 'SCANNING':
            draw_text(frame, "STATUS: SKANOWANIE QR...", 80, (255, 255, 255))
            draw_text(frame, "[G] - Zmien bramke", 450, (200, 200, 200), 0.6)

            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                current_qr = data
                state = 'WAIT_FOR_USER'

        elif state == 'WAIT_FOR_USER':
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 50), (640, 200), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            draw_text(frame, f"QR: {current_qr}", 90, (0, 255, 255))
            draw_text(frame, "[SPACJA] - Weryfikuj", 130, (0, 255, 0))
            draw_text(frame, "[ESC] - Anuluj", 170, (0, 0, 255))

            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Spacja
                state = 'PROCESSING'
            elif key == 27:  # ESC
                state = 'SCANNING'
                current_qr = None

        elif state == 'PROCESSING':
            draw_text(frame, "PRZETWARZANIE...", 100, (0, 165, 255))
            cv2.imshow('System Kontroli', frame)
            cv2.waitKey(1)

            result_data = verify_entry_api(frame, current_qr, current_gate['id'])
            state = 'RESULT'
            result_timer = time.time()

        elif state == 'RESULT':
            success = result_data.get('success', False)
            color = (0, 255, 0) if success else (0, 0, 255)
            msg = result_data.get('message', '')
            conf = result_data.get('confidence', 0)

            # Person name added
            name = result_data.get('person_name', 'Nieznany')

            cv2.rectangle(frame, (0, 50), (640, 200), (0, 0, 0), -1)
            draw_text(frame, f"{'DOSTEP PRZYZNANY' if success else 'ODMOWA'}", 90, color, 1.0)
            draw_text(frame, f"{msg}", 130, (255, 255, 255), 0.6)
            if success:
                draw_text(frame, f"Osoba: {name}", 160, (0, 255, 0), 0.7)

            draw_text(frame, f"Podobienstwo: {conf:.1f}%", 190, (200, 200, 200), 0.6)

            if time.time() - result_timer > 5:
                state = 'SCANNING'
                current_qr = None

        # --- OBSŁUGA KLAWISZY GLOBALNYCH ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('g') and state == 'SCANNING':
            # Przełączanie bramek "w locie"
            all_gates = get_available_gates()  # Odśwież listę
            if all_gates:
                gate_index = (gate_index + 1) % len(all_gates)
                current_gate = all_gates[gate_index]
                print(f"🔄 Przełączono na bramkę: {current_gate['nazwa']}")

        cv2.imshow('System Kontroli', frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()