# Repository architecture

## Canonical content paths

- `index.html` is the static entry point.
- `chapters/01.html` through `chapters/28.html` are canonical chapter URLs.
- `courses.json` is the structured course catalogue and stores canonical chapter paths.
- `assets/theme.css` and `assets/site.js` are the shared style and progressive-enhancement assets.
- Root `01.html`–`28.html` files are noindex compatibility redirects for old bookmarks and inbound links.

## Why the chapter directory exists

The original repository stored all 28 chapter pages beside the homepage, styles, data, and scripts. Moving the canonical articles into `chapters/` separates content from site infrastructure and makes the directory extensible. Legacy root URLs remain valid through redirects.

## Offline behavior

The homepage renders its course cards in static HTML. Search and phase filtering are progressive enhancements from `assets/site.js`; the page does not fetch `courses.json` at runtime. This avoids the browser security restriction that blocks local JSON fetches from `file://` pages. The JSON catalogue remains available for tooling and consistency checks.

## Chapter migration

Chapters 01–05 were rebuilt as self-contained articles with accessible original inline SVG, native MathML, primary-paper citations, and corrected benchmark context. Chapters 06–28 were moved without content rewriting; their relative stylesheet and homepage paths were adjusted. Future chapter editing should follow `AGENTS.md`.

## Quality gates

- `tests/test_site.py` checks catalogue integrity, local links, redirects, independent article structure, SVG XML, MathML presence, and external runtime dependencies.
- `tests/browser_check.py` runs Chromium against the static site at desktop and mobile widths, checks search/filter behavior, and inspects the first five chapters for overflow and browser errors.
- `.github/workflows/quality.yml` runs both gates on pushes and pull requests.

## Publishing

The root directory is suitable for GitHub Pages when Pages is configured to publish from the repository root. Repository code cannot prove that Pages settings are enabled; verify deployment state in Settings → Pages and Actions.
