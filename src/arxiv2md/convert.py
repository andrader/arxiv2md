"""HTML to markdown conversion with pandoc."""

import shutil
import subprocess
from pathlib import Path


class PandocMissing(Exception):
    pass


def pandoc_path() -> str:
    path = shutil.which("pandoc") or (
        "/opt/homebrew/bin/pandoc" if Path("/opt/homebrew/bin/pandoc").exists() else None
    )
    if path is None:
        raise PandocMissing("pandoc not found; install it (e.g. `brew install pandoc`)")
    return path


def pandoc_command(pandoc: str, workdir: Path) -> list[str]:
    return [
        pandoc, "-f", "html", "-t", "gfm-raw_html", "--wrap=none",
        "--extract-media=media", f"--resource-path={workdir}", "paper.html",
    ]  # fmt: skip


def html_to_markdown(workdir: Path) -> str:
    """Convert workdir/paper.html; extracted media land in workdir/media."""
    result = subprocess.run(
        pandoc_command(pandoc_path(), workdir),
        cwd=workdir, capture_output=True, text=True, check=False,
    )  # fmt: skip
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed:\n{result.stderr}")
    return result.stdout
