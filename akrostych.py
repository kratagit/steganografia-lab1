import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
load_dotenv()
STOP_MARKER = "QQQ"
MODEL_NAME = "gemini-3.1-flash-lite-preview"

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
# AI INTEGRATION
# ==========================================
def rephrase_sentence_with_ai(client: genai.Client, original_sentence: str, target_letter: str) -> str:
    prompt = f"""
    You are a linguistic assistant. Your task is to rephrase the following sentence so that 
    its first word begins with the letter '{target_letter.upper()}'.
    
    RULES:
    1. You MUST preserve the original meaning and context of the sentence.
    2. You MUST preserve the original language of the sentence.
    3. The sentence must sound completely natural and be grammatically correct.
    4. RETURN ONLY THE REPHRASED SENTENCE. Do not add any quotes.
    
    Original sentence: {original_sentence}
    """
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
        temperature=0.3
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
    """
    Hides a secret message within the source text.
    Takes 'source_text' and 'secret_message' as input parameters.
    """
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
        raise ValueError(f"Source text is too short!")

    result_text = []
    
    # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> wykorzystywać pierwsze litery kolejnych wyrazów lub zdań do utworzenia akrostychu
    for i, letter in enumerate(message_with_marker):
        original_sentence = sentences[i]
        
        # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
        # -> wprowadzać jedynie takie zmiany w tekście, które pozwalają zachować jego 
        # czytelność i możliwie zbliżony sens.
        # (Achieved by using LLM to semantically rephrase the sentence without losing its meaning)
        new_sentence = rephrase_sentence_with_ai(client, original_sentence, letter)
        
        first_char_match = re.search(r'[A-Za-z]', new_sentence)
        if first_char_match and first_char_match.group(0).upper() != letter:
            new_sentence = f"{letter} actually, " + new_sentence[0].lower() + new_sentence[1:]
            
        result_text.append(new_sentence)
        
    result_text.extend(sentences[len(message_with_marker):])
    
    # [ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
    # -> zwracać tekst z ukrytą wiadomością.
    return " ".join(result_text)


#[ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
# -> przyjmować tekst z ukrytą wiadomością.
def extract_message(stego_text: str) -> str:
    """
    Extracts the hidden message.
    Takes 'stego_text' (text with hidden message) as the only parameter.
    """
    sentences = split_into_sentences(stego_text)
    extracted_message = ""
    
    # [ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
    # -> odczytywać ukrytą wiadomość z pierwszych liter wyrazów lub zdań, 
    # zgodnie z przyjętym wariantem akrostychu.
    for sentence in sentences:
        first_char_match = re.search(r'[A-Za-z]', sentence)
        if first_char_match:
            extracted_message += first_char_match.group(0).upper()
            
        if STOP_MARKER in extracted_message:
            #[ASSIGNMENT REQUIREMENT]: Funkcja wyodrębniająca wiadomość powinna:
            # -> zwracać odczytaną wiadomość tekstową.
            return extracted_message.replace(STOP_MARKER, "")
            
    # Fallback return
    return extracted_message

# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print(" AI STEGANOGRAPHY SYSTEM (Powered by Google Gemini) ")
    print("=" * 50)

    try:
        text = read_from_file("input.txt")
        secret = read_from_file("secret.txt")
        
        if not text or not secret:
            raise FileNotFoundError("Missing 'input.txt' or 'secret.txt'")

        # Execute hiding function
        encrypted_text = hide_message(text, secret)
        write_to_file("output.txt", encrypted_text)
        print("\n[+] SUCCESS: The message has been securely hidden.")
        
        # Execute extracting function
        text_to_decode = read_from_file("output.txt")
        decoded_secret = extract_message(text_to_decode)
        
        print("\n" + "=" * 50)
        print(f"-> EXTRACTED SECRET FROM FILE: '{decoded_secret}'")
        print("=" * 50)
        
    except Exception as err:
        print(f"\n[ERROR]: {err}")