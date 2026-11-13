"""Hybrid retrieval combining TF-IDF and dense retrieval."""
import numpy as np
from src.retrieval.tfidf_retrieval import TFIDFRetriever
from src.retrieval.dense_retrieval import DenseRetriever


class HybridRetriever:
    """Combines lexical (TF-IDF) and semantic (dense) retrieval."""

    def __init__(self, tfidf_retriever: TFIDFRetriever, dense_retriever: DenseRetriever,
                 alpha: float = 0.7):
        self.tfidf = tfidf_retriever
        self.dense = dense_retriever
        self.alpha = alpha  # weight for semantic score

    def search(self, query: str, top_k: int = 10, alpha: float = None) -> list[dict]:
        """Hybrid search combining lexical and semantic scores."""
        if alpha is None:
            alpha = self.alpha

        # Get results from both
        tfidf_results = self.tfidf.search(query, top_k=top_k * 2)
        dense_results = self.dense.search(query, top_k=top_k * 2)

        # Normalize scores to [0, 1]
        tfidf_scores = {r.get('question_id', r.get('question', '')): r['similarity_score']
                       for r in tfidf_results}
        dense_scores = {r.get('question_id', r.get('question', '')): r['similarity_score']
                       for r in dense_results}

        # Min-max normalize
        def normalize(scores_dict):
            if not scores_dict:
                return scores_dict
            vals = list(scores_dict.values())
            mn, mx = min(vals), max(vals)
            rng = mx - mn if mx > mn else 1.0
            return {k: (v - mn) / rng for k, v in scores_dict.items()}

        tfidf_norm = normalize(tfidf_scores)
        dense_norm = normalize(dense_scores)

        # Combine all candidates
        all_docs = {}
        for r in tfidf_results + dense_results:
            key = r.get('question_id', r.get('question', ''))
            if key not in all_docs:
                all_docs[key] = r.copy()

        # Calculate hybrid scores
        for key, doc in all_docs.items():
            lex_score = tfidf_norm.get(key, 0.0)
            sem_score = dense_norm.get(key, 0.0)
            doc['similarity_score'] = alpha * sem_score + (1 - alpha) * lex_score
            doc['lexical_score'] = tfidf_scores.get(key, 0.0)
            doc['semantic_score'] = dense_scores.get(key, 0.0)
            doc['retrieval_method'] = 'hybrid'

        # Sort and return top-k
        sorted_results = sorted(all_docs.values(), key=lambda x: x['similarity_score'], reverse=True)
        return sorted_results[:top_k]
