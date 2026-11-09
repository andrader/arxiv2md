"""Locating figure files referenced by the paper HTML (pure functions)."""

import re
from urllib.parse import urljoin

_IMG_SRC_RE = re.compile(r"<img\b[^>]*?\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)

_MAGIC = {
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".gif": b"GIF8",
}


def page_dir(final_url: str) -> str:
    """Directory URL of the page (with trailing slash) for resolving figure srcs."""
    return final_url.rstrip("/").rsplit("/", 1)[0] + "/"


def resolve_figure_url(final_url: str, src: str) -> str:
    """Resolve an <img src> against the page URL (a figure at 'ID/x.png' lives in /html/ID/x.png)."""
    return urljoin(final_url.rstrip("/"), src)


def local_figures(html: str, final_url: str) -> dict[str, str]:
    """Map each relative figure src (as written) to its absolute URL.

    Data URIs, absolute paths and URLs outside the page directory (site chrome) are skipped.
    """
    base = page_dir(final_url)
    found: dict[str, str] = {}
    for src in _IMG_SRC_RE.findall(html):
        if src.startswith(("data:", "/", "http:", "https:", "//")):
            continue
        url = resolve_figure_url(final_url, src)
        if url.startswith(base):
            found[src] = url
    return found


def looks_like_image(name: str, data: bytes) -> bool:
    """Check magic bytes so an HTML 404 page saved as a figure is detected."""
    lower = name.lower()
    for ext, magic in _MAGIC.items():
        if lower.endswith(ext):
            return data.startswith(magic)
    if lower.endswith(".svg"):
        return b"<svg" in data[:2048]
    return not data.lstrip()[:15].lower().startswith((b"<!doctype html", b"<html"))
