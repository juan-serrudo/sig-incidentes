"""Inference and limited, non-causal explanations for the linear text model."""

import numpy as np

from app.baseline import rule_prediction
from app.settings import CATEGORIES


def classify_message(bundle, message):
    model = bundle["model"]
    vectorizer = model.named_steps["vectorizer"]
    classifier = model.named_steps["classifier"]
    probabilities = model.predict_proba([message])[0]
    order = np.argsort(-probabilities)
    best_index = int(order[0])
    category = str(classifier.classes_[best_index])
    vector = vectorizer.transform([message])
    known_vocabulary = vector.nnz > 0
    score = float(probabilities[best_index])
    needs_review = not known_vocabulary or score < bundle["review_threshold"]

    # These terms increase the selected class's linear score, not a causal effect.
    terms = vectorizer.get_feature_names_out()
    weights = classifier.coef_[best_index]
    contributions = [(str(terms[index]), float(value * weights[index])) for index, value in zip(vector.indices, vector.data) if value * weights[index] > 0]
    contributions.sort(key=lambda item: item[1], reverse=True)
    reason = "unknown_vocabulary" if not known_vocabulary else "below_threshold" if needs_review else "above_threshold"
    return {
        "category": category, "category_name": CATEGORIES[category]["name"], "score": score,
        "needs_review": needs_review, "review_reason": reason, "review_threshold": bundle["review_threshold"],
        "ranking": [{"category": str(classifier.classes_[index]), "name": CATEGORIES[str(classifier.classes_[index])]["name"], "score": float(probabilities[index])} for index in order],
        "signals": [{"term": term, "contribution": contribution} for term, contribution in contributions[:5]],
        "baseline": rule_prediction(message, bundle["baseline_fallback"]),
        "model_version": bundle["model_version"], "synthetic_data": True,
    }

