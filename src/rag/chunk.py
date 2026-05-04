"""Text splitting — recursive character splitter con metadata."""

import hashlib
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

# chunk_size en chars: 512 tokens * ~4 chars/token es una aproximación
# conservadora que funciona bien para español e inglés
_CHARS_PER_TOKEN = 4


def split_document(doc: dict, chunk_size: int = 512, overlap: int = 64) -> List[dict]:
    """
    Recibe un dict {text, metadata} y devuelve lista de chunks.
    Cada chunk: {text, metadata: {source, page, chunk_id, chunk_index, ...}}

    chunk_size: tamaño aproximado en tokens por chunk
    overlap: tokens de solapamiento entre chunks consecutivos
    """
    text = doc["text"]
    base_metadata = doc["metadata"]

    chunk_size_chars = chunk_size * _CHARS_PER_TOKEN
    overlap_chars = overlap * _CHARS_PER_TOKEN

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=overlap_chars,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)

    chunks = []
    for index, chunk_text in enumerate(raw_chunks):
        chunk_text = chunk_text.strip()
        if not chunk_text:
            continue

        chunk_id = hashlib.md5(
            f"{base_metadata.get('source', '')}:{index}:{chunk_text[:64]}".encode()
        ).hexdigest()

        chunks.append({
            "text": chunk_text,
            "metadata": {
                **base_metadata,
                "chunk_id": chunk_id,
                "chunk_index": index,
            },
        })

    return chunks


def split_documents(docs: List[dict], chunk_size: int = 512, overlap: int = 64) -> List[dict]:
    """Aplica split_document a una lista de documentos."""
    chunks = []
    for doc in docs:
        chunks.extend(split_document(doc, chunk_size, overlap))
    return chunks
