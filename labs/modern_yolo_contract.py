"""Reproducible standard-library toy contracts for YOLO articles 16-20.

These deterministic computations are not trained model inference or paper replications.
"""
from __future__ import annotations
from math import ceil, floor, isclose


def dfl_target_weights(target: float, max_bin: int = 15) -> tuple[int, int, float, float]:
    if not 0 <= target < max_bin:
        raise ValueError("target must be in [0, max_bin)")
    left = floor(target)
    right = left + 1
    return left, right, right - target, target - left


def dfl_expected(probabilities: list[float]) -> float:
    if not probabilities or any(p < 0 for p in probabilities) or not isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError("nonnegative probabilities must sum to 1")
    return sum(i * p for i, p in enumerate(probabilities))


def grid_positions(shape: int = 640, strides: tuple[int, ...] = (8, 16, 32)) -> int:
    if shape <= 0 or any(s <= 0 or shape % s for s in strides):
        raise ValueError("shape must be positive and divisible by all strides")
    return sum((shape // s) ** 2 for s in strides)


def attention_relationship_counts(tokens: int, window_tokens: int) -> tuple[int, int]:
    if tokens <= 0 or window_tokens <= 0 or tokens % window_tokens:
        raise ValueError("tokens must be divisible by window_tokens")
    return tokens * tokens, tokens * window_tokens


def raw_weight_bytes(parameters: int, bit_width: int) -> int:
    if parameters < 0 or bit_width not in (4, 8, 16, 32):
        raise ValueError("unsupported bit width or negative parameters")
    return ceil(parameters * bit_width / 8)


def tile_origins(length: int, tile: int, overlap: float) -> list[int]:
    if length <= 0 or tile <= 0 or tile > length or not 0 <= overlap < 1:
        raise ValueError("invalid tile dimensions or overlap")
    step = tile * (1 - overlap)
    out: list[int] = []
    cursor = 0.0
    while cursor < length - tile:
        origin = round(cursor)
        if not out or origin > out[-1]:
            out.append(origin)
        cursor += step
    if not out or out[-1] != length - tile:
        out.append(length - tile)
    return out


def offset_box(box: tuple[float, float, float, float], origin: tuple[float, float]) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    if x2 < x1 or y2 < y1:
        raise ValueError("invalid box ordering")
    x0, y0 = origin
    return x0 + x1, y0 + y1, x0 + x2, y0 + y2


def main() -> None:
    print("YOLO teaching contracts | 640 pixels:", grid_positions())
    print("DFL t=3.7:", dfl_target_weights(3.7))
    print("Attention N=256 W=64:", attention_relationship_counts(256,64))
    starts = tile_origins(2048,640,.2)
    print("Tiling 2048/640 20%:",len(starts),"per axis,",len(starts)**2,"patches")


if __name__ == "__main__":
    main()
