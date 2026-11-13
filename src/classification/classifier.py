"""Generic text classifier using TF-IDF + ML models."""
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


class TextClassifier:
    """TF-IDF based text classifier with LR or SVM backend."""

    def __init__(self, classifier_type: str = "logistic_regression",
                 max_features: int = 10000, ngram_range: tuple = (1, 2)):
        self.classifier_type = classifier_type
        self.vectorizer = TfidfVectorizer(
            max_features=max_features, ngram_range=ngram_range,
            sublinear_tf=True, strip_accents=None  # preserve Bangla
        )
        if classifier_type == "svm":
            self.model = LinearSVC(max_iter=5000, random_state=42, class_weight='balanced')
        else:
            self.model = LogisticRegression(max_iter=2000, random_state=42,
                                           class_weight='balanced', solver='lbfgs')
        self.classes_ = None

    def fit(self, texts: list[str], labels: list[str]) -> "TextClassifier":
        """Train the classifier."""
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.classes_ = self.model.classes_ if hasattr(self.model, 'classes_') else np.unique(labels)
        return self

    def predict(self, texts: list[str]) -> np.ndarray:
        """Predict labels for texts."""
        X = self.vectorizer.transform(texts)
        return self.model.predict(X)

    def evaluate(self, texts: list[str], labels: list[str]) -> dict:
        """Evaluate and return classification report + confusion matrix."""
        preds = self.predict(texts)
        report = classification_report(labels, preds, output_dict=True, zero_division=0)
        cm = confusion_matrix(labels, preds)
        acc = accuracy_score(labels, preds)
        return {
            "accuracy": acc,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "predictions": preds.tolist(),
        }

    def save(self, model_path: str, vectorizer_path: str) -> None:
        """Save model and vectorizer."""
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

    def load(self, model_path: str, vectorizer_path: str) -> "TextClassifier":
        """Load model and vectorizer."""
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.classes_ = self.model.classes_ if hasattr(self.model, 'classes_') else None
        return self
