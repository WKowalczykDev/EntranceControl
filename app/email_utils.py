import smtplib
import os
from email.message import EmailMessage


def send_qr_email(recipient_email: str, employee_name: str, qr_bytes: bytes):
    """
    Wysyła wiadomość email z załączonym kodem QR (w formacie PNG).
    """
    # Pobieranie konfiguracji ze zmiennych środowiskowych (z docker-compose)
    mail_server = os.getenv("MAIL_SERVER", "mailhog")
    mail_port = int(os.getenv("MAIL_PORT", 1025))
    mail_from = os.getenv("MAIL_FROM", "no-reply@qr-system.local")

    msg = EmailMessage()
    msg['Subject'] = 'Witaj w firmie! Twój kod dostępu'
    msg['From'] = mail_from
    msg['To'] = recipient_email

    # Treść wiadomości HTML
    msg.set_content(f"""
    Witaj {employee_name},

    Twoje konto zostało pomyślnie aktywowane.
    W załączniku znajduje się Twój unikalny kod QR.

    Kod jest ważny przez rok od daty wygenerowania.
    Prosimy o zachowanie go w bezpiecznym miejscu (np. w telefonie).

    Pozdrawiamy,
    Dział Bezpieczeństwa
    """)

    # Dodawanie załącznika (obraz QR z pamięci)
    msg.add_attachment(
        qr_bytes,
        maintype='image',
        subtype='png',
        filename='przepustka_qr.png'
    )

    try:
        # Łączenie z MailHog (bez uwierzytelniania, bo to środowisko testowe)
        with smtplib.SMTP(mail_server, mail_port) as smtp:
            smtp.send_message(msg)
        print(f"📧 [Email] Wysłano kod QR do: {recipient_email}")
    except Exception as e:
        print(f"❌ [Email] Błąd wysyłki: {e}")