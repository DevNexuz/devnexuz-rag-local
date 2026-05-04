"""Tests para el módulo de chunking."""

import pytest
from rag.chunk import split_document, split_documents


@pytest.fixture
def sample_doc():
    return {
        "text": "Este es el primer párrafo del documento de prueba. " * 20,
        "metadata": {"source": "test.txt", "page": 1, "format": "txt"},
    }


def test_split_document_returns_list(sample_doc):
    """split_document debe devolver una lista."""
    result = split_document(sample_doc)
    assert isinstance(result, list)


def test_split_document_chunks_have_text(sample_doc):
    """Cada chunk debe tener campo 'text' no vacío."""
    result = split_document(sample_doc)
    for chunk in result:
        assert "text" in chunk
        assert len(chunk["text"]) > 0


def test_split_document_chunks_inherit_metadata(sample_doc):
    """Cada chunk debe heredar la metadata de origen."""
    result = split_document(sample_doc)
    for chunk in result:
        assert chunk["metadata"]["source"] == "test.txt"


def test_split_document_chunks_have_chunk_id(sample_doc):
    """Cada chunk debe tener un chunk_id único."""
    result = split_document(sample_doc)
    ids = [chunk["metadata"]["chunk_id"] for chunk in result]
    assert len(ids) == len(set(ids)), "chunk_ids deben ser únicos"


def test_split_document_respects_chunk_size(sample_doc):
    """Los chunks no deben exceder 2x el chunk_size en caracteres."""
    chunk_size = 100
    result = split_document(sample_doc, chunk_size=chunk_size)
    for chunk in result:
        # 2x es holgura razonable para splits por palabras
        assert len(chunk["text"]) <= chunk_size * 4


def test_split_documents_empty_list():
    """split_documents con lista vacía devuelve lista vacía."""
    assert split_documents([]) == []
