"""Sphinx configuration. Every setting is commented. Read top to bottom."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent  # repo root; this file lives in docs/
sys.path.insert(0, str(ROOT / "_ext"))  # our local extension(s)

# -- Project -------------------------------------------------------------------
project = "backpropagandists"
# `copyright` is deliberately unset until the group decides the footer text.

# -- Extensions ----------------------------------------------------------------
extensions = [
    "myst_nb",  # Markdown (MyST) and Jupyter notebooks; loads myst_parser itself
    "sphinx_design",  # cards, grids, tabs, dropdowns
    "sphinx_external_toc",  # navigation from _toc.yml instead of toctree directives
    "resources",  # _ext/resources.py: the `resource-list` directive over data/resources.yaml
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
# The SPS_Curriculum notebooks jump from H1 to H3 ("### Setup"). Remove this
# once their headings are fixed; it is the only warning type suppressed.
suppress_warnings = ["myst.header"]

# -- Notebooks -----------------------------------------------------------------
# Never execute notebooks during the build: their outputs are committed. A
# light notebook can opt in through its own metadata, e.g.
# {"mystnb": {"execution_mode": "force"}}.
nb_execution_mode = "off"
# Read .ipynb through _ext/nb_reader.py so that images pasted into markdown cells render.
nb_custom_formats = {".ipynb": ["nb_reader.read_ipynb", {}, False]}

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
templates_path = ["_templates"]  # partials/webfonts.html: stops Shibuya's Google Fonts request
html_static_path = ["_static"]  # self-hosted fonts + custom.css
html_css_files = ["custom.css"]  # all visual choices live there, commented
html_js_files = [("landscape.js", {"type": "module"})]  # landing-page art; does nothing on other pages
_toc = yaml.safe_load((ROOT / "_toc.yml").read_text())
html_theme_options = {
    "accent_color": "teal",  # Radix ramp nearest the pine-ink links: notes, tips, search highlights
    # Top bar: one link per _toc.yml section, pointing at its first page, so
    # _toc.yml stays the only place navigation is defined. The landing page
    # picks its layout itself (`layout: landing` front matter in index.md).
    "nav_links": [
        {"title": section["caption"], "url": section["entries"][0]["file"]}
        for section in _toc["subtrees"]
    ],
}
