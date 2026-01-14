from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base # Importujemy Base z database.py, aby uniknąć cyklicznych importów

class Administrator(Base):
    __tablename__ = "administrator"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    haslo_hash = Column(String, nullable=False)
    imie = Column(String, nullable=False)
    nazwisko = Column(String, nullable=False)
    data_utworzenia = Column(DateTime(timezone=True), server_default=func.now())

    # Relacje
    pracownicy = relationship("Pracownik", back_populates="administrator")
    raporty = relationship("Raport", back_populates="administrator")

class Pracownik(Base):
    __tablename__ = "pracownik"

    id = Column(Integer, primary_key=True, index=True)
    administrator_id = Column(Integer, ForeignKey("administrator.id"), nullable=False)
    id_pracownika = Column(String, unique=True, nullable=False) # To będzie np. nazwa folderu ze zdjęciami
    imie = Column(String, nullable=False)
    nazwisko = Column(String, nullable=False)
    stanowisko = Column(String)
    email = Column(String)
    data_zatrudnienia = Column(Date, nullable=False)
    aktywny = Column(Boolean, default=True)
    data_utworzenia = Column(DateTime(timezone=True), server_default=func.now())

    # Relacje
    administrator = relationship("Administrator", back_populates="pracownicy")
    przepustka = relationship("Przepustka", back_populates="pracownik", uselist=False)
    zdjecia = relationship("ZdjecieReferencyjne", back_populates="pracownik")
    proby_wejscia = relationship("ProbaWejscia", back_populates="pracownik")

class Przepustka(Base):
    __tablename__ = "przepustka"

    id = Column(Integer, primary_key=True, index=True)
    pracownik_id = Column(Integer, ForeignKey("pracownik.id"), unique=True, nullable=False)
    kod_qr = Column(String, nullable=False, unique=True) # Unikalny kod QR
    data_wygenerowania = Column(DateTime(timezone=True), server_default=func.now())
    data_waznosci = Column(Date, nullable=False)
    aktywna = Column(Boolean, default=True)

    pracownik = relationship("Pracownik", back_populates="przepustka")

class ZdjecieReferencyjne(Base):
    __tablename__ = "zdjecie_referencyjne"

    id = Column(Integer, primary_key=True, index=True)
    pracownik_id = Column(Integer, ForeignKey("pracownik.id"), nullable=False)
    sciezka_pliku = Column(String, nullable=False)
    data_dodania = Column(DateTime(timezone=True), server_default=func.now())
    aktywne = Column(Boolean, default=True)

    pracownik = relationship("Pracownik", back_populates="zdjecia")

class Bramka(Base):
    __tablename__ = "bramka"

    id = Column(Integer, primary_key=True, index=True)
    nazwa = Column(String, nullable=False)
    lokalizacja = Column(String)
    aktywna = Column(Boolean, default=True)
    adres_ip = Column(String)

    proby_wejscia = relationship("ProbaWejscia", back_populates="bramka")

class ProbaWejscia(Base):
    __tablename__ = "proba_wejscia"

    id = Column(Integer, primary_key=True, index=True)
    bramka_id = Column(Integer, ForeignKey("bramka.id"), nullable=False)
    pracownik_id = Column(Integer, ForeignKey("pracownik.id"), nullable=True) # Null, jeśli nie rozpoznano
    data_czas = Column(DateTime(timezone=True), server_default=func.now())

    wynik_qr = Column(String) # 'OK', 'INVALID'
    wynik_biometryczny = Column(String) # 'MATCH', 'NO_MATCH'
    procent_podobienstwa = Column(Float)
    status_finalny = Column(String, nullable=False) # 'GRANTED', 'DENIED'
    sciezka_zdjecia = Column(String) # Zdjęcie z wejścia
    podejrzana = Column(Boolean, default=False)

    bramka = relationship("Bramka", back_populates="proby_wejscia")
    pracownik = relationship("Pracownik", back_populates="proby_wejscia")

class Raport(Base):
    __tablename__ = "raport"

    id = Column(Integer, primary_key=True, index=True)
    administrator_id = Column(Integer, ForeignKey("administrator.id"), nullable=False)
    typ = Column(String, nullable=False)
    data_wygenerowania = Column(DateTime(timezone=True), server_default=func.now())
    data_od = Column(Date, nullable=False)
    data_do = Column(Date, nullable=False)
    sciezka_pliku = Column(String)

    administrator = relationship("Administrator", back_populates="raporty")