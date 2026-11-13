import re

def detect_language(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return 'english'
        
    bengali_pattern = re.compile(r'[\u0980-\u09FF]')
    bengali_chars = len(bengali_pattern.findall(text))
    total_chars = len(text.replace(' ', ''))
    
    if total_chars == 0:
        return 'english'
        
    bengali_ratio = bengali_chars / total_chars
    
    if bengali_ratio > 0.3:
        return 'bangla'
        
    if bengali_ratio > 0:
        return 'code_mixed'
        
    banglish_words = ['ki', 'keno', 'hoy', 'ache', 'theke', 'korte', 'bolte', 'jani', 'ami', 'apni', 'shomosya']
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    
    banglish_count = sum(1 for w in words if w in banglish_words)
    
    if banglish_count > 0:
        return 'banglish'
        
    return 'english'
