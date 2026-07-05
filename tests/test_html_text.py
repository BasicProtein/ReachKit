from reachkit.normalization.html_text import html_to_text


def test_html_to_text_extracts_title_and_visible_text():
    html = """
    <html><head><title> Example Page </title><style>.x{}</style></head>
    <body><h1>Hello</h1><script>alert(1)</script><p>World</p></body></html>
    """

    text, title = html_to_text(html)

    assert title == "Example Page"
    assert "Hello" in text
    assert "World" in text
    assert "alert" not in text


def test_html_to_text_ignores_template_content():
    text, title = html_to_text("<title>T</title><template>Hidden</template><p>Shown</p>")

    assert title == "T"
    assert text == "Shown"
