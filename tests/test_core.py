"""Unit tests for MediRAG-BD core components."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import pandas as pd
from pathlib import Path


class TestLanguageDetector:
    def test_english(self):
        from src.language.detector import detect_language
        assert detect_language("What are the symptoms of dengue?") == "english"

    def test_bangla(self):
        from src.language.detector import detect_language
        assert detect_language("পানিশূন্যতার সাধারণ লক্ষণ কী কী?") == "bangla"

    def test_banglish(self):
        from src.language.detector import detect_language
        assert detect_language("Pani shunnotar symptoms ki ki?") == "banglish"

    def test_code_mixed(self):
        from src.language.detector import detect_language
        result = detect_language("Pani shunnota হলে common symptoms ki?")
        assert result == "code_mixed"

    def test_empty(self):
        from src.language.detector import detect_language
        assert detect_language("") == "english"


class TestTextProcessor:
    def test_unicode_normalize(self):
        from src.preprocessing.text_processor import normalize_unicode
        assert isinstance(normalize_unicode("hello"), str)

    def test_whitespace(self):
        from src.preprocessing.text_processor import normalize_whitespace
        assert normalize_whitespace("  hello   world  ") == "hello world"

    def test_remove_noise(self):
        from src.preprocessing.text_processor import remove_noise
        result = remove_noise("Check http://example.com and email@test.com")
        assert "http" not in result
        assert "@" not in result

    def test_preprocess_question(self):
        from src.preprocessing.text_processor import preprocess_question
        result = preprocess_question("What is dengue?", "english")
        assert 'raw_question' in result
        assert 'processed_question' in result
        assert result['raw_question'] == "What is dengue?"

    def test_banglish_normalize(self):
        from src.preprocessing.text_processor import normalize_banglish
        result = normalize_banglish("fever kee?")
        assert "ki" in result


class TestDataLoader:
    def test_load_config(self):
        from src.data.loader import load_config
        config = load_config()
        assert 'project' in config
        assert config['project']['name'] == 'MediRAG-BD'

    def test_splits_exist(self):
        for split in ['train.csv', 'validation.csv', 'test.csv']:
            assert Path(f'data/splits/{split}').exists(), f"Missing {split}"

    def test_final_dataset_exists(self):
        assert Path('data/processed/mediqa_bd_final.csv').exists()

    def test_dataset_schema(self):
        df = pd.read_csv('data/processed/mediqa_bd_final.csv', nrows=5)
        required = ['question_id', 'question', 'answer', 'language', 'topic',
                    'intent', 'safety_category', 'data_origin']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_no_leakage(self):
        train = pd.read_csv('data/splits/train.csv')
        test = pd.read_csv('data/splits/test.csv')
        train_groups = set(train['variant_group_id'].unique())
        test_groups = set(test['variant_group_id'].unique())
        assert len(train_groups & test_groups) == 0, "Data leakage detected!"


class TestClassifier:
    def test_classifier_creates(self):
        from src.classification.classifier import TextClassifier
        clf = TextClassifier(classifier_type="logistic_regression")
        assert clf is not None

    def test_classifier_train_predict(self):
        from src.classification.classifier import TextClassifier
        clf = TextClassifier(max_features=100)
        texts = ["What is fever?", "How to treat cold?", "Symptoms of flu", "Prevent malaria"]
        labels = ["info", "treatment", "symptoms", "prevention"]
        clf.fit(texts, labels)
        preds = clf.predict(["What is dengue?"])
        assert len(preds) == 1
        assert preds[0] in labels

    def test_models_saved(self):
        for f in ['intent_model.pkl', 'topic_model.pkl', 'safety_model.pkl']:
            assert Path(f'models/{f}').exists(), f"Missing model: {f}"


class TestSafetyClassifier:
    def test_diagnosis_keywords(self):
        from src.safety.classifier import SafetyClassifier
        clf = SafetyClassifier()
        assert clf.predict("Do I have dengue?") == "PERSONAL_DIAGNOSIS_REQUEST"
        assert clf.predict("Ami ki malaria e bhugchi?") == "PERSONAL_DIAGNOSIS_REQUEST"

    def test_treatment_keywords(self):
        from src.safety.classifier import SafetyClassifier
        clf = SafetyClassifier()
        assert clf.predict("What medicine should I take for fever?") == "PERSONAL_TREATMENT_REQUEST"

    def test_safe_question(self):
        from src.safety.classifier import SafetyClassifier
        clf = SafetyClassifier()
        result = clf.predict("What is dehydration?")
        assert result == "SAFE_GENERAL_INFORMATION"


class TestRetrieval:
    def test_tfidf_retriever(self):
        from src.retrieval.tfidf_retrieval import TFIDFRetriever
        ret = TFIDFRetriever(max_features=100)
        docs = [
            {"question": "What is dengue?", "answer": "A viral disease", "question_id": "Q1"},
            {"question": "How to prevent malaria?", "answer": "Use nets", "question_id": "Q2"},
        ]
        ret.build_index(docs)
        results = ret.search("dengue symptoms", top_k=2)
        assert len(results) == 2
        assert 'similarity_score' in results[0]

    def test_indexes_exist(self):
        for f in ['tfidf_vectorizer.pkl', 'tfidf_matrix.pkl']:
            assert Path(f'data/indexes/{f}').exists(), f"Missing index: {f}"


class TestEvalMetrics:
    def test_recall_at_k(self):
        from src.evaluation.metrics import recall_at_k
        assert recall_at_k(["A", "B", "C"], "A", 1) == 1.0
        assert recall_at_k(["A", "B", "C"], "D", 3) == 0.0
        assert recall_at_k(["A", "B", "C"], "C", 3) == 1.0

    def test_mrr(self):
        from src.evaluation.metrics import mrr
        assert mrr(["A", "B", "C"], "A") == 1.0
        assert mrr(["A", "B", "C"], "B") == 0.5
        assert mrr(["A", "B", "C"], "D") == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
