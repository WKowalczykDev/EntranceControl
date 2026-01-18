import cv2
import requests
import time

# --- KONFIGURACJA ---
API_URL = "http://localhost:8000/verify"
BRAMKA_ID = 1  # Zmień to ID, aby testować inną bramkę


# --------------------

def verify_entry_api(frame, qr_data):
    """Wysyła ramkę i kod QR do backendu"""
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'face_image': ('capture.jpg', img_encoded.tobytes(), 'image/jpeg')}
        data = {'bramka_id': BRAMKA_ID, 'qr_data': qr_data}

        print(f"📡 Wysyłanie do weryfikacji... QR: {qr_data}")
        response = requests.post(API_URL, data=data, files=files)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Błąd sieci: {e}", "confidence": 0}


def draw_text(img, text, y_pos, color=(0, 255, 0)):
    cv2.putText(img, text, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def main():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    # Maszyna stanów: 'SCANNING' -> 'WAIT_FOR_USER' -> 'PROCESSING' -> 'RESULT'
    state = 'SCANNING'

    current_qr = None
    result_data = None
    result_timer = 0

    print("🚀 Symulator Bramki Uruchomiony")
    print(f"🔧 Podłączony do Bramki ID: {BRAMKA_ID}")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # --- LOGIKA STANÓW ---

        if state == 'SCANNING':
            draw_text(frame, "STATUS: SKANOWANIE QR...", 40, (255, 255, 255))
            draw_text(frame, "Pokaz kod QR do kamery", 80, (200, 200, 200))

            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                current_qr = data
                state = 'WAIT_FOR_USER'
                print(f"✅ Wykryto QR: {current_qr}")

        elif state == 'WAIT_FOR_USER':
            # Rysujemy instrukcje dla użytkownika
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (640, 150), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            draw_text(frame, f"QR: {current_qr}", 40, (0, 255, 255))
            draw_text(frame, "[SPACJA] - Wykonaj zdjecie i weryfikuj", 80, (0, 255, 0))
            draw_text(frame, "[ESC] - Anuluj", 120, (0, 0, 255))

            # Czekamy na input
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Spacja
                state = 'PROCESSING'
            elif key == 27:  # ESC
                state = 'SCANNING'
                current_qr = None

        elif state == 'PROCESSING':
            draw_text(frame, "PRZETWARZANIE...", 100, (0, 165, 255))
            cv2.imshow('Bramka', frame)
            cv2.waitKey(1)  # Odśwież okno

            # Strzał do API
            result_data = verify_entry_api(frame, current_qr)

            state = 'RESULT'
            result_timer = time.time()

        elif state == 'RESULT':
            # Wyświetlanie wyniku przez 5 sekund
            success = result_data.get('success', False)
            color = (0, 255, 0) if success else (0, 0, 255)
            msg = result_data.get('message', '')
            conf = result_data.get('confidence', 0)

            # Tło pod tekst
            cv2.rectangle(frame, (0, 0), (640, 120), (0, 0, 0), -1)

            draw_text(frame, f"WYNIK: {msg}", 40, color)
            draw_text(frame, f"Podobienstwo: {conf:.2f}% (Wymagane: 90%)", 80, (255, 255, 255))

            if time.time() - result_timer > 5:
                state = 'SCANNING'
                current_qr = None
                result_data = None

        cv2.imshow('Bramka', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()