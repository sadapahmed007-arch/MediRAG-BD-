# MediRAG-BD Annotation Guidelines

## Overview

This document describes the annotation categories used in the MediRAG-BD dataset for labeling medical questions across multiple dimensions: language, topic, intent, safety, and question type.

---

## 1. Language Categories

### English (`english`)
- Text written entirely in standard English using Latin script
- Example: "What are the common symptoms of dehydration?"

### Bangla (`bangla`)
- Text written in Bengali (বাংলা) script
- May include standard Bengali medical terminology
- Example: "পানিশূন্যতার সাধারণ লক্ষণ কী কী?"

### Banglish (`banglish`)
- Bengali language content written in Latin/Roman script (transliteration)
- Does NOT follow any standard transliteration scheme — reflects informal usage
- Common patterns:
  - "ki" / "kee" / "key" → কী (what)
  - "keno" → কেন (why)
  - "hoy" / "hoi" → হয় (happens)
  - "ache" / "ase" → আছে (exists)
  - "korte" → করতে (to do)
  - "bolte" → বলতে (to say)
  - "ami" → আমি (I)
  - "apni" → আপনি (you)
  - "shomosya" / "somossa" → সমস্যা (problem)
  - "rog" / "roog" → রোগ (disease)
  - "oshudh" / "osudh" → ওষুধ (medicine)
- Example: "Pani shunnotar common symptoms ki ki?"

### Code-Mixed (`code_mixed`)
- Contains BOTH Bengali script AND English/Latin script in the same text
- The mixing must be at the word or phrase level (not just a single borrowed term)
- Example: "Pani shunnota হলে common symptoms ki?"
- Example: "Dehydration এর লক্ষণ কী কী?"

### Decision Rules
1. If text contains >30% Bengali Unicode characters → `bangla`
2. If text contains both Bengali Unicode AND Latin characters → `code_mixed`
3. If text is all Latin script but contains recognizable Banglish patterns → `banglish`
4. Otherwise → `english`

---

## 2. Topic Categories

| Topic | Description | Example |
|-------|-------------|---------|
| **General Health** | Broad health topics, wellness, common conditions | "How to maintain good health?" |
| **Fever** | Fever-related conditions including dengue, malaria, typhoid | "What causes high fever?" |
| **First Aid** | Emergency response, wound care, burns, CPR | "How to treat a minor burn?" |
| **Respiratory** | Breathing, asthma, pneumonia, COVID-19 lung issues | "What are asthma triggers?" |
| **Maternal Health** | Pregnancy, childbirth, neonatal care | "What are signs of preeclampsia?" |
| **Nutrition** | Diet, vitamins, malnutrition, dietary requirements | "Which foods are rich in iron?" |
| **Diabetes** | Blood sugar, insulin, diabetic complications | "How to manage Type 2 diabetes?" |
| **Cardiovascular** | Heart disease, blood pressure, stroke | "What causes high blood pressure?" |
| **Dehydration** | Water loss, oral rehydration, electrolytes | "What are signs of dehydration?" |
| **Mental Health** | Anxiety, depression, stress, psychological conditions | "What are symptoms of depression?" |
| **Vaccination** | Immunization, vaccine schedules, side effects | "When should a child get vaccinated?" |
| **Other** | Topics not covered by above categories | Clinical vignettes, rare conditions |

### Topic Assignment Rules
- Assign the MOST SPECIFIC topic that applies
- If multiple topics apply, choose the PRIMARY focus of the question
- Use "Other" only when no specific category fits
- Clinical vignette questions often map to "Other" if the condition is specialized

---

## 3. Intent Categories

| Intent | Description | Example |
|--------|-------------|---------|
| **GENERAL_INFORMATION** | Asking what something is or how it works | "What is diabetes?" |
| **SYMPTOM_INFORMATION** | Asking about signs, symptoms, or manifestations | "What are symptoms of dengue?" |
| **FIRST_AID_INFORMATION** | Asking about emergency or first-aid procedures | "How do I perform CPR?" |
| **NUTRITION_INFORMATION** | Asking about diet, food, vitamins | "What foods help with anemia?" |
| **MEDICATION_INFORMATION** | Asking about drugs, dosage, side effects | "What is paracetamol used for?" |
| **PREVENTION** | Asking how to prevent a condition | "How to prevent malaria?" |
| **WHEN_TO_SEEK_CARE** | Asking when to see a doctor | "When should I go to the ER?" |
| **OTHER** | Does not fit above categories | Exam-style, mechanism-of-action questions |

### Intent Assignment Rules
- Focus on WHAT the user wants to know, not the topic
- "What is X?" → GENERAL_INFORMATION
- "What are symptoms of X?" → SYMPTOM_INFORMATION
- "How to prevent X?" → PREVENTION
- "What medicine for X?" → MEDICATION_INFORMATION
- Clinical vignettes asking for diagnosis/treatment → typically OTHER (exam-style)

---

## 4. Safety Categories

| Category | Description | System Response |
|----------|-------------|-----------------|
| **SAFE_GENERAL_INFORMATION** | General health knowledge question | Normal retrieval response |
| **PERSONAL_DIAGNOSIS_REQUEST** | User asking if they have a specific condition | Scope limitation message |
| **PERSONAL_TREATMENT_REQUEST** | User asking what treatment they should receive | Scope limitation message |
| **OUT_OF_SCOPE** | Non-medical or irrelevant question | Out-of-scope message |

### Safety Classification Rules

**SAFE_GENERAL_INFORMATION** — The question asks about medical knowledge in general terms:
- "What is dehydration?" ✓
- "What are common signs of dengue?" ✓
- "How does insulin work?" ✓

**PERSONAL_DIAGNOSIS_REQUEST** — The question uses first-person language and asks about having a condition:
- "Do I have dengue?" → PERSONAL
- "Ami ki dengue te bhugchi?" → PERSONAL
- "আমার কি ডায়াবেটিস হয়েছে?" → PERSONAL
- Key indicators: "do I have", "am I", "ami ki", "আমার কি", "is this [symptom] dangerous for me"

**PERSONAL_TREATMENT_REQUEST** — The question asks for personal medical advice:
- "What medicine should I take?" → PERSONAL
- "Ami ki oshudh khabo?" → PERSONAL
- "আমার কী ওষুধ খাওয়া উচিত?" → PERSONAL
- Key indicators: "should I take", "ki medicine khabo", "কী ওষুধ", "what should I do about my"

**OUT_OF_SCOPE** — Not a medical question at all:
- "What is the capital of Bangladesh?" → OUT_OF_SCOPE
- "Best restaurant in Dhaka?" → OUT_OF_SCOPE
- "Tell me about quantum physics" → OUT_OF_SCOPE

### Ambiguous Cases
- "Is fever dangerous?" → SAFE (general question about fever)
- "Is my fever dangerous?" → PERSONAL_DIAGNOSIS_REQUEST (personalized)
- "What medicine is used for fever?" → SAFE (general knowledge)
- "What medicine should I take for my fever?" → PERSONAL_TREATMENT_REQUEST

---

## 5. Question Type

| Type | Description |
|------|-------------|
| **direct_question** | Short, clear question about a medical topic |
| **clinical_vignette** | Long scenario-based question with patient details (typically from medical exams) |
| **mcq** | Multiple-choice format question |

### Classification Rule
- Question length > 200 characters AND contains patient scenario → `clinical_vignette`
- Question from MCQ source with option letters → `mcq`
- Otherwise → `direct_question`

---

## 6. Banglish Spelling Variation

Banglish has NO standard spelling. Common variants that should be treated as equivalent:

| Bangla | Common Banglish Spellings |
|--------|--------------------------|
| কী (what) | ki, kee, key |
| কেন (why) | keno, kano, kn |
| হয় (happens) | hoy, hoi, hoe |
| আছে (is/exists) | ache, ase, asche |
| করা (to do) | kora, kra |
| রোগ (disease) | rog, roog, roag |
| ওষুধ (medicine) | oshudh, osudh, ousodh |
| জ্বর (fever) | jor, jhor, jbor |
| মাথা (head) | matha, mtha |
| পেট (stomach) | pet, pait |

---

## 7. Evidence Linking

When evidence is available:
- `evidence_text`: The relevant passage supporting the answer
- `evidence_id`: Unique identifier for the evidence passage
- `document_id`: Identifier for the source document
- `section`: Section within the source document

Not all records have evidence data. This is tracked in the dataset statistics.

---

## 8. Disagreement Handling

For ambiguous annotations:
1. Apply the MOST SPECIFIC label that clearly applies
2. When in doubt between two categories, prefer the one that better serves the system's safety goals
3. When in doubt about safety, err on the side of PERSONAL (safer to flag as personal than to miss it)
4. Document edge cases for future review
