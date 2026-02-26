from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from openai import OpenAI

from .vectorstore import query as vs_query

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RagResult:
    answer: str
    sources: list[dict]
    answer_lines: tuple[str, ...] = field(default_factory=tuple)
    intent: str | None = None
    product: str | None = None


# Product names for query rewriting context
KNOWN_PRODUCTS = [
    "Lays",
    "Kurkure",
    "Cadbury Dairy Milk Silk",
    "Maggi",
    "Nescafe Classic",
    "Parle G",
]

# In-memory cache for rewritten queries to avoid repeat LLM calls. Key = (question_lower, context_key), max 150.
_rewrite_cache: dict[tuple[str, str], str] = {}
_rewrite_cache_max = 150

# Doc vocabulary: if the query already contains these (case-insensitive), we can skip LLM rewrite for speed
_DOC_TERMS = (
    "pack size", "price", "cost", "availability", "in stock", "ingredients",
    "nutritional", "allergen", "shelf", "storage", "price range", "stock availability",
)

# Product name aliases for flexible matching (shortened/case-insensitive names users might use)
PRODUCT_ALIASES = {
    "lays": "Lays",
    "kurkure": "Kurkure",
    "maggi": "Maggi",
    "parle g": "Parle G",
    "parle-g": "Parle G",
    "dairy milk": "Cadbury Dairy Milk Silk",
    "cadbury": "Cadbury Dairy Milk Silk",
    "cadbury silk": "Cadbury Dairy Milk Silk",
    "cadbury dairy milk silk": "Cadbury Dairy Milk Silk",
    "nescafe": "Nescafe Classic",
    "nescafe classic": "Nescafe Classic",
    "classic": "Nescafe Classic",
    "maggi noodles": "Maggi",
}


def _normalize_product_names_in_query(query: str) -> str:
    """
    Replace product aliases and lowercase product names in the query with canonical names
    so retrieval matches chunks that use "Lays", "Kurkure", etc. (e.g. "details of lays" → "details of Lays").
    """
    if not query or not query.strip():
        return query
    text = query
    # Build (pattern, canonical) sorted by length descending so longer aliases match first
    replacements: list[tuple[str, str]] = []
    for alias, canonical in PRODUCT_ALIASES.items():
        replacements.append((alias, canonical))
    for product in KNOWN_PRODUCTS:
        if product.lower() not in {a for a, _ in replacements}:
            replacements.append((product.lower(), product))
    replacements.sort(key=lambda x: -len(x[0]))
    for alias, canonical in replacements:
        # Word-boundary replacement, case-insensitive
        pattern = r"\b" + re.escape(alias) + r"\b"
        text = re.sub(pattern, canonical, text, flags=re.IGNORECASE)
    return text


def _query_needs_rewrite(question: str) -> bool:
    """Skip LLM rewrite when the query already has doc vocabulary or is just a product name (saves latency)."""
    q = question.lower().strip()
    if any(term in q for term in _DOC_TERMS):
        return False
    words = q.split()
    if len(words) <= 2 and any(p.lower() in q for p in KNOWN_PRODUCTS):
        return False  # e.g. "Kurkure" or "Kurkure price"
    return True


def _normalize_product_name(text: str) -> str | None:
    """
    Try to match a product name from text (handles partial/alias names).
    Returns the full product name if found, None otherwise.
    """
    text_lower = text.lower().strip()
    
    # Check exact match first
    for product in KNOWN_PRODUCTS:
        if product.lower() in text_lower or text_lower in product.lower():
            return product
    
    # Check aliases
    for alias, product in PRODUCT_ALIASES.items():
        if alias in text_lower:
            return product
    
    return None


# When user confirms Parle G purchase: short answer + intent for frontend pack picker
PARLE_G_PURCHASE_ANSWER = "Please choose a pack:"
PARLE_G_PURCHASE_LINKS = (
    "[56g](/products/parle-g-56g)\n"
    "[200g](/products/parle-g-200g)\n"
    "[800g](/products/parle-g-800g)"
)
# Product names that get purchase links; others get "unavailable" (scalable for future products)
PURCHASE_ENABLED_PRODUCTS = {"Parle G", "Parle-G"}


def _try_handle_yes_to_buy(question: str, history: list[dict[str, str]] | None) -> RagResult | None:
    """
    If the user is saying Yes to the purchase question, return the correct response
    (Parle G links or "unavailable") without calling RAG/LLM. This avoids the LLM
    answering from retrieved context (e.g. "Lays is out of stock") instead of the rule.
    """
    if not history or len(history) < 2:
        return None
    q = question.strip().lower()
    # Short affirmative replies that mean "yes I want to buy"
    affirmatives = (
        "yes", "yeah", "yep", "sure", "ok", "okay", "i want to buy", "i'll take it",
        "want to buy", "please", "i want it", "give me", "i'll buy", "buy it",
    )
    is_affirmative = q in affirmatives or any(a in q for a in ("yes", "yeah", "sure", "ok", "buy", "i want"))
    if not is_affirmative or len(q) > 80:
        return None
    # Prefer last assistant message (they just asked "Would you like to buy...?")
    last_assistant = None
    for h in reversed(history):
        role = (h.get("role") or "").strip().lower()
        if role == "assistant":
            last_assistant = (h.get("content") or "").strip()
            break
    if not last_assistant or "would you like to buy" not in last_assistant.lower():
        return None
    # Extract product from "Yes, we have X." at the start of that message
    match = re.search(r"(?i)Yes,?\s*we have\s+([^.\n]+)\.", last_assistant)
    product_raw = match.group(1).strip() if match else ""
    product = _normalize_product_name(product_raw) if product_raw else _normalize_product_name(last_assistant)
    if not product:
        return None
    if product == "Parle G":
        answer = PARLE_G_PURCHASE_ANSWER + "\n\n" + PARLE_G_PURCHASE_LINKS
        lines = tuple(s.strip() or "\u00A0" for s in answer.split("\n"))
        return RagResult(answer=answer, sources=[], answer_lines=lines, intent="SHOW_PACK_PICKER", product="parle-g")
    answer = "Purchase options for this product are currently unavailable."
    lines = tuple(s.strip() or "\u00A0" for s in answer.split("\n"))
    return RagResult(answer=answer, sources=[], answer_lines=lines, intent=None, product=None)


def _clean_product_response(text: str) -> str:
    """
    Option 3: If LLM returns one messy line, clean it so each section/bullet is on its own line.
    Matches the expected format: blank line between sections, one bullet per line.
    """
    if not text or "Availability:" not in text:
        return text
    # Sections: put labels on new lines with blank line before (handle both " Availability:" and ". Availability:")
    t = re.sub(r"[.\s]+Availability:\s*", "\n\nAvailability: ", text)
    t = re.sub(r"[.\s]+Price:\s*", "\n\nPrice:\n", t)
    t = re.sub(r"[.\s]+Pack sizes:\s*", "\n\nPack sizes:\n", t)
    # List bullets: " - 30g" or " - 55g – ₹20" each on own line (space-hyphen-space; en-dash in "30g – ₹10" unchanged)
    t = re.sub(r"\s+-\s+", "\n- ", t)
    # Closing line
    t = re.sub(r"\s+Would you like to buy it\?", "\n\nWould you like to buy it?", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+Would you like to buy this product\?\s*\(Yes/No\)", "\n\nWould you like to buy this product? (Yes/No)", t, flags=re.IGNORECASE)
    # Collapse more than 2 newlines to 2
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def rewrite_query_for_rag(
    *,
    client: OpenAI,
    query_model: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """
    Use LLM to normalize the user query for RAG: fix typos, map variations to document vocabulary.
    E.g. "paxcakge sizing", "package dise" -> "pack sizes Available Pack Sizes".
    No per-keyword logic; one prompt handles all intent and spelling variations.
    """
    recent_product = ""
    if history:
        recent_text = " ".join([h.get("content", "") for h in history[-6:]])
        for product in KNOWN_PRODUCTS:
            if product.lower() in recent_text.lower():
                recent_product = product
                break

    cache_key = (question.strip().lower(), recent_product)
    if cache_key in _rewrite_cache:
        return _rewrite_cache[cache_key]
    if len(_rewrite_cache) >= _rewrite_cache_max:
        _rewrite_cache.pop(next(iter(_rewrite_cache)))

    product_context = f" Conversation context: user was recently asking about: {recent_product}." if recent_product else ""

    prompt = (
        "You normalize and rewrite the user's question so it works well for searching product documents. "
        "Fix misspellings and map their intent to the EXACT terms used in our documents.\n\n"
        "Document vocabulary (use these phrases in your output when relevant):\n"
        "- Pack / package / sizing / size / packaging -> include: pack sizes Available Pack Sizes\n"
        "- Price / cost / how much / rupees / ₹ -> include: Price Range INR\n"
        "- Available / stock / in stock / availability -> include: Stock Availability In Stock\n"
        "- Ingredients / content / what's in it -> include: Ingredients\n"
        "- Nutrition / calories / fat / protein -> include: Nutritional Information\n"
        "- Allergen / allergy -> include: Allergen Information\n"
        "- Shelf life / expiry -> include: Shelf Life\n"
        "- Storage / store -> include: Storage Instructions\n"
        "- Brand / category -> include: Brand Category\n\n"
        "Rules:\n"
        "- Fix typos (e.g. paxcakge->package, dise->size, avaliable->available, ingrediants->ingredients).\n"
        f"- Use ONLY these product names if a product is mentioned: {', '.join(KNOWN_PRODUCTS)}.\n"
        f"{product_context}\n"
        "- If the question is vague (e.g. 'its price', 'what about it'), include the product name from context.\n"
        "- Output ONLY the rewritten search query, no explanation. Short and keyword-rich is best.\n\n"
        f"User question: {question}\n"
        "Rewritten query:"
    )

    try:
        resp = client.chat.completions.create(
            model=query_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=80,
        )
        rewritten = (resp.choices[0].message.content or question).strip()
        if not rewritten or len(rewritten) < 2:
            return question
        _rewrite_cache[cache_key] = rewritten
        return rewritten
    except Exception:
        return question


def answer_question(
    *,
    openai_api_key: str,
    chat_model: str,
    embed_model: str,
    embed_dimensions: int | None = None,
    persist_dir: str,
    question: str,
    k: int = 12,  # Fewer chunks = faster LLM; 12 is enough for most queries
    history: list[dict[str, str]] | None = None,
    use_query_rewrite: bool = True,
) -> RagResult:
    t_rag_start = time.perf_counter()
    # Handle "Yes" to buy before RAG: return Parle G links or "unavailable" (no retrieval/LLM)
    yes_result = _try_handle_yes_to_buy(question, history)
    if yes_result is not None:
        logger.warning("Handled 'Yes to buy' without RAG")
        return yes_result

    client = OpenAI(api_key=openai_api_key)

    # Step 1: Normalize product names (lays -> Lays), then optionally LLM rewrite (skip when query has doc terms or is short product-only)
    t0 = time.perf_counter()
    search_query = _normalize_product_names_in_query(question)
    if use_query_rewrite and _query_needs_rewrite(question):
        rewritten = rewrite_query_for_rag(
            client=client,
            query_model=chat_model,
            question=search_query,
            history=history,
        )
        if rewritten and rewritten.strip():
            search_query = _normalize_product_names_in_query(rewritten.strip())
            logger.warning(f"Query rewrite: '{question[:50]}...' -> '{search_query[:70]}...'")
    else:
        # Lightweight expansion when we skip rewrite (e.g. "Kurkure" or "Kurkure price") so retrieval still gets availability/price
        q_lower = question.lower()
        if not any(term in q_lower for term in _DOC_TERMS):
            search_query = f"{search_query} Stock Availability Price Range INR pack sizes".strip()
            logger.warning(f"Skip rewrite; expanded query: '{search_query[:70]}...'")

    # If history exists and question is vague, prepend product name so retrieval finds that product's chunks
    if history:
        recent_text = " ".join([h.get("content", "") for h in history[-4:]])
        for product in KNOWN_PRODUCTS:
            if product.lower() in recent_text.lower():
                vague_words = ["it", "its", "the", "this", "that", "they", "their"]
                if any(word in question.lower() for word in vague_words):
                    search_query = f"{product} {search_query}"
                    logger.warning(f"Added product context for vague question: '{search_query[:60]}...'")
                break
    logger.warning(f"TIMING query_expansion: {time.perf_counter() - t0:.3f}s")

    # Step 2: Retrieve from vector store
    # TEMPORARILY DISABLE product filtering - it might be too strict
    # Just retrieve all chunks and let similarity do the work
    detected_product = None
    # if history:
    #     recent_text = " ".join([h.get("content", "") for h in history[-6:]])
    #     detected_product = _normalize_product_name(recent_text)
    # 
    # # Also check current question for product name
    # if not detected_product:
    #     detected_product = _normalize_product_name(question)
    
    # Don't filter by product - get all chunks
    retrieval_k = k

    t0 = time.perf_counter()
    hits = vs_query(
        persist_dir=persist_dir,
        openai_api_key=openai_api_key,
        embed_model=embed_model,
        embed_dimensions=embed_dimensions,
        q=search_query,
        k=retrieval_k,
        product_filter=None,  # NO FILTERING - get all chunks
    )
    logger.warning(f"TIMING retrieval: {time.perf_counter() - t0:.3f}s")

    docs = (hits.get("documents") or [[]])[0]
    metas = (hits.get("metadatas") or [[]])[0]
    ids = (hits.get("ids") or [[]])[0]
    distances = (hits.get("distances") or [[]])[0]
    
    logger.warning(f"🔍 QUERY DEBUG: '{question}' → rewritten to: '{search_query}'")
    logger.warning(f"📊 Retrieved {len(docs)} chunks from database (NO product filter)")

    # Step 3: Very lenient similarity filtering - accept almost all chunks
    t0 = time.perf_counter()
    SIMILARITY_THRESHOLD = 0.98  # Very lenient - only reject completely unrelated

    context_blocks: list[str] = []
    filtered_count = 0

    for i, doc in enumerate(docs):
        distance = distances[i] if i < len(distances) else 1.0
        meta = metas[i] if i < len(metas) else {}
        product_name = meta.get("product", "Unknown")

        if i < 3:
            logger.warning(f"Chunk {i}: distance={distance:.3f}, product={product_name}, preview={doc[:100]}")

        if distance > SIMILARITY_THRESHOLD:
            filtered_count += 1
            logger.debug(f"Filtered out chunk {i} with distance {distance:.3f}")
            continue

        context_blocks.append(f"[{len(context_blocks) + 1}] {doc}")

    context = "\n\n".join(context_blocks).strip()
    logger.warning(f"TIMING filter_and_context: {time.perf_counter() - t0:.3f}s")
    if len(context_blocks) == 0:
        logger.error(f"❌ CRITICAL: No chunks in context! Retrieved {len(docs)} but all filtered out.")
        logger.error(f"Distances: {distances[:10] if len(distances) > 0 else 'none'}")
        logger.error(f"Docs preview: {[d[:50] for d in docs[:3]] if docs else 'none'}")
    
    # When no context was retrieved, use a minimal context so we can still answer catalog questions (which products we have, etc.)
    product_list_str = ", ".join(KNOWN_PRODUCTS)
    if not context:
        context = (
            "(No product details were retrieved for this query. "
            "You may only answer which products we have or list products using the product list below. "
            "For price, availability, content, or packaging you must say you don't have that information in the product docs.)"
        )

    # Document structure (exact format from product doc - use these labels when reading CONTEXT)
    DOC_STRUCTURE = (
        "The CONTEXT comes from product docs with this exact structure. Use these labels:\n"
        "- Stock Availability: 'In Stock' or 'Out of Stock' (this is availability)\n"
        "- Price Range (INR): pack sizes with rupee amounts, e.g. '30g – ₹10', '55g – ₹20' (₹ is rupees)\n"
        "- Available Pack Sizes: e.g. 30g, 55g, 90g, 115g\n"
        "- Ingredients, Nutritional Information (per 100g), Allergen Information\n"
        "- Shelf Life, Storage Instructions, Brand, Category\n"
    )

    system = (
        "You are Snackbot, the chatbot for an e-commerce snacks site. Help users with product catalog, availability, price, pack sizes, and other details.\n\n"
        "OUR PRODUCTS (use this list for catalog questions):\n"
        f"  {product_list_str}\n\n"
        f"DOCUMENT STRUCTURE (read CONTEXT using these exact labels):\n{DOC_STRUCTURE}\n"
        "HOW TO READ CONTEXT (mandatory):\n"
        "- For AVAILABILITY: look for 'Stock Availability' followed by 'In Stock' or 'Out of Stock'. If you see it in any chunk, you HAVE availability—state it. Never say you don't have it.\n"
        "- For PRICE: look for 'Price Range (INR)' or lines with '₹' and amounts (e.g. '30g – ₹10', '55g – ₹20'). If you see it in any chunk, you HAVE price—state the range or pack-wise prices. Never say you don't have it.\n"
        "- For pack sizes: use 'Available Pack Sizes' and 'Price Range (INR)' from CONTEXT.\n"
        "CRITICAL RULES:\n"
        "- When the user asks about a SPECIFIC product (e.g. Kurkure, Lays): Say 'Yes, we have [Product].' Then from CONTEXT: state Stock Availability (In Stock/Out of Stock). Then state Price Range (INR) or pack-wise prices (₹) if present. Optionally mention pack sizes. You MUST end with exactly: 'Would you like to buy this product? (Yes/No)'\n"
        "- For 'which products do you have?' list the products above. For 'other than X?' list all except the one(s) mentioned.\n"
        "- Answer only from CONTEXT using the labels above. Use CONVERSATION HISTORY for follow-ups. Keep answers short; end with the purchase question for product replies.\n\n"
        "WHEN USER SAYS YES TO BUYING (e.g. 'yes', 'yeah', 'sure', 'I want to buy'):\n"
        "- If the product they were asking about is Parle G (or Parle-G): Reply with exactly these clickable links (one per line):\n"
        "Choose a pack size:\n"
        "[56g](/products/parle-g-56g)\n"
        "[200g](/products/parle-g-200g)\n"
        "[800g](/products/parle-g-800g)\n"
        "- If the product is ANY other product (Lays, Kurkure, Maggi, etc.): Reply with exactly: 'Purchase options for this product are currently unavailable.'\n\n"
        "OUTPUT FORMAT (strict): Return product replies in this exact structure. Do not combine lines. Each bullet must be on a new line.\n"
        "Yes, we have {Product Name}.\n\n"
        "Availability: {In Stock or Out of Stock}\n\n"
        "Price:\n"
        "- {Size} – ₹{Price}\n"
        "(one line per pack/price)\n\n"
        "Pack sizes:\n"
        "- {Size}\n"
        "(one line per size)\n\n"
        "Would you like to buy this product? (Yes/No)\n"
        "Use plain text. For Parle G purchase links use the format [text](/products/parle-g-XXg) as shown above."
    )

    # Build messages: system + conversation history + current turn (context + question)
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]

    if history:
        for h in history:
            role = (h.get("role") or "").strip().lower()
            content = (h.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    current_user = (
        f"CONTEXT:\n{context if context else '(no context found)'}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Return a helpful answer. Do not combine lines. Each bullet must be on a new line."
    )
    messages.append({"role": "user", "content": current_user})

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        temperature=0.2,
        max_completion_tokens=400,  # Cap length for faster response
    )
    logger.warning(f"TIMING llm_call: {time.perf_counter() - t0:.3f}s")

    answer = resp.choices[0].message.content or ""
    raw = answer.strip()
    # Option 3: Always clean messy one-line output so we get proper line breaks (don't depend on LLM formatting)
    cleaned = _clean_product_response(raw)
    answer_lines = tuple((s.strip() or "\u00A0") for s in cleaned.split("\n"))
    if not answer_lines:
        answer_lines = (raw,)
    logger.warning(f"TIMING rag_pipeline_total: {time.perf_counter() - t_rag_start:.3f}s")
    return RagResult(answer=cleaned.strip() or raw, sources=[], answer_lines=answer_lines)
