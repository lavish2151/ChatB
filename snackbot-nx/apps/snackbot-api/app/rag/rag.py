from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from openai import OpenAI

from .vectorstore import query as vs_query

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RagResult:
    answer: str
    sources: list[dict]


# Product names for query rewriting context
KNOWN_PRODUCTS = [
    "Lays",
    "Kurkure",
    "Cadbury Dairy Milk Silk",
    "Maggi",
    "Nescafe Classic",
    "Parle G",
]

# Product name aliases for flexible matching (shortened names users might use)
PRODUCT_ALIASES = {
    "parle g": "Parle G",
    "parle-g": "Parle G",
    "dairy milk": "Cadbury Dairy Milk Silk",
    "cadbury": "Cadbury Dairy Milk Silk",
    "cadbury silk": "Cadbury Dairy Milk Silk",
    "nescafe": "Nescafe Classic",
    "nescafe classic": "Nescafe Classic",
    "classic": "Nescafe Classic",
    "maggi noodles": "Maggi",
    "maggi noodles": "Maggi",
}


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


def rewrite_query_for_rag(
    *,
    client: OpenAI,
    query_model: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """
    Use LLM to rewrite the user query to be more specific and better suited for RAG retrieval.
    Uses conversation history to understand context (e.g., "its price" → "Lays price").
    """
    # Extract products from BOTH user and assistant messages (assistant might have mentioned product names)
    recent_product = ""
    if history:
        # Look at last 6 messages (both user and assistant) to find product mentions
        recent_text = " ".join([h.get("content", "") for h in history[-6:]])
        for product in KNOWN_PRODUCTS:
            if product.lower() in recent_text.lower():
                recent_product = product
                break  # Use the first/most recent one found

    # Expand cost/price related terms for better retrieval
    cost_synonyms = {
        "cost": "cost price amount rupees rs",
        "price": "price cost amount rupees rs",
        "costs": "cost price amount rupees rs",
        "pricing": "price cost amount rupees rs",
        "how much": "cost price amount",
        "expensive": "cost price amount",
        "cheap": "cost price amount",
    }
    question_lower = question.lower()
    expanded_question = question
    for term, expansion in cost_synonyms.items():
        if term in question_lower:
            # Add synonyms to help retrieval
            expanded_question = f"{question} {expansion}"
            break
    
    # If we found a product and the question is vague (uses "its", "their", "this", etc.), directly prepend it
    vague_indicators = ["its", "their", "this", "that", "the", "it's", "they"]
    is_vague = any(indicator in question_lower for indicator in vague_indicators)
    
    if recent_product and is_vague:
        # Direct rewrite: "its cost" → "Lays cost price amount"
        rewritten = f"{recent_product} {expanded_question}"
        return rewritten
    
    # Otherwise, use LLM to rewrite
    product_context = f" The user was recently asking about: {recent_product}." if recent_product else ""

    prompt = (
        f"Rewrite this user question to be more specific and better for searching product documents.\n"
        f"Available products (use EXACTLY these names, nothing else): {', '.join(KNOWN_PRODUCTS)}.\n"
        f"{product_context}\n"
        f"CRITICAL RULES:\n"
        f"- Use ONLY these exact product names: {', '.join(KNOWN_PRODUCTS)}\n"
        f"- DO NOT use old product names like 'Masala Parle-G', 'Nimbu Masala Soda', 'Peanut Chikki', 'Filter Coffee Cold Brew', 'Aam Papad'\n"
        f"- If you see 'Masala Parle-G' or 'masala parle g', replace it with 'Parle G'\n"
        f"- If the question is vague (e.g., 'its price', 'what about allergens', 'their difference'), include the product name(s) from context.\n"
        f"- For cost/price questions, include synonyms: 'cost', 'price', 'amount', 'pricing'.\n"
        f"- Keep the core intent but make it more searchable with relevant keywords.\n"
        f"- Remove conversational filler (e.g., 'can you tell me', 'I want to know').\n"
        f"- Return ONLY the rewritten query, nothing else.\n\n"
        f"Original question: {expanded_question}\n"
        f"Rewritten query:"
    )

    resp = client.chat.completions.create(
        model=query_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=100,
    )
    rewritten = (resp.choices[0].message.content or question).strip()
    # Fallback: if rewrite is empty or too different, use original
    if not rewritten or len(rewritten) < len(question) * 0.3:
        return question
    return rewritten


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
    client = OpenAI(api_key=openai_api_key)

    # Step 1: Simple query expansion for better retrieval
    t0 = time.perf_counter()
    search_query = question

    # If history exists, try to add product context for follow-up questions
    if history:
        recent_text = " ".join([h.get("content", "") for h in history[-4:]])
        for product in KNOWN_PRODUCTS:
            if product.lower() in recent_text.lower():
                # If question is vague (uses "it", "its", "the", etc.), add product name
                vague_words = ["it", "its", "the", "this", "that", "they", "their"]
                if any(word in question.lower() for word in vague_words):
                    search_query = f"{product} {question}"
                    logger.warning(f"Added product context: '{question}' → '{search_query}'")
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
    
    # Hard guardrail: if retrieval found nothing, don't call the model (prevents hallucinations).
    if not context:
        return RagResult(
            answer=(
                "I don't have those details in the product documents I'm using. "
                "Please ask about one of these products: Lays, Kurkure, Cadbury Dairy Milk Silk, "
                "Maggi, Nescafe Classic, Parle G."
            ),
            sources=[],
        )

    # Available data fields in the product documents (pseudo schema)
    AVAILABLE_DATA_FIELDS = (
        "The product documents typically contain information about:\n"
        "- Product name and description\n"
        "- Price and cost information\n"
        "- Ingredients and composition\n"
        "- Allergens and dietary information\n"
        "- Nutritional information\n"
        "- Flavor profiles and taste\n"
        "- Packaging details\n"
        "- Origin or manufacturing details\n"
        "- Usage instructions or serving suggestions\n"
    )

    system = (
        "You are Snackbot, a helpful assistant for a one-page snacks website.\n"
        "CRITICAL RULES - YOU MUST FOLLOW THESE:\n"
        "- Answer ONLY using the provided CONTEXT below. You have NO access to the internet or any other knowledge.\n"
        "- Do NOT use outside knowledge. Do NOT guess. Do NOT make up information.\n"
        f"\nAVAILABLE DATA IN DOCUMENTS:\n{AVAILABLE_DATA_FIELDS}\n"
        "- IMPORTANT: Cost/price information IS available in the documents. Look carefully through ALL provided chunks for:\n"
        "  * Price, cost, amount, rupees, Rs, pricing information\n"
        "  * These may appear in various formats (e.g., 'Rs 50', '50 rupees', 'cost: 50', 'price: 50')\n"
        "  * Search ALL chunks thoroughly - cost info might be in any chunk related to the product\n"
        "- Use the CONVERSATION HISTORY to understand follow-up questions and comparisons:\n"
        "  * 'its price', 'what about allergens?', 'how much?', 'its cost' → refer to the product just discussed in history\n"
        "  * 'difference between their costs', 'compare both' → use information from ALL products mentioned in CONTEXT\n"
        "  * ALWAYS check conversation history - if user says 'its' or 'their', look at what product was mentioned before\n"
        "  * Remember what was discussed earlier in the conversation\n"
        "- If the CONTEXT does not contain the answer, reply EXACTLY:\n"
        "  \"I don't have those details in the product documents I'm using.\"\n"
        "  Then ask 1 short follow-up question to clarify the product.\n"
        "- For COMPARISON questions: If CONTEXT has info about multiple products, compare them directly using the data provided.\n"
        "- Keep answers short and focused: 2-5 sentences unless the user asks for more detail.\n"
        "- If relevant, mention the product name(s) you are referring to.\n"
        "- NEVER say 'I don't know' or 'I'm not sure' - instead say you don't have those details in the documents."
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
        "Return a helpful answer."
    )
    messages.append({"role": "user", "content": current_user})

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        temperature=0.2,
        max_tokens=500,  # Cap length for faster response (~375 words max)
    )
    logger.warning(f"TIMING llm_call: {time.perf_counter() - t0:.3f}s")

    answer = resp.choices[0].message.content or ""
    logger.warning(f"TIMING rag_pipeline_total: {time.perf_counter() - t_rag_start:.3f}s")
    return RagResult(answer=answer.strip(), sources=[])
