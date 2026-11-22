"""Deterministic class-wise Hard NMS and linear Soft-NMS reference.

Boxes use continuous xyxy coordinates and area=(x2-x1)*(y2-y1).
Scores must be finite and in [0,1]. Greedy ties break by ID lexically.
The linear Soft-NMS implementation re-sorts after each score update.
This is a correctness lab, not a GPU inference kernel.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import math


@dataclass(frozen=True)
class Detection:
    id: str
    cls: str
    score: float
    box: tuple[float, float, float, float]


def _validate(d: Detection) -> None:
    if not d.id or not d.cls or not math.isfinite(d.score) or not 0 <= d.score <= 1:
        raise ValueError("id/class must be nonempty and score in [0,1]")
    if len(d.box) != 4 or not all(math.isfinite(v) for v in d.box):
        raise ValueError("xyxy box must have four finite coordinates")
    x1, y1, x2, y2 = d.box
    if not (x1 < x2 and y1 < y2):
        raise ValueError("xyxy box must have positive area")


def iou(a, b) -> float:
    x1, y1, x2, y2 = a
    u1, v1, u2, v2 = b
    intersection = max(0.0, min(x2, u2) - max(x1, u1)) * max(
        0.0, min(y2, v2) - max(y1, v1))
    union = (x2 - x1) * (y2 - y1) + (u2 - u1) * (v2 - v1) - intersection
    return intersection / union


def suppress(
    detections: list[Detection],
    iou_threshold: float = 0.5,
    score_floor: float = 0.25,
    mode: str = "hard",
) -> list[Detection]:
    if not 0 <= iou_threshold <= 1 or not 0 <= score_floor <= 1:
        raise ValueError("thresholds must be in [0,1]")
    if mode not in ("hard", "soft-linear"):
        raise ValueError("mode must be hard or soft-linear")
    for d in detections:
        _validate(d)
    # NMS operates within a class; identical geometry across classes can survive.
    grouped: dict[str, list[Detection]] = {}
    for d in detections:
        if d.score >= score_floor:
            grouped.setdefault(d.cls, []).append(d)
    kept = []
    for cls in sorted(grouped):
        pending = grouped[cls]
        while pending:
            pending.sort(key=lambda d: (-d.score, d.id))
            best = pending.pop(0)
            kept.append(best)
            updated = []
            for other in pending:
                overlap = iou(best.box, other.box)
                if mode == "hard":
                    if overlap > iou_threshold:
                        continue
                    score = other.score
                else:
                    score = other.score * (1.0 - overlap) if overlap > iou_threshold else other.score
                if score >= score_floor:
                    updated.append(replace(other, score=score))
            pending = updated
    return sorted(kept, key=lambda d: (-d.score, d.id))


def sample_boxes() -> list[Detection]:
    return [
        Detection("A", "cat", 0.95, (40, 40, 140, 140)),
        Detection("B", "cat", 0.88, (50, 50, 150, 150)),
        Detection("C", "cat", 0.72, (190, 40, 290, 140)),
        Detection("D", "dog", 0.80, (40, 40, 140, 140)),
    ]


if __name__ == "__main__":
    sample = sample_boxes()
    print(f"IoU(A,B): {iou(sample[0].box, sample[1].box):.6f}")
    for mode in ("hard", "soft-linear"):
        print(mode, [(d.id, d.cls, round(d.score, 4))
                     for d in suppress(sample, 0.5, 0.25, mode)])
