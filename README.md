# arxiv2md

Convert the HTML version of an arXiv paper to markdown files.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [pandoc](https://pandoc.org/) (`brew install pandoc`)

## Usage

```
uv run arxiv2md 2607.01456v2 [-o OUTDIR]
```

Accepts an id with or without version (`2607.01456`, resolved from the redirect of
`arxiv.org/html/<id>`), or an `arxiv.org/abs/`, `/html/` or `/pdf/` URL.
Papers without an HTML version exit with an error and a PDF link (PDF conversion is not supported).

## Output

Default directory: `./arxiv/<id>/` (id with version).

```
paper.md            whole paper (concatenation of the section files)
00-abstract.md      title, authors, abstract
01-introduction.md  one file per top-level `## ` section, numbered and slugified
...
NN-references.md
media/              figures referenced by the markdown (links are relative)
```

arXiv page chrome (header, report-issue UI, LaTeXML footer) is dropped.

## Development

```
uv run pytest
```
