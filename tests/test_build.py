"""Throwaway Sphinx builds that run the real docs/conf.py on fixture pages."""

import re
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def build(tmp_path: Path, pages: dict[str, str], resources: str | None = None):
    """Build `pages` ({docname: markdown, or "name.ipynb": json}) with the real conf.py into <tmp>/out.

    Every page except index is listed in the toc. `resources` (YAML text) goes
    to <tmp>/data/resources.yaml, which is where the extension looks relative to
    the source directory.
    """
    src = tmp_path / "src"
    for name, text in pages.items():
        path = src / (name if name.endswith(".ipynb") else f"{name}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    # conf.py sets external_toc_path = "../_toc.yml", relative to the source dir.
    entries = "".join(f"  - file: {name}\n" for name in pages if name != "index")
    (tmp_path / "_toc.yml").write_text("root: index\n" + (f"entries:\n{entries}" if entries else ""))
    if resources is not None:
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "resources.yaml").write_text(resources)
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-W", "-q", "-c", str(DOCS), str(src), str(tmp_path / "out")],
        capture_output=True,
        text=True,
    )


MATH_PAGE = r"""# Math

Inline $E = mc^2$ in a sentence.

\begin{align}
  \nabla \cdot \mathbf{E} &= \rho / \varepsilon_0 \\
  \nabla \cdot \mathbf{B} &= 0
\end{align}
"""


def test_inline_and_bare_align_math_render(tmp_path):
    proc = build(tmp_path, {"index": MATH_PAGE})
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "out" / "index.html").read_text()
    assert re.search(r'<span class="math[^"]*">\\\(E = mc\^2\\\)</span>', html)
    # amsmath blocks get an equation-number <span> before the \[...\] payload.
    assert re.search(r'<div class="amsmath math[^"]*"[^>]*>.*?\\\[\\begin\{align\}', html, re.S)


RESOURCES = """
- id: ext
  title: External Paper
  url: https://example.com/paper
  kind: paper
  topics: [x]
  level: foundational
  year: 2020
- id: ours
  doc: notebooks/nb
  kind: notebook
  topics: [x]
  level: intermediate
"""


def topic_page(topics):
    return f"# X\n\n```{{resource-list}}\n:topics: {topics}\n```\n"


def test_resource_list_renders_ours_first_with_both_link_kinds(tmp_path):
    pages = {"index": "# Home\n", "topics/x": topic_page("x"), "notebooks/nb": "# Our notebook\n"}
    proc = build(tmp_path, pages, RESOURCES)
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "out" / "topics" / "x.html").read_text()
    assert html.index("<h2>Our material") < html.index("<h2>Papers")
    assert re.search(r'<a class="reference internal" href="../notebooks/nb.html">.*Our notebook', html)
    assert 'href="https://example.com/paper"' in html
    assert 'class="ours"' in html
    # Kind is dropped where the group heading already says it; kept under "Our material".
    assert '<span class="meta">2020, foundational</span>' in html
    assert '<span class="meta">notebook, intermediate</span>' in html


def test_resource_list_unknown_topic_fails_build(tmp_path):
    pages = {"index": "# Home\n", "topics/x": topic_page("nope"), "notebooks/nb": "# Our notebook\n"}
    proc = build(tmp_path, pages, RESOURCES)
    assert proc.returncode != 0
    assert "nope" in proc.stderr


PNG_1PX = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def test_notebook_markdown_attachment_renders(tmp_path):
    import nbformat

    pasted = nbformat.v4.new_markdown_cell(
        "![pic](attachment:pic.png)", attachments={"pic.png": {"image/png": PNG_1PX}}
    )
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell("# NB"), pasted])
    proc = build(tmp_path, {"index": "# Home\n", "nb.ipynb": nbformat.writes(nb)})
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "out" / "nb.html").read_text()
    assert re.search(r'<img alt="pic" src="(?!attachment:)[^"]+"', html)
