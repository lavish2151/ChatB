from __future__ import annotations

from dataclasses import dataclass
from openai import OpenAI

from .vectorstore import query as vs_query


@dataclass(frozen=True)
class RagResult:
    answer: str
    sources: list[dict]


def answer_question(
    *,
    openai_api_key: str,
    chat_model: str,
    embed_model: str,
    persist_dir: str,
    question: str,
    k: int = 6,
    history: list[dict[str, str]] | None = None,
) -> RagResult:
    hits = vs_query(
        persist_dir=persist_dir,
        openai_api_key=openai_api_key,
        embed_model=embed_model,
        q=question,
        k=k,
    )

    docs = (hits.get("documents") or [[]])[0]
    metas = (hits.get("metadatas") or [[]])[0]
    ids = (hits.get("ids") or [[]])[0]

    sources: list[dict] = []
    context_blocks: list[str] = []
    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        chunk_id = ids[i] if i < len(ids) else f"chunk_{i}"
        sources.append(
            {
                "chunk_id": chunk_id,
                "title": meta.get("title"),
                "url": meta.get("url"),
                "product": meta.get("product"),
            }
        )
        context_blocks.append(f"[{i+1}] {doc}")

    context = "\n\n".join(context_blocks).strip()
    # Hard guardrail: if retrieval found nothing, don't call the model (prevents hallucinations).
    if not context:
        return RagResult(
            answer=(
                "I don't have those details in the product documents I'm using. "
                "Please ask about one of these products: Masala Parle-G, Cadbury Dairy Milk Silk, "
                "Nimbu Masala Soda, Peanut Chikki, Filter Coffee Cold Brew, Aam Papad."
            ),
            sources=[],
        )

    client = OpenAI(api_key=openai_api_key)

    system = (
        "You are Snackbot, a helpful assistant for a one-page snacks website.\n"
        "CRITICAL RULES:\n"
        "- Answer ONLY using the provided CONTEXT.\n"
        "- Do NOT use outside knowledge. Do NOT guess.\n"
        "- Use the CONVERSATION HISTORY to understand follow-up questions: "
        "e.g. 'what about its price?', 'any allergens?', 'how much?' refer to the product just discussed. "
        "Assume the user is still asking about that same product unless they name another.\n"
        "- If the CONTEXT does not contain the answer, reply exactly:\n"
        "  \"I don't have those details in the product documents I'm using.\"\n"
        "  Then ask 1 short follow-up question to clarify the product.\n"
        "- Keep answers short, clear, and product-focused.\n"
        "- If relevant, mention the product name you are referring to."
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

    resp = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        temperature=0.2,
    )

    answer = resp.choices[0].message.content or ""
    return RagResult(answer=answer.strip(), sources=sources)
