"""Dense retrieval using FAISS and sentence embeddings."""
import numpy as np
import faiss
import joblib
from pathlib import Path
from src.embeddings.encoder import SentenceEncoder


class DenseRetriever:
    """Semantic retrieval using FAISS with sentence embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.encoder = SentenceEncoder(model_name)
        self.index = None
        self.documents = None
        self.embeddings = None

    def build_index(self, documents: list[dict], text_field: str = "question") -> None:
        """Build FAISS index from documents."""
        self.documents = documents
        texts = [doc[text_field] for doc in documents]
        print(f"Encoding {len(texts)} documents...")
        self.embeddings = self.encoder.encode(texts, normalize=True)

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine for normalized)
        self.index.add(self.embeddings.astype(np.float32))
        print(f"FAISS index built: {self.index.ntotal} vectors, dim={dim}")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search for most similar documents."""
        query_emb = self.encoder.encode_single(query, normalize=True)
        query_emb = query_emb.reshape(1, -1).astype(np.float32)
        scores, indices = self.index.search(query_emb, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            doc = self.documents[idx].copy()
            doc['similarity_score'] = float(score)
            doc['retrieval_method'] = 'dense'
            results.append(doc)
        return results

    def save(self, index_path: str, docs_path: str, embeddings_path: str) -> None:
        """Save FAISS index and documents."""
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, index_path)
        joblib.dump(self.documents, docs_path)
        np.save(embeddings_path, self.embeddings)

    def load(self, index_path: str, docs_path: str, model_name: str = None) -> "DenseRetriever":
        """Load FAISS index and documents."""
        if model_name:
            self.encoder = SentenceEncoder(model_name)
        self.index = faiss.read_index(index_path)
        self.documents = joblib.load(docs_path)
        return self
