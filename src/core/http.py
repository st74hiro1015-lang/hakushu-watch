from __future__ import annotations

import time

from curl_cffi import requests as cffi_requests

# curl_cffi with Chrome TLS fingerprint is needed for Suntory (Akamai WAF blocks
# stock httpx). It also works fine for the other sources, so we use it for all.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
}
TIMEOUT = 30
RETRY_BACKOFF = (1, 4, 16)
IMPERSONATE = "chrome"


class FetchError(Exception):
    pass


def fetch(url: str, *, headers: dict[str, str] | None = None) -> str:
    """Fetch URL with retry on 5xx and transient errors. Returns response text."""
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    last_exc: Exception | None = None
    for attempt, delay in enumerate(RETRY_BACKOFF, start=1):
        try:
            resp = cffi_requests.get(
                url,
                headers=merged_headers,
                timeout=TIMEOUT,
                impersonate=IMPERSONATE,
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return resp.text
            if 500 <= resp.status_code < 600:
                last_exc = FetchError(f"HTTP {resp.status_code} from {url}")
            else:
                raise FetchError(f"HTTP {resp.status_code} from {url}")
        except cffi_requests.errors.RequestsError as e:
            last_exc = e
        if attempt < len(RETRY_BACKOFF):
            time.sleep(delay)
    raise FetchError(f"Failed after {len(RETRY_BACKOFF)} attempts: {url}") from last_exc
