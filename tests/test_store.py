"""Tests para el vector store ChromaStore."""

import pytest
from rag.store import ChromaStore


@pytest.fixture
def store(tmp_path):
    """ChromaStore en directorio temporal — se elimina al terminar el test."""
    return ChromaStore(persist_dir=str(tmp_path / "test_chroma"), collection="test")


def _make_chunks(n: int) -> list:
    return [
        {
            "text": f"Texto del chunk número {i}.",
            "metadata": {
                "source": "doc.txt",
                "page": 1,
                "format": "txt",
                "chunk_id": f"chunk-{i:03d}",
                "chunk_index": i,
            },
        }
        for i in range(n)
    ]


def _make_vectors(n: int, dim: int = 8) -> list:
    """Vectores sintéticos — evita cargar sentence-transformers en estos tests."""
    import math
    vectors = []
    for i in range(n):
        angle = (i / max(n, 1)) * 2 * math.pi
        base = [math.cos(angle + j * 0.5) for j in range(dim)]
        norm = math.sqrt(sum(v ** 2 for v in base))
        vectors.append([v / norm for v in base])
    return vectors


# ------------------------------------------------------------------
# count y estado inicial
# ------------------------------------------------------------------

def test_store_starts_empty(store):
    assert store.count() == 0


# ------------------------------------------------------------------
# add
# ------------------------------------------------------------------

def test_add_increments_count(store):
    chunks = _make_chunks(3)
    vectors = _make_vectors(3)
    store.add(chunks, vectors)
    assert store.count() == 3


def test_add_empty_list_does_nothing(store):
    store.add([], [])
    assert store.count() == 0


def test_add_upsert_no_duplicates(store):
    """Insertar los mismos chunk_ids dos veces no duplica registros."""
    chunks = _make_chunks(3)
    vectors = _make_vectors(3)
    store.add(chunks, vectors)
    store.add(chunks, vectors)
    assert store.count() == 3


# ------------------------------------------------------------------
# search
# ------------------------------------------------------------------

def test_search_empty_store_returns_empty(store):
    query = _make_vectors(1)[0]
    results = store.search(query, k=5)
    assert results == []


def test_search_returns_k_results(store):
    chunks = _make_chunks(10)
    vectors = _make_vectors(10)
    store.add(chunks, vectors)
    results = store.search(vectors[0], k=3)
    assert len(results) == 3


def test_search_results_have_required_fields(store):
    chunks = _make_chunks(5)
    vectors = _make_vectors(5)
    store.add(chunks, vectors)
    results = store.search(vectors[0], k=1)
    assert "text" in results[0]
    assert "metadata" in results[0]
    assert "score" in results[0]


def test_search_score_between_0_and_1(store):
    chunks = _make_chunks(5)
    vectors = _make_vectors(5)
    store.add(chunks, vectors)
    results = store.search(vectors[0], k=5)
    for r in results:
        assert 0.0 <= r["score"] <= 1.0


def test_search_k_larger_than_store_returns_all(store):
    """Si k > total de chunks, devuelve todos sin error."""
    chunks = _make_chunks(3)
    vectors = _make_vectors(3)
    store.add(chunks, vectors)
    results = store.search(vectors[0], k=100)
    assert len(results) == 3
