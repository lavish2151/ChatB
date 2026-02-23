from __future__ import annotations

import os
import sys
import re
from typing import Iterable

from dotenv import load_dotenv

# Add parent directory to path so 'app' module can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.dirname(script_dir)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app.config import load_settings
from app.rag.chunking import chunk_text
from app.rag.gdocs import fetch_published_doc
from app.rag.vectorstore import upsert_documents


PRODUCTS = [
    "Lays",
    "Kurkure",
    "Cadbury Dairy Milk Silk",
    "Maggi",
    "Nescafe Classic",
    "Parle G",
]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _split_doc_by_products(doc_text: str, products: Iterable[str]) -> dict[str, str]:
    """
    Split a single doc into sections by product headings.

    This expects the doc to contain the product names as standalone headings/lines, like:
      Lays
      ...
      Cadbury Dairy Milk Silk
      ...
    """
    text = doc_text or ""
    parts: dict[str, str] = {}

    # Normalize whitespace a bit while keeping newlines for heading detection.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Build a case-insensitive regex that matches any product heading on its own line.
    # Also try to match headings that might have extra formatting
    escaped = [re.escape(p) for p in products]
    # Match product name at start of line, optionally followed by whitespace and end of line
    # Case-insensitive matching - also allow partial matches
    headings_re = re.compile(rf"(?mi)^(?:{'|'.join(escaped)})\s*$")
    
    # Also try to find headings that contain product names (more flexible)
    partial_headings_re = re.compile(rf"(?mi)^.*(?:{'|'.join(escaped)}).*$")

    matches = list(headings_re.finditer(text))
    
    # If no exact matches, try partial matches
    if not matches:
        print("No exact product heading matches found, trying partial matches...")
        partial_matches = list(partial_headings_re.finditer(text))
        if partial_matches:
            print(f"Found {len(partial_matches)} partial matches, using those")
            matches = partial_matches
    
    if not matches:
        # Debug: print first 1000 chars to help diagnose
        print(f"\n{'='*80}")
        print("WARNING: Could not find product headings!")
        print(f"{'='*80}")
        print(f"Looking for these headings (case-insensitive): {list(products)}")
        print(f"\nFirst 1000 chars of document:")
        print("-"*80)
        print(text[:1000])
        print("-"*80)
        print("\nIf your Google Doc has different product names, update the PRODUCTS list in ingest_gdocs.py")
        print("="*80)
        return parts

    print(f"Found {len(matches)} product headings in document")
    
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group(0).strip()
        
        # Normalize heading to match one of our product names (case-insensitive)
        # Try exact match first, then partial match
        normalized_heading = None
        for product in products:
            if heading.lower() == product.lower():
                normalized_heading = product
                break
        
        # If no exact match, try partial match
        if not normalized_heading:
            for product in products:
                if product.lower() in heading.lower() or heading.lower() in product.lower():
                    normalized_heading = product
                    break
        
        if not normalized_heading:
            normalized_heading = heading  # Use as-is if no match

        section = text[start:end].strip()
        if section:
            parts[normalized_heading] = section

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
                "\n" + "="*80 + "\n"
                "WARNING: Could not find product headings in the doc.\n"
                "The script is looking for these exact headings (case-insensitive):\n"
            )
            for p in PRODUCTS:
                print(f"  - {p}")
            print(
                "\nMake sure each product name appears as a heading on its own line.\n"
                "First 1000 characters of the document:\n"
                + "-"*80 + "\n"
                + doc.text[:1000]
                + "\n" + "-"*80 + "\n"
                "Ingesting the entire doc as a single source (not split by products).\n"
                + "="*80 + "\n"
            )
            sections = {doc.title: doc.text}

        for product, section_text in sections.items():
            chunks = chunk_text(section_text)
            for c_idx, c in enumerate(chunks):
                cid = f"{_slug(product)}-{c_idx}"
                all_ids.append(cid)
                all_texts.append(c)
                all_metas.append({"url": doc.url, "title": doc.title, "product": product})

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

    upsert_documents(
        persist_dir=s.chroma_persist_dir,
        openai_api_key=s.openai_api_key,
        embed_model=s.openai_embed_model,
        embed_dimensions=s.openai_embed_dimensions,
        ids=all_ids,
        texts=all_texts,
        metadatas=all_metas,
    )


if __name__ == "__main__":
    main()

