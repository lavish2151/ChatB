from __future__ import annotations

import os
from dataclasses import dataclass


def _getenv(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def _parse_embed_dimensions(raw: str | None) -> int | None:
    if not raw or not raw.strip():
        return None
    try:
        n = int(raw.strip())
        if n <= 0:
            return None
        return n
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_chat_model: str
    openai_embed_model: str
    openai_embed_dimensions: int | None  # None = model default (1536). Use 512 for faster/smaller; requires re-ingest.
    chroma_persist_dir: str
    gdocs_published_urls: list[str]
    allowed_origins: list[str]
    port: int


def load_settings() -> Settings:
    # Comma-separated URLs
    raw_urls = os.getenv("GDOCS_PUBLISHED_URLS", "").strip()
    urls = [u.strip() for u in raw_urls.split(",") if u.strip()]

    raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()] if raw_origins else ["*"]

    return Settings(
        openai_api_key=_getenv("OPENAI_API_KEY"),
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        openai_embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        openai_embed_dimensions=_parse_embed_dimensions(os.getenv("OPENAI_EMBED_DIMENSIONS")),
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", os.path.join(".", "data", "chroma")),
        gdocs_published_urls=urls,
        allowed_origins=origins,
        port=int(os.getenv("PORT", "5000")),
    )

