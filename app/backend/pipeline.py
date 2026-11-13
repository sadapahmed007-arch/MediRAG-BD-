"""MediRAG-BD Processing Pipeline - core question answering logic."""
import sys, os, time, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import joblib
from pathlib import Path

from src.data.loader import load_config
from src.language.detector import detect_language
from src.preprocessing.text_processor import preprocess_question
from src.classification.classifier import TextClassifier
from src.safety.classifier import SafetyClassifier
from src.retrieval.tfidf_retrieval import TFIDFRetriever
from src.retrieval.dense_retrieval import DenseRetriever
from src.retrieval.hybrid_retrieval import HybridRetriever


class MediRAGPipeline:
    """Complete question-answering pipeline."""

    def __init__(self):
        self.config = load_config()
        self.models_loaded = False
        self.intent_clf = None
        self.topic_clf = None
        self.safety_clf = None
        self.tfidf_ret = None
        self.dense_ret = None
        self.hybrid_ret = None
        self.dataset = None
        self.experiment_results = None

    def load_models(self) -> bool:
        """Load all trained models and indexes."""
        try:
            models_dir = Path(self.config['paths']['models_dir'])
            idx_dir = Path(self.config['paths']['indexes_dir'])

            # Classifiers
            self.intent_clf = TextClassifier()
            self.intent_clf.load(str(models_dir / 'intent_model.pkl'),
                               str(models_dir / 'intent_vectorizer.pkl'))

            self.topic_clf = TextClassifier()
            self.topic_clf.load(str(models_dir / 'topic_model.pkl'),
                               str(models_dir / 'topic_vectorizer.pkl'))

            self.safety_clf = SafetyClassifier()
            self.safety_clf.load(str(models_dir / 'safety_model.pkl'),
                                str(models_dir / 'safety_vectorizer.pkl'))

            # Retrieval
            self.tfidf_ret = TFIDFRetriever()
            self.tfidf_ret.load(str(idx_dir / 'tfidf_vectorizer.pkl'),
                               str(idx_dir / 'tfidf_matrix.pkl'),
                               str(idx_dir / 'tfidf_docs.pkl'))

            self.dense_ret = DenseRetriever(self.config['embeddings']['model_name'])
            self.dense_ret.load(str(idx_dir / 'faiss_index.bin'),
                               str(idx_dir / 'faiss_docs.pkl'))

            self.hybrid_ret = HybridRetriever(
                self.tfidf_ret, self.dense_ret,
                alpha=self.config['retrieval']['hybrid']['alpha']
            )

            # Dataset
            self.dataset = pd.read_csv(
                Path(self.config['paths']['processed_data_dir']) / self.config['data']['final_file'],
                encoding='utf-8'
            )

            # Experiment results
            results_path = Path(self.config['paths']['experiments_dir']) / 'raw_results' / 'all_experiment_results.json'
            if results_path.exists():
                with open(results_path, 'r', encoding='utf-8') as f:
                    self.experiment_results = json.load(f)

            self.models_loaded = True
            print("All models loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_question(self, question: str) -> dict:
        """Process a question through the full pipeline."""
        start_time = time.time()
        stages = []

        # Stage 1: Language detection
        t0 = time.time()
        language = detect_language(question)
        stages.append({"stage": "Language Detection", "status": "done",
                       "detail": language, "time_ms": (time.time() - t0) * 1000})

        # Stage 2: Safety check
        t0 = time.time()
        safety = self.safety_clf.predict(question) if self.safety_clf else 'SAFE_GENERAL_INFORMATION'
        stages.append({"stage": "Safety Check", "status": "done",
                       "detail": safety, "time_ms": (time.time() - t0) * 1000})

        # If unsafe, return safety response
        if safety == 'PERSONAL_DIAGNOSIS_REQUEST':
            return self._safety_response(question, language, safety, stages, start_time,
                                         self.config['safety']['unsafe_response_diagnosis'])
        elif safety == 'PERSONAL_TREATMENT_REQUEST':
            return self._safety_response(question, language, safety, stages, start_time,
                                         self.config['safety']['unsafe_response_treatment'])
        elif safety == 'OUT_OF_SCOPE':
            return self._safety_response(question, language, safety, stages, start_time,
                                         self.config['safety']['out_of_scope_response'])

        # Stage 3: Preprocessing
        t0 = time.time()
        processed = preprocess_question(question, language)
        processed_q = processed['processed_question']
        stages.append({"stage": "Text Preprocessing", "status": "done",
                       "detail": "normalized", "time_ms": (time.time() - t0) * 1000})

        # Stage 4: Topic classification
        t0 = time.time()
        topic = self.topic_clf.predict([processed_q])[0] if self.topic_clf else 'Other'
        stages.append({"stage": "Topic Classification", "status": "done",
                       "detail": topic, "time_ms": (time.time() - t0) * 1000})

        # Stage 5: Intent classification
        t0 = time.time()
        intent = self.intent_clf.predict([processed_q])[0] if self.intent_clf else 'OTHER'
        stages.append({"stage": "Intent Classification", "status": "done",
                       "detail": intent, "time_ms": (time.time() - t0) * 1000})

        # Stage 6: Retrieval
        t0 = time.time()
        candidates = self.hybrid_ret.search(processed_q, top_k=10) if self.hybrid_ret else []
        stages.append({"stage": "Semantic Retrieval", "status": "done",
                       "detail": f"{len(candidates)} candidates", "time_ms": (time.time() - t0) * 1000})

        # Stage 7: Answer selection
        t0 = time.time()
        threshold = self.config['retrieval']['relevance_threshold']

        if candidates and candidates[0]['similarity_score'] >= threshold:
            best = candidates[0]
            answer = str(best.get('answer', ''))
            matched_q = str(best.get('question', ''))
            score = best['similarity_score']
            abstained = False

            # Evidence & source
            evidence = []
            sources = []
            ev_text = best.get('evidence_text', '')
            if ev_text and str(ev_text) != 'nan' and str(ev_text).strip():
                evidence.append({"text": str(ev_text), "document_id": str(best.get('document_id', '')),
                                "section": str(best.get('section', ''))})
            src = best.get('source', '')
            if src and str(src) != 'nan':
                sources.append(str(src))

            # Related questions
            related = []
            for cand in candidates[1:5]:
                related.append({
                    "question": str(cand.get('question', ''))[:200],
                    "topic": str(cand.get('topic', '')),
                    "similarity_score": round(cand['similarity_score'], 4),
                })
        else:
            answer = self.config['retrieval']['low_similarity_message']
            matched_q = ""
            score = candidates[0]['similarity_score'] if candidates else 0.0
            abstained = True
            evidence = []
            sources = []
            related = []

        stages.append({"stage": "Answer Selection", "status": "done",
                       "detail": "abstained" if abstained else "matched",
                       "time_ms": (time.time() - t0) * 1000})

        total_ms = (time.time() - start_time) * 1000
        return {
            "question": question,
            "language": language,
            "topic": topic,
            "intent": intent,
            "safety_category": safety,
            "answer": answer,
            "matched_question": matched_q,
            "similarity_score": round(score, 4),
            "evidence": evidence,
            "sources": sources,
            "abstained": abstained,
            "related_questions": related,
            "processing_stages": stages,
            "latency_ms": round(total_ms, 1),
        }

    def _safety_response(self, question, language, safety, stages, start_time, message):
        total_ms = (time.time() - start_time) * 1000
        return {
            "question": question,
            "language": language,
            "topic": "",
            "intent": "",
            "safety_category": safety,
            "answer": message,
            "matched_question": "",
            "similarity_score": 0.0,
            "evidence": [],
            "sources": [],
            "abstained": True,
            "related_questions": [],
            "processing_stages": stages,
            "latency_ms": round(total_ms, 1),
        }

    def get_source(self, question_id: str) -> dict:
        """Get source record by question_id."""
        if self.dataset is None:
            return {}
        match = self.dataset[self.dataset['question_id'] == question_id]
        if len(match) == 0:
            return {}
        return match.iloc[0].to_dict()

    def get_dashboard_data(self) -> dict:
        """Get research dashboard data."""
        data = {"dataset_stats": {}, "classification_results": {},
                "retrieval_results": {}, "multilingual_results": {}}
        if self.experiment_results:
            data["dataset_stats"] = self.experiment_results.get("dataset_stats", {})
            data["classification_results"] = self.experiment_results.get("classification", {})
            data["retrieval_results"] = self.experiment_results.get("retrieval", {})
            data["multilingual_results"] = self.experiment_results.get("multilingual", {})

        # Add live stats
        if self.dataset is not None:
            data["dataset_stats"]["total_records"] = len(self.dataset)
            data["dataset_stats"]["index_size"] = self.dense_ret.index.ntotal if self.dense_ret and self.dense_ret.index else 0
        return data
