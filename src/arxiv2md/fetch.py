"""Network access: the only module that talks to arxiv.org."""

import time
import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "arxiv2md/0.1"
DELAY_S = 0.5


class NotFound(Exception):
    """The URL returned 404."""


@dataclass
class Response:
    data: bytes
    final_url: str
    content_type: str


def fetch(url: str, timeout: float = 60) -> Response:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp = Response(r.read(), r.geturl(), r.headers.get("Content-Type", ""))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise NotFound(url) from e
        raise
    time.sleep(DELAY_S)
    return resp
