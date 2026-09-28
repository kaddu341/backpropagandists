"""Notebook support for myst-nb.

- read_ipynb: a notebook reader that renders images pasted into markdown cells.
  Jupyter stores a pasted image as a cell attachment (`![x](attachment:x.png)`),
  which myst-nb cannot resolve, so each one becomes a data: URI.
- setup: an extension that puts "Open in Colab" and "View on GitHub" badges
  at the top of every notebook page. The links come from the notebook's own
  path, so they cannot go stale the way hand-written badges do.
"""

import base64
from pathlib import Path

import nbformat
from docutils import nodes

REPO = "kaddu341/backpropagandists"  # must stay public: Colab only opens notebooks it can read
BRANCH = "main"
# Downloaded once, unmodified, and embedded, so pages make no request to Google or shields.io:
#   colab.svg  <- https://colab.research.google.com/assets/colab-badge.svg
#   github.svg <- https://img.shields.io/badge/View%20on-GitHub-181717?logo=github
BADGES = Path(__file__).parent / "badges"


def read_ipynb(text):
    nb = nbformat.reads(text, as_version=4)
    for cell in nb.cells:
        for name, bundle in cell.pop("attachments", {}).items():
            mime, data = next(iter(bundle.items()))  # Jupyter stores one mime type per paste
            cell.source = cell.source.replace(f"attachment:{name}", f"data:{mime};base64,{data}")
    return nb


def badge(svg, alt, url):
    data = base64.b64encode((BADGES / svg).read_bytes()).decode()
    link = nodes.reference(refuri=url)
    link += nodes.image(uri=f"data:image/svg+xml;base64,{data}", alt=alt)
    return link


def add_badges(app, doctree):
    source = app.env.doc2path(app.env.docname, base=False)  # relative to docs/
    if source.suffix != ".ipynb":
        return
    blob = f"{REPO}/blob/{BRANCH}/docs/{source.as_posix()}"
    row = nodes.paragraph(classes=["nb-badges"])
    row += badge("colab.svg", "Open in Colab", f"https://colab.research.google.com/github/{blob}")
    row += nodes.Text(" ")
    row += badge("github.svg", "View on GitHub", f"https://github.com/{blob}")
    doctree.insert(0, row)  # top of the page, above the title, like the PyTorch tutorials


def setup(app):
    # Run before Sphinx's image collector (priority 500), so it registers the badges too.
    app.connect("doctree-read", add_badges, priority=400)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
