import random

# Nasz tymczasowy słownik
SLOWNIK_ZASTEPCZY = {
    'T':['Tak', 'Teraz', 'Tutaj', 'Tylko', 'Tradycyjnie'],
    'A':['Ale', 'Akurat', 'Albo', 'Aby', 'Absolutnie'],
    'J':['Jak', 'Jeszcze', 'Jutro', 'Jasne', 'Jednak'],
    'N':['Nagle', 'Nigdy', 'Nawet', 'Niestety', 'Nareszcie'],
    'E': ['Efekt', 'Ekstra', 'Element', 'Ewentualnie', 'Ewidentnie']
}

def wczytaj_z_pliku(nazwa_pliku):
    """Odczytuje zawartość pliku tekstowego."""
    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
            return plik.read().strip()
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{nazwa_pliku}'!")
        return None

def wyodrebnij_wiadomosc(tekst_z_ukryta_wiadomoscia):
    """Odczytuje pierwsze litery każdego słowa."""
    slowa = tekst_z_ukryta_wiadomoscia.split()
    ukryta_wiadomosc = ""
    for slowo in slowa:
        ukryta_wiadomosc += slowo[0].upper()
    return ukryta_wiadomosc

def ukryj_wiadomosc(tekst_zrodlowy, tajna_wiadomosc):
    """Podmienia pierwsze słowa w tekście, by pasowały do hasła."""
    slowa_tekstu = tekst_zrodlowy.split()
    tajna_wiadomosc = tajna_wiadomosc.replace(" ", "").upper()
    
    if len(tajna_wiadomosc) > len(slowa_tekstu):
        return "Błąd: Tekst źródłowy jest za krótki!"
    
    wynikowy_tekst = slowa_tekstu.copy()
    
    for i in range(len(tajna_wiadomosc)):
        litera = tajna_wiadomosc[i]
        if litera in SLOWNIK_ZASTEPCZY:
            wynikowy_tekst[i] = random.choice(SLOWNIK_ZASTEPCZY[litera])
        else:
            wynikowy_tekst[i] = f"[{litera}-BRAK]"
            
    return " ".join(wynikowy_tekst)

# ==========================================
# GŁÓWNA CZĘŚĆ PROGRAMU
# ==========================================
if __name__ == "__main__":
    print("--- START PROGRAMU ---")

    # 1. Wczytywanie plików
    zwykly_tekst = wczytaj_z_pliku("input.txt")
    haslo_do_ukrycia = wczytaj_z_pliku("secret.txt")

    if zwykly_tekst and haslo_do_ukrycia:
        print(f"\n[+] Wczytano hasło: '{haslo_do_ukrycia}'")
        print(f"[+] Wczytano tekst źródłowy:\n{zwykly_tekst}\n")

        # 2. Szyfrowanie
        zaszyfrowany_tekst = ukryj_wiadomosc(zwykly_tekst, haslo_do_ukrycia)
        
        # Wypisywanie w konsoli
        print("========================================")
        print("-> ZASZYFROWANY TEKST (WYNIK):")
        print(zaszyfrowany_tekst)
        print("========================================\n")

        # 3. Odczytywanie
        odkodowane_haslo = wyodrebnij_wiadomosc(zaszyfrowany_tekst)
        dlugosc_hasla = len(haslo_do_ukrycia.replace(" ", ""))
        czyste_haslo = odkodowane_haslo[:dlugosc_hasla]
        
        print(f"-> ODKODOWANE HASŁO: {czyste_haslo}")