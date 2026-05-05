"""One-shot helper to capture your LINE User ID.

Usage:
    1. Run this script:    python -m tools.dump_user_id
    2. In another terminal: ngrok http 8000
    3. In LINE Developers Console for your channel:
       - Webhook URL: https://<ngrok-id>.ngrok-free.app/webhook
       - Use webhook: ON
       - Auto-reply / greeting: OFF (recommended)
    4. From your iPhone LINE, send any message to your bot.
    5. This script prints the User ID to stdout. Copy the U... string.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body)
            for ev in data.get("events", []):
                source = ev.get("source", {})
                uid = source.get("userId")
                if uid:
                    print(f"\n>>> LINE_USER_ID = {uid}\n", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"parse error: {e}", flush=True)
        self.send_response(200)
        self.end_headers()

    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args: object, **kwargs: object) -> None:
        return


def main() -> None:
    addr = ("0.0.0.0", 8000)
    print(f"listening on http://{addr[0]}:{addr[1]} — point your LINE webhook here via ngrok")
    HTTPServer(addr, Handler).serve_forever()


if __name__ == "__main__":
    main()
