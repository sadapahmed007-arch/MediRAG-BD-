# MediRAG-BD Dataset Card

## Dataset Summary

**MediRAG-BD** (Medical Retrieval-Augmented Generation for Bangladesh) is a multilingual medical question-answering dataset designed for retrieval-based medical information systems. The dataset contains medical questions and answers in four language modes: English, Bangla, Banglish (Romanized Bangla), and Bangla-English code-mixed text.

## Purpose

The dataset serves as the primary knowledge source for a semantic retrieval system that answers general medical-information questions. It is designed for:

- Training text classifiers (intent, topic, safety)
- Building semantic search indexes
- Evaluating multilingual retrieval performance
- Research on Bangla/Banglish medical NLP

## Data Sources

| Source | Records | Language | Description |
|--------|---------|----------|-------------|
| MedQA-USMLE | ~10,176 | English | US Medical Licensing Exam questions |
| BanglaMedQA | ~1,681 | Bangla | Bangla medical entrance exam questions |
| PublicHealth-QA | ~172 | English | Public health Q&A (COVID-19 focused) |
| MedMCQA | ~3,505 | English | Medical MCQ dataset |
| RealMedQA | ~1,100 | English | Real-world medical questions |
| Augmented | Variable | All | System-generated multilingual variants |

## Languages

- **English** (`english`): Standard medical English
- **Bangla** (`bangla`): Bengali script medical text
- **Banglish** (`banglish`): Romanized Bengali using Latin script
- **Code-mixed** (`code_mixed`): Mixed Bengali and English in a single question

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | string | Unique identifier (e.g., Q000001) |
| `variant_group_id` | string | Links multilingual variants of the same question |
| `question` | string | The medical question text |
| `language` | string | Language label |
| `topic` | string | Medical topic category |
| `intent` | string | Question intent category |
| `question_type` | string | clinical_vignette / direct_question / mcq |
| `safety_category` | string | Safety classification |
| `answer` | string | The validated answer |
| `answer_type` | string | explanatory / short_answer / mcq_letter |
| `evidence_text` | string | Supporting evidence (if available) |
| `source` | string | Original data source |
| `data_origin` | string | ORIGINAL / AUGMENTED / MANUAL / REVIEWED |
| `annotation_status` | string | auto_labeled / manually_reviewed |

## Topics

General Health, Fever, First Aid, Respiratory, Maternal Health, Nutrition, Diabetes, Cardiovascular, Dehydration, Mental Health, Vaccination, Other

## Intents

GENERAL_INFORMATION, SYMPTOM_INFORMATION, FIRST_AID_INFORMATION, NUTRITION_INFORMATION, MEDICATION_INFORMATION, PREVENTION, WHEN_TO_SEEK_CARE, OTHER

## Safety Categories

- **SAFE_GENERAL_INFORMATION**: General health knowledge questions
- **PERSONAL_DIAGNOSIS_REQUEST**: User asking for personal diagnosis
- **PERSONAL_TREATMENT_REQUEST**: User asking for personal treatment advice
- **OUT_OF_SCOPE**: Non-medical or irrelevant questions

## Data Quality

### Original Data
- Sourced from established medical QA datasets
- Labels auto-assigned based on content analysis
- Answer quality varies by source (PublicHealth-QA has best explanatory answers)

### Augmented Data
- Generated through controlled multilingual augmentation
- Banglish variants created via phonetic transliteration
- Code-mixed variants combine Bengali and English text
- Safety examples created from templates
- All augmented records tracked with `data_origin: AUGMENTED`

### Quality Control
- Automated validation pipeline checks for duplicates, missing values, invalid labels
- Normalized duplicate detection
- Group-aware train/test splitting prevents data leakage
- PII detection for phone numbers and emails

## Limitations

- Medical topics are not comprehensive — focused on common conditions
- Banglish transliteration is approximate (Banglish has no standard orthography)
- MCQ-sourced answers may be too brief for explanatory QA
- Labels were auto-assigned, not expert-verified
- Limited clinical validation
- Dataset may reflect biases present in source medical exams
- Not suitable for clinical decision-making

## Privacy

- No real patient data
- No personally identifiable information
- Derived from publicly available medical QA datasets
- PII detection pipeline applied during validation

## Intended Use

- Academic research on multilingual medical NLP
- Development of retrieval-based QA systems
- Evaluation of Bangla/Banglish text processing
- Study of code-mixed language in medical contexts

## Out-of-Scope Use

- Clinical diagnosis or treatment decisions
- Replacement for professional medical consultation
- Commercial medical advice systems
- Any use requiring clinical validation
