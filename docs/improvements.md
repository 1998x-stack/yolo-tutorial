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
- Validation: GitHub Actions Quality run #1 for PR #3 (run ID 44986969762) passed: all 17 Python static/lab tests, Chromium for the homepage and chapters 01–10 at 1440/768/390/360 px, Chapter 08 shape controls, MathML/SVG rendering, responsive figure scrolling and browser errors (none). Browser screenshots and JSON report were uploaded as an Actions artifact.

### 2026-11-22 — Batch 03 (chapters 11–15, detailed one-by-one rebuild)

- Five independent explainers: synchronized detection augmentation and clipping; Darknet/CSP/Rep backbone evolution and MAC conventions; SPPF/PAN/decoupled heads vs training-only assignment; class-wise Hard/Soft NMS and NMS-free training; pinned YOLOv5 v7.0 training/data/export path.
- Added 8 independently viewable original SVGs with exact inline parity; total reviewed gallery for chapters 06–15 is now 16 figures.
- Added deterministic stdlib labs with their own unit tests for image/label geometry, Rep linear folding, SPPF max-pool equivalence, NMS semantics and v7.0 anchor decode/label validation.
- Preserved verifiable primary citations, frozen source references and per-chapter evidence ledgers `11.json`–`15.json`; explicitly separate illustrative calculations from paper metrics.
- Updated the 28-card offline-first homepage and 01–15 sidebar navigation, README, architecture notes, AGENTS guardrails, browser interactivity tests and responsive coverage.
- CI and Pages release: pending validation at the time of authoring. Inspect workflow execution before marking the batch as passed.

### 2026-11-22 — Batch 04: modern YOLOs and small-object deployment (16–20)
- Replaced five legacy lecture-style pages with self-contained technical explainers, consistent 01–20 navigation, five exported original SVG diagrams, native MathML and offline interactive teaching controls.
- Cross-checked original ECCV 2024 YOLOv9, NeurIPS 2024 YOLOv10, NeurIPS 2025 YOLOv12, Ultralytics YOLOv8/YOLO11 architecture, original RepVGG/knowledge-distillation publications, COCO area definitions and SAHI paper/code; removed ungrounded anecdotal boosts and incomparable speed claims.
- Added per-page evidence ledgers 16–20 (>=6 claims each), standard-library deterministic computations covering DFL bin interpolation, anchor-free grid count, attention relation counts, raw weight bytes, tile starts and global coordinate offsets.
- Expanded site/evidence/SVG source checks and Chromium checks from 15 to 20 chapters; new browser interactions test numeric updates on five pages. Pending GitHub Actions run results should be consulted before marking CI/Pages successful.
