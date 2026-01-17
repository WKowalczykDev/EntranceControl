const API_URL = "http://localhost:8000"; // Adres Twojego backendu FastAPI

export const api = {
    // --- PRACOWNICY ---

    // Pobierz wszystkich pracowników
    async getEmployees() {
        const response = await fetch(`${API_URL}/pracownicy`);
        if (!response.ok) throw new Error('Błąd pobierania danych');
        const data = await response.json();

        // Mapowanie: Backend (PL snake_case) -> Frontend (ENG camelCase)
        return data.map(emp => ({
            id: emp.id,                 // ID numeryczne z bazy (INT)
            employeeId: emp.id_pracownika, // ID tekstowe np. EMP001
            firstName: emp.imie,
            lastName: emp.nazwisko,
            email: emp.email,
            position: emp.stanowisko,
            hireDate: emp.data_zatrudnienia,
            isActive: emp.aktywny
        }));
    },

    // Dodaj nowego pracownika (zwraca obiekt z nowym ID)
    async createEmployee(employeeData) {
        const payload = {
            administrator_id: 1, // Hardcoded, bo backend wymaga
            id_pracownika: employeeData.id,
            imie: employeeData.firstName,
            nazwisko: employeeData.lastName,
            email: employeeData.email,
            stanowisko: employeeData.position,
            data_zatrudnienia: employeeData.hireDate
        };

        const response = await fetch(`${API_URL}/pracownik`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Błąd zapisu');
        }
        return await response.json();
    },

    // Usuń pracownika
    async deleteEmployee(id) {
        const response = await fetch(`${API_URL}/pracownik/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Błąd usuwania');
        return true;
    },

    // --- ZDJĘCIA (UPLOAD) ---
    async uploadPhoto(dbId, file) {
        const formData = new FormData();
        formData.append('pracownik_id', dbId);
        formData.append('plik', file);

        const response = await fetch(`${API_URL}/pracownik/zdjecie`, {
            method: 'POST',
            body: formData,
            // Content-Type jest ustawiany automatycznie przez przeglądarkę dla FormData
        });

        if (!response.ok) throw new Error('Błąd wgrywania zdjęcia');
        return await response.json();
    },

    // --- PRZEPUSTKI QR ---
    async generateQrPass(dbId) {
        // Ważność: 1 rok od dzisiaj
        const nextYear = new Date();
        nextYear.setFullYear(nextYear.getFullYear() + 1);

        const payload = {
            pracownik_id: dbId,
            data_waznosci: nextYear.toISOString().split('T')[0]
        };

        const response = await fetch(`${API_URL}/przepustka/generuj`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            try {
                const err = await response.json();
                throw new Error(err.detail || 'Błąd generowania QR');
            } catch (e) {
                throw new Error('Błąd serwera lub pracownik ma już przepustkę.');
            }
        }

        // Odbieramy PLIK BINARNY (Blob) i tworzymy z niego URL
        const blob = await response.blob();
        return URL.createObjectURL(blob);
    },

    // --- RAPORTY / LOGI ---
    async getEmployeeLogs(dbId) {
        const response = await fetch(`${API_URL}/logi/?pracownik_id=${dbId}`);
        if (!response.ok) throw new Error('Błąd pobierania logów');
        return await response.json();
    }
};