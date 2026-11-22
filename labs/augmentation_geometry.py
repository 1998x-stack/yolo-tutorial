"""Deterministic bounding-box geometry for detector augmentation audits.

All coordinates are continuous pixel-edge xyxy, not integer-inclusive pixels.
Only box transforms are provided; pixel transformations and visibility masks
are the responsibility of the caller. No third-party dependencies.
Run: python -m labs.augmentation_geometry
"""
from __future__ import annotations
import math
from typing import Iterable

Box = tuple[float, float, float, float]


def _validate(box: Iterable[float]) -> Box:
    values = tuple(map(float, box))
    if len(values) != 4 or not all(map(math.isfinite, values)):
        raise ValueError("box must be four finite xyxy values")
    x1, y1, x2, y2 = values
    if not (x1 < x2 and y1 < y2):
        raise ValueError("box must have positive width and height")
    return x1, y1, x2, y2


def area(box: Box) -> float:
    x1, y1, x2, y2 = _validate(box)
    return (x2 - x1) * (y2 - y1)


def flip_horizontal(box: Box, width: float) -> Box:
    x1, y1, x2, y2 = _validate(box)
    if not (math.isfinite(width) and width > 0 and 0 <= x1 < x2 <= width):
        raise ValueError("box must lie inside a positive-width image")
    return width - x2, y1, width - x1, y2


def crop_xyxy(
    box: Box, crop: Box, min_visible: float = 0.0
) -> Box | None:
    """Clip to crop and translate into its local origin.

    At zero threshold, zero-area intersections are still discarded. When the
    remaining area is less than the selected visibility ratio, return None.
    """
    if not (0 <= min_visible <= 1):
        raise ValueError("min_visible must be in [0,1]")
    x1, y1, x2, y2 = _validate(box)
    l, t, r, b = _validate(crop)
    a, b1, c, d = max(x1, l), max(y1, t), min(x2, r), min(y2, b)
    if c <= a or d <= b1:
        return None
    if ((c - a) * (d - b1)) / area(box) < min_visible:
        return None
    return a - l, b1 - t, c - l, d - t


def resize_translate_clip(
    box: Box, scale_x: float, scale_y: float, dx: float, dy: float,
    viewport: Box, min_visible: float = 0.0
) -> Box | None:
    """Map a source box to an output canvas, crop to its viewport.

    Returns global output-canvas coordinates, unlike crop_xyxy which
    returns crop-local coordinates. Pixel resampling is NOT implemented.
    """
    x1, y1, x2, y2 = _validate(box)
    if not all(math.isfinite(v) for v in (scale_x, scale_y, dx, dy)):
        raise ValueError("scale/offset must be finite")
    if scale_x <= 0 or scale_y <= 0:
        raise ValueError("scales must be positive")
    output_box = (x1 * scale_x + dx, y1 * scale_y + dy,
                  x2 * scale_x + dx, y2 * scale_y + dy)
    region = _validate(viewport)
    cropped = crop_xyxy(output_box, region, min_visible)
    if cropped is None:
        return None
    return (cropped[0] + region[0], cropped[1] + region[1],
            cropped[2] + region[0], cropped[3] + region[1])


if __name__ == "__main__":
    print("horizontal flip:", flip_horizontal((120, 80, 280, 240), 640))
    print("crop:", crop_xyxy((100, 50, 340, 290), (150, 70, 320, 280), 0.2))
    print("scaled and clipped:",
          resize_translate_clip((10, 10, 80, 90), 2, 2, 50, 0, (0, 0, 180, 160)))
