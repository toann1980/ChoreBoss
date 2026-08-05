from pathlib import Path


STYLESHEET = Path(__file__).parents[1] / "web" / "static" / "css" / "styles.css"


def _rule_block(css: str, selector: str) -> str:
    start = css.index(f"{selector} {{")
    end = css.index("}", start)
    return css[start:end]


def test_home_page_uses_document_scroll_for_header_image() -> None:
    css = STYLESHEET.read_text()
    body = _rule_block(css, "body")
    header = _rule_block(css, "header")
    logo = _rule_block(css, ".svg-logo")
    main = _rule_block(css, "main")

    assert "display: flex" not in body
    assert "\n    height: 100vh;" not in body
    assert "overflow: hidden" not in body
    assert "overflow-y: auto" in body
    assert "\n    height: 50vh;" not in header
    assert "height: auto" in header
    assert "height: 25vh" in logo
    assert "max-height: 25vh" in logo
    assert "width: auto" in logo
    assert "overflow-y: auto" not in main
    assert "overflow: visible" in main
