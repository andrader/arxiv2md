from arxiv2md import figures

URL = "https://arxiv.org/html/2607.01456v2"

HTML = """
<img src="https://static.arxiv.org/logo.svg">
<img src="data:image/svg+xml;base64,AAAA">
<img src="/static/icon.png">
<img class="x" src="2607.01456v2/overall.png" alt="">
<img src='2607.01456v2/b.png'>
"""


def test_resolve_has_no_doubled_id():
    assert (
        figures.resolve_figure_url(URL, "2607.01456v2/overall.png")
        == "https://arxiv.org/html/2607.01456v2/overall.png"
    )
    assert figures.resolve_figure_url(URL + "/", "2607.01456v2/overall.png").endswith(
        "/html/2607.01456v2/overall.png"
    )


def test_local_figures_skips_chrome():
    assert figures.local_figures(HTML, URL) == {
        "2607.01456v2/overall.png": "https://arxiv.org/html/2607.01456v2/overall.png",
        "2607.01456v2/b.png": "https://arxiv.org/html/2607.01456v2/b.png",
    }


def test_looks_like_image():
    assert figures.looks_like_image("a.png", b"\x89PNG\r\n\x1a\nxxxx")
    assert not figures.looks_like_image("a.png", b"<!DOCTYPE html><html>404")
    assert figures.looks_like_image("a.svg", b'<svg xmlns="..."></svg>')
