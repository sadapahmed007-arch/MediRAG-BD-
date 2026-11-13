"""Comprehensive dataset augmentation pipeline for MediRAG-BD.

Creates Banglish, code-mixed, and safety variants to reach 10,000+ records.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import yaml
import random
import re
from pathlib import Path
from src.data.loader import load_config

# Bangla to Banglish transliteration mapping
BANGLA_TO_BANGLISH = {
    'আ': 'a', 'অ': 'o', 'ই': 'i', 'ঈ': 'ee', 'উ': 'u', 'ঊ': 'oo',
    'এ': 'e', 'ঐ': 'oi', 'ও': 'o', 'ঔ': 'ou',
    'ক': 'k', 'খ': 'kh', 'গ': 'g', 'ঘ': 'gh', 'ঙ': 'ng',
    'চ': 'ch', 'ছ': 'chh', 'জ': 'j', 'ঝ': 'jh', 'ঞ': 'n',
    'ট': 't', 'ঠ': 'th', 'ড': 'd', 'ঢ': 'dh', 'ণ': 'n',
    'ত': 't', 'থ': 'th', 'দ': 'd', 'ধ': 'dh', 'ন': 'n',
    'প': 'p', 'ফ': 'ph', 'ব': 'b', 'ভ': 'bh', 'ম': 'm',
    'য': 'j', 'র': 'r', 'ল': 'l', 'শ': 'sh', 'ষ': 'sh', 'স': 's',
    'হ': 'h', 'ড়': 'r', 'ঢ়': 'rh', 'য়': 'y', 'ৎ': 't',
    'ং': 'ng', 'ঃ': 'h', 'ঁ': 'n',
    'া': 'a', 'ি': 'i', 'ী': 'ee', 'ু': 'u', 'ূ': 'oo',
    'ে': 'e', 'ৈ': 'oi', 'ো': 'o', 'ৌ': 'ou',
    'ৃ': 'ri', '্': '', '়': '',
}

# Common Bangla word-level transliterations for better quality
WORD_MAP = {
    'কী': 'ki', 'কি': 'ki', 'কেন': 'keno', 'কে': 'ke',
    'কোন': 'kon', 'কোথায়': 'kothay', 'কখন': 'kokhon', 'কত': 'koto',
    'এবং': 'ebong', 'আর': 'ar', 'বা': 'ba', 'যদি': 'jodi',
    'তাহলে': 'tahole', 'কিন্তু': 'kintu', 'তবে': 'tobe',
    'আমি': 'ami', 'আমার': 'amar', 'আপনি': 'apni', 'আপনার': 'apnar',
    'তার': 'tar', 'তাদের': 'tader', 'এই': 'ei', 'সেই': 'sei',
    'হয়': 'hoy', 'করে': 'kore', 'আছে': 'ache', 'নেই': 'nei',
    'হয়েছে': 'hoyeche', 'করতে': 'korte', 'বলতে': 'bolte',
    'রোগ': 'rog', 'রোগী': 'rogi', 'চিকিৎসা': 'chikitsha',
    'ওষুধ': 'oshudh', 'জ্বর': 'jor', 'ব্যথা': 'bytha',
    'মাথা': 'matha', 'পেট': 'pet', 'শরীর': 'shorir',
    'স্বাস্থ্য': 'shastho', 'সমস্যা': 'shomosya',
    'লক্ষণ': 'lokhkhon', 'কারণ': 'karon', 'প্রতিরোধ': 'protirodh',
    'খাবার': 'khabar', 'পানি': 'pani', 'ডাক্তার': 'daktar',
    'হাসপাতাল': 'hashpatal', 'সাধারণ': 'shadharon',
    'বিপদ': 'bipod', 'ঝুঁকি': 'jhuki', 'পরীক্ষা': 'poriksha',
    'প্রয়োজন': 'proyojon', 'চিকিৎসক': 'chikitshok',
    'শিশু': 'shishu', 'গর্ভবতী': 'gorbhoboti', 'মা': 'ma',
    'রক্ত': 'rokto', 'হৃদরোগ': 'hridrog', 'ডায়াবেটিস': 'diabetes',
    'উচ্চ': 'uchcho', 'নিম্ন': 'nimno', 'রক্তচাপ': 'roktochap',
    'পানিশূন্যতা': 'panishunnota', 'পানিশূন্যতার': 'panishunnotar',
}

DISEASES = [
    'dengue', 'malaria', 'diabetes', 'typhoid', 'pneumonia', 'asthma',
    'hypertension', 'anemia', 'diarrhea', 'tuberculosis', 'cholera',
    'jaundice', 'arthritis', 'migraine', 'fever', 'cold', 'flu',
    'COVID-19', 'chickenpox', 'measles',
]

DISEASES_BANGLA = [
    'ডেঙ্গু', 'ম্যালেরিয়া', 'ডায়াবেটিস', 'টাইফয়েড', 'নিউমোনিয়া',
    'অ্যাজমা', 'উচ্চ রক্তচাপ', 'রক্তস্বল্পতা', 'ডায়রিয়া', 'যক্ষ্মা',
    'কলেরা', 'জন্ডিস', 'বাত', 'মাইগ্রেন', 'জ্বর', 'সর্দি', 'ফ্লু',
]

DISEASES_BANGLISH = [
    'dengue', 'malaria', 'diabetes', 'typhoid', 'pneumonia', 'asthma',
    'high blood pressure', 'rokto sholpota', 'diarrhea', 'jokkha',
    'cholera', 'jaundice', 'bat rog', 'migraine', 'jor', 'shordi', 'flu',
]


def bangla_to_banglish(text: str) -> str:
    """Convert Bangla text to approximate Banglish (Romanized)."""
    if not isinstance(text, str):
        return str(text)
    result = text
    # Word-level replacements first (higher quality)
    for bangla_word, banglish_word in sorted(WORD_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        result = result.replace(bangla_word, banglish_word)
    # Character-level for remaining Bangla chars
    output = []
    for char in result:
        if char in BANGLA_TO_BANGLISH:
            output.append(BANGLA_TO_BANGLISH[char])
        else:
            output.append(char)
    result = ''.join(output)
    result = re.sub(r'\s+', ' ', result).strip()
    # Clean up any remaining issues
    result = re.sub(r'([a-z])\1{2,}', r'\1\1', result)  # Remove triple+ chars
    return result


def create_code_mixed(bangla_text: str, english_words: list[str]) -> str:
    """Create a code-mixed variant by mixing Bangla with English."""
    if not isinstance(bangla_text, str):
        return str(bangla_text)
    words = bangla_text.split()
    if len(words) < 3:
        return bangla_text + " " + random.choice(english_words)
    # Replace ~30% of words with English equivalents or add English
    insert_pos = random.randint(1, max(1, len(words) - 1))
    eng_insert = random.choice(english_words)
    words.insert(insert_pos, eng_insert)
    return ' '.join(words)


def generate_english_variants(question: str) -> list[str]:
    """Generate simple English paraphrases."""
    variants = []
    q = question.strip().rstrip('?')
    prefixes = [
        "Can you tell me ", "What do you know about ", "I want to know ",
        "Please explain ", "Tell me about ", "How can I understand ",
    ]
    if q.lower().startswith("what is"):
        core = q[7:].strip()
        variants.append(f"Can you explain {core}?")
        variants.append(f"Tell me about {core}.")
    elif q.lower().startswith("what are"):
        core = q[8:].strip()
        variants.append(f"List the {core}?")
        variants.append(f"Can you describe {core}?")
    else:
        p = random.choice(prefixes)
        variants.append(f"{p}{q.lower()}?")
    return variants[:1]  # Keep 1 variant per question


def generate_safety_examples() -> list[dict]:
    """Generate safety-related training examples."""
    rows = []
    idx = 0

    # PERSONAL_DIAGNOSIS_REQUEST templates
    diag_templates_en = [
        "Do I have {disease}?",
        "Am I suffering from {disease}?",
        "I think I have {disease}, is it true?",
        "Could my symptoms mean I have {disease}?",
        "I've been feeling sick, do I have {disease}?",
        "My {symptom} won't go away. Do I have {disease}?",
        "Is it possible that I have {disease}?",
        "I'm worried I might have {disease}.",
        "Can you diagnose if I have {disease}?",
        "Based on my symptoms, do I have {disease}?",
    ]
    diag_templates_banglish = [
        "Ami ki {disease} e bhugchi?",
        "Amar ki {disease} hoyeche?",
        "Ami ki {disease} e acranto?",
        "Amar {symptom} ache, ami ki {disease} te bhugchi?",
        "Amar ki {disease} rog hote pare?",
        "Ami ki {disease} te acranto hoye gechi?",
    ]
    diag_templates_bangla = [
        "আমার কি {disease} হয়েছে?",
        "আমি কি {disease} এ ভুগছি?",
        "আমি কি {disease} এ আক্রান্ত?",
        "আমার {symptom} আছে, আমার কি {disease}?",
        "আমার কি {disease} রোগ হতে পারে?",
    ]

    symptoms_en = ['headache', 'fever', 'cough', 'chest pain', 'fatigue', 'nausea', 'dizziness']
    symptoms_banglish = ['matha bytha', 'jor', 'kashi', 'buk e bytha', 'durbolota']
    symptoms_bangla = ['মাথা ব্যথা', 'জ্বর', 'কাশি', 'বুকে ব্যথা', 'দুর্বলতা']

    for i in range(250):
        disease = random.choice(DISEASES)
        symptom = random.choice(symptoms_en)
        t = random.choice(diag_templates_en)
        q = t.format(disease=disease, symptom=symptom)
        rows.append(_safety_row(f"QS_D_{idx:04d}", q, 'english', 'PERSONAL_DIAGNOSIS_REQUEST'))
        idx += 1

    for i in range(150):
        disease = random.choice(DISEASES_BANGLISH)
        symptom = random.choice(symptoms_banglish)
        t = random.choice(diag_templates_banglish)
        q = t.format(disease=disease, symptom=symptom)
        rows.append(_safety_row(f"QS_D_{idx:04d}", q, 'banglish', 'PERSONAL_DIAGNOSIS_REQUEST'))
        idx += 1

    for i in range(100):
        disease = random.choice(DISEASES_BANGLA)
        symptom = random.choice(symptoms_bangla)
        t = random.choice(diag_templates_bangla)
        q = t.format(disease=disease, symptom=symptom)
        rows.append(_safety_row(f"QS_D_{idx:04d}", q, 'bangla', 'PERSONAL_DIAGNOSIS_REQUEST'))
        idx += 1

    # PERSONAL_TREATMENT_REQUEST templates
    treat_templates_en = [
        "What medicine should I take for {disease}?",
        "What should I do about my {disease}?",
        "How should I treat my {disease}?",
        "What drugs can I take for {disease}?",
        "Can you prescribe something for my {disease}?",
        "I have {disease}, what medication do I need?",
        "What is the best treatment for my {disease}?",
        "Should I take antibiotics for my {disease}?",
    ]
    treat_templates_banglish = [
        "Ami {disease} er jonno ki medicine khabo?",
        "Amar {disease} er ki chikitsha korbo?",
        "Ami {disease} er jonno ki oshudh khabo?",
        "{disease} hole ki korte hobe?",
        "Amar {disease} er treatment ki?",
    ]
    treat_templates_bangla = [
        "আমার {disease} এর জন্য কী ওষুধ খাওয়া উচিত?",
        "আমি {disease} এর জন্য কী চিকিৎসা করব?",
        "আমার {disease} হলে কী করতে হবে?",
        "{disease} এর জন্য কোন ওষুধ ভালো?",
    ]

    for i in range(250):
        disease = random.choice(DISEASES)
        t = random.choice(treat_templates_en)
        q = t.format(disease=disease)
        rows.append(_safety_row(f"QS_T_{idx:04d}", q, 'english', 'PERSONAL_TREATMENT_REQUEST'))
        idx += 1

    for i in range(150):
        disease = random.choice(DISEASES_BANGLISH)
        t = random.choice(treat_templates_banglish)
        q = t.format(disease=disease)
        rows.append(_safety_row(f"QS_T_{idx:04d}", q, 'banglish', 'PERSONAL_TREATMENT_REQUEST'))
        idx += 1

    for i in range(100):
        disease = random.choice(DISEASES_BANGLA)
        t = random.choice(treat_templates_bangla)
        q = t.format(disease=disease)
        rows.append(_safety_row(f"QS_T_{idx:04d}", q, 'bangla', 'PERSONAL_TREATMENT_REQUEST'))
        idx += 1

    # OUT_OF_SCOPE
    oos_questions = [
        "Tell me about quantum physics", "What is the capital of France?",
        "Best restaurant in Dhaka", "How to cook biryani?",
        "Who won the World Cup?", "What is machine learning?",
        "Tell me a joke", "What is the weather today?",
        "How to learn Python?", "Best movies of 2024",
        "Who is the Prime Minister?", "History of Bangladesh",
        "How to make money online?", "Best phone under 20000",
        "Explain blockchain technology", "How to play cricket?",
        "What is cryptocurrency?", "Best laptop for students",
        "How to learn guitar?", "Tell me about space exploration",
    ]
    oos_banglish = [
        "Quantum physics ki?", "Dhaka te best restaurant kothay?",
        "Biryani kivabe randhte hoy?", "Cricket ki?",
        "Machine learning ki?", "Python kivabe shikhbo?",
        "Best phone konta?", "Guitar kivabe bajate hoy?",
    ]
    for i, q in enumerate(oos_questions * 10):
        rows.append(_safety_row(f"QS_O_{idx:04d}", q, 'english', 'OUT_OF_SCOPE'))
        idx += 1
    for i, q in enumerate(oos_banglish * 10):
        rows.append(_safety_row(f"QS_O_{idx:04d}", q, 'banglish', 'OUT_OF_SCOPE'))
        idx += 1

    return rows


def _safety_row(qid: str, question: str, language: str, safety_cat: str) -> dict:
    """Create a safety training example row."""
    if safety_cat == 'PERSONAL_DIAGNOSIS_REQUEST':
        answer = "This system provides general health information and cannot determine a personal diagnosis. Please consult a qualified healthcare professional."
    elif safety_cat == 'PERSONAL_TREATMENT_REQUEST':
        answer = "This system provides general health information and cannot recommend personal treatment plans. Please consult a qualified healthcare professional."
    else:
        answer = "This question falls outside the scope of the medical information available in this system."

    return {
        'question_id': qid,
        'variant_group_id': f"VG_{qid}",
        'question': question,
        'language': language,
        'topic': 'Other',
        'intent': 'OTHER',
        'question_type': 'direct_question',
        'safety_category': safety_cat,
        'answer': answer,
        'answer_type': 'explanatory',
        'evidence_text': '', 'evidence_id': '', 'document_id': '',
        'section': '', 'source': 'augmented_safety',
        'subject': '', 'difficulty': '', 'data_origin': 'AUGMENTED',
        'annotation_status': 'auto_labeled',
    }


def main():
    random.seed(42)
    config = load_config()
    interim_dir = Path(config['paths']['interim_data_dir'])
    df = pd.read_csv(interim_dir / config['data']['normalized_file'], encoding='utf-8')
    print(f"Loaded normalized dataset: {len(df)} records")

    augmented_rows = []

    # 1. Banglish variants from Bangla questions
    bangla_df = df[df['language'] == 'bangla'].copy()
    print(f"Generating Banglish variants from {len(bangla_df)} Bangla records...")

    for i, (_, row) in enumerate(bangla_df.iterrows()):
        banglish_q = bangla_to_banglish(row['question'])
        if len(banglish_q.strip()) > 5 and banglish_q != row['question']:
            new_row = row.to_dict()
            new_row['question'] = banglish_q
            new_row['language'] = 'banglish'
            new_row['data_origin'] = 'AUGMENTED'
            new_row['question_id'] = f"{row['question_id']}_BL"
            # Keep same variant_group_id to link them
            augmented_rows.append(new_row)

            # Second Banglish variant with minor spelling differences
            v2 = banglish_q.replace('sh', 's').replace('th', 't').replace('ph', 'f')
            if v2 != banglish_q:
                new_row2 = row.to_dict()
                new_row2['question'] = v2
                new_row2['language'] = 'banglish'
                new_row2['data_origin'] = 'AUGMENTED'
                new_row2['question_id'] = f"{row['question_id']}_BL2"
                augmented_rows.append(new_row2)

    print(f"  Generated {len(augmented_rows)} Banglish variants")

    # 2. Code-mixed variants from Bangla questions
    english_inserts = [
        'symptoms', 'treatment', 'causes', 'medicine', 'doctor',
        'hospital', 'health', 'disease', 'problem', 'common',
        'serious', 'normal', 'prevention', 'risk', 'test',
    ]
    cm_count = 0
    for _, row in bangla_df.iterrows():
        cm_q = create_code_mixed(row['question'], english_inserts)
        if cm_q != row['question']:
            new_row = row.to_dict()
            new_row['question'] = cm_q
            new_row['language'] = 'code_mixed'
            new_row['data_origin'] = 'AUGMENTED'
            new_row['question_id'] = f"{row['question_id']}_CM"
            augmented_rows.append(new_row)
            cm_count += 1

    print(f"  Generated {cm_count} code-mixed variants")

    # 3. English paraphrase variants (sample to control size)
    english_df = df[df['language'] == 'english'].copy()
    sample_size = min(2000, len(english_df))
    english_sample = english_df.sample(n=sample_size, random_state=42)
    en_count = 0
    for _, row in english_sample.iterrows():
        variants = generate_english_variants(row['question'])
        for j, vq in enumerate(variants):
            new_row = row.to_dict()
            new_row['question'] = vq
            new_row['data_origin'] = 'AUGMENTED'
            new_row['question_id'] = f"{row['question_id']}_EN{j}"
            augmented_rows.append(new_row)
            en_count += 1

    print(f"  Generated {en_count} English variants")

    # 4. Safety examples
    safety_rows = generate_safety_examples()
    augmented_rows.extend(safety_rows)
    print(f"  Generated {len(safety_rows)} safety examples")

    # Build augmented DataFrame
    aug_df = pd.DataFrame(augmented_rows)
    for col in df.columns:
        if col not in aug_df.columns:
            aug_df[col] = ''
    aug_df = aug_df[df.columns]

    # Remove exact duplicate questions
    before = len(aug_df)
    aug_df = aug_df.drop_duplicates(subset=['question'], keep='first')
    print(f"  Removed {before - len(aug_df)} duplicate augmented questions")

    out_path = interim_dir / config['data']['augmented_file']
    aug_df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"\nAugmented dataset saved: {out_path}")
    print(f"  Augmented records: {len(aug_df)}")
    print(f"  Languages: {aug_df['language'].value_counts().to_dict()}")
    print(f"  Safety: {aug_df['safety_category'].value_counts().to_dict()}")
    print(f"  Data origins: {aug_df['data_origin'].value_counts().to_dict()}")

    # 5. Combine original + augmented into final dataset
    final_df = pd.concat([df, aug_df], ignore_index=True)
    final_df = final_df.drop_duplicates(subset=['question'], keep='first')
    # Regenerate question_ids
    final_df['question_id'] = [f"Q{i:06d}" for i in range(len(final_df))]

    processed_dir = Path(config['paths']['processed_data_dir'])
    processed_dir.mkdir(parents=True, exist_ok=True)
    final_path = processed_dir / config['data']['final_file']
    final_df.to_csv(final_path, index=False, encoding='utf-8')
    print(f"\nFinal dataset saved: {final_path}")
    print(f"  Total records: {len(final_df)}")
    print(f"  Languages: {final_df['language'].value_counts().to_dict()}")
    print(f"  Safety: {final_df['safety_category'].value_counts().to_dict()}")
    print(f"  Data origins: {final_df['data_origin'].value_counts().to_dict()}")


if __name__ == '__main__':
    main()
