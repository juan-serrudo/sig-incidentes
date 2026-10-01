"""Linear baseline using word TF-IDF + char n-gram TF-IDF + LogisticRegression."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from app.settings import SEED


def build_linear_baseline(
    word_ngram_range=(1, 2),
    char_ngram_range=(3, 5),
    min_df_word=2,
    min_df_char=3,
    max_features_word=5000,
    max_features_char=5000,
    c_param=1.0,
    class_weight="balanced",
):
    """Build a strong regularized linear baseline with word and character TF-IDF."""
    features = FeatureUnion([
        (
            "word_tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=word_ngram_range,
                min_df=min_df_word,
                max_features=max_features_word,
                sublinear_tf=True,
            ),
        ),
        (
            "char_tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                analyzer="char_wb",
                ngram_range=char_ngram_range,
                min_df=min_df_char,
                max_features=max_features_char,
                sublinear_tf=True,
            ),
        ),
    ])

    classifier = LogisticRegression(
        C=c_param,
        class_weight=class_weight,
        max_iter=1000,
        random_state=SEED,
    )

    return Pipeline([
        ("features", features),
        ("classifier", classifier),
    ])


def prepare_incident_text(data):
    """Deterministically combine title and initial description for text models."""
    return data["title"].astype(str) + ". " + data["initial_description"].astype(str)
