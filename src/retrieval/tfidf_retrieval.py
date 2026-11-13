"""TF-IDF based retrieval system."""
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFRetriever:
    """Lexical retrieval using TF-IDF cosine similarity."""

    def __init__(self, max_features: int = 20000, ngram_range: tuple = (1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features, ngram_range=ngram_range,
            sublinear_tf=True, strip_accents=None
        )
        self.tfidf_matrix = None
        self.documents = None  # list of dicts with question, answer, etc.

    def build_index(self, documents: list[dict], text_field: str = "question") -> None:
        """Build TF-IDF index from documents."""
        self.documents = documents
        texts = [doc[text_field] for doc in documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search for most similar documents."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc = self.documents[idx].copy()
            doc['similarity_score'] = float(scores[idx])
            doc['retrieval_method'] = 'tfidf'
            results.append(doc)
        return results

    def save(self, vectorizer_path: str, matrix_path: str, docs_path: str) -> None:
        """Save the retriever state."""
        Path(vectorizer_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, vectorizer_path)
        joblib.dump(self.tfidf_matrix, matrix_path)
        joblib.dump(self.documents, docs_path)

    def load(self, vectorizer_path: str, matrix_path: str, docs_path: str) -> "TFIDFRetriever":
        """Load the retriever state."""
        self.vectorizer = joblib.load(vectorizer_path)
        self.tfidf_matrix = joblib.load(matrix_path)
        self.documents = joblib.load(docs_path)
        return self
