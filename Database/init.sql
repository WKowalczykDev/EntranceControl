-- Jeśli tabele istnieją, usuń je (przydatne przy resecie)
DROP TABLE IF EXISTS proba_wejscia CASCADE;
DROP TABLE IF EXISTS zdjecie_referencyjne CASCADE;
DROP TABLE IF EXISTS bramka CASCADE;
DROP TABLE IF EXISTS raport CASCADE;
DROP TABLE IF EXISTS przepustka CASCADE;
DROP TABLE IF EXISTS pracownik CASCADE;
DROP TABLE IF EXISTS administrator CASCADE;

-- 1. Tabela Administrator
CREATE TABLE administrator (
                               id SERIAL PRIMARY KEY,
                               email VARCHAR(255) NOT NULL UNIQUE,
                               haslo_hash VARCHAR(255) NOT NULL,
                               imie VARCHAR(100) NOT NULL,
                               nazwisko VARCHAR(100) NOT NULL,
                               data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela Pracownik
CREATE TABLE pracownik (
                           id SERIAL PRIMARY KEY,
                           administrator_id INT NOT NULL,
                           id_pracownika VARCHAR(50) UNIQUE NOT NULL,
                           imie VARCHAR(100) NOT NULL,
                           nazwisko VARCHAR(100) NOT NULL,
                           stanowisko VARCHAR(100),
                           email VARCHAR(255),
                           data_zatrudnienia DATE NOT NULL,
                           aktywny BOOLEAN DEFAULT TRUE,
                           data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           CONSTRAINT fk_pracownik_admin FOREIGN KEY (administrator_id) REFERENCES administrator(id)
);

-- 3. Tabela Przepustka
CREATE TABLE przepustka (
                            id SERIAL PRIMARY KEY,
                            pracownik_id INT NOT NULL UNIQUE,
                            kod_qr VARCHAR(255) NOT NULL,
                            data_wygenerowania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            data_waznosci DATE NOT NULL,
                            aktywna BOOLEAN DEFAULT TRUE,
                            CONSTRAINT fk_przepustka_pracownik FOREIGN KEY (pracownik_id) REFERENCES pracownik(id) ON DELETE CASCADE
);

-- 4. Tabela Raport
CREATE TABLE raport (
                        id SERIAL PRIMARY KEY,
                        administrator_id INT NOT NULL,
                        typ VARCHAR(50) NOT NULL,
                        data_wygenerowania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_od DATE NOT NULL,
                        data_do DATE NOT NULL,
                        sciezka_pliku VARCHAR(255),
                        CONSTRAINT fk_raport_admin FOREIGN KEY (administrator_id) REFERENCES administrator(id)
);

-- 5. Tabela Bramka
CREATE TABLE bramka (
                        id SERIAL PRIMARY KEY,
                        nazwa VARCHAR(100) NOT NULL,
                        lokalizacja VARCHAR(255),
                        aktywna BOOLEAN DEFAULT TRUE,
                        adres_ip VARCHAR(45)
);

-- 6. Tabela ZdjecieReferencyjne
CREATE TABLE zdjecie_referencyjne (
                                      id SERIAL PRIMARY KEY,
                                      pracownik_id INT NOT NULL,
                                      sciezka_pliku VARCHAR(255) NOT NULL,
                                      data_dodania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                      aktywne BOOLEAN DEFAULT TRUE,
                                      CONSTRAINT fk_zdjecie_pracownik FOREIGN KEY (pracownik_id) REFERENCES pracownik(id) ON DELETE CASCADE
);

-- 7. Tabela ProbaWejscia
CREATE TABLE proba_wejscia (
                               id SERIAL PRIMARY KEY,
                               bramka_id INT NOT NULL,
                               pracownik_id INT, -- Może być NULL (dla nieznanych osób)
                               data_czas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               wynik_qr VARCHAR(50),
                               wynik_biometryczny VARCHAR(50),
                               confidence FLOAT,
                               status VARCHAR(50) NOT NULL,
                               sciezka_zdjecia VARCHAR(255),
                               podejrzana BOOLEAN DEFAULT FALSE,

                               CONSTRAINT fk_proba_bramka FOREIGN KEY (bramka_id) REFERENCES bramka(id),


                               CONSTRAINT fk_proba_pracownik FOREIGN KEY (pracownik_id) REFERENCES pracownik(id) ON DELETE CASCADE
);