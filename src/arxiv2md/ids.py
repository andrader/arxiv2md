"""Parsing of arXiv identifiers and URLs (pure functions)."""

import re

_ID = r"(?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})"
_VERSION = r"(?:v\d+)?"
_ID_RE = re.compile(rf"^(?P<id>{_ID})(?P<version>v\d+)?$")
_URL_RE = re.compile(
    rf"^(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|html|pdf)/(?P<ref>{_ID}{_VERSION})(?:\.pdf)?/?(?:[?#].*)?$"
)


def parse_arxiv_ref(text: str) -> str:
    """Return the bare id (with version if given) from an id or arXiv URL."""
    text = text.strip()
    m = _URL_RE.match(text)
    ref = m.group("ref") if m else text
    if not _ID_RE.match(ref):
        raise ValueError(f"not an arXiv id or URL: {text!r}")
    return ref


def has_version(ref: str) -> bool:
    return re.search(r"v\d+$", ref) is not None


def version_from_url(url: str) -> str | None:
    """Return the id with version found in an arxiv.org/html URL, or None."""
    m = re.search(rf"/html/(?P<ref>{_ID}v\d+)", url)
    return m.group("ref") if m else None


def html_url(ref: str) -> str:
    return f"https://arxiv.org/html/{ref}"


def pdf_url(ref: str) -> str:
    return f"https://arxiv.org/pdf/{ref}"
