# Phase 3: Notebooks

**Goal:** the user's two SPS_Curriculum notebooks render under a Foundations
section, from their stored outputs, and the strict build and linkcheck both
pass.

**Spec:** `plans/2026-09-28-wiki-design.md`, section "Notebooks and math".

This phase adds no new code, only content and config, so there is no new test.
The gates are the `-W` build and linkcheck.

## Tasks

- [x] Copy `intro_pytorch.ipynb` and `intro_transformers.ipynb` from
  SPS_Curriculum@8c291ad **unmodified** into `docs/notebooks/intro-pytorch.ipynb`
  and `intro-transformers.ipynb`. Prove they are unmodified: the
  `git hash-object` of each copy must equal the blob SHA that the GitHub API
  reports at that commit.
- [x] Add a Foundations section as the first subtree in `_toc.yml`. The top
  bar picks it up automatically.
- [x] Run `uv run sphinx-build -W -b html docs _build/html`. Suppress each
  warning type that the notebooks trip in `conf.py` `suppress_warnings`, with
  a comment, and do not edit the notebooks. Expected: `myst.header` (H1 → H3).
- [x] Check the rendered HTML: output images, markdown-cell math and the
  attachment image are all present.
- [x] Run `uv run sphinx-build -b linkcheck docs _build/linkcheck` and check
  that it passes.
- [x] Update the CLAUDE.md status, tick this plan, log deviations, commit, and
  stop for review.

## Execution log

All tasks are done (2026-09-28).
- The copies are byte-identical to SPS_Curriculum@8c291ad: `git hash-object`
  equals the GitHub blob SHA for both files.
- **Deviation:** intro-pytorch cell 29 embeds the FFT formula as a Jupyter
  attachment (`attachment:image.png`), which myst-nb cannot render. The
  choice was between suppressing `image.not_readable` and fixing it.
  Suppressing it would also hide genuinely broken images in the future, so I
  added `_ext/nb_reader.py` (TDD), a custom `.ipynb` reader that inlines
  attachments as `data:` URIs.
- The only suppression is `myst.header` (H1 → H3 in both notebooks).
- Linkcheck passes. Colab badge, both Colab links and arXiv all work.

Items for the user's typo pass (content, left unedited):
- Both notebooks have the H1 "Intro to Deep Learning using PyTorch", so the
  sidebar shows two identical entries.
- "### Setup" directly under the H1. Fixing it lets `myst.header` come out of
  `suppress_warnings`.
- The PyTorch-tutorial credit is a bare URL in parentheses. MyST renders it as
  plain text, so it needs `<https://...>` or `[text](url)` to be clickable.
- (Done in Phase 6: the badge cells were removed, and the build adds badges.)
- The authors and credit cells come before the H1, so they render above the
  page title and the badges.
- The FFT formula is an image; `$$...$$` would render natively.
