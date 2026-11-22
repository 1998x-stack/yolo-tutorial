"""Check FPN and YOLOv3 feature-fusion shape compatibility (stdlib only).

The calculation validates spatial dimensions, NOT convolutional weights or
actual data flow. Tensor layouts are (batch, channels, height, width).
"""
from __future__ import annotations
import argparse


def shape_map(input_size: int, channels=(256, 512, 1024)) -> dict[str, tuple[int, int, int, int]]:
    if input_size <= 0 or input_size % 32:
        raise ValueError("input_size must be a positive multiple of 32")
    if len(channels) != 3 or min(channels) <= 0:
        raise ValueError("expected three positive channel counts")
    return {
        "C3": (1, channels[0], input_size // 8, input_size // 8),
        "C4": (1, channels[1], input_size // 16, input_size // 16),
        "C5": (1, channels[2], input_size // 32, input_size // 32),
    }


def upsample2(shape: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    n, c, h, w = shape
    return n, c, h * 2, w * 2


def concat_channels(a: tuple[int, int, int, int], b: tuple[int, int, int, int]):
    if a[0] != b[0] or a[2:] != b[2:]:
        raise ValueError(f"cannot concat spatially incompatible shapes: {a} vs {b}")
    return a[0], a[1] + b[1], a[2], a[3]


def add_features(a: tuple[int, int, int, int], b: tuple[int, int, int, int]):
    if a != b:
        raise ValueError(f"elementwise addition requires identical shapes: {a} vs {b}")
    return a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=416)
    args = parser.parse_args()
    c = shape_map(args.size)
    # Original FPN's lateral 1x1 projection aligns channel counts at 256.
    projected_p5 = (1, 256, c["C5"][2], c["C5"][3])
    lateral_c4 = (1, 256, c["C4"][2], c["C4"][3])
    p4 = add_features(lateral_c4, upsample2(projected_p5))
    # YOLOv3-inspired concatenation instead combines channels.
    # Actual YOLOv3 first projects deep features to fewer channels; this is\n    # a shape-only example of 256 projected deep channels + 512 lateral.\n    yolo_merge = concat_channels(c["C4"], upsample2(projected_p5))
    print("Backbone:", c)
    print("FPN P4 after lateral addition:", p4)
    print("YOLOv3-style channel concat at stride 16:", yolo_merge)


if __name__ == "__main__":
    main()
