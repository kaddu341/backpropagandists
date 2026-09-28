"""Throwaway Sphinx builds that run the real docs/conf.py on fixture pages."""

import re
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def build(tmp_path: Path, index_md: str) -> str:
    """Build a one-page site with the real conf.py and return index.html."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "index.md").write_text(index_md)
    # conf.py sets external_toc_path = "../_toc.yml", relative to the source dir.
    (tmp_path / "_toc.yml").write_text("root: index\n")
    out = tmp_path / "out"
    subprocess.run(
        [sys.executable, "-m", "sphinx", "-W", "-q", "-c", str(DOCS), str(src), str(out)],
        check=True,
    )
    return (out / "index.html").read_text()


MATH_PAGE = r"""# Math

Inline $E = mc^2$ in a sentence.

\begin{align}
  \nabla \cdot \mathbf{E} &= \rho / \varepsilon_0 \\
  \nabla \cdot \mathbf{B} &= 0
\end{align}
"""


def test_inline_and_bare_align_math_render(tmp_path):
    html = build(tmp_path, MATH_PAGE)
    assert re.search(r'<span class="math[^"]*">\\\(E = mc\^2\\\)</span>', html)
    # amsmath blocks get an equation-number <span> before the \[...\] payload.
    assert re.search(r'<div class="amsmath math[^"]*"[^>]*>.*?\\\[\\begin\{align\}', html, re.S)
