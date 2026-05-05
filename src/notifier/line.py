from __future__ import annotations

import os
import sys

import httpx

PUSH_URL = "https://api.line.me/v2/bot/message/push"
MAX_TEXT_LEN = 4900  # LINE limit is 5000; leave headroom for header.


class LineConfigError(RuntimeError):
    pass


def _config() -> tuple[str, str]:
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    if not token or not user_id:
        raise LineConfigError(
            "LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID must be set in environment"
        )
    return token, user_id


def push(text: str) -> None:
    """Send a single text message to the configured LINE user."""
    token, user_id = _config()
    body = text[:MAX_TEXT_LEN]
    payload = {"to": user_id, "messages": [{"type": "text", "text": body}]}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(PUSH_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"LINE push failed: {resp.status_code} {resp.text}")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        push("hakushu-watch test message")
        print("ok")
        return 0
    print("usage: python -m src.notifier.line --test", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
