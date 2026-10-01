"""Classification metrics, Top-K accuracy and review policy thresholds."""

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from app.settings import LABELS, MIN_ACCEPTED_ACCURACY, MIN_ACCEPTED_CASES


def top_k_accuracy(actual, probabilities, classes, k=3):
    """Compute Top-K accuracy given probability distributions and class array."""
    actual = np.asarray(actual)
    classes = np.asarray(classes)
    top_k_indices = np.argsort(-probabilities, axis=1)[:, :k]
    top_k_classes = classes[top_k_indices]
    hits = [actual[i] in top_k_classes[i] for i in range(len(actual))]
    return float(np.mean(hits)) if len(actual) > 0 else 0.0


def classification_metrics(actual, predicted, probabilities=None, classes=None):
    """Calculate primary Macro-F1, per-class metrics, confusion matrix and Top-3 accuracy."""
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=LABELS, zero_division=0
    )
    result = {
        "macro_f1": float(f1_score(actual, predicted, labels=LABELS, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(actual, predicted, labels=LABELS, average="weighted", zero_division=0)),
        "accuracy": float(accuracy_score(actual, predicted)),
        "confusion_matrix": confusion_matrix(actual, predicted, labels=LABELS).tolist(),
        "by_category": [
            {
                "category": label,
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABELS)
        ],
    }
    if probabilities is not None and classes is not None:
        result["top_3_accuracy"] = top_k_accuracy(actual, probabilities, classes, k=min(3, len(LABELS)))
    return result


def review_metrics(actual, probabilities, classes, threshold, known_vocabulary):
    scores = probabilities.max(axis=1)
    predicted = np.asarray(classes)[probabilities.argmax(axis=1)]
    accepted = (scores >= threshold) & np.asarray(known_vocabulary)
    accepted_count = int(accepted.sum())
    return {
        "coverage": float(accepted.mean()) if len(actual) > 0 else 0.0,
        "accepted_count": accepted_count,
        "review_count": int(len(actual) - accepted_count),
        "accepted_accuracy": float(np.mean(predicted[accepted] == np.asarray(actual)[accepted])) if accepted_count else None,
    }


def choose_review_threshold(actual, probabilities, classes, known_vocabulary):
    """Maximize validation coverage while meeting a target accuracy on supported cases."""
    for threshold in np.unique(probabilities.max(axis=1)):
        result = review_metrics(actual, probabilities, classes, float(threshold), known_vocabulary)
        if result["accepted_count"] >= MIN_ACCEPTED_CASES and result["accepted_accuracy"] >= MIN_ACCEPTED_ACCURACY:
            return float(threshold)
    return 1.000001  # Fallback: request human review for every message
