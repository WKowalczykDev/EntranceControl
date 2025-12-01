FROM python:3.11-slim

# Instalacja zależności systemowych dla OpenCV i bibliotek face recognition
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopiowanie requirements i instalacja
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie aplikacji
COPY . .

# Tworzenie katalogów
RUN mkdir -p /app/uploads /app/reference_faces

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]