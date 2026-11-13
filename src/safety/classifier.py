"""Safety classifier with keyword fallback."""
import re
from src.classification.classifier import TextClassifier


class SafetyClassifier:
    """Classifies questions into safety categories with keyword fallback."""

    DIAGNOSIS_KEYWORDS = [
        r'\bdo i have\b', r'\bam i suffering\b', r'\bcould i have\b',
        r'\bi think i have\b', r'\bam i sick\b', r'\bdiagnose me\b',
        r'\bami ki\b', r'\bamar ki\b', r'\b\u0986\u09ae\u09be\u09b0 \u0995\u09bf\b',
        r'\b\u0986\u09ae\u09bf \u0995\u09bf\b', r'\bhoyeche\b.*\bami\b',
        r'\bbhugchi\b', r'\bacranto\b',
    ]
    TREATMENT_KEYWORDS = [
        r'\bwhat medicine should i\b', r'\bwhat should i take\b',
        r'\bprescribe\b.*\bme\b', r'\btreat my\b', r'\bwhat drug\b',
        r'\bki medicine khabo\b', r'\bki oshudh\b', r'\bchikitsha korbo\b',
        r'\b\u0995\u09c0 \u0993\u09b7\u09c1\u09a7\b', r'\b\u099a\u09bf\u0995\u09bf\u09ce\u09b8\u09be\b.*\b\u0986\u09ae\u09be\u09b0\b',
    ]

    def __init__(self):
        self.model = TextClassifier(classifier_type="logistic_regression",
                                    max_features=8000, ngram_range=(1, 3))
        self._trained = False

    def fit(self, texts: list[str], labels: list[str]) -> "SafetyClassifier":
        """Train the safety classifier."""
        self.model.fit(texts, labels)
        self._trained = True
        return self

    def predict(self, text: str) -> str:
        """Predict safety category with keyword fallback."""
        text_lower = text.lower()
        # Keyword check first for high-confidence patterns
        for pattern in self.DIAGNOSIS_KEYWORDS:
            if re.search(pattern, text_lower):
                return 'PERSONAL_DIAGNOSIS_REQUEST'
        for pattern in self.TREATMENT_KEYWORDS:
            if re.search(pattern, text_lower):
                return 'PERSONAL_TREATMENT_REQUEST'
        # Use trained model if available
        if self._trained:
            return self.model.predict([text])[0]
        return 'SAFE_GENERAL_INFORMATION'

    def predict_batch(self, texts: list[str]) -> list[str]:
        """Predict safety for a batch of texts."""
        return [self.predict(t) for t in texts]

    def evaluate(self, texts: list[str], labels: list[str]) -> dict:
        """Evaluate the classifier."""
        preds = self.predict_batch(texts)
        from sklearn.metrics import classification_report, accuracy_score
        report = classification_report(labels, preds, output_dict=True, zero_division=0)
        return {
            "accuracy": accuracy_score(labels, preds),
            "classification_report": report,
        }

    def save(self, model_path: str, vectorizer_path: str) -> None:
        self.model.save(model_path, vectorizer_path)

    def load(self, model_path: str, vectorizer_path: str) -> "SafetyClassifier":
        self.model.load(model_path, vectorizer_path)
        self._trained = True
        return self
