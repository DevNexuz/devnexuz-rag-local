"""Tests para el módulo de Q&A — no requieren Ollama."""

import pytest
from rag.qa import build_context, answer_extractive, answer, PROMPT_TEMPLATE


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "RAG combina recuperación de documentos con generación de texto.",
            "metadata": {"source": "data/paper.pdf", "page": 1, "format": "pdf"},
            "score": 0.91,
        },
        {
            "text": "El retrieval-augmented generation reduce alucinaciones.",
            "metadata": {"source": "data/paper.pdf", "page": 4, "format": "pdf"},
            "score": 0.84,
        },
        {
            "text": "Los modelos de lenguaje pueden generar información falsa.",
            "metadata": {"source": "data/notes.txt", "page": 1, "format": "txt"},
            "score": 0.76,
        },
    ]


# ------------------------------------------------------------------
# build_context
# ------------------------------------------------------------------

def test_build_context_returns_string(sample_chunks):
    result = build_context(sample_chunks)
    assert isinstance(result, str)


def test_build_context_contains_chunk_text(sample_chunks):
    result = build_context(sample_chunks)
    assert "RAG combina" in result
    assert "reduce alucinaciones" in result


def test_build_context_contains_citations(sample_chunks):
    result = build_context(sample_chunks)
    assert "paper.pdf:1" in result
    assert "paper.pdf:4" in result
    assert "notes.txt:1" in result


def test_build_context_uses_filename_not_full_path(sample_chunks):
    result = build_context(sample_chunks)
    assert "data/paper.pdf" not in result
    assert "paper.pdf" in result


def test_build_context_empty_chunks():
    assert build_context([]) == ""


# ------------------------------------------------------------------
# answer_extractive
# ------------------------------------------------------------------

def test_answer_extractive_returns_dict(sample_chunks):
    result = answer_extractive(sample_chunks, "¿Qué es RAG?")
    assert isinstance(result, dict)


def test_answer_extractive_has_required_fields(sample_chunks):
    result = answer_extractive(sample_chunks, "¿Qué es RAG?")
    assert "answer" in result
    assert "sources" in result
    assert "mode" in result


def test_answer_extractive_mode_is_extractive(sample_chunks):
    result = answer_extractive(sample_chunks, "¿Qué es RAG?")
    assert result["mode"] == "extractive"


def test_answer_extractive_sources_are_unique(sample_chunks):
    result = answer_extractive(sample_chunks, "¿Qué es RAG?")
    assert len(result["sources"]) == len(set(result["sources"]))


def test_answer_extractive_empty_chunks():
    result = answer_extractive([], "¿Qué es RAG?")
    assert "No encontré información" in result["answer"]
    assert result["sources"] == []


# ------------------------------------------------------------------
# answer — entry point con fallback
# ------------------------------------------------------------------

def test_answer_uses_extractive_when_use_ollama_false(sample_chunks):
    result = answer(sample_chunks, "¿Qué es RAG?", use_ollama=False)
    assert result["mode"] == "extractive"


def test_answer_falls_back_to_extractive_when_ollama_unavailable(sample_chunks):
    """Si Ollama no está corriendo, debe caer silenciosamente a extractivo."""
    result = answer(sample_chunks, "¿Qué es RAG?", use_ollama=True, model="modelo-inexistente")
    assert result["mode"] == "extractive"


def test_answer_returns_consistent_structure(sample_chunks):
    result = answer(sample_chunks, "¿Qué es RAG?", use_ollama=False)
    assert all(k in result for k in ["answer", "sources", "mode"])


# ------------------------------------------------------------------
# PROMPT_TEMPLATE
# ------------------------------------------------------------------

def test_prompt_template_has_placeholders():
    assert "{context}" in PROMPT_TEMPLATE
    assert "{question}" in PROMPT_TEMPLATE


def test_prompt_template_renders_correctly():
    rendered = PROMPT_TEMPLATE.format(context="contexto aquí", question="¿pregunta?")
    assert "contexto aquí" in rendered
    assert "¿pregunta?" in rendered
