"""SPPF pooling equivalence and YOLO detection-head output shape contracts.

Pure stdlib, deterministic. Pooling is stride 1, odd kernel, 'same' spatial
size, and padding -inf (the mathematically correct max-pooling neutral).
This demonstrates the pooling *subgraph* only; SPPF also has convolutions.
"""
from __future__ import annotations
import math
from typing import Sequence


def max_pool_same(image: Sequence[Sequence[float]], kernel: int):
    if kernel < 1 or kernel % 2 == 0:
        raise ValueError("pool kernel must be a positive odd integer")
    h = len(image)
    if h == 0 or len(image[0]) == 0 or any(len(row) != len(image[0]) for row in image):
        raise ValueError("input matrix must be nonempty and rectangular")
    if any(not math.isfinite(value) for row in image for value in row):
        raise ValueError("pooling input values must be finite")
    w = len(image[0])
    r = kernel // 2
    return [[
        max(
            image[i][j]
            for i in range(max(0, y - r), min(h, y + r + 1))
            for j in range(max(0, x - r), min(w, x + r + 1))
        )
        for x in range(w)] for y in range(h)]


def sppf_levels(image):
    y1 = max_pool_same(image, 5)
    y2 = max_pool_same(y1, 5)
    y3 = max_pool_same(y2, 5)
    return image, y1, y2, y3


def assert_sppf_equivalence(image):
    original, y1, y2, y3 = sppf_levels(image)
    if y1 != max_pool_same(image, 5):
        raise AssertionError("first SPPF branch is not 5x5")
    if y2 != max_pool_same(image, 9):
        raise AssertionError("second SPPF branch is not equivalent to 9x9")
    if y3 != max_pool_same(image, 13):
        raise AssertionError("third SPPF branch is not equivalent to 13x13")
    return True


def anchor_head_shape(batch: int, classes: int, anchors_per_cell: int, height: int, width: int):
    """Classic anchor-based head with 4 box + 1 objectness + C categories."""
    if min(batch, classes, anchors_per_cell, height, width) <= 0:
        raise ValueError("all dimensions must be positive")
    channels = anchors_per_cell * (classes + 5)
    return batch, channels, height, width


def concat_channels(*shapes):
    if not shapes or len(shapes[0]) != 4:
        raise ValueError("provide nonempty NCHW shapes")
    n, _, h, w = shapes[0]
    if any(len(s) != 4 or (s[0], s[2], s[3]) != (n, h, w) for s in shapes):
        raise ValueError("concat requires identical N/H/W")
    return n, sum(s[1] for s in shapes), h, w


if __name__ == "__main__":
    image = [[float((x * 23 + y * 13) % 37 - 18) for x in range(7)] for y in range(7)]
    assert assert_sppf_equivalence(image)
    print("SPPF pool5×3 equals direct pool5, pool9 and pool13 at every cell")
    print("YOLOv5-style classic 3-anchor, C=2 head:",
          anchor_head_shape(1, 2, 3, 80, 80))
    print("SPPF pooling branch concat:",
          concat_channels(*[(1, 64, 20, 20)] * 4))
