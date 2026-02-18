/**
 * Snackbot widget – adds ONLY a floating button (bottom-right) + chat panel when clicked.
 * No full page. Paste this script on your site and the button sticks to the bottom-right.
 * Usage: <script src="https://YOUR-API-URL/widget.js"></script>
 */
(function() {
  'use strict';

  var script = document.currentScript;
  var baseUrl = script ? new URL(script.src).origin : '';

  var css = (
    '.snackbot-root{--sb-bg:#0b1220;--sb-panel:#0f1a2f;--sb-text:#e8eefc;--sb-muted:#a9b6d2;--sb-accent:#7c5cff;--sb-border:#1c2a4a;}' +
    '.snackbot-root *{box-sizing:border-box;}' +
    '.snackbot-root{position:fixed;bottom:20px;right:20px;z-index:999999;font-size:15px;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;}' +
    '.snackbot-bubble{display:flex;align-items:center;justify-content:center;gap:8px;padding:14px 20px;background:var(--sb-accent);color:#fff;border:none;border-radius:28px;font-weight:600;cursor:pointer;box-shadow:0 4px 14px rgba(124,92,255,.4);}' +
    '.snackbot-bubble:hover{filter:brightness(1.08);}' +
    '.snackbot-bubble svg{width:22px;height:22px;flex-shrink:0;}' +
    '.snackbot-panel{display:none;width:380px;max-width:calc(100vw - 24px);height:520px;max-height:calc(100vh - 24px);flex-direction:column;background:var(--sb-bg);color:var(--sb-text);border:1px solid var(--sb-border);border-radius:12px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,.3);}' +
    '.snackbot-root.expanded .snackbot-bubble{display:none;}' +
    '.snackbot-root.expanded .snackbot-panel{display:flex;}' +
    '.snackbot-wrap{flex:1;display:flex;flex-direction:column;min-height:0;}' +
    '.snackbot-head{padding:12px 14px;background:linear-gradient(180deg,var(--sb-panel),var(--sb-bg));border-bottom:1px solid var(--sb-border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}' +
    '.snackbot-head .snackbot-title{font-weight:700;letter-spacing:.2px;}' +
    '.snackbot-head-actions{display:flex;gap:8px;align-items:center;}' +
    '.snackbot-btn-min{background:transparent;border:none;color:var(--sb-muted);cursor:pointer;padding:6px 10px;font-size:12px;border-radius:8px;}' +
    '.snackbot-btn-min:hover{color:var(--sb-text);background:rgba(255,255,255,.06);}' +
    '.snackbot-log{flex:1;overflow:auto;padding:12px 14px;display:flex;flex-direction:column;gap:10px;min-height:0;}' +
    '.snackbot-msg{max-width:92%;padding:10px 12px;border-radius:12px;border:1px solid var(--sb-border);}' +
    '.snackbot-msg.user{align-self:flex-end;background:rgba(124,92,255,.15);}' +
    '.snackbot-msg.bot{align-self:flex-start;background:rgba(255,255,255,.06);}' +
    '.snackbot-meta{color:var(--sb-muted);font-size:11px;margin-top:6px;}' +
    '.snackbot-bar{display:flex;gap:10px;padding:12px 14px;border-top:1px solid var(--sb-border);background:rgba(255,255,255,.03);flex-shrink:0;}' +
    '.snackbot-input{flex:1;background:rgba(255,255,255,.06);border:1px solid var(--sb-border);border-radius:10px;padding:10px 12px;color:var(--sb-text);outline:none;min-width:0;}' +
    '.snackbot-btn{background:var(--sb-accent);border:none;color:#fff;padding:10px 14px;border-radius:10px;font-weight:600;cursor:pointer;}' +
    '.snackbot-btn:disabled{opacity:.6;cursor:not-allowed;}' +
    '.snackbot-btn.sec{background:transparent;color:var(--sb-muted);}' +
    '.snackbot-btn.sec:hover{color:var(--sb-text);background:rgba(255,255,255,.06);}' +
    '.snackbot-typing{color:var(--sb-muted);font-style:italic;}'
  );

  var html = (
    '<button type="button" class="snackbot-bubble" aria-label="Open chat">' +
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/></svg>' +
      '<span>Chat with us</span>' +
    '</button>' +
    '<div class="snackbot-panel">' +
      '<div class="snackbot-wrap">' +
        '<div class="snackbot-head">' +
          '<span class="snackbot-title">Snackbot</span>' +
          '<div class="snackbot-head-actions">' +
            '<button type="button" class="snackbot-btn sec snackbot-clear" style="padding:6px 10px;font-size:12px;">Clear</button>' +
            '<button type="button" class="snackbot-btn-min snackbot-min">Minimize</button>' +
          '</div>' +
        '</div>' +
        '<div class="snackbot-log" id="snackbot-log"></div>' +
        '<div class="snackbot-bar">' +
          '<input class="snackbot-input" id="snackbot-input" placeholder="Ask a question..." />' +
          '<button type="button" class="snackbot-btn" id="snackbot-send">Send</button>' +
        '</div>' +
      '</div>' +
    '</div>'
  );

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  var root = document.createElement('div');
  root.className = 'snackbot-root';
  root.id = 'snackbot-root';
  root.innerHTML = html;
  document.body.appendChild(root);

  var bubble = root.querySelector('.snackbot-bubble');
  var minBtn = root.querySelector('.snackbot-min');
  var logEl = root.querySelector('#snackbot-log');
  var inputEl = root.querySelector('#snackbot-input');
  var sendBtn = root.querySelector('#snackbot-send');
  var clearBtn = root.querySelector('.snackbot-clear');

  var maxHistoryTurns = 10;
  var conversationHistory = [];

  function openChat() { root.classList.add('expanded'); inputEl.focus(); }
  function closeChat() { root.classList.remove('expanded'); }
  bubble.addEventListener('click', openChat);
  minBtn.addEventListener('click', closeChat);

  function add(role, text, sources, opts) {
    opts = opts || {};
    var div = document.createElement('div');
    div.className = 'snackbot-msg ' + (role === 'user' ? 'user' : 'bot') + (opts.typing ? ' snackbot-typing' : '');
    div.textContent = text;
    if (role !== 'user' && sources && sources.length && !opts.typing) {
      var meta = document.createElement('div');
      meta.className = 'snackbot-meta';
      meta.textContent = 'Sources: ' + sources.map(function(s) { return s.product || s.title || s.url || s.chunk_id || ''; }).filter(Boolean).join(' · ');
      div.appendChild(meta);
    }
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
    return div;
  }

  function showWelcome() {
    add('bot', 'Hi! Ask me anything about the Snackbot products.');
  }

  clearBtn.addEventListener('click', function() {
    logEl.innerHTML = '';
    conversationHistory = [];
    showWelcome();
    inputEl.focus();
  });

  function ask() {
    var text = (inputEl.value || '').trim();
    if (!text) return;
    inputEl.value = '';
    add('user', text);
    sendBtn.disabled = true;
    var placeholder = add('bot', 'Thinking…', [], { typing: true });
    fetch(baseUrl + '/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: conversationHistory })
    })
      .then(function(res) { return res.json().then(function(data) { return { res: res, data: data }; }); })
      .then(function(_) {
        var res = _.res;
        var data = _.data;
        placeholder.remove();
        if (!res.ok) throw new Error(data.error || 'Request failed');
        var answer = data.answer || '(no answer)';
        add('bot', answer, data.sources || []);
        conversationHistory.push({ role: 'user', content: text });
        conversationHistory.push({ role: 'assistant', content: answer });
        if (conversationHistory.length > maxHistoryTurns * 2) {
          conversationHistory = conversationHistory.slice(-maxHistoryTurns * 2);
        }
      })
      .catch(function(e) {
        placeholder.remove();
        add('bot', 'Error: ' + (e.message || String(e)));
      })
      .finally(function() {
        sendBtn.disabled = false;
        inputEl.focus();
      });
  }

  sendBtn.addEventListener('click', ask);
  inputEl.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') ask();
  });

  showWelcome();
})();
