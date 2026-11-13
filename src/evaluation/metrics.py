"""Evaluation metrics for retrieval and classification."""
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def recall_at_k(retrieved_ids: list[str], ground_truth_id: str, k: int) -> float:
    """Check if ground truth is in top-k retrieved results."""
    return 1.0 if ground_truth_id in retrieved_ids[:k] else 0.0


def mrr(retrieved_ids: list[str], ground_truth_id: str) -> float:
    """Mean Reciprocal Rank for a single query."""
    for i, rid in enumerate(retrieved_ids):
        if rid == ground_truth_id:
            return 1.0 / (i + 1)
    return 0.0


def batch_recall_at_k(all_retrieved: list[list[str]], all_ground_truth: list[str], k: int) -> float:
    """Average Recall@K across all queries."""
    scores = [recall_at_k(ret, gt, k) for ret, gt in zip(all_retrieved, all_ground_truth)]
    return np.mean(scores) if scores else 0.0


def batch_mrr(all_retrieved: list[list[str]], all_ground_truth: list[str]) -> float:
    """Average MRR across all queries."""
    scores = [mrr(ret, gt) for ret, gt in zip(all_retrieved, all_ground_truth)]
    return np.mean(scores) if scores else 0.0


def top_k_accuracy(all_retrieved: list[list[str]], all_ground_truth: list[str], k: int) -> float:
    """Fraction of queries where ground truth is in top-k."""
    return batch_recall_at_k(all_retrieved, all_ground_truth, k)


def classification_metrics(y_true: list, y_pred: list) -> dict:
    """Compute classification metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
