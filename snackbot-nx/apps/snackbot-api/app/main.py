from __future__ import annotations

import logging
import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS

from .config import load_settings
from .rag.rag import answer_question

logger = logging.getLogger(__name__)

# Limits to avoid abuse and huge payloads
MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_ITEMS = 20

# Simple in-memory list to store "request order" submissions (no database for now).
# In production you would use a database (e.g. SQLite, PostgreSQL).
ORDER_STORE: list[dict] = []


def create_app() -> Flask:
    # Load env from Nx workspace root if present
    # Try multiple paths to find .env file
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    env_paths = [
        os.path.join(workspace_root, ".env"),  # snackbot-nx/.env
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),  # Fallback
        ".env",  # Current directory
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=False)
            break
    else:
        # If no .env found, try default location
        load_dotenv(override=False)

    # Enable WARNING level logging to see debug messages
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    s = load_settings()

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": s.allowed_origins}})

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/api/test-newlines")
    def test_newlines():
        """Return plain text with newlines. If you see separate lines → newlines work."""
        text = (
            "Yes, we have Kurkure.\n\n"
            "Availability: In Stock\n\n"
            "Price:\n"
            "- 30g – ₹10\n"
            "- 55g – ₹20\n"
            "- 90g – ₹35\n"
            "- 115g – ₹50\n\n"
            "Pack sizes:\n"
            "- 30g\n"
            "- 55g\n"
            "- 90g\n"
            "- 115g\n\n"
            "Would you like to buy it?"
        )
        return Response(text, mimetype="text/plain")

    @app.post("/api/order")
    def order():
        """
        Request order: save name, phone, address and cart items.
        Returns success. Orders are stored in memory (ORDER_STORE).
        """
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        address = (data.get("address") or "").strip()
        items = data.get("items")
        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not phone:
            return jsonify({"error": "Phone is required"}), 400
        if not address:
            return jsonify({"error": "Address is required"}), 400
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"error": "At least one item is required"}), 400
        order_record = {
            "name": name,
            "phone": phone,
            "address": address,
            "items": [
                {
                    "productId": str(i.get("productId", "")),
                    "productName": str(i.get("productName", "")),
                    "quantity": int(i.get("quantity", 1)) if isinstance(i.get("quantity"), (int, float)) else 1,
                }
                for i in items[:50]
                if isinstance(i, dict)
            ],
        }
        ORDER_STORE.append(order_record)
        logger.warning(f"Order received from {name}: {len(order_record['items'])} item(s)")
        return jsonify({"success": True, "message": "Order received! We'll contact you soon."})

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
            t_request_start = time.perf_counter()
            logger.warning(f"📨 Received question: '{msg}'")
            logger.warning(f"📚 History: {len(history) if history else 0} messages")

            t_rag_start = time.perf_counter()
            res = answer_question(
                openai_api_key=s.openai_api_key,
                chat_model=s.openai_chat_model,
                embed_model=s.openai_embed_model,
                embed_dimensions=s.openai_embed_dimensions,
                persist_dir=s.chroma_persist_dir,
                question=msg,
                history=history,
            )
            t_rag_elapsed = time.perf_counter() - t_rag_start
            logger.warning(f"TIMING rag_total: {t_rag_elapsed:.3f}s")

            t_request_elapsed = time.perf_counter() - t_request_start
            logger.warning(f"TIMING request_total: {t_request_elapsed:.3f}s")
            logger.warning(f"✅ Answer length: {len(res.answer)} chars")
            return jsonify({"answer": res.answer, "answer_lines": list(res.answer_lines)})
        except Exception as e:
            logger.exception("❌ Chat request failed")
            return jsonify({"error": "Something went wrong. Please try again."}), 500

    # One-app: serve React site at / when built (product listing + chat)
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    site_dir = os.path.join(static_dir, "site")
    site_has_build = os.path.isfile(os.path.join(site_dir, "index.html"))

    if site_has_build:

        @app.get("/")
        def index():
            return send_from_directory(site_dir, "index.html")

        @app.get("/<path:path>")
        def serve_site(path):
            if not path or path.startswith("api/") or path == "health":
                from flask import abort
                abort(404)
            file_path = os.path.join(site_dir, path)
            if os.path.isfile(file_path):
                return send_from_directory(site_dir, path)
            return send_from_directory(site_dir, "index.html")  # SPA fallback
    else:

        @app.get("/")
        def index_missing():
            return Response(
                "<!doctype html><html><body style='font-family:sans-serif;padding:2rem;'><h1>Snackbot</h1><p>Build the web app first:</p><pre>npm run build:web</pre><p>From repo root, or <code>cd apps/snackbot-web && npm run build</code></p></body></html>",
                mimetype="text/html",
            )

    return app


def main() -> None:
    app = create_app()
    s = load_settings()
    debug = os.getenv("FLASK_DEBUG", "0").strip().lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=s.port, debug=debug)


if __name__ == "__main__":
    main()
