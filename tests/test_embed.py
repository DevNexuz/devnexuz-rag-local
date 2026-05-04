"""Tests para el módulo de embeddings."""

import pytest
from rag.embed import Embedder


@pytest.fixture(scope="module")
def embedder():
    """Una sola instancia por módulo — el modelo carga una vez."""
    return Embedder()


def test_embed_one_returns_list(embedder):
    vector = embedder.embed_one("Texto de prueba.")
    assert isinstance(vector, list)


def test_embed_one_correct_dimension(embedder):
    vector = embedder.embed_one("Texto de prueba.")
    assert len(vector) == 384


def test_embed_one_values_are_floats(embedder):
    vector = embedder.embed_one("Texto de prueba.")
    assert all(isinstance(v, float) for v in vector)


def test_embed_batch_returns_one_vector_per_text(embedder):
    texts = ["Primer texto.", "Segundo texto.", "Tercer texto."]
    vectors = embedder.embed(texts)
    assert len(vectors) == len(texts)


def test_embed_batch_all_same_dimension(embedder):
    texts = ["Primer texto.", "Segundo texto.", "Tercer texto."]
    vectors = embedder.embed(texts)
    assert all(len(v) == 384 for v in vectors)


def test_similar_texts_closer_than_different(embedder):
    """Textos semánticamente similares deben tener mayor similitud coseno."""
    import math

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(x ** 2 for x in b))
        return dot / (norm_a * norm_b)

    v_gato    = embedder.embed_one("El gato duerme.")
    v_felino  = embedder.embed_one("El felino descansa.")
    v_economia = embedder.embed_one("La economia mundial crecio.")

    sim_similar  = cosine(v_gato, v_felino)
    sim_diferente = cosine(v_gato, v_economia)

    assert sim_similar > sim_diferente


def test_dimension_property(embedder):
    assert embedder.dimension == 384


def test_lazy_load_model_is_none_before_use():
    """El modelo no debe cargarse hasta la primera llamada."""
    fresh = Embedder()
    assert fresh._model is None
    fresh.embed_one("trigger load")
    assert fresh._model is not None
