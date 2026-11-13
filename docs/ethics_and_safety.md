# MediRAG-BD: Ethics, Safety and Responsible Use

## Intended Use

MediRAG-BD is designed as an **academic research prototype** for studying multilingual medical question answering. It is intended for:

- University research on NLP and information retrieval
- Demonstration of multilingual text processing (Bangla, English, Banglish, code-mixed)
- Evaluation of retrieval-based QA systems
- Study of safety-aware question handling

## Prohibited Use

This system must **NOT** be used for:

- Clinical diagnosis or medical decision-making
- Replacing professional medical consultation
- Providing personalized treatment recommendations
- Commercial medical advice services
- Any application where incorrect information could cause harm

## Medical Scope and Limitations

### What the system does
- Retrieves pre-validated answers from a curated medical QA dataset
- Provides **general health information** only
- Detects and refuses personal diagnosis/treatment requests
- Abstains when no relevant answer exists in the dataset

### What the system does NOT do
- Generate new medical information
- Diagnose conditions
- Recommend treatments
- Access real-time medical databases
- Replace professional medical judgment

## Privacy Considerations

- No real patient data is stored or processed
- User queries are processed locally without external API calls
- No personally identifiable information (PII) is collected
- Query logs should be handled according to local data protection regulations
- The PII detection pipeline checks for accidental phone/email patterns in the dataset

## Bias and Fairness

### Known biases
- **Source bias**: Dataset is primarily from medical exams (USMLE, BanglaMedQA), which may not represent common public health questions
- **Language bias**: English data significantly outweighs Bangla data (~15,000 vs ~2,000 original records)
- **Topic bias**: Some medical topics are over-represented (Fever, General Health) while others are sparse (Vaccination, Mental Health)
- **Banglish bias**: Banglish variants are system-generated approximations, not naturally occurring text

### Mitigation steps taken
- Multilingual augmentation to balance language representation
- Safety classifier to prevent unsafe responses
- Abstention mechanism for low-confidence queries
- Transparent reporting of per-language performance differences

## Uncertainty and Abstention

The system implements explicit uncertainty handling:
- **Relevance threshold**: Queries below the similarity threshold receive no answer rather than a wrong answer
- **Safety classification**: Personal diagnosis/treatment requests are detected and refused
- **Out-of-scope detection**: Non-medical queries are identified and rejected

## Source Provenance

All data sources are documented:
- **MedQA-USMLE**: US Medical Licensing Examination questions (public dataset)
- **BanglaMedQA**: Bangla medical entrance exam questions (public dataset)
- **PublicHealth-QA**: Public health information (CDC-sourced)
- **MedMCQA**: Medical MCQ dataset (public)
- **RealMedQA**: Real-world medical questions (public)
- **Augmented data**: System-generated variants, clearly labeled with `data_origin: AUGMENTED`

## Human Oversight

- All augmented data should be reviewed before use in production
- Classification labels were auto-assigned and should be expert-verified for clinical applications
- The system is designed as a research tool, not an autonomous medical system
- Human medical professionals should always be the final authority on medical questions

## Limitations Summary

1. Limited to topics present in the training dataset
2. Banglish transliteration is approximate (no standard orthography exists)
3. Code-mixed text handling is rule-based, not learned
4. MCQ-sourced answers may be too brief for explanatory QA
5. No clinical validation has been performed
6. Dataset may reflect biases from source medical examinations
7. The system cannot handle follow-up questions or conversation context
8. Performance varies across languages (English typically better than Banglish)
