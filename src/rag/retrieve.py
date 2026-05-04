"""Retrieval — similarity search y MMR sobre el vector store."""

import math
from typing import List

from rag.embed import Embedder
from rag.store import ChromaStore


def retrieve(
    query: str,
    embedder: Embedder,
    store: ChromaStore,
    k: int = 5,
) -> List[dict]:
    """
    Convierte query en embedding y recupera los k chunks más relevantes.
    Devuelve lista de chunks con su score de similitud.
    """
    query_vector = embedder.embed_one(query)
    return store.search(query_vector, k=k)


def retrieve_mmr(
    query: str,
    embedder: Embedder,
    store: ChromaStore,
    k: int = 5,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
) -> List[dict]:
    """
    Maximal Marginal Relevance: balancea relevancia y diversidad.
    fetch_k: cuántos candidatos traer antes de re-rankear.
    lambda_mult: 1.0 = solo relevancia, 0.0 = solo diversidad.
    """
    query_vector = embedder.embed_one(query)

    # Traer candidatos con sus embeddings para calcular diversidad entre ellos
    candidates = store.search(
        query_vector,
        k=min(fetch_k, store.count()),
        include_embeddings=True,
    )
    if not candidates:
        return []

    selected = []
    remaining = candidates.copy()

    while len(selected) < k and remaining:
        best_idx = None
        best_score = float("-inf")

        for i, candidate in enumerate(remaining):
            relevance = candidate["score"]

            if not selected:
                diversity = 1.0
            else:
                # Penalizar candidatos similares a los ya seleccionados
                max_sim = max(
                    _cosine_similarity(
                        candidate.get("embedding", []),
                        sel.get("embedding", []),
                    )
                    for sel in selected
                )
                diversity = 1.0 - max_sim

            mmr_score = lambda_mult * relevance + (1 - lambda_mult) * diversity

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        best = remaining.pop(best_idx)
        # No exponemos el embedding en el resultado final
        best.pop("embedding", None)
        selected.append(best)

    return selected


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Similitud coseno entre dos vectores. Devuelve 0 si alguno está vacío."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x ** 2 for x in a))
    norm_b = math.sqrt(sum(x ** 2 for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
