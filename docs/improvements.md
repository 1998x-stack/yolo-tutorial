# Portfolio Engineering Improvements

### 2026-11-06 08:24 UTC — ChatGPT Portfolio Iteration
- Run ID: portfolio-20261106T082337Z-4f8a
- Repo / Base SHA: 1998x-stack/yolo-tutorial / 707bc2ca894dfc85d311b8f1fc04297de7904733
- Historical context: Default-branch docs/improvements.md returned GitHub 404 before any changes; first initialization. No existing pull requests; only three historical commits. No prior agent changes or pending same-topic PR found.
- Product problem & expected user value: README instructs opening index.html directly, but the index calls fetch('courses.json'), which is blocked by many browsers for file:// pages. Offline learners cannot see chapter links. The fallback supplies all 28 local chapter links without network or local server.
- Engineering diagnosis & evidence: index.html inline script calls fetch('courses.json') unconditionally, with catch rendering only an error; direct file:// navigation is unsupported. Existing 01.html through 28.html files are present in the repository tree.
- Options & decision: P2 offline navigation (benefit 5 + correctness 4 + evidence 5 + verification 4 - cost 2 - risk 1 = 15) selected. P2 network error recovery (3+3+4+3-2-2=9) and P3 catalogue schema validation (2+3+3+3-3-2=6) deferred. This is a static source diagnosis, not measured user research.
- Changes: index.html selects offline navigation for file:// and leaves HTTP fetch behavior unchanged; local-navigation.js creates accessible text chapter links using DOM APIs; tests/local-navigation.test.cjs covers normal chapter count, repeated render, and invalid counts. No dependencies or schema changes.
- Validation: A: Node.js v22.16.0 node --test tests/local-navigation.test.cjs, 3/3 passed (local copy of the new module/test). C: node --check local-navigation.js passed. D: real browser file:// and HTTP visual E2E not run; isolated environment cannot resolve github.com for cloning. Existing course chapter pages not modified. CI not claimed.
- Security & regression review: No innerHTML with untrusted content, no network in fallback, no secrets, no workflow/deployment changes. HTTP behavior preserved by early return only for file://. Risk: chapter count fixed to current 28; update it when new chapters are added.
- Risk & rollback: Close Draft PR without merging, or revert its commits. No changes to main.
- Follow-up: Browser E2E test both file:// and HTTP modes and verify all 28 links and course metadata.
- Commit: 90f132b24822ba9dc31cdc3c0e2ac1e8d4920b1c (index); cde93033c00477fa9a86987f3a6b7c9d889afbf4 (module); 73935c5a0c0543d001c6361b2836a51884e0297b (tests)
- PR: https://github.com/1998x-stack/yolo-tutorial/pull/1 (Draft)

### 2026-11-21 — Course architecture and foundation batch (01–05)
- Scope: reorganize all 28 canonical chapter pages under `chapters/`, preserve root chapter URLs as noindex redirects, move shared assets under `assets/`, and rebuild the course homepage/README.
- Content: rewrite chapters 01–05 as self-contained technical articles with original inline SVG, native MathML, paper references, corrected benchmark context, and an evidence ledger.
- Engineering: static homepage cards (no runtime JSON fetch), search and stage filtering as progressive enhancement, `AGENTS.md` content rules, local-link/static tests, Chromium desktop/mobile browser checks, and a GitHub Actions quality workflow.
- Technical audit notes: distinguish YOLOv1's 2015 arXiv submission from CVPR 2016 publication; separate YOLOv2 ablation rows from final resolution benchmarks; describe YOLO9000 WordTree as hierarchical joint classification/detection rather than prompt-based open-vocabulary detection; correct YOLOv3 COCO AP_L to 41.9.
- Validation: GitHub Actions Quality run #9 (run ID 44912512867) passed. All 9 Python static tests passed; Chromium checked the homepage and chapters 01–05 at 1440, 768, 390, and 360 px, verified search/filter and empty-state behavior, MathML rendering/focus, print visibility, horizontal overflow, and browser errors (none).

### 2026-11-22 — Evidence-backed batch 02 (chapters 06–10)
- Scope: rewrite the YOLOv3 engineering, YOLOv4, anchor clustering, IoU-family losses and FPN articles as independent entries.
- Source control: primary paper locators and per-chapter `docs/evidence/06.json`–`10.json`; distinguish original YOLOv3 from later YOLOv4 and Ultralytics conventions.
- Geometry: add deterministic anchor clusters, IoU/GIoU/DIoU/CIoU, cfg audit, FPN shape checks; add optional OpenCV/Darknet inference with explicit class-wise NMS and coordinate conventions.
- Visual narrative: 8 original explanatory SVGs (also exported under `assets/figures/`), native MathML, Chapter 08 anchor selector with keyboard-accessible controls, mobile figure scrolling.
- Navigation: first ten articles share a stage sidebar, Chapter 05 now advances to 06; homepage metadata and README reflect actual reviewed coverage.
- Validation: CI pending for this batch; do not mark checks passed until run log verifies.
