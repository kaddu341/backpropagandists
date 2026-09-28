# Phase 1: Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an empty but correctly configured Sphinx site that builds under
`-W`, renders inline and `\begin{align}` math, and is served by
`sphinx-autobuild`.

**Architecture:** The Sphinx source dir is `docs/`. Navigation comes only from
`_toc.yml` at the repo root. `conf.py` also derives Shibuya's top-bar
`nav_links` from that file, so no navigation is duplicated. A pytest test
builds a throwaway page using the real `docs/conf.py` (via `-c docs`) to prove
the math configuration works.

**Tech Stack:** Python 3.13, uv, Sphinx 9.1, myst-nb 1.4 (which loads
myst-parser), sphinx-design, sphinx-external-toc, Shibuya, pytest.

Spec: `plans/2026-09-28-wiki-design.md`.

**Facts verified against the installed packages (do not re-derive):**
- `external_toc_path` is resolved relative to `app.srcdir` (`sphinx_external_toc/events.py:67`).
- Shibuya's `nav_links` URLs that aren't `http(s)` go through `pathto()`, so
  docnames work (`shibuya/theme/shibuya/components/nav-links.html`).
- Shibuya hides the "Copy page" button only when `meta.hide_ai_links == "true"`.
  MyST turns a YAML `true` into the string `"True"`
  (`myst_parser/mdit_to_docutils/base.py:1345-1347`), so the front matter must
  be the **quoted string** `hide_ai_links: "true"`.
- Shibuya picks a per-page layout from `meta.layout`, so `index.md` gets
  `layout: landing`. Every other page uses the theme default, `default`.
- `myst_nb` loads `myst_parser` itself. Never list both in `extensions`.
- The Foundations section (notebooks) is **not** added in this phase. A
  `_toc.yml` entry for a file that doesn't exist yet is a build error. It
  arrives in Phase 3.

---

## File map

| File | Responsibility |
|------|----------------|
| `pyproject.toml`, `uv.lock` | add `pyyaml` (runtime, used by conf.py) and `pytest` (dev group), both pinned exactly |
| `tests/test_build.py` | throwaway build with the real `conf.py`; asserts that inline and align math render |
| `docs/conf.py` | all Sphinx config, short and commented |
| `_toc.yml` | the only navigation definition |
| `docs/index.md` | landing page: name, tagline, one card per section |
| `docs/topics/{diffusion,flow-matching,reinforcement-learning}.md` | stub topic pages |
| `CLAUDE.md` | status update |

---

### Task 1: Runtime and dev dependencies

**Files:**
- Modify: `pyproject.toml`, `uv.lock` (via uv)

- [ ] **Step 1: Add pinned deps**

```bash
uv add --bounds exact pyyaml
uv add --dev --bounds exact pytest
```

- [ ] **Step 2: Verify pins**

Run: `grep -E 'pyyaml|pytest' pyproject.toml`
Expected: both lines use `==` pins. `pytest` must sit under
`[dependency-groups] dev`.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "Add pyyaml and pytest (pinned)"
```

---

### Task 2: Failing math acceptance test

**Files:**
- Create: `tests/test_build.py`

- [ ] **Step 1: Write the test**

```python
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
    assert re.search(r'<div class="math[^"]*"[^>]*>\s*\\begin\{align\}', html)
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `uv run pytest tests/test_build.py -v`
Expected: FAIL with `CalledProcessError`. Sphinx reports that the config
directory doesn't contain a `conf.py`.

---

### Task 3: `conf.py` and `_toc.yml`

**Files:**
- Create: `docs/conf.py`
- Create: `_toc.yml`

- [ ] **Step 1: Write `_toc.yml`**

```yaml
# Site navigation. This is the ONLY place it is defined: no toctree
# directives in pages. Each subtree is a sidebar section, and its caption also
# becomes a top-bar link to the section's first page (see docs/conf.py).
root: index
subtrees:
  - caption: Generative models
    entries:
      - file: topics/diffusion
      - file: topics/flow-matching
  - caption: Reinforcement learning
    entries:
      - file: topics/reinforcement-learning
```

- [ ] **Step 2: Write `docs/conf.py`**

```python
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
```

- [ ] **Step 3: Run the math test and confirm it passes**

Run: `uv run pytest tests/test_build.py -v`
Expected: PASS. If a regex fails, look at the actual markup with
`grep -o '<[^>]*class="math[^>]*>[^<]*' <tmp>/out/index.html`. Fix the
**regex** so it matches the actual MathJax markup. Do not change the page
content.

- [ ] **Step 4: Commit**

```bash
git add tests/test_build.py docs/conf.py _toc.yml
git commit -m "Add conf.py, _toc.yml, and math acceptance test"
```

---

### Task 4: Landing page and stub topic pages

**Files:**
- Create: `docs/index.md`
- Create: `docs/topics/diffusion.md`, `docs/topics/flow-matching.md`, `docs/topics/reinforcement-learning.md`

- [ ] **Step 1: Confirm the real site currently fails**

Run: `uv run sphinx-build -W -b html docs _build/html`
Expected: FAIL. The pages that `_toc.yml` references don't exist yet.

- [ ] **Step 2: Write `docs/index.md`**

The tagline is the README's. There is no other prose, because the user writes
the content.

```markdown
---
layout: landing
---

# backpropagandists

Machine learning learning

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Generative models
:link: topics/diffusion
:link-type: doc
:::

:::{grid-item-card} Reinforcement learning
:link: topics/reinforcement-learning
:link-type: doc
:::
::::
```

- [ ] **Step 3: Write the three stub topic pages**

The only thing that differs between them is the H1. The `resource-list`
directive is added to these pages in Phase 2.

`docs/topics/diffusion.md`:
```markdown
---
hide_ai_links: "true"  # must be a quoted string: Shibuya compares against "true"
---

# Diffusion models
```

`docs/topics/flow-matching.md`:
```markdown
---
hide_ai_links: "true"  # must be a quoted string: Shibuya compares against "true"
---

# Flow matching
```

`docs/topics/reinforcement-learning.md`:
```markdown
---
hide_ai_links: "true"  # must be a quoted string: Shibuya compares against "true"
---

# Reinforcement learning
```

- [ ] **Step 4: Strict build passes**

Run: `uv run sphinx-build -W -b html docs _build/html`
Expected: `build succeeded.` with no warnings.

- [ ] **Step 5: Verify the rendered output**

```bash
grep -c 'copy-page-wrapper' _build/html/topics/diffusion.html   # expect 0 (hidden on topic pages)
grep -c 'copy-page-wrapper' _build/html/index.html              # expect 1 (kept elsewhere)
grep -o 'href="topics/diffusion.html"' _build/html/index.html | head -1   # top-bar and card links resolve
```

- [ ] **Step 6: Commit**

```bash
git add docs/index.md docs/topics/
git commit -m "Add landing page and stub topic pages"
```

---

### Task 5: Dev server and phase wrap-up

**Files:**
- Modify: `CLAUDE.md` (status line)
- Modify: `plans/2026-09-28-wiki-design.md` (record the facts learned in this phase)

- [ ] **Step 1: Confirm `sphinx-autobuild` serves**

Run the CLAUDE.md command in the background on port 8000. If it errors
because `data/` or `_ext/` don't exist yet, drop those two `--watch` flags for
Phase 1, since they arrive in Phase 2. Then check the server and stop it:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/   # expect 200
```

- [ ] **Step 2: Update the spec with what this phase settled**

In `plans/2026-09-28-wiki-design.md`:
- Add `tests/test_build.py` to the Layout block.
- Record that `nav_links` is derived from `_toc.yml` in `conf.py`.
- Replace the "check how MyST passes a YAML bool" sentence with: must be
  `hide_ai_links: "true"`, quoted.

- [ ] **Step 3: Update the CLAUDE.md status line**

Change it to: "Status: Phase 1 (skeleton) done; see `plans/` for the next
phase."

- [ ] **Step 4: Full verification**

```bash
uv run pytest -v
uv run sphinx-build -W -b html docs _build/html
```
Expected: both pass.

- [ ] **Step 5: Commit and stop for user review**

```bash
git add CLAUDE.md plans/
git commit -m "Phase 1 done: record settled details in spec and CLAUDE.md"
```
