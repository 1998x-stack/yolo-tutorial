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

- Canonical chapter pages live in `chapters/NN.html`. Chapters 01–20 have been rewritten and reviewed as of 2026-11-22; 21–28 still need deep editorial/technical review.
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

## Reproducible labs (06–10)

- Place standalone deterministic checks in `labs/` and cover their numeric invariants in `tests/test_labs.py`.
- Declare external dependencies, input files, coordinate assumptions and model/config version before showing inference or training commands.
- Verify the full Darknet three-head `filters=A*(5+C)` and `classes/mask/anchors` contract. Do not assume tiny YOLOv3 has three heads.
- The `labs/anchor_clusters.py` result is a teaching approximation, not a pixel-for-pixel Darknet `calc_anchors` reproduction.
- Separate a geometry-only Python IoU demonstration from a differentiable training loss.
- Validate chapter-level interactions (the Chapter 08 anchor-shape selector) in Playwright, including value changes and browser errors.
- Each rewritten chapter needs its own `docs/evidence/NN.json` with claims, source locator, status and limitations.

## Expanded chapter contracts (11–15)

- Data augmentation needs forward coordinate transforms and inverse preprocessing conventions; for Mosaic/CutMix, document visibility clipping and label remapping. Never average bounding box coordinates in MixUp by default.
- For backbones, differentiate parameter count, MACs, FLOPs, memory traffic and measured latency. Structural reparameterization requires algebraically equivalent linear paths and frozen BN before folding.
- SPPF pool5×3 equals direct max pools 5/9/13 only for matching stride/padding/max operation; do not claim a whole-model speed benchmark from that identity.
- Assignment algorithms such as TaskAlignedAssigner use ground truth during training. Do not mislabel them as inference layers or Neck modules.
- For NMS, specify class-aware versus agnostic suppression, score threshold, IoU comparator, tie order, max detections; NMS-free models require appropriate training, not only removal of the postprocessor.
- When describing YOLOv5, anchor-based `ultralytics/yolov5` v7.0 must not be conflated with later anchor-free YOLOv5u variants; pin the code tag for every command or architectural statement.
- Every batch needs accessible standalone SVG exports matching inline drawings, reproducible stdlib lab tests and full four-viewport Chromium checks.

## Chapter contracts (16–20)

- For YOLOv8 distinguish anchor-free points from pretrained box priors, DFL logits from target-interpolation weights, and training-only Task-Aligned Assigner from inference operators.
- YOLOv9 PGI reversible auxiliary branch is a training information route, not a mandatory inference head; YOLOv10 consistent dual assignments train two pathways but one-to-one predictions serve NMS-free inference.
- YOLO11 and YOLOv12 are separately sourced model lines; never infer benchmark superiority from version numbers alone.
- INT8 raw weight size does not predict latency or memory exactly. Representative PTQ calibration, precision/backend support and task quality are independent gates.
- COCO AP_s uses original annotation area under 32²; SAHI adds patch origin offsets and merges all predictions in the global coordinate system. Split source images before slicing to prevent leakage.
- New pages have 6+ item evidence ledgers, accessible standalone SVGs, one real local interactive control, native MathML where needed, deterministic stdlib labs, browser QA across four widths. Mark any unexecuted validation as unverified.
