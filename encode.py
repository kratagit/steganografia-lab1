import os
import re
import json
import urllib.request
import unicodedata
# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

STOP_MARKER = "MMM"
ZWSP = '\u200B'  # Zero-Width Space (niewidoczna spacja)
MODEL_NAME = "gemma4:e4b-it-q8_0"
OLLAMA_URL = "http://localhost:11434/api/generate"
CONTEXT_WINDOW = 3  # Number of sentences before and after
INPUT_FILE = "input1.txt"
SECRET_FILE = "secret1.txt"
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
def rephrase_sentence_with_context(target_sentence: str, target_letter: str, prev_context: list[str], next_context: list[str]) -> str:
    """
    Asks Ollama (gemma4) to rephrase a target sentence while providing surrounding context 
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
    
    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }).encode("utf-8")
    
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    
    try:
        print("    [+] Nowe zdanie: ", end="", flush=True)
        full_response = ""
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    text_chunk = chunk.get("response", "")
                    print(text_chunk, end="", flush=True)
                    full_response += text_chunk
        print() # Nowa linia po zakończeniu strumienowania
        return full_response.strip().strip('"').strip("'")
    except Exception as e:
        print(f"\n[!] Warning: Error communicating with Ollama: {e}")
        return target_sentence  # Fallback to original

def fix_sentences_semantics(sentences_chunk: list[str], required_letters: list[str]) -> list[str]:
    """
    Takes a chunk of sentences and validates/fixes their semantic flow, strictly
    preserving the exact first letter of each sentence.
    """
    text_chunk = " ".join(sentences_chunk)
    letters_str = ", ".join([f"sentence {i+1} must start with '{letter.upper()}'" for i, letter in enumerate(required_letters)])
    
    prompt = f"""
    You are an expert Polish editor. The following text may sound unnatural, have logical errors, or contain strange phrases. 
    Your task is to fix it to sound 100% natural, correct and logical. 
    
    CRITICAL STEGANOGRAPHY RULE:
    You MUST preserve the exact first letter of each sentence. We have {len(sentences_chunk)} sentences in this text.
    The rules for the first letters are:
    {letters_str}
    
    [TEXT TO FIX]
    {text_chunk}
    
    Return ONLY the corrected text. Do not add any extra comments, no quotation marks. Keep the same number of sentences ({len(sentences_chunk)}).
    """

    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }).encode("utf-8")
    
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    
    try:
        print("    [AI Editing]: ", end="", flush=True)
        full_response = ""
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    text_chunk = chunk.get("response", "")
                    print(text_chunk, end="", flush=True)
                    full_response += text_chunk
        print() # Nowa linia po zakończeniu
        corrected_text = full_response.strip().strip('"').strip("'")
        corrected_sentences = split_into_sentences(corrected_text)
            
        # Additional fallback check: verify if the model successfully preserved letters and sentence count
        if len(corrected_sentences) == len(sentences_chunk):
            match_all = True
            for j in range(len(sentences_chunk)):
                first_char_match = re.search(r'[A-Za-z]', corrected_sentences[j])
                if not first_char_match or first_char_match.group(0).upper() != required_letters[j].upper():
                    match_all = False
                    break
            if match_all:
                return corrected_sentences
        return sentences_chunk # Fallback if model failed constraints
    except Exception as e:
        print(f"\n[!] Warning: Error communicating with Ollama during fix: {e}")
        return sentences_chunk

# ==========================================
# CORE STEGANOGRAPHY SYSTEM
# ==========================================

#[ASSIGNMENT REQUIREMENT]: Funkcja ukrywająca wiadomość powinna:
# -> przyjmować tekst źródłowy oraz wiadomość do ukrycia
def hide_message(source_text: str, secret_message: str) -> str:
    # 1. Normalizacja i usunięcie polskich znaków (zostawiamy spacje!)
    pl_chars = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
    ascii_replacements = "acelnoszzACELNOSZZ"
    translator = str.maketrans(pl_chars, ascii_replacements)
    secret_translated = secret_message.translate(translator)

    secret_normalized = unicodedata.normalize('NFKD', secret_translated).encode('ASCII', 'ignore').decode('utf-8')
    clean_secret = re.sub(r'[^A-Za-z ]', '', secret_normalized).upper().strip()
    
    # 2. Tworzymy listę "Zadań" (oddzielamy litery od spacji)
    tasks =[]
    pending_spaces = 0
    for char in clean_secret:
        if char == ' ':
            pending_spaces += 1
        else:
            tasks.append({'letter': char, 'spaces_before': pending_spaces})
            pending_spaces = 0
            
    # 3. Dodajemy znacznik STOP do zadań (same litery)
    for char in STOP_MARKER:
        tasks.append({'letter': char, 'spaces_before': pending_spaces})
        pending_spaces = 0

    sentences = split_into_sentences(source_text)
    
    # Zauważ: sprawdzamy długość 'tasks', a nie całego hasła ze spacjami!
    if len(tasks) > len(sentences):
        raise ValueError(f"Tekst jest za krótki! Wymagane zdań: {len(tasks)}, dostępne: {len(sentences)}.")

    print(f"[*] Rozpoczynam AI Steganography ({len(tasks)} liter do ukrycia)...")
    
    def process_sentence(i, letter):
        target_sentence = sentences[i]
        start_prev = max(0, i - CONTEXT_WINDOW)
        prev_context = sentences[start_prev:i]
        end_next = min(len(sentences), i + 1 + CONTEXT_WINDOW)
        next_context = sentences[i+1:end_next]
        
        print(f"[>] Wysyłam request do AI: litera {i + 1}/{len(tasks)} ('{letter}')...")
        print(f"    [-] Oryginał: {target_sentence}")
        new_sentence = rephrase_sentence_with_context(target_sentence, letter, prev_context, next_context)
        
        first_char_match = re.search(r'[A-Za-z]', new_sentence)
        if first_char_match and first_char_match.group(0).upper() != letter:
            new_sentence = f"{letter}ożliwe, że " + new_sentence[0].lower() + new_sentence[1:]
            print(f"    [!] Wymuszono literę: {new_sentence}")
            
        print(f"[V] Otrzymano wynik: litera '{letter}'")
        return i, new_sentence

    result_text =[]

    # Generowanie zdań przez LLM (tylko dla liter!)
    for i, task in enumerate(tasks):
        letter = task['letter']
        idx, mod_sentence = process_sentence(i, letter)
        result_text.append(mod_sentence)
        
    print(f"[*] Post-processing: Sprawdzanie paczek zdań...")
    fixed_results =[]
    chunk_size = 3
    num_chunks = (len(result_text) + chunk_size - 1) // chunk_size
    for step, k in enumerate(range(0, len(result_text), chunk_size)):
        print(f"[>] Przetwarzanie paczki {step + 1}/{num_chunks}...")
        chunk = result_text[k:k+chunk_size]
        letters_chunk = [t['letter'] for t in tasks[k:k+chunk_size]]
        
        corrected_chunk = fix_sentences_semantics(chunk, letters_chunk)
        fixed_results.extend(corrected_chunk)
    
    result_text = fixed_results

    # 4. KLUCZOWY MOMENT: WSTRZYKIWANIE NIEWIDOCZNYCH SPACJI
    # Robimy to po tym, jak AI skończyło działać, żeby AI ich nie usunęło!
    for i, task in enumerate(tasks):
        if task['spaces_before'] > 0:
            result_text[i] = (ZWSP * task['spaces_before']) + result_text[i]

    # Doklejamy resztę niemodyfikowanych zdań
    result_text.extend(sentences[len(tasks):])
    
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
