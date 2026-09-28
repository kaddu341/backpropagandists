# Phase 4: Styling

**Goal:** two candidate looks, each built as a real `docs/_static/custom.css`
on the real site and screenshotted. The user picks one, and the other is
deleted.

**Subject:** a reading wiki for condensed-matter theorists who are new to ML.
They are fluent in LaTeX, arXiv, PRB and Jupyter. The site's job is to get
them to the right resource fast, and to make math and code comfortable to
read.

**Brief:** open-source hacker taste (Svelte, Remix, Arch, Framework, RISC-V,
Firefox, scienceplots). Confident type, generous whitespace, restrained
colour, and a real monospace face.

## The problem every docs theme ignores

MathJax sets equations in Computer Modern whatever the body font is, so text
and math never match. Both directions fix this by choosing the math font as
part of the type system (`mathjax4_config.output.font`).

## Direction A: "Beamer"

The idea is one family for prose, equations and code. Physicists already
read sans-serif math in every Beamer talk. Fira is Mozilla's typeface, which
ties to Firefox in the brief. The palette comes from scienceplots' `science`
colour cycle, the brief's own reference, so figures made with scienceplots
sit naturally on the page.

| token  | light     | dark      | use |
|--------|-----------|-----------|-----|
| paper  | `#FFFFFF` | `#0E141B` | background |
| ink    | `#15202B` | `#D8DEE4` | body text and headings |
| muted  | `#5A6672` | `#8A96A3` | meta lines, captions |
| rule   | `#E2E6EA` | `#243140` | borders |
| blue   | `#0C5DA5` | `#5AA2E6` | links, current page (scienceplots cycle[0]) |
| orange | `#FF9500` | `#FFB347` | the "ours" marker only, never text (cycle[2]) |

- **Type:** Fira Sans at 400, 500, 700 and 800, plus 400 italic. Code is
  Fira Code with ligatures off, because beginners copy code and `!=` must
  look like `!=`. Math is Fira Math. Body text is 17px with 1.6 line height,
  the scale ratio is 1.25, and the measure is at most 70ch.
- **Boldness goes in one place:** the landing wordmark is huge, weight 800,
  left-aligned, and sits on a hairline "axis" with inward minor ticks, a nod
  to scienceplots' tick style done in pure CSS. Everything else stays quiet.

## Direction B: "Preprint"

The idea is to set the prose in the journals' own typeface. STIX Two was
commissioned by the physics publishers (APS and AIP among them), and MathJax
ships a matching STIX Two math font, so text and equations are one design,
like reading PRB. Everything that is interface rather than prose (navigation,
sidebars, headings, code) is set in Iosevka, the narrow open-source monospace
that terminal people love. That supplies the hacker half.

| token  | light     | dark      | use |
|--------|-----------|-----------|-----|
| paper  | `#FFFFFF` | `#141311` | background (white, never cream) |
| ink    | `#1C1B19` | `#E6E1D8` | body text |
| muted  | `#6A665F` | `#9A948A` | meta lines, captions |
| rule   | `#E7E3DD` | `#2C2A26` | borders |
| red    | `#B31B1B` | `#F0605D` | links, current page, "ours" (arXiv's red) |

- **Type:** body is STIX Two Text (variable weight, plus italic) at 18px with
  1.65 line height, since serif text needs more leading. Headings, UI and code
  are Iosevka at 400 and 700. Math is STIX Two.
- **Boldness goes in one place:** the landing is a centred title block, like
  a paper's first page. The name is in STIX Two italic at display size, and
  the tagline is in Iosevka.

## Review against the brief and against generic defaults

- **A risks the stock-docs look** (white, blue links, sans). It stays
  distinct through the one-family math and code, the scienceplots palette and
  the ticked hero. I also changed its headings from Shibuya's medium weight
  to 700 with tight tracking, and removed the violet.
- **B risks the "cream + serif + terracotta" cliché.** It is guarded against
  by white paper, crimson rather than clay, and a serif used for body text
  only (the hero is italic text, not a high-contrast display face).
- **Both remove Shibuya's ALL-CAPS sidebar captions.**
- **Both replace the resource meta string.** The current
  `paper · 2020 · foundational` is a templated middle-dot string, and "paper"
  repeats the group heading. It becomes `2020, foundational`. "Our material"
  keeps the kind: `notebook, intermediate`.
- **External links in resource lists get ↗.** This is information (internal
  vs external), not decoration, and the user asked for the distinction.

## Fonts

All fonts are self-hosted from `docs/_static/fonts/`, with no Google Fonts
requests, which fits the Ungoogled-Chromium taste. They are the fontsource
woff2 files (latin subset) for Fira Sans, Fira Code, STIX Two Text and
Iosevka, all SIL OFL, with each package's licence copied alongside. MathJax's
math fonts still come from jsdelivr, like MathJax itself.

## Tasks

- [ ] TDD: meta string change (test first in `tests/test_build.py`).
- [ ] Fetch fonts and licences. Wire `conf.py`: `html_static_path`,
  `html_css_files`, `accent_color` (the nearest Radix ramp), and
  `mathjax4_config`.
- [ ] Build A, then screenshot the landing, topic and notebook pages in light
  and dark, plus a phone-width view. Critique and fix.
- [ ] Build B, then take the same screenshots. Critique and fix.
- [ ] Publish a side-by-side comparison. The user picks one.
- [ ] Delete the losing direction's CSS and fonts. Run the strict build and
  linkcheck, update CLAUDE.md, commit.

## Execution log
