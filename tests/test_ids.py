import pytest

from arxiv2md import ids


@pytest.mark.parametrize(
    "text, expected",
    [
        ("2607.01456v2", "2607.01456v2"),
        ("2607.01456", "2607.01456"),
        ("https://arxiv.org/abs/2607.01456v2", "2607.01456v2"),
        ("https://arxiv.org/html/2607.01456v2/", "2607.01456v2"),
        ("https://arxiv.org/pdf/2607.01456v2.pdf", "2607.01456v2"),
        ("arxiv.org/pdf/2607.01456", "2607.01456"),
        ("hep-th/9901001v1", "hep-th/9901001v1"),
    ],
)
def test_parse_arxiv_ref(text, expected):
    assert ids.parse_arxiv_ref(text) == expected


@pytest.mark.parametrize("text", ["", "hello", "https://example.com/abs/2607.01456"])
def test_parse_rejects_garbage(text):
    with pytest.raises(ValueError):
        ids.parse_arxiv_ref(text)


def test_versions():
    assert ids.has_version("2607.01456v2")
    assert not ids.has_version("2607.01456")
    assert ids.version_from_url("https://arxiv.org/html/2607.01456v3") == "2607.01456v3"
    assert ids.version_from_url("https://arxiv.org/abs/2607.01456") is None
