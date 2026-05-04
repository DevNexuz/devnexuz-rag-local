"""Vector store — interfaz + implementación Chroma."""

from typing import List, Protocol


class VectorStore(Protocol):
    """Interfaz mínima para un vector store."""

    def add(self, chunks: List[dict], embeddings: List[List[float]]) -> None:
        """Añade chunks con sus embeddings."""
        ...

    def search(self, query_embedding: List[float], k: int = 5) -> List[dict]:
        """Devuelve los k chunks más cercanos al query."""
        ...

    def count(self) -> int:
        """Número de chunks almacenados."""
        ...


class ChromaStore:
    """
    Vector store persistente usando ChromaDB.
    persist_dir: carpeta donde Chroma guarda los datos en disco.
    """

    def __init__(self, persist_dir: str = "chroma_db", collection: str = "rag"):
        self.persist_dir = persist_dir
        self.collection_name = collection
        self._client = None
        self._collection = None

    def _connect(self):
        """Crea cliente y colección — lazy, solo cuando se necesita."""
        import chromadb

        self._client = chromadb.PersistentClient(path=self.persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def _col(self):
        """Acceso a la colección con conexión garantizada."""
        if self._collection is None:
            self._connect()
        return self._collection

    def add(self, chunks: List[dict], embeddings: List[List[float]]) -> None:
        """Añade chunks con sus embeddings. Ignora duplicados por chunk_id."""
        if not chunks:
            return

        ids = [c["metadata"]["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        self._col.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: List[float],
        k: int = 5,
        include_embeddings: bool = False,
    ) -> List[dict]:
        """
        Devuelve los k chunks más cercanos al query.
        Cada resultado: {text, metadata, score}
        score: similitud coseno entre 0 y 1 (mayor = más relevante).
        include_embeddings: si True, añade 'embedding' a cada resultado (para MMR).
        """
        total = self.count()
        if total == 0:
            return []

        k = min(k, total)
        include = ["documents", "metadatas", "distances"]
        if include_embeddings:
            include.append("embeddings")

        results = self._col.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=include,
        )

        chunks = []
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        embeddings = results.get("embeddings", [[]])[0] if include_embeddings else []

        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            score = 1 - (dist / 2)
            chunk = {
                "text": doc,
                "metadata": meta,
                "score": round(score, 4),
            }
            if include_embeddings and embeddings is not None:
                chunk["embedding"] = list(embeddings[i])
            chunks.append(chunk)

        return chunks

    def count(self) -> int:
        """Número de chunks almacenados."""
        return self._col.count()

    def reset(self) -> None:
        """Elimina todos los chunks de la colección. Útil para tests."""
        self._client.delete_collection(self.collection_name)
        self._collection = None
