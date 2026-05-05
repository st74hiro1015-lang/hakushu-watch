from __future__ import annotations

import hashlib
import re
import unicodedata

# Patterns that change between fetches but don't represent meaningful content updates.
NOISE_PATTERNS = [
    # ISO-ish timestamps (must run first; otherwise the date regex strips the date
    # prefix and leaves the T-time portion behind).
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+\-Z][^\s<]*)?"),
    # Timestamps in common formats
    re.compile(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?(?:\s*\d{1,2}:\d{2}(?::\d{2})?)?"),
    # CSRF / nonce / cache-bust query parameters
    re.compile(r"[?&](?:nonce|_|cache|t|v|ver|version|csrf|token)=[\w%.-]+", re.IGNORECASE),
    # Numeric session/visitor counters embedded in HTML
    re.compile(r"(?:visitors?|views?|閲覧数|アクセス数)[:：]?\s*[\d,]+", re.IGNORECASE),
    # Whitespace runs
    re.compile(r"\s+"),
]


def normalize(text: str) -> str:
    """Strip noise that varies between fetches without semantic meaning."""
    text = unicodedata.normalize("NFKC", text)
    for pat in NOISE_PATTERNS[:-1]:
        text = pat.sub("", text)
    text = NOISE_PATTERNS[-1].sub(" ", text)
    return text.strip()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_normalized(text: str) -> str:
    return sha256(normalize(text))
