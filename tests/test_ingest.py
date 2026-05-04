"""Tests para el módulo de ingesta."""

import pytest
from pathlib import Path
from rag.ingest import load_document, load_directory


@pytest.fixture
def tmp_docs(tmp_path):
    """Crea archivos de prueba temporales en un directorio limpio."""
    (tmp_path / "doc.txt").write_text("Hola mundo desde TXT.", encoding="utf-8")
    (tmp_path / "doc.md").write_text("# Titulo\n\nParrafo de prueba.", encoding="utf-8")
    return tmp_path


# ------------------------------------------------------------------
# Estructura del output
# ------------------------------------------------------------------

def test_loader_txt_returns_text_and_metadata(tmp_docs):
    docs = list(load_document(tmp_docs / "doc.txt"))
    assert len(docs) == 1
    assert "text" in docs[0]
    assert "metadata" in docs[0]


def test_loader_txt_text_not_empty(tmp_docs):
    docs = list(load_document(tmp_docs / "doc.txt"))
    assert docs[0]["text"].strip() != ""


def test_loader_txt_metadata_fields(tmp_docs):
    doc = list(load_document(tmp_docs / "doc.txt"))[0]
    assert doc["metadata"]["format"] == "txt"
    assert doc["metadata"]["page"] == 1
    assert "source" in doc["metadata"]


def test_loader_markdown_extracts_text(tmp_docs):
    docs = list(load_document(tmp_docs / "doc.md"))
    assert len(docs) == 1
    assert "Titulo" in docs[0]["text"]
    assert "Parrafo de prueba" in docs[0]["text"]


def test_loader_markdown_metadata_format(tmp_docs):
    doc = list(load_document(tmp_docs / "doc.md"))[0]
    assert doc["metadata"]["format"] == "markdown"


# ------------------------------------------------------------------
# Casos borde
# ------------------------------------------------------------------

def test_loader_empty_txt_yields_nothing(tmp_path):
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    docs = list(load_document(tmp_path / "empty.txt"))
    assert docs == []


def test_loader_unsupported_format_raises(tmp_path):
    (tmp_path / "file.csv").write_text("a,b,c", encoding="utf-8")
    with pytest.raises(ValueError, match="no soportado"):
        list(load_document(tmp_path / "file.csv"))


# ------------------------------------------------------------------
# load_directory
# ------------------------------------------------------------------

def test_load_directory_finds_all_supported(tmp_docs):
    docs = list(load_directory(tmp_docs))
    formats = {d["metadata"]["format"] for d in docs}
    assert "txt" in formats
    assert "markdown" in formats


def test_load_directory_ignores_unsupported(tmp_docs):
    (tmp_docs / "ignore.csv").write_text("a,b,c", encoding="utf-8")
    docs = list(load_directory(tmp_docs))
    sources = [d["metadata"]["source"] for d in docs]
    assert not any("ignore.csv" in s for s in sources)


def test_load_directory_empty_dir_yields_nothing(tmp_path):
    docs = list(load_directory(tmp_path))
    assert docs == []
