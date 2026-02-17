from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    metadata: dict


def chunk_text(text: str, *, max_chars: int = 900, overlap_chars: int = 120) -> list[str]:
    """
    Lightweight chunker that keeps chunks under max_chars.
    Uses a sliding window to provide overlap for retrieval robustness.
    """
    t = " ".join(text.split())
    if not t:
        return []

    chunks: list[str] = []
    start = 0
    n = len(t)
    while start < n:
        end = min(n, start + max_chars)
        chunk = t[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(0, end - overlap_chars)
        if start == end:
            start = end + 1
    return chunks

