# Phase 2: Resource system

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:test-driven-development.
> Tests first, watch each fail, then write the minimum code that passes.

**Goal:** `data/resources.yaml` feeds a `resource-list` directive that renders a
compact list grouped by kind ("Our material" first) on each topic page.

**Spec:** `plans/2026-09-28-wiki-design.md`, section "Resource system".

**Spike result (2026-09-28):** `SphinxDirective.parse_text_to_nodes(text,
allow_section_headings=True)` in a MyST page turns generated `## Heading` lines
into real `<section>`/`<h2>` nested under the page's H1. They appear in
Shibuya's "On this page" sidebar, and inline raw `<span class="...">` passes
through. So groups are real sections, and the meta line and the "ours" label
are `<span>`s that Phase 4 CSS styles. No fallback is needed.

## Files

- `_ext/resources.py`: `KINDS` (`kind → heading`, in display order; this is
  also the kind enum), `LEVELS`, `load(path, valid_topics)`,
  `group(records, topics)`, and the directive.
- `tests/test_resources.py`: unit tests for `load` and `group`.
- `tests/test_build.py`: the `build()` helper takes `pages` and optional
  `resources`, plus two directive tests.
- `pyproject.toml`: `[tool.pytest.ini_options] pythonpath = ["_ext"]`.
- `docs/conf.py`: puts `_ext` on `sys.path` and adds the `resources`
  extension.
- `data/resources.yaml`: a commented template plus the DDPM record.
- `docs/topics/*.md`: each gets a `resource-list` directive.

## Tasks

### 1. `load` and `group` (unit, TDD)

- [ ] RED: `tests/test_resources.py`
  - `load` returns the records for a valid file.
  - `load` raises `ExtensionError`, with the record id in the message, for
    each of:
    - an unknown topic
    - an unknown level
    - an unknown kind
    - a missing required field
    - an unknown field
    - a wrong type (`year: "2020"`)
    - both `url` and `doc`
    - neither `url` nor `doc`
    - a `url` record without a title
    - empty `topics`
    - a duplicate id
  - `group`:
    - "Our material" comes first
    - kinds follow the `KINDS` order
    - YAML order is kept within a group
    - empty groups are omitted
    - the topic filter works
    - no filter means every record
- [ ] Watch them fail (`ModuleNotFoundError: resources`).
- [ ] GREEN: write `load` and `group` in `_ext/resources.py`, and add the
  pytest `pythonpath`.
- [ ] Commit.

### 2. Directive (integration, TDD)

- [ ] RED: `tests/test_build.py`
  - A topic page with a fixture YAML (one paper `url` record and one `doc`
    record pointing at a fixture page) renders the "Our material" `<h2>`
    before "Papers". The internal link resolves, the external link is present,
    and the `ours` and `meta` spans are present.
  - `:topics: nope` fails the build and names `nope`.
- [ ] Watch them fail (unknown directive).
- [ ] GREEN: write the directive and wire it into `conf.py`. The directive
  calls `note_dependency` on the YAML.
- [ ] Commit.

### 3. Real data and pages

- [ ] Add `data/resources.yaml` with a commented template and the DDPM record.
  DDPM has no `note`; the user writes it.
- [ ] Add a `resource-list` directive to all three topic pages.
- [ ] Run `uv run sphinx-build -W -b html docs _build/html` and check that
  DDPM appears under "Papers" on the Diffusion page and nowhere else.
- [ ] Run `uv run sphinx-build -b linkcheck docs _build/linkcheck` and check
  that it passes.
- [ ] Commit.

### 4. Wrap-up

- [ ] Add `--watch data --watch _ext` to the CLAUDE.md autobuild command and
  confirm that it serves.
- [ ] Update the CLAUDE.md status, tick this plan, and record any deviations
  below.
- [ ] Commit, then stop for user review.

## Execution log
