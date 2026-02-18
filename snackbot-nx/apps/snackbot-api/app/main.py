from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from .config import load_settings
from .rag.rag import answer_question

logger = logging.getLogger(__name__)

# Limits to avoid abuse and huge payloads
MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_ITEMS = 20


def create_app() -> Flask:
    # Load env from Nx workspace root if present
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), "..", "..", ".env"), override=False)
    load_dotenv(override=False)

    s = load_settings()

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": s.allowed_origins}})

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        msg = (data.get("message") or "").strip()
        if not msg:
            return jsonify({"error": "Missing 'message'"}), 400
        if len(msg) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"}), 400

        raw_history = data.get("history")
        history = None
        if isinstance(raw_history, list):
            history = [
                {"role": str(h.get("role", "")), "content": str(h.get("content", ""))[:MAX_MESSAGE_LENGTH]}
                for h in raw_history[:MAX_HISTORY_ITEMS]
                if isinstance(h, dict)
            ]
            history = history if history else None

        try:
            res = answer_question(
                openai_api_key=s.openai_api_key,
                chat_model=s.openai_chat_model,
                embed_model=s.openai_embed_model,
                persist_dir=s.chroma_persist_dir,
                question=msg,
                history=history,
            )
            return jsonify({"answer": res.answer, "sources": res.sources})
        except Exception as e:
            logger.exception("Chat request failed")
            return jsonify({"error": "Something went wrong. Please try again."}), 500

    @app.get("/")
    def widget():
        html = _WIDGET_HTML
        return Response(html, mimetype="text/html")

    return app


# Embeddable widget: bottom-right bubble "Chat with us" → expand to full chat, minimize to bubble
_WIDGET_HTML = r"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Snackbot</title>
    <style>
      :root { --bg:#0b1220; --panel:#0f1a2f; --text:#e8eefc; --muted:#a9b6d2; --accent:#7c5cff; --border:#1c2a4a; }
      * { box-sizing: border-box; }
      body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; background:transparent; min-height:100vh; }
      /* Container fixed bottom-right for Wix iframe embed */
      .snackbot-root { position: fixed; bottom: 0; right: 0; z-index: 999999; font-size: 15px; }
      .snackbot-bubble { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 20px; background: var(--accent); color: white; border: none; border-radius: 28px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 14px rgba(124,92,255,.4); }
      .snackbot-bubble:hover { filter: brightness(1.08); }
      .snackbot-bubble svg { width: 22px; height: 22px; flex-shrink: 0; }
      .snackbot-panel { display: none; width: 380px; max-width: calc(100vw - 24px); height: 520px; max-height: calc(100vh - 24px); flex-direction: column; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,.3); }
      .snackbot-root.expanded .snackbot-bubble { display: none; }
      .snackbot-root.expanded .snackbot-panel { display: flex; }
      .wrap { flex: 1; display: flex; flex-direction: column; min-height: 0; }
      .head { padding: 12px 14px; background: linear-gradient(180deg, var(--panel), var(--bg)); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
      .head .t { font-weight: 700; letter-spacing: .2px; }
      .head-actions { display: flex; gap: 8px; align-items: center; }
      .btn-minimize { background: transparent; border: none; color: var(--muted); cursor: pointer; padding: 6px 10px; font-size: 12px; border-radius: 8px; }
      .btn-minimize:hover { color: var(--text); background: rgba(255,255,255,.06); }
      .log { flex: 1; overflow: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 10px; min-height: 0; }
      .msg { max-width: 92%; padding: 10px 12px; border-radius: 12px; border: 1px solid var(--border); }
      .user { align-self: flex-end; background: rgba(124,92,255,.15); }
      .bot { align-self: flex-start; background: rgba(255,255,255,.06); }
      .meta { color: var(--muted); font-size: 11px; margin-top: 6px; }
      .bar { display: flex; gap: 10px; padding: 12px 14px; border-top: 1px solid var(--border); background: rgba(255,255,255,.03); flex-shrink: 0; }
      input { flex: 1; background: rgba(255,255,255,.06); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; color: var(--text); outline: none; min-width: 0; }
      button { background: var(--accent); border: none; color: white; padding: 10px 14px; border-radius: 10px; font-weight: 600; cursor: pointer; }
      button:disabled { opacity: .6; cursor: not-allowed; }
      button.secondary { background: transparent; color: var(--muted); }
      button.secondary:hover { color: var(--text); background: rgba(255,255,255,.06); }
      .typing { color: var(--muted); font-style: italic; }
      a { color: #b9a9ff; }
    </style>
  </head>
  <body>
    <div class="snackbot-root" id="snackbot-root">
      <button type="button" class="snackbot-bubble" id="snackbot-bubble" aria-label="Open chat">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/></svg>
        <span>Chat with us</span>
      </button>
      <div class="snackbot-panel">
        <div class="wrap">
          <div class="head">
            <div class="t">Snackbot</div>
            <div class="head-actions">
              <button type="button" id="clear" class="secondary" style="padding:6px 10px; font-size:12px;">Clear</button>
              <button type="button" id="minimize" class="btn-minimize">Minimize</button>
            </div>
          </div>
          <div id="log" class="log"></div>
          <div class="bar">
            <input id="q" placeholder="Ask a question..." />
            <button id="send">Send</button>
          </div>
        </div>
      </div>
    </div>

    <script>
      const root = document.getElementById('snackbot-root');
      const bubble = document.getElementById('snackbot-bubble');
      const minimizeBtn = document.getElementById('minimize');
      const log = document.getElementById('log');
      const q = document.getElementById('q');
      const send = document.getElementById('send');
      const clearBtn = document.getElementById('clear');

      const maxHistoryTurns = 10;
      let conversationHistory = [];

      function openChat() { root.classList.add('expanded'); }
      function closeChat() { root.classList.remove('expanded'); }
      bubble.addEventListener('click', openChat);
      minimizeBtn.addEventListener('click', closeChat);

      function add(role, text, sources, opts) {
        opts = opts || {};
        const div = document.createElement('div');
        div.className = 'msg ' + (role === 'user' ? 'user' : 'bot') + (opts.typing ? ' typing' : '');
        div.textContent = text;
        if (role !== 'user' && Array.isArray(sources) && sources.length && !opts.typing) {
          const meta = document.createElement('div');
          meta.className = 'meta';
          meta.textContent = 'Sources: ' + sources.map(s => s.product || s.title || s.url || s.chunk_id).filter(Boolean).join(' · ');
          div.appendChild(meta);
        }
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
        return div;
      }

      function showWelcome() {
        add('bot', 'Hi! Ask me anything about the Snackbot products.');
      }

      clearBtn.addEventListener('click', function() {
        log.innerHTML = '';
        conversationHistory = [];
        showWelcome();
        q.focus();
      });

      async function ask() {
        const text = (q.value || '').trim();
        if (!text) return;
        q.value = '';
        add('user', text);
        send.disabled = true;
        const placeholder = add('bot', 'Thinking…', [], { typing: true });
        try {
          const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: conversationHistory })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Request failed');
          const answer = data.answer || '(no answer)';
          placeholder.remove();
          add('bot', answer, data.sources || []);

          conversationHistory.push({ role: 'user', content: text });
          conversationHistory.push({ role: 'assistant', content: answer });
          if (conversationHistory.length > maxHistoryTurns * 2) {
            conversationHistory = conversationHistory.slice(-maxHistoryTurns * 2);
          }
        } catch (e) {
          placeholder.remove();
          add('bot', 'Error: ' + (e.message || e));
        } finally {
          send.disabled = false;
          q.focus();
        }
      }

      send.addEventListener('click', ask);
      q.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') ask();
      });

      showWelcome();
      q.focus();
    </script>
  </body>
</html>"""


def main() -> None:
    app = create_app()
    s = load_settings()
    debug = os.getenv("FLASK_DEBUG", "0").strip().lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=s.port, debug=debug)


if __name__ == "__main__":
    main()
