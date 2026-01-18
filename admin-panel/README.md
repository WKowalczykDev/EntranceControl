# Admin Panel - System Zarządzania Pracownikami

Prosta i nowoczesna aplikacja SPA do zarządzania bazą pracowników, stworzona w oparciu o React 19 i Tailwind CSS v4.

## Funkcjonalności

- **CRUD Pracowników:** Przeglądanie, dodawanie, edycja i usuwanie rekordów.
- **Interfejs:** Responsywny układ z wykorzystaniem najnowszych standardów CSS.
- **Komponenty:** Dynamiczna tabela, modale edycji oraz system ikon.

## Wykorzystane technologie

- React 19
- Vite
- Tailwind CSS v4
- Lucide React

## Instalacja i uruchomienie

1. Zainstaluj wymagane pakiety:
npm install

2. Uruchom serwer deweloperski:
npm run dev

3. Zbuduj wersję produkcyjną:
npm run build

Struktura plików:
src/
├── components/
│   ├── EmployeeModal.jsx   # Formularz dodawania/edycji
│   ├── EmployeeRow.jsx     # Wiersz tabeli
│   ├── EmployeeTable.jsx   # Główna tabela
│   └── Header.jsx          # Nagłówek aplikacji
├── App.jsx                 # Główny widok i logika stanu
├── index.css               # Importy Tailwind CSS