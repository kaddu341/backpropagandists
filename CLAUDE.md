# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Sphinx-built learning-resources wiki for incoming postdocs/grad students in a
condensed-matter theory group: physicists who are new to ML. It is roughly 80%
curated links to external resources and 20% our own pages and notebooks. It
covers diffusion and flow matching first and reinforcement learning next, and
more topics get added over time. Deployed to GitHub Pages from a private repo.

Status: Phase 1 (skeleton) done; Phase 2 (resource system) is next. `plans/` holds the approved design
(`*-design.md`) and the per-phase task lists (`phase-*.md`, with checkboxes).
Read them before starting work, and tick boxes as tasks finish. Plans live
outside `docs/` on purpose: any file under `docs/` becomes a Sphinx page and
breaks the `-W` build.

## Hard rules

- **Never invent content.** No made-up URLs, paper titles, authors, years, or
  resource notes. Use `TODO:` placeholders and let the user fill them in. Topic
  pages stay empty until the user supplies the content.
- Content is Markdown (MyST) only. Never write RST.
- Navigation lives only in `_toc.yml` (sphinx-external-toc). Content files
  never contain `toctree` directives.
- No Sphinx extensions beyond the approved stack (sphinx, myst-parser, myst-nb,
  sphinx-design, sphinx-external-toc, shibuya, sphinx-autobuild) without
  asking. No autodoc, no Python package scaffolding, no CSS framework.
- Dependencies are managed with `uv`, with pinned versions in `pyproject.toml`
  and a committed `uv.lock`.
- Built HTML (`_build/`) is never committed.

## Architecture (target)

- `data/resources.yaml` is the single list of resources. A record has either
  `url:` (external) or `doc:` (our own page or notebook, which renders as an
  "ours" `{doc}` cross-reference). A topic is valid iff `docs/topics/<topic>.md`
  exists.
- `_ext/resources.py` is a local Sphinx extension that provides the
  `resource-list` directive. The directive filters the YAML by `:topics:` and
  emits a compact list grouped by kind ("Our material" first). Items within a
  group keep their YAML order, so the curator controls reading order. Bad data
  raises `ExtensionError`, which aborts the build.
- Adding a topic takes one `_toc.yml` entry, one thin `docs/topics/<topic>.md`
  containing a `resource-list` directive, and new YAML records. Nothing else.
- Theme: Shibuya, customized only via CSS variable overrides (`--sy-f-*`,
  `--sy-c-*`) in `docs/_static/custom.css`.
- i18n hooks (`language`, `locale_dirs`, `gettext_compact`) are set in
  `conf.py` but unused. English/Chinese will come later.

## Commands

```sh
uv sync                                                     # install env
uv run sphinx-autobuild docs _build/html --watch _toc.yml    # live dev server (add --watch data --watch _ext once they exist)
uv run sphinx-build -W -b html docs _build/html              # strict build (CI gate)
uv run sphinx-build -b linkcheck docs _build/linkcheck       # dead-link check
uv run pytest                                               # all tests
uv run pytest tests/test_resources.py -k duplicate          # a single test
```
