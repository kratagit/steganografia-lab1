import re

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
STOP_MARKER = "MMMM" 
OUTPUT_FILE = "output.txt"

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def read_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [sentence for sentence in sentences if len(sentence) > 0]

# ==========================================
# CORE STEGANOGRAPHY SYSTEM
# ==========================================

#[ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
# -> przyjmować tekst z ukrytą wiadomością.
def extract_message(stego_text: str) -> str:
    sentences = split_into_sentences(stego_text)
    extracted_message = ""
    
    # [ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
    # -> odczytywać ukrytą wiadomość z pierwszych liter wyrazów lub zdań
    for sentence in sentences:
        first_char_match = re.search(r'[A-Za-z]', sentence)
        if first_char_match:
            extracted_message += first_char_match.group(0).upper()
            
        if STOP_MARKER in extracted_message:
            #[ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
            # -> zwracać odczytaną wiadomość tekstową.
            return extracted_message.replace(STOP_MARKER, "")
            
    return extracted_message

# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print(" AI STEGANOGRAPHY SYSTEM - DECODER ")
    print("=" * 50)

    try:
        text_to_decode = read_from_file(OUTPUT_FILE)
        if not text_to_decode:
             raise FileNotFoundError(f"Missing '{OUTPUT_FILE}' or it is empty.")
             
        decoded_secret = extract_message(text_to_decode)
        
        print("\n" + "=" * 50)
        print(f"-> EXTRACTED SECRET FROM FILE: '{decoded_secret}'")
        print("=" * 50)
        
    except Exception as err:
        print(f"\n[ERROR]: {err}")
