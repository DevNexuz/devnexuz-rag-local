"""Embeddings — wrapper sobre sentence-transformers."""

from typing import List

DEFAULT_MODEL = "all-MiniLM-L6-v2"


class Embedder:
    """
    Genera embeddings con sentence-transformers.
    Lazy-load: el modelo se descarga la primera vez que se usa.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None

    def _load(self):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Devuelve lista de vectores, uno por texto."""
        if self._model is None:
            self._load()
        vectors = self._model.encode(texts, convert_to_numpy=True)
        return vectors.tolist()

    def embed_one(self, text: str) -> List[float]:
        """Convierte un solo texto a vector — útil para queries."""
        return self.embed([text])[0]

    @property
    def dimension(self) -> int:
        """Dimensión del vector de salida (384 para MiniLM)."""
        if self._model is None:
            self._load()
        return self._model.get_embedding_dimension()
