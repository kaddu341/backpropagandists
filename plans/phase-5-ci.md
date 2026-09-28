# Phase 5: CI

**Spec:** `plans/2026-09-28-wiki-design.md`, section "CI (Phase 5)".

## Workflows

- `.github/workflows/build.yml`
  - **Triggers:** push to `main`, pull requests, and manual dispatch.
  - **Steps:** `uv sync --locked`, then `uv run pytest` (Node 24 is set up so
    the ball-physics test runs rather than skips), then
    `sphinx-build -W -b html`, then `upload-pages-artifact`.
  - **Deploy:** a separate job that runs only on `main` and never for PRs.
    Only that job gets `pages: write` + `id-token: write`; everything else is
    `contents: read`.
  - **Concurrency:** one group per ref. Superseded PR runs are cancelled;
    runs on `main` queue instead, so a deploy is never cut off mid-flight.
- `.github/workflows/linkcheck.yml`
  - **Triggers:** weekly (Mondays 06:00 UTC) and manual dispatch.
  - **Steps:** run `sphinx-build -b linkcheck`. On failure, post
    `output.txt` (only its broken, redirected and timed-out entries) to a
    single open issue labelled `linkcheck`, creating the issue if none exists
    and commenting if one does. The job still goes red. The issue step uses
    the `gh` CLI, with no third-party actions, and has `issues: write`.
- Action versions are pinned to the current majors (checked 2026-09-28):
  checkout v7, setup-uv v10.2.0 (exact: it has no major tags), setup-node v7, upload-pages-artifact v5,
  deploy-pages v5.

## Tasks

- [x] Write both workflows.
- [x] Lint them with `actionlint` (run via `uvx`, not a project dependency).
- [x] Dry-run the steps locally: `uv sync --locked`, pytest, the strict build
  and `.nojekyll`.
- [x] Update CLAUDE.md and commit.
- [ ] Hand-off, which needs the user: pushing, enabling Pages
  (Settings → Pages → Source: GitHub Actions), and merging `scaffold` → `main`.

## Execution log
- Both workflows pass `actionlint`, with shellcheck on the `run:` scripts.
- The build job's steps were dry-run locally from clean: `uv sync --locked`,
  19 tests, the strict build and `.nojekyll`. The published output is 1.6 MB.
- **Deviation:** the build writes doctrees to `_build/doctrees` (`-d`).
  Otherwise Sphinx puts its `.doctrees` pickle cache inside the published
  site.
- `gh issue list ... --jq '.[0].number'` prints an empty string when there is
  no issue (checked against the real repo), so the create-or-comment branch is
  correct.
- The report body was checked with a fake `output.txt`. The real `gh` calls
  can only run in Actions.
- **First real run (2026-09-28) failed at "Set up job":** `astral-sh/setup-uv@v10`
  does not exist, because setup-uv publishes exact release tags only. It is
  now pinned to `v10.2.0`. All other action tags were checked with
  `gh api repos/<action>/git/ref/tags/<tag>`.
- **Removed the `.nojekyll` step (user decision, 2026-09-28).**
  `upload-pages-artifact` excludes dotfiles unless `include-hidden-files: true`,
  so the file never reached the site: the live `/.nojekyll` returned 404. It
  is also unnecessary, because an Actions deploy never runs Jekyll; the live
  `_static/` and `_sources/` were already served.
- The live site was checked after the first green run: the pages,
  `landscape.js` (`application/javascript`), the CSS, the woff2 font and
  `_sources/*.txt` all return 200. The CI log shows `test_landscape.py`
  passed, not skipped.
