import re
import unicodedata

def normalize_unicode(text: str) -> str:
    if not isinstance(text, str): return text
    return unicodedata.normalize('NFC', text)

def normalize_whitespace(text: str) -> str:
    if not isinstance(text, str): return text
    return re.sub(r'\s+', ' ', text).strip()

def remove_noise(text: str) -> str:
    if not isinstance(text, str): return text
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    return text

def normalize_banglish(text: str) -> str:
    if not isinstance(text, str): return text
    text = re.sub(r'\bkee\b|\bkey\b', 'ki', text, flags=re.IGNORECASE)
    text = re.sub(r'\btah\b', 'ta', text, flags=re.IGNORECASE)
    return text

def preprocess_question(text: str, language: str) -> dict:
    if not isinstance(text, str):
        return {'raw_question': text, 'processed_question': text}
    
    processed = normalize_unicode(text)
    processed = remove_noise(processed)
    
    if language == 'banglish':
        processed = normalize_banglish(processed)
        
    processed = normalize_whitespace(processed)
    
    return {
        'raw_question': text,
        'processed_question': processed
    }
