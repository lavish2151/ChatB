from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI


COLLECTION_NAME = "snackbot_products"


def _openai_embedder(client: OpenAI, model: str):
    def embed(texts: list[str]) -> list[list[float]]:
        # OpenAI embeddings API supports batching
        res = client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in res.data]

    return embed


def get_chroma_collection(*, persist_dir: str):
    """
    Persistent local Chroma collection.
    """
    chroma_client = chromadb.PersistentClient(
        path=persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def upsert_documents(
    *,
    persist_dir: str,
    openai_api_key: str,
    embed_model: str,
    ids: list[str],
    texts: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    if not ids:
        return

    client = OpenAI(api_key=openai_api_key)
    embed = _openai_embedder(client, embed_model)
    embeddings = embed(texts)

    col = get_chroma_collection(persist_dir=persist_dir)
    col.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)


def query(
    *,
    persist_dir: str,
    openai_api_key: str,
    embed_model: str,
    q: str,
    k: int = 6,
) -> dict:
    client = OpenAI(api_key=openai_api_key)
    embed = _openai_embedder(client, embed_model)
    print("🔎 Production collection count:", col.count())
    q_emb = embed([q])[0]

    col = get_chroma_collection(persist_dir=persist_dir)
    # Note: Chroma always returns `ids` in the response; `include` is only for
    # additional payload fields. Passing "ids" here raises a ValueError.
    return col.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances"])

