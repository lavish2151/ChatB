## Snackbot API (Flask + OpenAI RAG)

### Setup

1) Create a virtualenv (recommended) and install deps:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2) Create `.env` in `snackbot-nx/` (copy from `.env.example`) and fill values.

3) Add your Google Docs URL(s) in `GDOCS_PUBLISHED_URLS`.
   - Best: "Publish to web" link (no auth required)
   - Also supported: a normal `/edit` link **if** the doc is shared publicly ("Anyone with the link" can view)

### Ingest (build vector DB)

From the Nx workspace root:

```bash
npx nx ingest snackbot-api
```

### Run server

From the Nx workspace root:

```bash
npx nx serve snackbot-api
```

Then open `http://localhost:5000` (after building the web app with `npm run build:web` from repo root).  
API: `POST http://localhost:5000/api/chat` (JSON).

