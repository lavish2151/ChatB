from __future__ import annotations

import os
import re
from typing import Iterable

from dotenv import load_dotenv

from app.config import load_settings
from app.rag.chunking import chunk_text
from app.rag.gdocs import fetch_published_doc
from app.rag.vectorstore import upsert_documents


PRODUCTS = [
    "Masala Parle-G",
    "Cadbury Dairy Milk Silk",
    "Nimbu Masala Soda",
    "Peanut Chikki",
    "Filter Coffee Cold Brew",
    "Aam Papad",
]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _split_doc_by_products(doc_text: str, products: Iterable[str]) -> dict[str, str]:
    """
    Split a single doc into sections by product headings.

    This expects the doc to contain the product names as standalone headings/lines, like:
      Masala Parle-G
      ...
      Cadbury Dairy Milk Silk
      ...
    """
    text = doc_text or ""
    parts: dict[str, str] = {}

    # Normalize whitespace a bit while keeping newlines for heading detection.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Build a regex that matches any product heading on its own line.
    escaped = [re.escape(p) for p in products]
    headings_re = re.compile(rf"(?m)^(?:{'|'.join(escaped)})\s*$")

    matches = list(headings_re.finditer(text))
    if not matches:
        return parts

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group(0).strip()
        section = text[start:end].strip()
        if section:
            parts[heading] = section

    return parts


def main() -> None:
    # Load env from Nx workspace root if present
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), "..", "..", ".env"), override=False)
    load_dotenv(override=False)

    s = load_settings()
    if not s.gdocs_published_urls:
        raise SystemExit(
            "GDOCS_PUBLISHED_URLS is empty. Publish your Google Docs to web and set URLs (comma-separated) in .env."
        )

    all_ids: list[str] = []
    all_texts: list[str] = []
    all_metas: list[dict] = []

    # If you provided ONE doc URL, we treat it as a single "master" doc and
    # split it into per-product sections by product headings.
    if len(s.gdocs_published_urls) == 1:
        url = s.gdocs_published_urls[0]
        doc = fetch_published_doc(url)
        sections = _split_doc_by_products(doc.text, PRODUCTS)

        if not sections:
            print(
                "Warning: Could not find product headings in the doc. "
                "Ingesting the entire doc as a single source."
            )
            sections = {doc.title: doc.text}

        for product, section_text in sections.items():
            chunks = chunk_text(section_text)
            for c_idx, c in enumerate(chunks):
                cid = f"{_slug(product)}-{c_idx}"
                all_ids.append(cid)
                all_texts.append(c)
                all_metas.append({"url": doc.url, "title": doc.title, "product": product})
            print(f"Ingested {len(chunks)} chunks for: {product}")

    # Otherwise, assume one doc per product, mapped by order.
    else:
        for idx, url in enumerate(s.gdocs_published_urls):
            doc = fetch_published_doc(url)
            product = PRODUCTS[idx] if idx < len(PRODUCTS) else doc.title
            chunks = chunk_text(doc.text)
            for c_idx, c in enumerate(chunks):
                cid = f"{_slug(product)}-{c_idx}"
                all_ids.append(cid)
                all_texts.append(c)
                all_metas.append({"url": doc.url, "title": doc.title, "product": product})

            print(f"Ingested {len(chunks)} chunks for: {product}")

    upsert_documents(
        persist_dir=s.chroma_persist_dir,
        openai_api_key=s.openai_api_key,
        embed_model=s.openai_embed_model,
        ids=all_ids,
        texts=all_texts,
        metadatas=all_metas,
    )
    print(f"Upserted total chunks: {len(all_ids)}")


if __name__ == "__main__":
    main()

