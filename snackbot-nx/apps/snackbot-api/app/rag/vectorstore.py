from __future__ import annotations

import logging
import os
import time
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI


COLLECTION_NAME = "snackbot_products"

# Reuse the same Chroma client/collection per persist_dir so we don't reopen the DB on every request.
_chroma_collection_cache: dict[str, Any] = {}

# Cache for query embeddings (same question + model + dimensions → skip API call). Max 200 entries.
_embed_query_cache: dict[tuple[str, str, int | None], list[float]] = {}
_embed_query_cache_max = 200


def _openai_embedder(client: OpenAI, model: str, dimensions: int | None = None):
    def embed(texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        kwargs: dict[str, Any] = {"model": model, "input": texts}
        if dimensions is not None:
            kwargs["dimensions"] = dimensions
        res = client.embeddings.create(**kwargs)
        return [d.embedding for d in res.data]

    return embed


def get_chroma_collection(*, persist_dir: str):
    """
    Persistent local Chroma collection. Cached per persist_dir so the DB is not reopened on every request.
    """
    key = os.path.abspath(os.path.normpath(persist_dir))
    if key in _chroma_collection_cache:
        return _chroma_collection_cache[key]
    chroma_client = chromadb.PersistentClient(
        path=persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    col = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    _chroma_collection_cache[key] = col
    return col


def upsert_documents(
    *,
    persist_dir: str,
    openai_api_key: str,
    embed_model: str,
    embed_dimensions: int | None = None,
    ids: list[str],
    texts: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    if not ids:
        return

    key = os.path.abspath(os.path.normpath(persist_dir))
    if embed_dimensions is not None:
        # Chroma collections have a fixed dimension; replace collection so new dimension is used
        _chroma_collection_cache.pop(key, None)
        chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        col = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
        _chroma_collection_cache[key] = col

    client = OpenAI(api_key=openai_api_key)
    embed = _openai_embedder(client, embed_model, dimensions=embed_dimensions)
    embeddings = embed(texts)

    col = get_chroma_collection(persist_dir=persist_dir)
    col.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)


def query(
    *,
    persist_dir: str,
    openai_api_key: str,
    embed_model: str,
    embed_dimensions: int | None = None,
    q: str,
    k: int = 6,
    product_filter: str | None = None,
) -> dict:
    log = logging.getLogger(__name__)
    cache_key = (q.strip(), embed_model, embed_dimensions)
    if cache_key in _embed_query_cache:
        q_emb = _embed_query_cache[cache_key]
        log.warning("TIMING retrieval_embed: 0.000s (cached)")
    else:
        client = OpenAI(api_key=openai_api_key)
        embed = _openai_embedder(client, embed_model, dimensions=embed_dimensions)
        t0 = time.perf_counter()
        q_emb = embed([q])[0]
        log.warning(f"TIMING retrieval_embed: {time.perf_counter() - t0:.3f}s")
        if len(_embed_query_cache) >= _embed_query_cache_max:
            _embed_query_cache.pop(next(iter(_embed_query_cache)))
        _embed_query_cache[cache_key] = q_emb

    t0 = time.perf_counter()
    col = get_chroma_collection(persist_dir=persist_dir)
    log.warning(f"TIMING retrieval_chroma_load: {time.perf_counter() - t0:.3f}s")
    log.debug("Chroma collection count: %s", col.count())

    where_clause = None
    if product_filter:
        where_clause = {"product": product_filter}
        log.debug("Filtering by product: %s", product_filter)

    t0 = time.perf_counter()
    result = col.query(
        query_embeddings=[q_emb],
        n_results=k,
        where=where_clause,
        include=["documents", "metadatas", "distances"],
    )
    log.warning(f"TIMING retrieval_chroma: {time.perf_counter() - t0:.3f}s")
    return result

