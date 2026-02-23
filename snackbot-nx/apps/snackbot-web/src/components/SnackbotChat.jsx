import { useState, useRef, useEffect } from 'react';
import './SnackbotChat.css';

const MAX_HISTORY_TURNS = 10;

export default function SnackbotChat({ apiUrl }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi! I can help you learn about our products—ingredients, allergens, pricing, and more. What would you like to know?', sources: [] },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const logRef = useRef(null);
  const inputRef = useRef(null);

  const baseUrl = apiUrl || import.meta.env.VITE_SNACKBOT_API_URL || '';

  const history = messages
    .filter((m) => m.role === 'user' || m.role === 'bot')
    .slice(-MAX_HISTORY_TURNS * 2)
    .map((m) => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }));

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    if (open && inputRef.current) inputRef.current.focus();
  }, [open]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setLoading(true);
    const placeholder = { role: 'bot', text: 'Thinking…', sources: [], typing: true };
    setMessages((prev) => [...prev, placeholder]);

    try {
      const res = await fetch(`${baseUrl || ''}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history }),
      });
      const data = await res.json();
      setMessages((prev) =>
        prev.filter((m) => !m.typing).concat({
          role: 'bot',
          text: res.ok ? data.answer || '(no answer)' : `Error: ${data.error || 'Request failed'}`,
          lines: Array.isArray(data.answer_lines) ? data.answer_lines : null,
          sources: data.sources || [],
        })
      );
    } catch (e) {
      setMessages((prev) =>
        prev.filter((m) => !m.typing).concat({
          role: 'bot',
          text: `Error: ${e.message || e}`,
          sources: [],
        })
      );
    } finally {
      setLoading(false);
    }
  };

  const clear = () => {
    setMessages([
      { role: 'bot', text: 'Hi! I can help you learn about our products—ingredients, allergens, pricing, and more. What would you like to know?', sources: [] },
    ]);
  };

  return (
    <div className={`snackbot-root ${open ? 'expanded' : ''}`}>
      <button
        type="button"
        className="snackbot-bubble"
        onClick={() => setOpen(true)}
        aria-label="Open chat"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <span>Chat with us</span>
      </button>

      <div className="snackbot-panel">
        <div className="snackbot-wrap">
          <div className="snackbot-head">
            <span className="snackbot-title">Snackbot</span>
            <div className="snackbot-head-actions">
              <button type="button" className="snackbot-btn sec" onClick={clear}>
                Clear
              </button>
              <button type="button" className="snackbot-btn-min" onClick={() => setOpen(false)} aria-label="Minimize chat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div className="snackbot-log" ref={logRef}>
            {messages.map((m, i) => (
              <div
                key={i}
                className={`snackbot-msg ${m.role} ${m.typing ? 'typing' : ''}`}
              >
                {m.role === 'bot' && !m.typing ? (
                  <div className="bot-message">
                    {(() => {
                      const message = m.text || '';
                      const formattedMessage = message.replace(/\\n/g, '\n');
                      return formattedMessage.split('\n').map((line, index) => (
                        <div key={index}>{line}</div>
                      ));
                    })()}
                  </div>
                ) : (
                  m.text
                )}
                {m.role === 'bot' && m.sources?.length > 0 && (
                  <div className="snackbot-meta">
                    Sources: {m.sources.map((s) => s.product || s.title || s.url || s.chunk_id).filter(Boolean).join(' · ')}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="snackbot-bar">
            <input
              ref={inputRef}
              className="snackbot-input"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              disabled={loading}
            />
            <button type="button" className="snackbot-btn" onClick={send} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
