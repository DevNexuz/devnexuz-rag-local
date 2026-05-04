"""Q&A — prompt template + cliente Ollama + extracción de citas."""

from pathlib import Path
from typing import List

PROMPT_TEMPLATE = """\
Eres un asistente que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.
Si la respuesta no está en el contexto, di exactamente: "No encontré información sobre eso en los documentos."
Cita siempre la fuente usando el formato [fuente:página].

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:
"""

DEFAULT_MODEL = "llama3.2:3b"


def build_context(chunks: List[dict]) -> str:
    """
    Formatea los chunks como bloque de texto para el prompt.
    Cada chunk aparece con su cita [fuente:página] encabezando el fragmento.
    """
    parts = []
    for chunk in chunks:
        meta = chunk["metadata"]
        source = Path(meta.get("source", "desconocido")).name
        page = meta.get("page", 1)
        parts.append(f"[{source}:{page}]\n{chunk['text']}")
    return "\n\n".join(parts)


def _extract_sources(chunks: List[dict]) -> List[str]:
    """Devuelve lista de citas únicas ordenadas: ['doc.pdf:1', 'doc.pdf:3', ...]"""
    seen = set()
    sources = []
    for chunk in chunks:
        meta = chunk["metadata"]
        source = Path(meta.get("source", "desconocido")).name
        page = meta.get("page", 1)
        citation = f"{source}:{page}"
        if citation not in seen:
            seen.add(citation)
            sources.append(citation)
    return sources


def answer_extractive(chunks: List[dict], question: str) -> dict:
    """
    Modo sin LLM: devuelve los chunks como respuesta directa.
    Útil como fallback cuando Ollama no está disponible.
    """
    if not chunks:
        return {
            "answer": "No encontré información sobre eso en los documentos.",
            "sources": [],
            "mode": "extractive",
        }

    lines = []
    for chunk in chunks:
        meta = chunk["metadata"]
        source = Path(meta.get("source", "desconocido")).name
        page = meta.get("page", 1)
        score = chunk.get("score", 0)
        lines.append(f"[{source}:{page}] (score: {score:.2f})\n{chunk['text']}")

    return {
        "answer": "\n\n".join(lines),
        "sources": _extract_sources(chunks),
        "mode": "extractive",
    }


def answer_with_ollama(
    chunks: List[dict],
    question: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Llama a Ollama con el contexto y la pregunta.
    Lanza OllamaUnavailableError si Ollama no responde.
    """
    import ollama

    context = build_context(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    answer_text = response["message"]["content"].strip()

    return {
        "answer": answer_text,
        "sources": _extract_sources(chunks),
        "mode": "generative",
        "model": model,
    }


def answer(
    chunks: List[dict],
    question: str,
    use_ollama: bool = True,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Entry point unificado.
    Intenta Ollama si use_ollama=True, cae a extractivo si falla o no está disponible.
    """
    if not use_ollama:
        return answer_extractive(chunks, question)

    try:
        return answer_with_ollama(chunks, question, model)
    except Exception:
        return answer_extractive(chunks, question)
