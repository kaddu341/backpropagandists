# Phase 4: Styling

**Chosen direction: "Shanshui"** (ink-wash landscape). It was picked from
three candidates built on the real site: "Magic angle" (moiré), "Shanshui" and
"Star atlas".

**Readers:** condensed-matter theorists new to ML, reading long notebooks
full of math and code. The user's rule is **function first, beauty second**.
The reference for readability is the PyTorch tutorials.

## Decisions

- **Reading type = the operating system's own UI and monospace fonts**,
  exactly as the PyTorch tutorials do (16 px, line height about 1.7). This is
  Shibuya's default stack once its Google-Fonts Inter override is removed, so
  no override is needed.
  - Each OS supplies its best-tuned Latin face and its own Chinese face
    (PingFang, Microsoft YaHei, Noto Sans CJK) through fallback. That is
    "different fonts for different languages" at no cost.
- **Calligraphy only where text is short:** the landing wordmark, the header
  brand and page titles (H1).
  - These use LXGW WenKai Screen, with only its Latin chunk self-hosted
    (36 KB).
  - Chinese titles fall back to the system Kaiti (楷体), which is also a brush
    face, so nothing needs downloading.
- **Math uses MathJax's default, New Computer Modern:** the LaTeX look
  physicists read every day. There is no `mathjax4_config`.
- **Palette:** mist paper, pine-soot ink, and a pine-ink wash for links.
  Cinnabar is kept only for the "ours" badge, which is a text label.
- **The landing art is generated fresh on every visit** by
  `docs/_static/landscape.js`:
  - three random ridges, where each ridge is a convex bowl plus random
    ripples, i.e. a 1-D loss curve;
  - a soccer ball (a truncated icosahedron, which is also C₆₀,
    buckminsterfullerene) drops onto the nearest ridge, bounces, then rolls
    with momentum and settles at the **global** minimum.
  - To guarantee the global minimum, the trajectory is simulated before it is
    shown. If the ball would stop in a local minimum, a new landscape is drawn.
  - With reduced motion, the ball is simply drawn at rest at the minimum.
  - Without JS, the landing is just the title.
- **The physics is tested:** `tests/landscape.test.mjs` runs under
  `node --test`, and pytest runs that file (it is skipped if Node is absent),
  so `uv run pytest` stays the one command.

## Tasks

- [x] TDD: meta string change (`2020, foundational`).
- [x] Build three candidates. Screenshot the landing, topic, notebook, phone
  and Chinese views. The user picked Shanshui.
- [x] Delete the losing candidates' fonts and art.
- [x] TDD `landscape.js`: RED test (the ball settles at the global minimum,
  is deterministic per seed, and stays on screen), then GREEN.
- [x] Write final `custom.css` (Shanshui tokens + shared structure) and wire
  `conf.py` (the JS file, drop `mathjax4_config`, accent colour).
- [x] Screenshots: landing mid-animation and at rest (light, dark, phone), and
  a notebook page for readability.
- [x] Strict build, pytest, linkcheck. Update CLAUDE.md, commit, stop for
  review.

## Execution log

- The candidates were built in the scratchpad and served on ports
  8801–8803. None of their files are committed.
- The Google Fonts request was removed with a `docs/_templates/partials/webfonts.html`
  override. Shibuya otherwise loads Inter from Google on every page.
- An eyeball check caught myst-nb's green code-cell margin; it now uses theme
  tokens.
- `landscape.js` was TDD'd: RED on the missing module, then GREEN. The
  diagnostics over 300 seeds show zero fallbacks, 2–4 bounces, and settling in
  7–9 s on desktop or 4–8 s on a phone. `plan()` costs 1–5 ms.
- Headless Chrome's `--screenshot` never ticks `requestAnimationFrame` on
  macOS, so the animation was checked with Playwright driving the installed
  Chrome (`channel="chrome"`). This is a scratchpad-only tool, not a project
  dependency.
- An eyeball fix: in dark mode the ball lost its silhouette (dark rim on dark
  ridges), so the rim now uses `--bp-ink`.
- The user decided function first (2026-09-28): the "forbidden" system fonts
  are fine if they read best. They do, and they are what the PyTorch
  reference uses.
