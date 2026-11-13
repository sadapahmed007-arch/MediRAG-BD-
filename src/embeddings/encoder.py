"""Sentence embedding encoder using multilingual sentence-transformers."""
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class SentenceEncoder:
    """Encode text into dense embeddings using a multilingual model."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str], batch_size: int = 64,
              show_progress: bool = True, normalize: bool = True) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        embeddings = self.model.encode(
            texts, batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )
        return embeddings

    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encode a single text."""
        return self.model.encode(
            [text], normalize_embeddings=normalize, convert_to_numpy=True
        )[0]
