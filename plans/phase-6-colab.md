# Phase 6: Open in Colab

**Goal:** every notebook page has "Open in Colab" and "View on GitHub" badges.
Each badge opens the exact notebook that the page was built from.

## Why the current badges are wrong

- Both notebooks' first cell is a hand-written Colab badge that points at
  `Jibby2k1/SPS_Curriculum` `main`. Upstream has moved on since our snapshot
  (8c291ad): it has added teacher-note cells and session headers and fixed the
  intro-transformers H1. So Colab opens a different notebook from the page.
- SPS_Curriculum now puts a badge in every notebook (its `validate.py` check 8),
  so every future import will bring a stale badge along.

## Decisions (user-approved 2026-09-28)

- **Colab only, no Binder.**
  - Colab starts in seconds with PyTorch preinstalled and has free GPUs when
    available.
  - mybinder.org needs a public repo, builds an image on first launch and has
    no GPU. JupyterLite cannot run PyTorch.
  - The notebooks need nothing beyond torch, numpy and matplotlib, and they
    generate their own data files.
- **The repo becomes public.** Colab's GitHub links only work for people who
  can read the repo. The notebooks were already public through the site's
  `_sources/`.
  - Before the switch, scan the git history for secrets and show the user the
    commit email addresses.
  - The user makes the switch (Settings → General → Danger Zone), or tells
    Claude to run `gh repo edit`.
- **The build generates the badges; nobody writes them by hand.**
  `_ext/nb_reader.py` gains a `setup()` (and joins `extensions`) with a
  `doctree-read` handler.
  - For every doc whose source is `.ipynb`, it inserts one paragraph of two
    image links right after the first section title, or at the top if the
    notebook has no heading. Markdown pages get nothing.
  - Colab: `https://colab.research.google.com/github/kaddu341/backpropagandists/blob/main/docs/<path>`.
  - GitHub: `https://github.com/kaddu341/backpropagandists/blob/main/docs/<path>`.
  - `<path>` is the source path relative to `docs/`, e.g.
    `notebooks/intro-pytorch.ipynb`.
  - They are real reference nodes, so the weekly linkcheck tests them. The
    GitHub URL returns 404 if the repo goes private again or the file moves.
- **The badges are the real ones, self-hosted.**
  - Colab's official badge (`colab.research.google.com/assets/colab-badge.svg`)
    and a matching shields.io "View on GitHub" badge.
  - Both are downloaded once, unmodified, into `_ext/badges/`, and embedded as
    `data:` URIs. This is the same mechanism that pasted notebook images
    already use.
  - Result: no third-party request per page view (the same reason the fonts
    are self-hosted), and they work at any page depth and in test builds.
- **The stale badge cells are deleted:** the first cell of each notebook, and
  only that cell. A test fails if any notebook under `docs/` contains a
  `colab.research.google.com/github` link, so a future import cannot bring one
  back.

**Skipped, and when to add it:**
- Binder: add if someone asks (it becomes possible once the repo is public).
- A separate download button: the GitHub page already has one.
- Colab GPU metadata: add it with the first notebook that needs a GPU.

## Implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans
> (inline) to carry out this plan task by task. Steps use checkbox (`- [ ]`)
> syntax for tracking.

**Architecture:** a `doctree-read` hook in `_ext/nb_reader.py` inserts a
paragraph of two linked images after a notebook's first section title. The
link targets come from `env.doc2path(docname, base=False)`. The images are
`data:` URIs of SVGs stored in `_ext/badges/`.

**Files:**
- Create: `_ext/badges/colab.svg`, `_ext/badges/github.svg`.
- Modify:
  - `_ext/nb_reader.py`: add `badge`, `add_badges` and `setup`.
  - `docs/conf.py`: add `nb_reader` to `extensions` and fix the comment.
  - `tests/test_build.py`: two tests.
  - `docs/notebooks/*.ipynb`: drop cell 0.
  - Docs: `CLAUDE.md` and the spec.
  - `docs/_static/custom.css`: only if the screenshots need it.

**Commits:** the user commits per phase, so the work is committed once, at
the end, when they say so.

### Task 1: Check the history, then go public (needs the user)

- [x] List the commit authors, which will become visible:
  `git log --all --format='%an <%ae>' | sort | uniq -c`. Show the user.
- [x] Scan for secrets:
  `git log --all -p | grep -inE 'api[_-]?key|password|passwd|BEGIN [A-Z ]*PRIVATE KEY|ghp_|github_pat_|sk-[A-Za-z0-9]{20}'`.
  Expected: no output. Report any hit to the user and stop.
- [x] The user switches the repo to public. Verify:
  - `gh repo view --json visibility` prints `PUBLIC`.
  - `curl -s -o /dev/null -w '%{http_code}\n' https://github.com/kaddu341/backpropagandists/blob/main/docs/notebooks/intro-pytorch.ipynb`
    prints `200`.

### Task 2: Badge images

- [x] Download both badges, unmodified:
  ```sh
  mkdir -p _ext/badges
  curl -sSfL -o _ext/badges/colab.svg https://colab.research.google.com/assets/colab-badge.svg
  curl -sSfL -o _ext/badges/github.svg "https://img.shields.io/badge/View%20on-GitHub-181717?logo=github"
  ```
  Expected: two SVGs of about 2.4 KB each, both starting with `<svg`.

### Task 3: RED tests

- [x] Append to `tests/test_build.py`:
  ```python
  BLOB = "kaddu341/backpropagandists/blob/main/docs/notebooks/nb.ipynb"


  def test_notebook_gets_colab_and_github_badges_under_its_title(tmp_path):
      import nbformat

      nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell("# NB\n\nFirst paragraph.")])
      pages = {"index": "# Home\n", "notebooks/nb.ipynb": nbformat.writes(nb), "page": "# Plain page\n"}
      proc = build(tmp_path, pages)
      assert proc.returncode == 0, proc.stderr
      html = (tmp_path / "out" / "notebooks" / "nb.html").read_text()
      colab = html.index(f'href="https://colab.research.google.com/github/{BLOB}"')
      github = html.index(f'href="https://github.com/{BLOB}"')
      assert html.index("<h1") < colab < github < html.index("First paragraph")
      # Embedded, so a page view makes no request to Google or shields.io.
      assert html.count('src="data:image/svg+xml;base64,') == 2
      assert "colab.research.google.com" not in (tmp_path / "out" / "page.html").read_text()


  def test_no_hand_written_colab_badges():
      # The build adds the badges. Hand-written ones go stale: the SPS_Curriculum
      # ones opened a different repo's copy of the notebook.
      stale = [p.name for p in DOCS.rglob("*.ipynb") if "colab.research.google.com/github" in p.read_text()]
      assert not stale
  ```
- [x] Run `uv run pytest tests/test_build.py -k badge -v`.
  Expected: both FAIL.
  - The first fails with `ValueError: substring not found`, because there is
    no Colab link yet.
  - The second fails and lists `intro-pytorch.ipynb` and
    `intro-transformers.ipynb`.

### Task 4: GREEN, the badge hook

- [x] In `_ext/nb_reader.py`:
  - Replace the module docstring and imports with:
    ```python
    """Notebook support for myst-nb.

    - read_ipynb: a notebook reader that renders images pasted into markdown
      cells. Jupyter stores a pasted image as a cell attachment
      (`![x](attachment:x.png)`), which myst-nb cannot resolve, so each one
      becomes a data: URI.
    - setup: an extension that puts "Open in Colab" and "View on GitHub" badges
      under every notebook's title. The links come from the notebook's own path,
      so they cannot go stale the way hand-written badges do.
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
    ```
  - Keep `read_ipynb` unchanged, and append:
    ```python
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
        section = next(doctree.findall(nodes.section), None)  # the H1's section
        if section is None:
            doctree.insert(0, row)
        else:
            section.insert(1, row)  # section[0] is the title


    def setup(app):
        # Run before Sphinx's image collector (priority 500), so it registers the badges too.
        app.connect("doctree-read", add_badges, priority=400)
        return {"parallel_read_safe": True, "parallel_write_safe": True}
    ```
- [x] In `docs/conf.py`, after the `"resources"` line in `extensions`, add:
  ```python
      "nb_reader",  # _ext/nb_reader.py: Colab/GitHub badges on notebook pages (also the reader below)
  ```
- [x] Run `uv run pytest tests/test_build.py -k badge -v`.
  Expected: the badge test PASSES, and the guard still FAILS on the two
  notebooks.

### Task 5: Delete the stale badge cells

- [x] Drop cell 0 from each notebook, keeping Jupyter's formatting (indent 1,
  no ASCII escaping, trailing newline):
  ```sh
  uv run --no-project python - <<'EOF'
  import json
  for f in ["docs/notebooks/intro-pytorch.ipynb", "docs/notebooks/intro-transformers.ipynb"]:
      nb = json.load(open(f))
      assert "colab.research.google.com/github" in "".join(nb["cells"][0]["source"])
      del nb["cells"][0]
      open(f, "w").write(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
  EOF
  git diff --stat docs/notebooks
  ```
  Expected: deletions only (0 insertions) in both files. If there are
  insertions, the formatting changed: `git checkout docs/notebooks` and match
  the original formatting before retrying.
- [x] Run `uv run pytest`. Expected: all 21 pass.

### Task 6: Build, look, linkcheck

- [x] Run `uv run sphinx-build -W -b html docs _build/html`. Expected: it
  succeeds.
- [x] Take screenshots of `_build/html/notebooks/intro-pytorch.html` in the
  scratchpad: light, dark (`color_scheme="dark"`) and phone (390×844). Use
  `uv run --no-project --with playwright python`, with
  `chromium.launch(channel="chrome")` and `page.goto(<file URI>)`.
  Expected: the two badges sit side by side on one line under the title.
- [x] If the badges stack or get link underlines, append to
  `docs/_static/custom.css`, then rebuild and take the screenshots again:
  ```css
  /* "Open in Colab" / "View on GitHub" row under a notebook's title (_ext/nb_reader.py). */
  .nb-badges img { display: inline-block; margin: 0; vertical-align: middle; }
  .nb-badges a { text-decoration: none; }
  ```
- [x] Run `uv run sphinx-build -b linkcheck docs _build/linkcheck`, then
  `grep -E 'colab|github.com/kaddu341' _build/linkcheck/output.json`.
  Expected: every such link has `"status": "working"`. The GitHub links only
  work once Task 1 has made the repo public.

### Task 7: Docs

- [x] `docs/conf.py`, the `html_baseurl` comment. Change it to:
  ```python
  # The published site's URL. Shibuya needs it to render the "Copy page" button:
  # the button fetches the page source from <baseurl>/_sources/. Update it if the
  # site moves (org account or custom domain), together with REPO in _ext/nb_reader.py.
  ```
- [x] `CLAUDE.md`:
  - "Deployed to GitHub Pages from a private repo." becomes "Deployed to GitHub
    Pages from a public repo (public so Colab can open the notebooks)."
  - The status becomes "Phases 1–6 done (skeleton, resources, notebooks,
    styling, CI, Colab badges)".
  - Add an Architecture bullet: "`_ext/nb_reader.py` reads notebooks (pasted
    images become `data:` URIs) and adds "Open in Colab" / "View on GitHub"
    badges under each notebook's title, built from its path. Never hand-write
    a badge: `test_no_hand_written_colab_badges` rejects them."
- [x] `plans/2026-09-28-wiki-design.md`:
  - Line 12: "built from a private repo" becomes "built from a public repo
    (private until Phase 6)".
  - Line 32: the `_ext/nb_reader.py` comment becomes ".ipynb reader (pasted
    images) + Colab/GitHub badges".
  - Lines 72–73: drop ", because the repo is private".
  - Lines 197–198: replace with "Their hand-written Colab badges were removed
    in Phase 6; the build adds badges (see `phase-6-colab.md`)."
- [x] `plans/phase-3-notebooks.md`, typo list:
  - Replace the Colab item with "(Done in Phase 6: the badge cells were
    removed, and the build adds badges.)"
  - Add: "The authors and credit cells come before the H1, so they render
    above the page title and the badges."
- [x] Tick this plan's boxes and add an execution log. Then ask the user
  whether to commit:
  ```sh
  git add _ext docs/conf.py docs/notebooks docs/_static/custom.css tests/test_build.py CLAUDE.md plans
  git commit -m "Phase 6: Open in Colab / View on GitHub badges on notebook pages"
  ```
  The commit message ends with the attribution trailer.

### Task 8: After the user pushes

- [x] The live page `notebooks/intro-pytorch.html` has both badges, and their
  `href`s are the URLs from Task 3.
- [x] Open the Colab URL with Playwright (installed Chrome) and take a
  screenshot. Expected: the notebook's title is visible, not a "not found" or
  sign-in wall.

## Execution log

- Work is on branch `colab`.
- **History scan:** no secret-like strings. Commit authors that become public:
  `kaddu341 <awwabaliazam@gmail.com>` (18 commits) and a GitHub noreply
  address (1 commit). This was shown to the user.
- RED, then GREEN, as planned. The hook needed no changes from the plan. 21
  tests pass.
- Dropping cell 0 gave a diff of deletions only (8 lines per notebook), so
  Jupyter's formatting was preserved.
- The screenshots (light, dark, phone) show both badges on one line under the
  H1. The conditional CSS was **not** needed, so `custom.css` is unchanged.
- **Linkcheck:** everything passes except the two GitHub blob URLs, which
  return 404 while the repo is private (expected). Colab URLs report "working"
  for any path, so the GitHub links are the ones that detect a private repo or
  a moved file.
- Both notebooks' Setup text says to open the notebook in Colab "using the
  link at the top". This is still true on the site: the badges are under the
  title.
- The user made the repo public. `gh repo view` prints `PUBLIC`, and the
  blob URL returns 200 anonymously. Linkcheck is now fully green (exit 0).
- The user approved committing, merging `colab` into `main` locally and
  pushing.
- Merged into `main` (fast-forward) and pushed. CI run 36438439210: build and
  deploy succeeded. The live `notebooks/intro-pytorch.html` links to the
  planned Colab and GitHub URLs. Opened anonymously, Colab shows our copy of
  the notebook (it starts at "Content Produced by…", with no stale badge
  cell).
