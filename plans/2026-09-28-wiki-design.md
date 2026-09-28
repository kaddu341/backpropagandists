# backpropagandists wiki: design

Approved 2026-09-28. This file records decisions. Per-phase task lists live in
`plans/phase-*.md`.

## Goal

This is a Sphinx site that works as a curated learning-resources wiki for
incoming postdocs and grad students in a condensed-matter theory group. The
readers are strong physicists who are new to ML. About 80% of the content is
curated external links and about 20% is our own pages and notebooks. It is
published to GitHub Pages as a **public** site, built from a public repo
(private until Phase 6).

## Non-negotiables

- Never invent content. No URLs, titles, authors or notes that the user has not
  supplied or approved. Topic pages stay stubs until the user writes them.
- Content is Markdown (MyST) only. Navigation lives only in `_toc.yml`.
- The approved stack is sphinx, myst-parser, myst-nb, sphinx-design,
  sphinx-external-toc, shibuya and sphinx-autobuild. The non-Sphinx additions
  are `pyyaml` (runtime, imported by the extension) and `pytest` (dev group).
  Anything else needs the user's approval.
- Every version is pinned exactly in `pyproject.toml`, and `uv.lock` is
  committed. The project uses Python 3.13.

## Layout

```
_toc.yml                  # sole navigation source
data/resources.yaml       # external resources, one record each
_ext/resources.py         # `resource-list` directive
_ext/nb_reader.py         # .ipynb reader (pasted images) + Colab/GitHub badges
tests/test_resources.py   # load/group unit tests
tests/test_build.py       # throwaway builds with the real conf.py (math, directive)
tests/landscape.test.mjs  # landing physics under node --test (run by tests/test_landscape.py)
plans/                    # this spec + phase plans (outside docs/ so Sphinx ignores it)
docs/conf.py
docs/index.md             # Shibuya landing layout
docs/topics/*.md          # one per topic: title + resource-list
docs/notebooks/*.ipynb    # our own teaching notebooks
docs/_static/custom.css   # every visual choice, commented
docs/_static/landscape.js # landing art: random loss landscape + ball
docs/_static/fonts/       # LXGW WenKai (Latin chunk) + OFL licence
docs/_templates/partials/webfonts.html  # removes Shibuya's Google Fonts request
.github/workflows/{build,linkcheck}.yml
```

`conf.py` sets `external_toc_path = "../_toc.yml"`, which is resolved
relative to `docs/`.

## Navigation and pages

- `_toc.yml` has three captioned sections:
  - **Foundations**: `topics/basics`, `notebooks/intro-pytorch`,
    `notebooks/intro-transformers`.
  - **Generative models**: `topics/diffusion-flow-matching` (diffusion and
    flow matching were merged into one page on 2026-09-28, at the user's request).
  - **Reinforcement learning**: `topics/reinforcement-learning`.
- Shibuya `nav_links` mirrors the sections. `conf.py` derives them from
  `_toc.yml`, with one link per caption pointing at the section's first page,
  so navigation is defined only once.
- `index.md` uses `layout: landing`, and every other page uses Shibuya's
  default layout. The landing page contains the site name
  "backpropagandists" and the README tagline "Machine learning learning".
  There is no other prose. It had no section cards (cut after Phase 1): they
  would have been a hand-kept copy of `_toc.yml`, and the top bar, which is
  derived from `_toc.yml`, already links every section.
- Footer copyright is left unset until the user specifies it.
- Shibuya's "Copy page ▾" button (copy/view Markdown source, open in ChatGPT
  or Claude) stays on globally. Topic pages hide it with `hide_ai_links` front
  matter, because their source is just the directive. The front matter must
  be the quoted string `hide_ai_links: "true"`: MyST turns a YAML `true`
  into `"True"`, and Shibuya compares against `"true"`. The button only
  renders when `html_baseurl` is set. It then
  fetches the source from `<baseurl>/_sources/`.

## Resource system

### Records (`data/resources.yaml`)

The file is a top-level YAML list. A commented record template sits at the top
of the file.

| field    | required | type           | allowed values                                    |
|----------|----------|----------------|---------------------------------------------------|
| `id`     | yes      | str, unique    | any                                               |
| `url`    | xor¹     | str            | external link                                     |
| `doc`    | xor¹     | str            | internal docname, e.g. `notebooks/intro-pytorch`  |
| `title`  | ²        | str            | any; MyST inline markup (incl. `$math$`) renders  |
| `kind`   | yes      | str            | paper lecture video course book blog code notebook|
| `topics` | yes      | non-empty list | stems of `docs/topics/*.md`                       |
| `level`  | yes      | str            | foundational, intermediate, advanced              |
| `year`   | no       | int            | any                                               |
| `note`   | no       | str            | any                                               |

¹ Exactly one of `url` or `doc`.
² Required for `url` records. Optional for `doc` records, where it defaults to
the page's own title.

**A topic is valid iff `docs/topics/<topic>.md` exists.** There is no separate
topic registry.

A record with `doc:` is **our own material**. It renders as a Sphinx `{doc}`
cross-reference, so a renamed or deleted page fails the `-W` build instead of
rotting silently.

The seed record (DDPM) was replaced on 2026-09-28 by the user's first curated
list. Every title, year and link was checked against its source, and the notes
are the user's own, lightly edited. The two notebooks are `doc:` records on
the Basics page.

### Directive

````
```{resource-list}
:topics: diffusion
```
````

- `:topics:` is optional and takes a comma-separated list. Omitting it lists
  every record. A record is shown if it shares at least one topic with the
  filter.
- The output is a compact, conventional wiki list. Resources are **not**
  rendered as cards; cards appear only on the landing page.
- **Grouped by kind.** The first group is "Our material" (every `doc:`
  record, whatever its kind). After it comes one group per kind, in this
  order: Papers, Lectures, Videos, Courses, Books, Blog posts, Code,
  Notebooks. The order and headings come from a single `kind → heading` dict
  in `_ext/resources.py`, which is also the kind enum. **A group appears only
  if it has at least one matching record.** For example, a topic with no blog
  posts has no "Blog posts" heading.
- Group headings should be real sections, so they appear in Shibuya's "On
  this page" sidebar. If MyST cannot emit sections from a directive cleanly,
  they fall back to rubrics. A spike at the start of Phase 2 decides which.
- **Within a group, items keep their YAML order.** The curator sets the
  reading order by moving records, and there is no sorting logic.
- Each item shows:
  - the linked title
  - an "ours" label on internal items
  - a muted meta line: `kind · year · level`
  - the note, if there is one

  The CSS hooks are `span.meta`, `span.ours`, and `ul:has(.meta)` for the
  lists themselves. There is no wrapper class, because MyST attaches the
  generated sections directly to the page (found in Phase 2). A note renders
  as a second `<p>` in its `<li>`. Phase 4 CSS gives external links a ↗ glyph
  and
  internal ones a distinct glyph, using Sphinx's existing `reference external`
  and `reference internal` classes. The "ours" text label means the
  distinction does not rely on colour or glyphs alone.
- A valid filter that matches nothing renders nothing. This is expected for
  new stub topics.
- The directive calls `env.note_dependency` on the YAML, so editing the data
  triggers a rebuild of the pages that use it.
- The `:level:` filter is dropped (YAGNI). The level shows on each item
  instead. Add the filter back when a page needs it.

### Failure behaviour

These conditions raise `sphinx.errors.ExtensionError`, which aborts the build
even without `-W`:

- an unknown topic, level or kind, whether in a record or in the `:topics:`
  option
- a missing required field or a wrong type
- a record with both `url` and `doc`, or with neither
- an unknown field (catches typos such as `levl:`)
- a duplicate `id`

The error message names the record `id` (or its list index) and the offending
value.

### Code shape

- `_ext/resources.py` has pure functions `load(path, valid_topics)` and
  `group(records, topics)`, plus a thin directive class. `group` filters the
  records and returns an ordered list of `(heading, records)` pairs.
- Paths are derived from `app.srcdir`: the YAML is at `srcdir/../data/resources.yaml`
  and the topics are `srcdir/topics/*.md`.

## Notebooks and math

- `nb_execution_mode = "off"`. The build never executes notebooks, and outputs
  are committed. The user re-runs notebooks locally. A future lightweight
  notebook may opt in to execution through its own `mystnb` metadata.
- `intro_pytorch.ipynb` and `intro_transformers.ipynb` were copied unmodified
  from SPS_Curriculum@8c291ad and renamed to `intro-pytorch.ipynb` and
  `intro-transformers.ipynb`. Since then they are edited only at the user's
  request (see the typo list in `phase-3-notebooks.md`).
  - If they trip `-W`, the specific warning type is added to
    `suppress_warnings`. The content is not edited, and each suppression is
    reported to the user. The only one, `myst.header` (H1 → H3), was
    removed once the user had the headings fixed; none remain.
  - `.ipynb` files are read through `_ext/nb_reader.py`, which inlines
    markdown-cell attachments (images pasted in Jupyter) as `data:` URIs,
    because myst-nb cannot resolve `attachment:` links. This was added in
    Phase 3 for the FFT formula image in intro-pytorch (now LaTeX; the
    reader stays for future pasted images).
  - Their hand-written Colab badges were removed in Phase 6; the build adds
    badges (see `phase-6-colab.md`).
- `myst_enable_extensions = ["amsmath", "dollarmath", "colon_fence", "deflist",
  "fieldlist"]`. Math is rendered by MathJax (Sphinx's default). Shared macros
  are added when first needed.
- There is no `.tex` document pipeline (YAGNI). Bare amsmath environments in
  Markdown are covered by the `amsmath` extension.

## i18n

`language = "en"`, `locale_dirs = ["locale/"]` and `gettext_compact = False`
are set but unused. Chinese comes later. Shibuya ships `zh`/`zh_TW` UI strings
and a `--sy-f-cjk` font token.

## Styling (Phase 4)

The chosen direction is "Shanshui". The full reasoning and the rejected
candidates are in `plans/phase-4-styling.md`.

- **Function first.** Reading text and code use the OS fonts (Shibuya's
  default stack), as the PyTorch tutorials do. Math uses MathJax's default
  font, New Computer Modern.
- **Calligraphy only on short text.** LXGW WenKai (Latin chunk self-hosted)
  is used for H1, the brand and the landing wordmark. Chinese titles fall back
  to the system Kaiti.
- **No third-party font requests.** `docs/_templates/partials/webfonts.html`
  removes Shibuya's Google Fonts Inter.
- **The landing art is `docs/_static/landscape.js`.** It generates random loss
  landscapes on every visit, and a soccer ball (C₆₀) bounces down and settles
  at the global minimum. Its physics is tested by `tests/landscape.test.mjs`,
  which pytest runs through `tests/test_landscape.py` and skips when Node is
  absent.
- All visual choices are in `docs/_static/custom.css`, commented. It
  overrides Shibuya's `--sy-*` tokens plus a few targeted rules. No CSS
  framework is used.

## CI (Phase 5)

- `build.yml` runs on every PR and on pushes to `main`. The steps are `uv sync`,
  `uv run pytest`, then `sphinx-build -W -b html`. No `.nojekyll` is needed:
  an Actions deploy never runs Jekyll, and `upload-pages-artifact` drops
  dotfiles anyway. The site is deployed from `main` only, using
  `actions/upload-pages-artifact` + `actions/deploy-pages`. Permissions are
  `pages: write`, `id-token: write` and `contents: read`, and a `concurrency`
  group prevents overlapping deploys.
- `linkcheck.yml` runs weekly and on `workflow_dispatch`. It runs
  `sphinx-build -b linkcheck`, and on failure it opens a single issue with the
  `gh` CLI, or updates it if one is already open. No third-party actions are
  used.

- Node 24 is installed in the build job so pytest runs the landing-page
  physics test instead of skipping it. See `plans/phase-5-ci.md`.

## Testing

- `tests/test_resources.py` tests `load` and `group`: the valid path, every
  failure condition listed above, topic filtering, group order, "Our
  material" first, YAML order being kept within a group, and the absence of
  any heading for an empty group.
- The math acceptance check runs a throwaway build with the real `conf.py`,
  using `sphinx-build -W -c docs <tmp>/src <tmp>/out`. The throwaway project
  has a `<tmp>/_toc.yml` with `root: index`, and its `index.md` holds an
  inline `$...$` and a bare `\begin{align}` block. The test asserts that both
  appear as MathJax math nodes in the HTML.
- The same throwaway build also runs the directive end to end. It uses a
  fixture `<tmp>/data/resources.yaml` with one `url` record and one `doc`
  record, plus a `<tmp>/src/topics/x.md` page. This matters because the real
  site's seed data has no `doc` record yet. The test asserts on the rendered
  HTML: the "Our material" group comes first, the internal link resolves, and
  the external link is present.
- The real site building under `-W` is the final gate.

## Acceptance

- `uv run pytest` passes.
- `uv run sphinx-build -W -b html docs _build/html` passes.
- `uv run sphinx-build -b linkcheck docs _build/linkcheck` passes.
- `uv run sphinx-autobuild docs _build/html --watch data --watch _ext --watch _toc.yml`
  serves the site and rebuilds on data edits.
- Adding a topic takes exactly three steps: an entry in `_toc.yml`,
  `docs/topics/<topic>.md` with a `resource-list`, and records in the YAML.

## Phases

Each phase ends with a commit and a stop for user review.

1. Skeleton: conf.py, `_toc.yml`, landing page and stub topic pages. The site
   builds with `-W`, and autobuild serves it.
2. Resource system: built test-first. The DDPM card renders on the diffusion
   page.
3. Notebooks: both render with their stored outputs.
4. Styling.
5. CI.

## Deviations from the original AI-drafted prompt

- The `flow-matching-2d.ipynb` notebook is dropped. The user's two notebooks
  are used instead.
- `nb_execution_mode` is `off`, not `cache`, because the transformer notebook
  takes about 45 minutes and intro_pytorch writes about 300 MB of tensors.
- There are no `TODO:` placeholder records. The file holds one real record
  plus a commented template, which keeps linkcheck clean.
- Resources render as a compact list grouped by kind, not as a sphinx-design
  card grid. Internal material shares the same YAML through `doc:` records.
- Valid topics come from the filenames in `docs/topics/`, not from a list.
- Plans live in `plans/`, not `docs/`.
