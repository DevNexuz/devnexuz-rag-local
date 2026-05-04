"""Tests para el módulo de retrieval."""

import math
import pytest
from rag.store import ChromaStore
from rag.retrieve import retrieve, retrieve_mmr, _cosine_similarity


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _unit_vector(angle: float, dim: int = 8) -> list:
    """Vector unitario en dirección 'angle' — reproducible y normalizado."""
    v = [math.cos(angle + j * 0.5) for j in range(dim)]
    norm = math.sqrt(sum(x ** 2 for x in v))
    return [x / norm for x in v]


class FakeEmbedder:
    """Embedder falso — devuelve vectores predefinidos sin cargar el modelo."""

    def __init__(self, vector: list):
        self._vector = vector

    def embed_one(self, text: str) -> list:
        return self._vector

    def embed(self, texts: list) -> list:
        return [self._vector for _ in texts]


@pytest.fixture
def populated_store(tmp_path):
    """Store con 6 chunks y vectores conocidos."""
    store = ChromaStore(persist_dir=str(tmp_path / "chroma"), collection="test")
    chunks = [
        {
            "text": f"Chunk {i}",
            "metadata": {
                "source": "doc.txt",
                "page": 1,
                "format": "txt",
                "chunk_id": f"id-{i}",
                "chunk_index": i,
            },
        }
        for i in range(6)
    ]
    vectors = [_unit_vector(i * 0.8) for i in range(6)]
    store.add(chunks, vectors)
    return store, vectors


# ------------------------------------------------------------------
# retrieve
# ------------------------------------------------------------------

def test_retrieve_returns_list(populated_store):
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[0])
    results = retrieve("query", embedder, store, k=3)
    assert isinstance(results, list)


def test_retrieve_returns_k_results(populated_store):
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[0])
    results = retrieve("query", embedder, store, k=3)
    assert len(results) == 3


def test_retrieve_results_have_score(populated_store):
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[0])
    results = retrieve("query", embedder, store, k=3)
    assert all("score" in r for r in results)


def test_retrieve_most_similar_is_first(populated_store):
    """El chunk con vector idéntico al query debe tener el score más alto."""
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[2])
    results = retrieve("query", embedder, store, k=6)
    assert results[0]["score"] >= results[1]["score"]


def test_retrieve_empty_store_returns_empty(tmp_path):
    store = ChromaStore(persist_dir=str(tmp_path / "empty"), collection="test")
    embedder = FakeEmbedder(_unit_vector(0.0))
    results = retrieve("query", embedder, store, k=5)
    assert results == []


# ------------------------------------------------------------------
# retrieve_mmr
# ------------------------------------------------------------------

def test_retrieve_mmr_returns_k_results(populated_store):
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[0])
    results = retrieve_mmr("query", embedder, store, k=3, fetch_k=6)
    assert len(results) == 3


def test_retrieve_mmr_no_embeddings_in_output(populated_store):
    """Los embeddings son internos — no deben aparecer en el resultado final."""
    store, vectors = populated_store
    embedder = FakeEmbedder(vectors[0])
    results = retrieve_mmr("query", embedder, store, k=3, fetch_k=6)
    assert all("embedding" not in r for r in results)


def test_retrieve_mmr_empty_store_returns_empty(tmp_path):
    store = ChromaStore(persist_dir=str(tmp_path / "empty"), collection="test")
    embedder = FakeEmbedder(_unit_vector(0.0))
    results = retrieve_mmr("query", embedder, store, k=5)
    assert results == []


# ------------------------------------------------------------------
# _cosine_similarity
# ------------------------------------------------------------------

def test_cosine_similarity_identical_vectors():
    v = _unit_vector(0.5)
    assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_similarity_empty_returns_zero():
    assert _cosine_similarity([], [1.0, 0.0]) == 0.0


def test_cosine_similarity_between_0_and_1():
    a = _unit_vector(0.0)
    b = _unit_vector(1.5)
    sim = _cosine_similarity(a, b)
    assert 0.0 <= sim <= 1.0
