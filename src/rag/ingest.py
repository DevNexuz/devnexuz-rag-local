"""Document loaders — PDF, Markdown, TXT, DOCX."""

from pathlib import Path
from typing import Iterator


def load_document(path: Path) -> Iterator[dict]:
    """
    Carga un documento y yield dicts con {text, metadata}.
    metadata incluye: source, page (si aplica), format.
    """
    suffix = path.suffix.lower()
    loaders = {
        ".pdf": _load_pdf,
        ".md": _load_markdown,
        ".txt": _load_txt,
        ".docx": _load_docx,
    }
    loader = loaders.get(suffix)
    if loader is None:
        raise ValueError(f"Formato no soportado: {suffix}")
    yield from loader(path)


def load_directory(directory: Path) -> Iterator[dict]:
    """Carga todos los documentos soportados en un directorio (recursivo)."""
    supported = {".pdf", ".md", ".txt", ".docx"}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in supported:
            yield from load_document(path)


def _load_pdf(path: Path) -> Iterator[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    source = str(path)

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        yield {
            "text": text,
            "metadata": {
                "source": source,
                "page": page_num,
                "total_pages": len(reader.pages),
                "format": "pdf",
            },
        }


def _load_markdown(path: Path) -> Iterator[dict]:
    from markdown_it import MarkdownIt

    source = str(path)
    raw = path.read_text(encoding="utf-8")

    # Extraer texto plano — los tokens tipo 'inline' contienen el texto
    md = MarkdownIt()
    tokens = md.parse(raw)
    lines = []
    for token in tokens:
        if token.type == "inline" and token.content:
            lines.append(token.content)

    text = "\n".join(lines).strip()
    if not text:
        return

    yield {
        "text": text,
        "metadata": {
            "source": source,
            "page": 1,
            "format": "markdown",
        },
    }


def _load_txt(path: Path) -> Iterator[dict]:
    source = str(path)
    text = path.read_text(encoding="utf-8").strip()

    if not text:
        return

    yield {
        "text": text,
        "metadata": {
            "source": source,
            "page": 1,
            "format": "txt",
        },
    }


def _load_docx(path: Path) -> Iterator[dict]:
    from docx import Document

    source = str(path)
    doc = Document(str(path))

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)

    if not text:
        return

    yield {
        "text": text,
        "metadata": {
            "source": source,
            "page": 1,
            "format": "docx",
        },
    }
