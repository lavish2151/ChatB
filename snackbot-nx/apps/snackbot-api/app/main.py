from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from .config import load_settings
from .rag.rag import answer_question


def create_app() -> Flask:
    # Load env from Nx workspace root if present
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), "..", "..", ".env"), override=False)
    load_dotenv(override=False)  # also allow local apps/snackbot-api/.env if you want

    s = load_settings()

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": s.allowed_origins}})

from flask import redirect

@app.get("/")
def root():
    return redirect("/widget")
    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        msg = (data.get("message") or "").strip()
        if not msg:
            return jsonify({"error": "Missing 'message'"}), 400

        res = answer_question(
            openai_api_key=s.openai_api_key,
            chat_model=s.openai_chat_model,
            embed_model=s.openai_embed_model,
            persist_dir=s.chroma_persist_dir,
            question=msg,
        )
        return jsonify({"answer": res.answer, "sources": res.sources})

    @app.get("/widget")
    def widget():
        html = _WIDGET_HTML
        return Response(html, mimetype="text/html")

    return app


_WIDGET_HTML = r"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Snackbot</title>
    <style>
      :root { --bg:#0b1220; --panel:#0f1a2f; --text:#e8eefc; --muted:#a9b6d2; --accent:#7c5cff; --border:#1c2a4a; }
      body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; background:transparent; }
      .wrap { background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 12px; overflow:hidden; }
      .head { padding: 12px 14px; background: linear-gradient(180deg, var(--panel), var(--bg)); border-bottom: 1px solid var(--border); }
      .head .t { font-weight: 700; letter-spacing: .2px; }
      .head .s { color: var(--muted); font-size: 12px; margin-top: 4px; }
      .log { height: 360px; overflow:auto; padding: 12px 14px; display:flex; flex-direction:column; gap:10px; }
      .msg { max-width: 92%; padding: 10px 12px; border-radius: 12px; border:1px solid var(--border); }
      .user { align-self:flex-end; background: rgba(124,92,255,.15); }
      .bot  { align-self:flex-start; background: rgba(255,255,255,.06); }
      .meta { color: var(--muted); font-size: 11px; margin-top: 6px; }
      .bar { display:flex; gap:10px; padding: 12px 14px; border-top: 1px solid var(--border); background: rgba(255,255,255,.03); }
      input { flex:1; background: rgba(255,255,255,.06); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; color: var(--text); outline:none; }
      button { background: var(--accent); border:none; color:white; padding: 10px 14px; border-radius: 10px; font-weight: 600; cursor:pointer; }
      button:disabled { opacity:.6; cursor:not-allowed; }
      a { color: #b9a9ff; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="head">
        <div class="t">Snackbot</div>
      </div>
      <div id="log" class="log"></div>
      <div class="bar">
        <input id="q" placeholder="Ask a question..." />
        <button id="send">Send</button>
      </div>
    </div>

    <script>
      const log = document.getElementById('log');
      const q = document.getElementById('q');
      const send = document.getElementById('send');

      function add(role, text, sources) {
        const div = document.createElement('div');
        div.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
        div.textContent = text;
        if (role !== 'user' && Array.isArray(sources) && sources.length) {
          const meta = document.createElement('div');
          meta.className = 'meta';
          meta.textContent = 'Sources: ' + sources.map(s => s.product || s.title || s.url || s.chunk_id).filter(Boolean).join(' · ');
          div.appendChild(meta);
        }
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
      }

      async function ask() {
        const text = (q.value || '').trim();
        if (!text) return;
        q.value = '';
        add('user', text);
        send.disabled = true;
        try {
          const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Request failed');
          add('bot', data.answer || '(no answer)', data.sources || []);
        } catch (e) {
          add('bot', 'Error: ' + (e.message || e));
        } finally {
          send.disabled = false;
          q.focus();
        }
      }

      send.addEventListener('click', ask);
      q.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') ask();
      });

      add('bot', 'Hi! Ask me anything about the Snackbot products.');
      q.focus();
    </script>
  </body>
</html>"""


def main() -> None:
    app = create_app()
    s = load_settings()
    app.run(host="0.0.0.0", port=s.port, debug=True)


if __name__ == "__main__":
    main()
  
# changes

