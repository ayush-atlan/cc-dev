"""Browser chat for the Stock agent — a lazy Streamlit replacement, no npm/React/build.

Wraps the existing localdev Conversation (same agent, same Claude subscription as chat_cli.py) and
serves a single dark chat page. Single local user → one Conversation, requests serialize on it.

Run from the repo root:  .venv/bin/python chat/server.py   then open http://localhost:8765
Pick a different agent:   CHAT_AGENT=demo .venv/bin/python chat/server.py
"""
import json
import os
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "localdev"))   # so `import runner` works
os.chdir(ROOT)                                 # agent dirs (e.g. "stock") resolve from repo root

from runner import Conversation  # noqa: E402

AGENT = os.environ.get("CHAT_AGENT", "stock")
CHAT_HTML = (pathlib.Path(__file__).parent / "index.html").read_text()
LANDING = ROOT / "product" / "index.html"
_conv = None


def get_conv() -> Conversation:
    global _conv
    if _conv is None:
        print(f"  [chat] starting agent '{AGENT}' (first message warms up the MCP)…")
        _conv = Conversation(AGENT)
    return _conv


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):   # the product landing page
            self._send(200, LANDING.read_text(), "text/html; charset=utf-8")
        elif self.path in ("/chat", "/chat.html"):   # the chat UI
            self._send(200, CHAT_HTML, "text/html; charset=utf-8")
        elif self.path == "/agent":
            self._send(200, json.dumps({"agent": AGENT}))
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, "{}")
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            msg = (json.loads(self.rfile.read(n) or "{}").get("message") or "").strip()
        except Exception:
            return self._send(400, json.dumps({"error": "bad request"}))
        if not msg:
            return self._send(400, json.dumps({"error": "empty message"}))
        c = get_conv()
        seen = len(c.tool_calls)
        try:
            reply = c.send(msg)
        except Exception as e:
            return self._send(500, json.dumps({"error": str(e)}))
        tools = [{"tool": a["tool"], "input": a["input"]} for a in c.tool_calls[seen:]]
        self._send(200, json.dumps({"reply": reply, "tools": tools}, default=str))

    def log_message(self, *_):  # quiet
        pass


if __name__ == "__main__":
    port = int(os.environ.get("CHAT_PORT", "8765"))
    print(f"Scott → landing http://localhost:{port}/   ·   chat http://localhost:{port}/chat"
          f"   (agent: {AGENT})   Ctrl-C to stop.")
    try:
        HTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        if _conv:
            _conv.close()
        print("\nbye 🍔")
