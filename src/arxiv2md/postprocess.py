"""Markdown post-processing: trim page chrome, split sections, find media (pure functions)."""

import re

_ROMAN_PREFIX = re.compile(r"^[IVXLC]+\s+(?=\S)")
_MEDIA_RE = re.compile(r"\]\((media/[^)\s]+)\)")


def trim_chrome(md: str) -> str:
    """Drop everything before the `# title` heading and the LaTeXML footer."""
    lines = md.splitlines()
    start = next((i for i, ln in enumerate(lines) if re.match(r"# \S", ln)), 0)
    end = next(
        (i for i, ln in enumerate(lines) if i > start and ln.startswith("Experimental support")),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip() + "\n"


def slugify(heading: str) -> str:
    """'## I Introduction' -> 'introduction'."""
    text = heading.lstrip("#").strip()
    text = _ROMAN_PREFIX.sub("", text)
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def split_sections(md: str) -> list[tuple[str, str]]:
    """Split at top-level `## ` headings into (filename, text) pairs.

    The first file ('00-abstract.md') holds everything before the first `## `
    (title, authors, abstract). Concatenating the texts gives back the paper.
    """
    parts: list[list[str]] = [[]]
    heads: list[str] = ["abstract"]
    fenced = False
    for line in md.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            parts.append([])
            heads.append(slugify(line))
        parts[-1].append(line)
    return [
        (f"{i:02d}-{slug}.md", "\n".join(body).strip() + "\n\n")
        for i, (slug, body) in enumerate(zip(heads, parts))
    ]  # fmt: skip


def join_sections(sections: list[tuple[str, str]]) -> str:
    return "".join(text for _, text in sections)


def media_references(md: str) -> list[str]:
    """Relative media paths (e.g. 'media/abc.svg') referenced by the markdown, in order."""
    return list(dict.fromkeys(_MEDIA_RE.findall(md)))
