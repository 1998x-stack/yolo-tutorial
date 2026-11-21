# AGENTS.md

## Purpose

Maintain this repository as a rigorous, self-contained Chinese technical course on object detection and the YOLO model family. Use the workflow and review gates from [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts), especially its evidence ledger, progressive narrative, original SVG diagrams, offline-first HTML, and browser QA.

## Article contract

Every chapter is an independent article. A reader arriving from search, a bookmark, or an external link must be able to understand it without opening another chapter first.

- Define the problem, required terms, symbols, tensor shapes, and assumptions locally.
- Never use phrases such as “上一章已经介绍”, “本章将继续”, “讲义介绍了”, “下面我们来回顾” as substitutes for explanation.
- Do not write lecturer roleplay, fabricated first-person project anecdotes, or production-process notes in the article.
- Keep the article focused on the technical subject; authoring workflow, build steps, and QA status belong in README/docs.
- Use a causal progression: reader question → baseline limitation → core mechanism → diagram → equation/shape → minimal code or worked example → evidence → limitations.

## Scientific and historical accuracy

- Prefer primary papers, official benchmark protocols, official repositories, and original datasets.
- Distinguish arXiv submission date, conference publication date, technical report date, and later code releases.
- Separate paper claims, explanatory simplifications, implementation details, and later variants.
- Every numeric result must identify the dataset/version/split, metric, model/input resolution, and relevant hardware/timing boundary when available.
- Do not compare AP@0.5 with COCO AP (IoU 0.50:0.95) as if they were the same metric.
- Do not describe YOLO9000's WordTree as modern text-prompt open-vocabulary detection.
- Never invent training details, metrics, benchmarks, API behavior, or personal experiences. If evidence is unavailable, qualify or omit the claim.

## Figures, equations, and code

- Draw original SVGs; do not copy third-party figures, Colah diagrams, or paper artwork without explicit rights.
- Each SVG must include `viewBox`, `<title>`, `<desc>`, and meaningful labels. The caption must state what the figure demonstrates.
- Keep color semantics consistent within an article; color must not be the only way to distinguish concepts.
- Use native MathML for mathematical expressions where appropriate. Verify exponents, subscripts, normalization axes, and coordinate conventions.
- Code examples must state their input/output conventions and handle relevant edge cases. A toy example must not be presented as a complete training or deployment implementation.

## Repository conventions

- Canonical chapter pages live in `chapters/NN.html`.
- Root `NN.html` files are compatibility redirects; do not author chapter content there.
- `courses.json` is the structured course catalogue; keep all 28 entries and their `file` paths in sync.
- `index.html` is a static, file://-compatible course home. Do not make initial rendering depend on fetch().
- Shared styles and scripts live in `assets/`; keep pages offline-first and avoid external runtime dependencies.
- Preserve existing PDFs and historical chapter content unless the task explicitly changes them.
- Do not add a license or imply a third-party asset is reusable without checking its terms.

## Required validation before publishing

1. Run `python -m unittest discover -s tests -v`.
2. Run `python tests/browser_check.py` after installing Playwright and Chromium.
3. Inspect 1440px desktop, tablet, 390px and 360px mobile layouts.
4. Check local links, console/page errors, horizontal overflow, SVG labels, keyboard focus and at least one real interaction (home search/filter).
5. Review the diff for incorrect claims, stale paths, duplicate navigation, accidental external dependencies and unverified metrics.
6. Report checks that were skipped as “not verified”; never claim a browser test passed unless it ran.
