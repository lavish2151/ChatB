/**
 * Snackbot widget – floating sticky button (Wix-safe version)
 * Usage:
 * <script src="https://YOUR-API-URL/widget.js"></script>
 */

(function () {
  "use strict";

  function initSnackbot() {

    var script = document.currentScript;
    var baseUrl = script ? new URL(script.src).origin : "";

    var css = `
    .snackbot-root{
      --sb-bg:#0b1220;
      --sb-panel:#0f1a2f;
      --sb-text:#e8eefc;
      --sb-muted:#a9b6d2;
      --sb-accent:#7c5cff;
      --sb-border:#1c2a4a;
      position:fixed !important;
      bottom:20px !important;
      right:20px !important;
      z-index:2147483647 !important;
      font-size:15px;
      font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
    }
    .snackbot-root *{box-sizing:border-box;}
    .snackbot-bubble{
      display:flex;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:14px 20px;
      background:var(--sb-accent);
      color:#fff;
      border:none;
      border-radius:28px;
      font-weight:600;
      cursor:pointer;
      box-shadow:0 4px 14px rgba(124,92,255,.4);
    }
    .snackbot-panel{
      display:none;
      width:380px;
      max-width:calc(100vw - 24px);
      height:520px;
      max-height:calc(100vh - 24px);
      flex-direction:column;
      background:var(--sb-bg);
      color:var(--sb-text);
      border:1px solid var(--sb-border);
      border-radius:12px;
      overflow:hidden;
      box-shadow:0 8px 32px rgba(0,0,0,.3);
    }
    .snackbot-root.expanded .snackbot-bubble{display:none;}
    .snackbot-root.expanded .snackbot-panel{display:flex;}
    .snackbot-head{
      padding:12px 14px;
      background:linear-gradient(180deg,var(--sb-panel),var(--sb-bg));
      border-bottom:1px solid var(--sb-border);
      display:flex;
      justify-content:space-between;
      align-items:center;
    }
    .snackbot-log{
      flex:1;
      overflow:auto;
      padding:12px 14px;
      display:flex;
      flex-direction:column;
      gap:10px;
    }
    .snackbot-msg{
      max-width:92%;
      padding:10px 12px;
      border-radius:12px;
      border:1px solid var(--sb-border);
    }
    .snackbot-msg.user{
      align-self:flex-end;
      background:rgba(124,92,255,.15);
    }
    .snackbot-msg.bot{
      align-self:flex-start;
      background:rgba(255,255,255,.06);
    }
    .snackbot-bar{
      display:flex;
      gap:10px;
      padding:12px 14px;
      border-top:1px solid var(--sb-border);
    }
    .snackbot-input{
      flex:1;
      background:rgba(255,255,255,.06);
      border:1px solid var(--sb-border);
      border-radius:10px;
      padding:10px 12px;
      color:var(--sb-text);
      outline:none;
    }
    .snackbot-btn{
      background:var(--sb-accent);
      border:none;
      color:#fff;
      padding:10px 14px;
      border-radius:10px;
      font-weight:600;
      cursor:pointer;
    }
    `;

    var styleEl = document.createElement("style");
    styleEl.innerHTML = css;
    document.head.appendChild(styleEl);

    var root = document.createElement("div");
    root.className = "snackbot-root";
    root.innerHTML = `
      <button class="snackbot-bubble">Chat with us</button>
      <div class="snackbot-panel">
        <div class="snackbot-head">
          <span>Snackbot</span>
          <button id="snackbot-min">Minimize</button>
        </div>
        <div class="snackbot-log" id="snackbot-log"></div>
        <div class="snackbot-bar">
          <input class="snackbot-input" id="snackbot-input" placeholder="Ask a question..." />
          <button class="snackbot-btn" id="snackbot-send">Send</button>
        </div>
      </div>
    `;

    // Attach directly to <html> (Wix safe)
    document.documentElement.appendChild(root);

    var bubble = root.querySelector(".snackbot-bubble");
    var panel = root.querySelector(".snackbot-panel");
    var minBtn = root.querySelector("#snackbot-min");
    var logEl = root.querySelector("#snackbot-log");
    var inputEl = root.querySelector("#snackbot-input");
    var sendBtn = root.querySelector("#snackbot-send");

    bubble.onclick = function () {
      root.classList.add("expanded");
      inputEl.focus();
    };

    minBtn.onclick = function () {
      root.classList.remove("expanded");
    };

    function add(role, text) {
      var div = document.createElement("div");
      div.className = "snackbot-msg " + role;
      div.textContent = text;
      logEl.appendChild(div);
      logEl.scrollTop = logEl.scrollHeight;
    }

    async function ask() {
      var text = inputEl.value.trim();
      if (!text) return;
      inputEl.value = "";
      add("user", text);

      const res = await fetch(baseUrl + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });

      const data = await res.json();
      add("bot", data.answer || "No answer");
    }

    sendBtn.onclick = ask;
    inputEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter") ask();
    });

    add("bot", "Hi! Ask me anything about the Snackbot products.");
  }

  // Wix-safe initialization
  if (document.readyState === "complete") {
    initSnackbot();
  } else {
    window.addEventListener("load", initSnackbot);
  }

})();
