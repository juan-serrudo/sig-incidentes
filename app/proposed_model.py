"""Proposed model using frozen pre-trained Transformer embeddings + supervised classifier."""

from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

from app.settings import SEED

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384


class TransformerIncidentClassifier:
    """Supervised classifier trained on frozen pre-trained multilingual transformer embeddings."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        c_param: float = 1.0,
        class_weight: str = "balanced",
        random_state: int = SEED,
    ):
        self.model_name = model_name
        self.c_param = c_param
        self.class_weight = class_weight
        self.random_state = random_state
        self.encoder = None
        self.classes_ = None
        self.classifier = LogisticRegression(
            C=c_param,
            class_weight=class_weight,
            max_iter=1000,
            random_state=random_state,
        )

    def get_encoder(self) -> SentenceTransformer:
        if self.encoder is None:
            self.encoder = SentenceTransformer(self.model_name)
        return self.encoder

    def extract_embeddings(self, texts, batch_size: int = 32):
        encoder = self.get_encoder()
        texts_list = list(texts)
        return encoder.encode(
            texts_list,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

    def fit(self, texts, labels):
        embeddings = self.extract_embeddings(texts)
        self.classifier.fit(embeddings, labels)
        self.classes_ = self.classifier.classes_
        return self

    def predict(self, texts):
        embeddings = self.extract_embeddings(texts)
        return self.classifier.predict(embeddings)

    def predict_proba(self, texts):
        embeddings = self.extract_embeddings(texts)
        return self.classifier.predict_proba(embeddings)
