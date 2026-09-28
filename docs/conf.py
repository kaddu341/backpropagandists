"""Sphinx configuration. Every setting is commented. Read top to bottom."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent  # repo root; this file lives in docs/

# -- Project -------------------------------------------------------------------
project = "backpropagandists"
# `copyright` is deliberately unset until the group decides the footer text.

# -- Extensions ----------------------------------------------------------------
extensions = [
    "myst_nb",  # Markdown (MyST) and Jupyter notebooks; loads myst_parser itself
    "sphinx_design",  # cards, grids, tabs, dropdowns
    "sphinx_external_toc",  # navigation from _toc.yml instead of toctree directives
]

# -- Navigation ----------------------------------------------------------------
external_toc_path = "../_toc.yml"  # relative to this docs/ directory

# -- Markdown (MyST) -----------------------------------------------------------
myst_enable_extensions = [
    "amsmath",  # bare \begin{align}...\end{align} blocks, pasted straight from papers
    "dollarmath",  # $inline$ and $$display$$ math
    "colon_fence",  # ::: fences for directives (render sanely in plain Markdown viewers)
    "deflist",  # definition lists
    "fieldlist",  # :field: value lists
]

# -- Notebooks -----------------------------------------------------------------
# Never execute notebooks during the build: their outputs are committed. A
# light notebook can opt in through its own metadata, e.g.
# {"mystnb": {"execution_mode": "force"}}.
nb_execution_mode = "off"

# -- i18n (configured, not used yet) -------------------------------------------
language = "en"
locale_dirs = ["locale/"]
gettext_compact = False

# -- HTML / theme --------------------------------------------------------------
html_theme = "shibuya"
html_title = project
# The published site's URL. Shibuya needs it to render the "Copy page" button:
# the button fetches the page source from <baseurl>/_sources/, because the repo
# itself is private. Update it if the site moves (org account or custom domain).
html_baseurl = "https://kaddu341.github.io/backpropagandists/"
_toc = yaml.safe_load((ROOT / "_toc.yml").read_text())
html_theme_options = {
    # Top bar: one link per _toc.yml section, pointing at its first page, so
    # _toc.yml stays the only place navigation is defined. The landing page
    # picks its layout itself (`layout: landing` front matter in index.md).
    "nav_links": [
        {"title": section["caption"], "url": section["entries"][0]["file"]}
        for section in _toc["subtrees"]
    ],
}
