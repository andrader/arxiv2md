from arxiv2md import postprocess as pp

RAW = """![](data:image/svg+xml;base64,AAAA)

Report Issue chrome

# My Title

Alice Affiliation: X

###### Abstract

We study things.

## I Introduction

Intro text.

### A Subsection

More.

## II Related Work

![Refer to caption](media/2607.01456v2/fig.png)

![](media/abc123.svg)

![again](media/abc123.svg)

## References

- \\[1\\] Ref.

Experimental support, please view the build logs.

## Instructions for reporting errors

Click Report Issue.
"""


def test_trim_chrome():
    out = pp.trim_chrome(RAW)
    assert out.startswith("# My Title")
    assert "Report Issue" not in out
    assert "Experimental support" not in out
    assert out.rstrip().endswith("- \\[1\\] Ref.")


def test_slugify():
    assert pp.slugify("## I Introduction") == "introduction"
    assert pp.slugify("## VI Threats to Validity") == "threats-to-validity"
    assert pp.slugify("## References") == "references"
    assert pp.slugify("## Visual Methods") == "visual-methods"
    assert pp.slugify("## 3 Results & Discussion") == "3-results-discussion"


def test_split_sections():
    sections = pp.split_sections(pp.trim_chrome(RAW))
    assert [n for n, _ in sections] == [
        "00-abstract.md",
        "01-introduction.md",
        "02-related-work.md",
        "03-references.md",
    ]
    assert sections[0][1].startswith("# My Title")
    assert "We study things." in sections[0][1]
    assert "### A Subsection" in sections[1][1]  # `###` does not split


def test_join_roundtrip():
    trimmed = pp.trim_chrome(RAW)
    joined = pp.join_sections(pp.split_sections(trimmed))
    assert joined.split() == trimmed.split()


def test_split_ignores_headings_in_code_fences():
    md = "# T\n\n## A\n\n```\n## not a heading\n```\n"
    assert len(pp.split_sections(md)) == 2


def test_media_references():
    assert pp.media_references(pp.trim_chrome(RAW)) == [
        "media/2607.01456v2/fig.png",
        "media/abc123.svg",
    ]
