import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
load_dotenv()

STOP_MARKER = "MMMM" 
MODEL_NAME = "gemini-3.1-flash-lite-preview"
CONTEXT_WINDOW = 5  # Liczba zdań przed i po

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def read_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return[sentence for sentence in sentences if len(sentence) > 0]

# ==========================================
# AI INTEGRATION (NOW WITH CONTEXT)
# ==========================================
def rephrase_sentence_with_context(client: genai.Client, target_sentence: str, target_letter: str, prev_context: list[str], next_context: list[str]) -> str:
    """
    Asks Gemini to rephrase a target sentence while providing surrounding context 
    to ensure perfect flow and cohesion.
    """
    
    # Formatowanie kontekstu (jeśli puste, dajemy znak, że to początek/koniec)
    prev_text = " ".join(prev_context) if prev_context else "(None - this is the beginning of the text)"
    next_text = " ".join(next_context) if next_context else "(None - this is the end of the text)"

    prompt = f"""
    You are an expert copywriter. Your task is to rewrite the TARGET SENTENCE so its very FIRST word starts with the letter '{target_letter.upper()}'.
    
    To help you maintain a perfect, natural flow, here is the surrounding context of the article:
    
    [PREVIOUS SENTENCES]
    {prev_text}
    
    [TARGET SENTENCE TO REWRITE]
    {target_sentence}
    
    [NEXT SENTENCES]
    {next_text}
    
    CRITICAL RULES:
    1. The target sentence MUST sound 100% natural and fit logically between the PREVIOUS and NEXT sentences.
    2. DO NOT use artificial loanwords, strange hyphenations, or forced words. Use everyday, fluid vocabulary.
    3. You must preserve the core meaning and the original language of the target sentence.
    4. RETURN ONLY THE REPHRASED TARGET SENTENCE. Do not return the context. No extra text, no quotation marks.
    """
    
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="MEDIUM"),
    )
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    
    return response.text.strip().strip('"').strip("'")

# ==========================================
# CORE STEGANOGRAPHY SYSTEM
# ==========================================

#[ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
# -> przyjmować tekst źródłowy oraz wiadomość do ukrycia
def hide_message(source_text: str, secret_message: str) -> str:
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("API key is missing! Check .env file.")
        client = genai.Client()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    clean_secret = re.sub(r'[^A-Za-z]', '', secret_message).upper()
    message_with_marker = clean_secret + STOP_MARKER
    
    sentences = split_into_sentences(source_text)
    
    if len(message_with_marker) > len(sentences):
        raise ValueError(f"Source text is too short! Need at least {len(message_with_marker)} sentences, but got {len(sentences)}.")

    result_text =[]
    
    print(f"[*] Starting AI steganography with CONTEXT AWARENESS ({len(message_with_marker)} characters)...")
    
    # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> wykorzystywać pierwsze litery kolejnych wyrazów lub zdań do utworzenia akrostychu
    for i, letter in enumerate(message_with_marker):
        target_sentence = sentences[i]
        
        # Pobieramy do 5 ZMODYFIKOWANYCH już zdań wstecz
        start_prev = max(0, i - CONTEXT_WINDOW)
        prev_context = result_text[start_prev:i]
        
        # Pobieramy do 5 ORYGINALNYCH zdań w przód
        end_next = min(len(sentences), i + 1 + CONTEXT_WINDOW)
        next_context = sentences[i+1:end_next]
        
        # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
        # -> wprowadzać jedynie takie zmiany w tekście, które pozwalają zachować jego czytelność i możliwie zbliżony sens.
        new_sentence = rephrase_sentence_with_context(client, target_sentence, letter, prev_context, next_context)
        
        first_char_match = re.search(r'[A-Za-z]', new_sentence)
        if first_char_match and first_char_match.group(0).upper() != letter:
            # Fallback
            new_sentence = f"{letter}ożliwe, że " + new_sentence[0].lower() + new_sentence[1:]
            
        result_text.append(new_sentence)
        
    result_text.extend(sentences[len(message_with_marker):])
    
    #[ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> zwracać tekst z ukrytą wiadomością.
    return " ".join(result_text)


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
    print(" AI STEGANOGRAPHY SYSTEM (Context-Aware) ")
    print("=" * 50)

    try:
        text = read_from_file("input.txt")
        secret = read_from_file("secret.txt")
        
        if not text or not secret:
            raise FileNotFoundError("Missing 'input.txt' or 'secret.txt'")

        encrypted_text = hide_message(text, secret)
        write_to_file("output.txt", encrypted_text)
        print("\n[+] SUCCESS: The message has been securely hidden.")
        
        text_to_decode = read_from_file("output.txt")
        decoded_secret = extract_message(text_to_decode)
        
        print("\n" + "=" * 50)
        print(f"-> EXTRACTED SECRET FROM FILE: '{decoded_secret}'")
        print("=" * 50)
        
    except Exception as err:
        print(f"\n[ERROR]: {err}")