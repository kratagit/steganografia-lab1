# steganografia-lab1

# Laboratorium 1

## Instructions

### Cel zadania
Celem zadania jest implementacja prostego systemu **steganografii lingwistycznej** z wykorzystaniem techniki **akrostychu** w środowisku Python.

### Opis zadania
Zaimplementuj system steganograficzny, który pozwoli na ukrycie wiadomości tekstowej w tekście źródłowym poprzez wykorzystanie pierwszych liter kolejnych wyrazów lub zdań. System powinien składać się z dwóch głównych funkcji:

1.  **Funkcja ukrywająca** wiadomość w tekście źródłowym.
2.  **Funkcja wyodrębniająca** ukrytą wiadomość z tekstu.

### Wymagania funkcjonalne

#### Funkcja ukrywająca wiadomość powinna:
* Przyjmować tekst źródłowy oraz wiadomość do ukrycia.
* Wykorzystywać pierwsze litery kolejnych wyrazów lub zdań do utworzenia akrostychu zawierającego ukrytą wiadomość.
* Wprowadzać jedynie takie zmiany w tekście, które pozwalają zachować jego czytelność i możliwie zbliżony sens.
* Zwracać tekst z ukrytą wiadomością.

#### Funkcja wyodrębniająca wiadomość powinna:
* Przyjmować tekst z ukrytą wiadomością.
* Odczytywać ukrytą wiadomość z pierwszych liter wyrazów lub zdań, zgodnie z przyjętym wariantem akrostychu.
* Zwracać odczytaną wiadomość tekstową.

### Kryteria akceptacji
1. System poprawnie ukrywa i odczytuje wiadomości o długości **do 50 znaków**.
2. Tekst wynikowy z ukrytą wiadomością pozostaje **czytelny i logicznie spójny**.
3. System działa poprawnie dla tekstów w różnych językach opartych na **alfabecie łacińskim** (np. polskim i angielskim).
4. Kod jest czytelny, dobrze udokumentowany i zgodny z zasadami **Clean Code**.

### Przypadki testowe

1.  **Test ukrywania krótkiej wiadomości:**
    * **Wejście:** tekst źródłowy (~100 słów), wiadomość: `TAJNE`.
    * **Oczekiwany wynik:** tekst z poprawnie ukrytą wiadomością, zachowujący czytelność.
2.  **Test ukrywania długiej wiadomości:**
    * **Wejście:** tekst źródłowy (~500 słów), wiadomość o długości 50 znaków.
    * **Oczekiwany wynik:** tekst z poprawnie ukrytą wiadomością, zachowujący spójność.
3.  **Test odczytu ukrytej wiadomości:**
    * **Wejście:** tekst z ukrytą wiadomością: `STEGANOGRAFIA LINGWISTYCZNA`.
    * **Oczekiwany wynik:** odczytana wiadomość: `STEGANOGRAFIA LINGWISTYCZNA`.
4.  **Test dla różnych języków:**
    * **Wejście:** tekst źródłowy w języku angielskim, wiadomość w języku polskim.
    * **Oczekiwany wynik:** poprawne ukrycie i odczytanie wiadomości.

### Dodatkowe wytyczne
* Stwórz **sprawozdanie** opisujące weryfikację przypadków testowych.
* W implementacji należy jasno określić, który **wariant akrostychu** jest używany w danym teście.
* Rozważ implementację różnych wariantów (np. pierwsze litery wyrazów vs. pierwsze litery zdań). Warianty dodatkowe (np. ostatnie litery wyrazów) traktowane są jako rozszerzenie.
