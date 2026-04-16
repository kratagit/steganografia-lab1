import os
import re
import concurrent.futures
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
load_dotenv()

STOP_MARKER = "MMMM" 
MODEL_NAME = "gemini-3.1-flash-lite-preview"
CONTEXT_WINDOW = 5  # Number of sentences before and after
INPUT_FILE = "input2.txt"
SECRET_FILE = "secret2.txt"
OUTPUT_FILE = "output.txt"

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
    return [sentence for sentence in sentences if len(sentence) > 0]

# ==========================================
# AI INTEGRATION (NOW WITH CONTEXT)
# ==========================================
def rephrase_sentence_with_context(client: genai.Client, target_sentence: str, target_letter: str, prev_context: list[str], next_context: list[str]) -> str:
    """
    Asks Gemini to rephrase a target sentence while providing surrounding context 
    to ensure perfect flow and cohesion.
    """
    
    # Formatting the context (if empty, we indicate it's the beginning/end)
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

    result_text = []
    
    print(f"[*] Starting AI steganography with CONTEXT AWARENESS ({len(message_with_marker)} characters)...")
    
    def process_sentence(i, letter):
        target_sentence = sentences[i]
        
        # Używamy ORYGINALNYCH zdań zarówno w tył jak i w przód, co pozwala nam puścić to "bulkiem":
        start_prev = max(0, i - CONTEXT_WINDOW)
        prev_context = sentences[start_prev:i]
        
        end_next = min(len(sentences), i + 1 + CONTEXT_WINDOW)
        next_context = sentences[i+1:end_next]
        
        print(f"[>] Wysyłam request do AI: litera {i + 1}/{len(message_with_marker)} ('{letter}')...")
        new_sentence = rephrase_sentence_with_context(client, target_sentence, letter, prev_context, next_context)
        
        first_char_match = re.search(r'[A-Za-z]', new_sentence)
        if first_char_match and first_char_match.group(0).upper() != letter:
            # Fallback
            new_sentence = f"{letter}ożliwe, że " + new_sentence[0].lower() + new_sentence[1:]
            
        print(f"[V] Otrzymano wynik: litera {i + 1}/{len(message_with_marker)} ('{letter}').")
        return i, new_sentence

    result_text = []

    # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> wykorzystywać pierwsze litery kolejnych wyrazów lub zdań do utworzenia akrostychu
    # -> wprowadzać jedynie takie zmiany w tekście, które pozwalają zachować jego czytelność i możliwie zbliżony sens.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Wysyłamy zapytania "bulkiem" i zachowujemy oryginalną kolejność dzięki numerowi indeksu `i`
        futures = [executor.submit(process_sentence, i, letter) for i, letter in enumerate(message_with_marker)]
        
        results_in_order = [None] * len(message_with_marker)
        for future in concurrent.futures.as_completed(futures):
            idx, mod_sentence = future.result()
            results_in_order[idx] = mod_sentence

    result_text.extend(results_in_order)
        
    result_text.extend(sentences[len(message_with_marker):])
    
    #[ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> zwracać tekst z ukrytą wiadomością.
    return " ".join(result_text)

# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print(" AI STEGANOGRAPHY SYSTEM - ENCODER ")
    print("=" * 50)

    try:
        text = read_from_file(INPUT_FILE)
        secret = read_from_file(SECRET_FILE)
        
        if not text:
            raise ValueError(f"File '{INPUT_FILE}' is empty!")
        if not secret:
            raise ValueError(f"File '{SECRET_FILE}' is empty!")

        encrypted_text = hide_message(text, secret)
        write_to_file(OUTPUT_FILE, encrypted_text)
        print("\n[+] SUCCESS: The message has been securely hidden.")
        
    except Exception as err:
        print(f"\n[ERROR]: {err}")
