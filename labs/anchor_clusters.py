"""Simple YOLOv2-style anchor *dimension* clustering using distance 1-IoU.

Input CSV rows: width,height (positive floats), in the SAME reference units.
This is a deterministic teaching implementation of assignment + arithmetic
centroid updates. It is not a reproduction of Darknet's calc_anchors routine.

Usage: python -m labs.anchor_clusters boxes.csv --k 5 --seed 42
"""
from __future__ import annotations
import argparse
import csv
import random
from pathlib import Path


def shape_iou(a: tuple[float, float], b: tuple[float, float]) -> float:
    aw, ah = a
    bw, bh = b
    if min(aw, ah, bw, bh) <= 0:
        raise ValueError("box dimensions must be strictly positive")
    intersection = min(aw, bw) * min(ah, bh)
    return intersection / (aw * ah + bw * bh - intersection)


def cluster(
    widths_heights: list[tuple[float, float]],
    k: int,
    seed: int = 42,
    max_iters: int = 100,
) -> tuple[list[tuple[float, float]], float]:
    data = [(float(w), float(h)) for w, h in widths_heights]
    if not data or any(w <= 0 or h <= 0 for w, h in data):
        raise ValueError("provide positive width and height for each box")
    if not (1 <= k <= len(data)):
        raise ValueError("k must be between 1 and the number of boxes")
    if max_iters <= 0:
        raise ValueError("max_iters must be positive")
    rng = random.Random(seed)
    centers = rng.sample(data, k)
    prev = None
    for _ in range(max_iters):
        assignments = tuple(
            max(range(k), key=lambda j: shape_iou(point, centers[j]))
            for point in data
        )
        if assignments == prev:
            break
        prev = assignments
        updated = []
        for index in range(k):
            members = [point for point, assigned in zip(data, assignments) if assigned == index]
            if members:
                updated.append((
                    sum(w for w, _ in members) / len(members),
                    sum(h for _, h in members) / len(members),
                ))
            else:
                # Deterministic restart for an empty cluster.
                updated.append(data[rng.randrange(len(data))])
        centers = updated
    mean_best_iou = sum(max(shape_iou(p, c) for c in centers) for p in data) / len(data)
    return sorted(centers, key=lambda c: c[0] * c[1]), mean_best_iou


def read_boxes(path: Path) -> list[tuple[float, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream)
        result = []
        for row in rows:
            if not row:
                continue
            if len(row) != 2:
                raise ValueError("each row must contain width,height")
            try:
                result.append((float(row[0]), float(row[1])))
            except ValueError:
                if not result and [x.strip().lower() for x in row] == ["width", "height"]:
                    continue
                raise
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--iters", type=int, default=100)
    args = parser.parse_args()
    centers, best_iou = cluster(read_boxes(args.csv), args.k, args.seed, args.iters)
    print("Anchors ordered by area:")
    for w, h in centers:
        print(f"  ({w:.3f}, {h:.3f})")
    print(f"mean best-anchor IoU: {best_iou:.4f}")
    print("Teaching approximation only; evaluate recalls and training AP independently.")


if __name__ == "__main__":
    main()
