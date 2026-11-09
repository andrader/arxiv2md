"""Command line entry point."""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from . import convert, fetch, figures, ids, postprocess


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="arxiv2md",
        description="Convert an arXiv paper's HTML version to markdown files.",
    )
    p.add_argument("paper", help="arXiv id (2607.01456v2, versionless ok) or abs/html/pdf URL")
    p.add_argument("-o", "--outdir", type=Path, help="output directory (default: ./arxiv/<id>)")
    return p


def download_page(ref: str) -> tuple[str, str, str]:
    """Return (html, final_url, ref_with_version)."""
    try:
        resp = fetch.fetch(ids.html_url(ref))
    except fetch.NotFound:
        raise SystemExit(
            f"error: arXiv has no HTML version of {ref}.\n"
            f"PDF conversion is not supported; get the PDF at {ids.pdf_url(ref)}"
        ) from None
    full = ref if ids.has_version(ref) else ids.version_from_url(resp.final_url) or ref
    return resp.data.decode("utf-8", errors="replace"), resp.final_url, full


def download_figures(html: str, final_url: str, workdir: Path) -> None:
    for src, url in figures.local_figures(html, final_url).items():
        try:
            resp = fetch.fetch(url)
        except (fetch.NotFound, OSError) as e:
            print(f"warning: could not download figure {src}: {e}", file=sys.stderr)
            continue
        if not figures.looks_like_image(src, resp.data):
            print(f"warning: {url} is not a valid image, skipped", file=sys.stderr)
            continue
        target = workdir / src
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(resp.data)


def write_output(md: str, workdir: Path, outdir: Path) -> list[str]:
    sections = postprocess.split_sections(md)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, text in sections:
        (outdir / name).write_text(text, encoding="utf-8")
    paper = postprocess.join_sections(sections)
    (outdir / "paper.md").write_text(paper, encoding="utf-8")
    for rel in postprocess.media_references(paper):
        src = workdir / rel
        if not src.is_file():
            print(f"warning: referenced media missing: {rel}", file=sys.stderr)
            continue
        dest = outdir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    return [name for name, _ in sections]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        ref = ids.parse_arxiv_ref(args.paper)
        convert.pandoc_path()
    except (ValueError, convert.PandocMissing) as e:
        raise SystemExit(f"error: {e}") from None

    html, final_url, full_ref = download_page(ref)
    outdir = args.outdir or Path("arxiv") / full_ref.replace("/", "_")
    with tempfile.TemporaryDirectory(prefix="arxiv2md-") as tmp:
        workdir = Path(tmp)
        (workdir / "paper.html").write_text(html, encoding="utf-8")
        download_figures(html, final_url, workdir)
        md = postprocess.trim_chrome(convert.html_to_markdown(workdir))
        names = write_output(md, workdir, outdir)
    print(f"wrote paper.md and {len(names)} section files to {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
