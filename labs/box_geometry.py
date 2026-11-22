"""Numerically safe geometric IoU variants for *demonstration*, not backprop.

Each box is (x1, y1, x2, y2), with coordinates in the same continuous units.
The functions reject invalid or zero-area boxes and use standard non-inclusive
rectangle areas (no +1 pixel convention).
"""
from __future__ import annotations
import math
from typing import Sequence


def _box(b: Sequence[float]) -> tuple[float, float, float, float]:
    if len(b) != 4:
        raise ValueError("box must contain four coordinates")
    x1, y1, x2, y2 = map(float, b)
    if not all(map(math.isfinite, (x1, y1, x2, y2))):
        raise ValueError("box coordinates must be finite")
    if not (x2 > x1 and y2 > y1):
        raise ValueError("box must have strictly positive width and height")
    return x1, y1, x2, y2


def variants(a: Sequence[float], b: Sequence[float]) -> dict[str, float]:
    ax1, ay1, ax2, ay2 = _box(a)
    bx1, by1, bx2, by2 = _box(b)
    intersection = max(0.0, min(ax2, bx2) - max(ax1, bx1)) * max(
        0.0, min(ay2, by2) - max(ay1, by1)
    )
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - intersection
    iou = intersection / union
    cx1, cy1 = min(ax1, bx1), min(ay1, by1)
    cx2, cy2 = max(ax2, bx2), max(ay2, by2)
    cover_area = (cx2 - cx1) * (cy2 - cy1)
    giou = iou - (cover_area - union) / cover_area
    center_distance_sq = (
        ((ax1 + ax2) / 2 - (bx1 + bx2) / 2) ** 2
        + ((ay1 + ay2) / 2 - (by1 + by2) / 2) ** 2
    )
    diagonal_sq = (cx2 - cx1) ** 2 + (cy2 - cy1) ** 2
    distance_term = center_distance_sq / diagonal_sq
    diou = iou - distance_term
    aw, ah = ax2 - ax1, ay2 - ay1
    bw, bh = bx2 - bx1, by2 - by1
    v = (4 / math.pi**2) * (math.atan(bw / bh) - math.atan(aw / ah)) ** 2
    alpha = v / (1 - iou + v) if (1 - iou + v) > 0 else 0.0
    ciou = diou - alpha * v
    return {
        "iou": iou,
        "giou": giou,
        "diou": diou,
        "ciou": ciou,
        "iou_loss": 1 - iou,
        "giou_loss": 1 - giou,
        "diou_loss": 1 - diou,
        "ciou_loss": 1 - ciou,
    }


if __name__ == "__main__":
    sample = variants((0, 0, 2, 2), (3, 0, 5, 2))
    for name, score in sample.items():
        print(f"{name:12s}: {score:.6f}")
