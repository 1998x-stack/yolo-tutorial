"""Audit YOLOv5 v7.0 classic anchor-based geometry and YOLO labels.

No torch or model download. The output and decode conventions are grounded in
ultralytics/yolov5 v7.0 models/yolo.py Detect.forward/_make_grid.
Optional --labels scans a directory recursively for YOLO TXT label files.
It cannot verify images, data.yaml, missing label files or dataset leakage.

Run:
  python -m labs.yolov5_contract
  python -m labs.yolov5_contract --labels labs/sample-yolov5-labels --classes 2
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
from dataclasses import dataclass


def sigmoid(x: float) -> float:
    if not math.isfinite(x):
        raise ValueError("logit must be finite")
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    z = math.exp(x)
    return z / (1.0 + z)


def decode_v7(
    logits: tuple[float, float, float, float],
    grid: tuple[int, int],
    stride: int,
    anchor: tuple[float, float],
) -> tuple[float, float, float, float]:
    """Return center xy, width, height in input-image pixel units."""
    if len(logits) != 4 or len(grid) != 2 or len(anchor) != 2:
        raise ValueError("expected 4 logits, 2 grid coordinates, 2 anchor dimensions")
    if stride <= 0 or any(v < 0 for v in grid) or min(anchor) <= 0:
        raise ValueError("invalid grid, stride or anchor")
    if not all(map(math.isfinite, (*logits, *anchor))):
        raise ValueError("logits and anchors must be finite")
    tx, ty, tw, th = logits
    gx, gy = grid
    ax, ay = anchor
    return (
        (2 * sigmoid(tx) - 0.5 + gx) * stride,
        (2 * sigmoid(ty) - 0.5 + gy) * stride,
        (2 * sigmoid(tw)) ** 2 * ax,
        (2 * sigmoid(th)) ** 2 * ay,
    )


def candidates(image_size: int, anchors_per_cell: int = 3) -> int:
    if image_size <= 0 or image_size % 32 or anchors_per_cell <= 0:
        raise ValueError("size must be multiple of 32 and anchor count positive")
    return anchors_per_cell * sum((image_size // s) ** 2 for s in (8, 16, 32))


@dataclass
class LabelAudit:
    files: int
    objects: int
    errors: list[str]


def audit_labels(directory: Path, classes: int) -> LabelAudit:
    if classes <= 0 or not directory.is_dir():
        raise ValueError("classes must be positive and directory must exist")
    files = sorted(directory.rglob("*.txt"))
    errors = []
    objects = 0
    if not files:
        errors.append(f"no .txt label files beneath {directory}")
    for path in files:
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                errors.append(f"{path}:{lineno}: expected 5 fields, got {len(parts)}")
                continue
            class_id, *coords = parts
            try:
                if not class_id.isdecimal() or not 0 <= int(class_id) < classes:
                    raise ValueError("class ID out of range")
                x, y, w, h = [float(t) for t in coords]
                if not all(map(math.isfinite, (x, y, w, h))):
                    raise ValueError("non-finite coordinates")
                if w <= 0 or h <= 0 or x-w/2 < -1e-9 or x+w/2 > 1+1e-9 or y-h/2 < -1e-9 or y+h/2 > 1+1e-9:
                    raise ValueError("center, width or height make box invalid/out-of-bounds")
                objects += 1
            except ValueError as exc:
                errors.append(f"{path}:{lineno}: {exc}")
    return LabelAudit(files=len(files), objects=objects, errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--classes", type=int, default=2)
    args = parser.parse_args()
    print("candidate count @640:", candidates(640))
    print("v7.0 logits=0 decode:", decode_v7((0,0,0,0), (4,6), 32, (116,90)))
    if args.labels is not None:
        try:
            report = audit_labels(args.labels, args.classes)
        except ValueError as exc:
            parser.error(str(exc))
        print(f"files={report.files}, valid objects={report.objects}, errors={len(report.errors)}")
        for issue in report.errors:
            print("ERROR:", issue)
        if report.errors:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
