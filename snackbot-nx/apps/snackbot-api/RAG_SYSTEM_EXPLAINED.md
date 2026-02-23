# How the Snackbot RAG System Works

A simple guide to what the app does and what happens when you ask a question.

---

## What is RAG?

**RAG** = **R**etrieval **A**ugmented **G**eneration.

In plain words:

- **Retrieval** = “find the right bits of text” from your product documents.
- **Augmented** = we give those bits to the AI as extra information.
- **Generation** = the AI writes an answer **using only that information** (so it doesn’t guess or use random knowledge).

So: we **search** our own docs, **pass** the best matches to the AI, and the AI **answers from that text only**. That keeps answers accurate and grounded in your data.

---

## Two Big Phases

The system has two phases that don’t happen at the same time:

1. **Ingestion (one-time or when you update content)**  
   Put product information into a “searchable knowledge base.”

2. **Query (every time someone asks a question)**  
   Use that knowledge base to answer the question.

---

## Phase 1: Ingestion (Building the Knowledge Base)

This runs when you execute the ingest script (e.g. `python scripts/ingest_gdocs.py`). It does **not** run when a user sends a chat message.

### Step-by-step

1. **Get the document**  
   The script reads the Google Doc URL from your config (e.g. `.env`). It fetches the published doc and extracts **plain text** (no formatting).  
   *Module: `app/rag/gdocs.py`*

2. **Split by product**  
   The doc is split into sections using product names as headings (e.g. “Lays”, “Cadbury Dairy Milk Silk”). Each section is one product’s text.  
   *Done in: `scripts/ingest_gdocs.py`*

3. **Chunk the text**  
   Each section is split into smaller pieces (chunks) of about 900 characters, with a small overlap between chunks so we don’t cut sentences in a bad place.  
   *Module: `app/rag/chunking.py`*

4. **Turn text into vectors (embeddings)**  
   Each chunk is sent to OpenAI’s **embeddings** API. The API returns a list of numbers (a “vector”) that represents the meaning of that text. Similar meanings get similar vectors.  
   *Module: `app/rag/vectorstore.py`*

5. **Store in ChromaDB**  
   Each chunk is saved in ChromaDB along with its vector and some metadata (product name, doc title, URL). ChromaDB is a **vector database**: it can quickly find chunks whose vectors are “closest” to a given query vector.  
   *Module: `app/rag/vectorstore.py`*

After this, the “knowledge base” is ready: all product chunks are stored and searchable by meaning.

---

## Phase 2: What Happens When You Send a Query

This is what runs **every time** a user types a message in the chat and hits Send.

### High-level flow

1. The **frontend** sends your message (and recent chat history) to the backend.
2. The **backend** receives it and calls the RAG pipeline.
3. The RAG pipeline: **retrieves** relevant chunks, then **asks the AI** to answer using only those chunks (and the chat history).
4. The **answer** (and optional sources) is sent back to the frontend and shown in the chat.

Below is the same flow with a bit more detail.

---

### Step 1: Request reaches the backend

- The frontend does: **POST `/api/chat`** with a JSON body like:
  - `message`: the user’s current question (e.g. “What is the price of Lays?”).
  - `history`: the last several user and bot messages (so the system knows “it” or “its price” can refer to something said earlier).
- The Flask app in **`app/main.py`** receives this, checks that `message` is present and not too long, and normalizes `history`.  
- Then it calls the RAG function: **`answer_question(question=msg, history=history, ...)`**.

So: **your query and history enter the app in `main.py` and are passed into the RAG pipeline.**

---

### Step 2: Query expansion (using history)

- The pipeline looks at the **current question** and the **last few messages** in `history`.
- If the question is vague (e.g. “What about its price?” or “What about allergens?”) and a **product name** appeared in recent messages (e.g. “Lays”), the pipeline **rewrites** the search query to include that product.  
  Example: question = “What about its price?” → search query = “Lays What about its price?”  
- This happens so that when we search the knowledge base, we look for **Lays + price** instead of just “price.”  
- *Done in: `app/rag/rag.py` (start of `answer_question`).*

So: **history is used here only to make the search query more precise** (so “it” is resolved to a product).

---

### Step 3: Retrieval (finding relevant chunks)

- The **search query** (the original or rewritten question) is sent to OpenAI’s **embeddings** API. We get back a **query vector**.
- That vector is sent to **ChromaDB**. ChromaDB returns the **top‑k** (e.g. 20) chunks whose vectors are **closest** to the query vector (i.e. most similar in meaning).
- For each chunk we get: the **text**, **metadata** (product, title, URL), and a **distance** (how far from the query; lower = more similar).  
- *Embedding: `app/rag/vectorstore.py`. Using that in the pipeline: `app/rag/rag.py`.*

So: **retrieval = turn the query into a vector + ask ChromaDB for the most similar stored chunks.**

---

### Step 4: Filtering and building “context”

- Chunks with **distance above a threshold** (e.g. 0.98) are dropped as “not relevant enough.”
- The remaining chunks are turned into one long **context** string: each chunk is numbered and concatenated (e.g. “[1] … text … [2] … text …”).
- We also build a **sources** list (chunk id, product, title, URL) to show the user where the answer came from.

If **no** chunks pass the filter, we **don’t** call the AI. We return a fixed message like “I don’t have those details in the product documents…” and list the product names. So: **no context → no AI call → no guessing.**

So: **context = the exact text we will show the AI as the only allowed source for the answer.**

---

### Step 5: Calling the AI (generation)

- We build the **messages** for the OpenAI chat API:
  - **System message**: Instructions that say “You are Snackbot; answer ONLY from the CONTEXT below; don’t use other knowledge; if the answer isn’t in the context, say so; use conversation history to resolve ‘its’/‘their’.”
  - **Conversation history**: The previous user and assistant messages (so the model knows what “it” or “they” refer to).
  - **Current user message**: One message containing **CONTEXT** (the concatenated chunks) and **QUESTION** (the user’s question), e.g. “Return a helpful answer.”
- We call **OpenAI `chat.completions.create`** with these messages. The model returns an **answer**.
- We return that answer and the **sources** list to the Flask route.

So: **the AI sees only the CONTEXT (retrieved chunks) plus the QUESTION and history; it is not allowed to use other knowledge.**

---

### Step 6: Response back to the user

- The Flask route in **`main.py`** gets back **answer** and **sources** from the RAG pipeline.
- It sends to the frontend: **`{ "answer": "...", "sources": [...] }`**.
- The frontend shows the answer in the chat and can show sources (e.g. product name, doc title, link).

So: **what the user sees is the generated answer plus optional source links.**

---

## End-to-end picture (when you send a query)

```
You type: "What is the price of Lays?"
    ↓
Frontend sends: POST /api/chat  { message: "...", history: [...] }
    ↓
main.py: validates, then calls answer_question(question, history)
    ↓
RAG pipeline:
  1. Query expansion (maybe "Lays" + question if history says so)
  2. Embed question → query vector
  3. ChromaDB: get top‑k chunks by similarity
  4. Filter by distance, build CONTEXT string
  5. If no context → return "I don't have those details..."
  6. Else: build messages [ system, history, CONTEXT + QUESTION ]
  7. OpenAI chat → answer
    ↓
main.py returns { answer, sources } to frontend
    ↓
You see the answer and sources in the chat.
```

---

## Important ideas (summary)

- **RAG** = retrieve relevant chunks from your docs, then generate an answer from **only** those chunks (and chat history).
- **Ingestion** = one-time (or periodic) job: Google Doc → split by product → chunk → embed → store in ChromaDB.
- **Query** = every request: question (+ history) → optional query expansion → embed question → ChromaDB retrieval → filter → build context → send context + question + history to OpenAI → return answer and sources.
- **History** is used in two places: (1) to rewrite vague questions for retrieval (“its price” → “Lays price”), and (2) in the messages to the AI so it can resolve “it”/“their” and do follow-up or comparison questions.
- **No context** = we never call the AI; we return a safe “I don’t have those details” message.

If you want more detail on a specific step (e.g. chunking, embeddings, or ChromaDB), say which part and we can go deeper there.
