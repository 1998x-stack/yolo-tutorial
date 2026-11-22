"""Audit the critical [yolo] prediction head settings in a Darknet YOLOv3 cfg.

Usage: python -m labs.darknet_cfg_audit path/to/yolov3-custom.cfg --classes 2

This is a *consistency* check, not a replacement for compiling, training, or
validating the actual Darknet model. No third-party packages required.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def parse_cfg(text: str) -> list[tuple[str, dict[str, str]]]:
    blocks: list[tuple[str, dict[str, str]]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1].strip().lower()
            if not name:
                raise ValueError(f"line {number}: empty block name")
            blocks.append((name, {}))
        elif "=" in line:
            if not blocks:
                raise ValueError(f"line {number}: value without block")
            key, value = line.split("=", 1)
            blocks[-1][1][key.strip().lower()] = value.strip()
        else:
            raise ValueError(f"line {number}: unrecognized syntax {line!r}")
    return blocks


def _integers(value: str) -> list[int]:
    return [int(v.strip()) for v in value.split(",") if v.strip()]


def audit(text: str, expected_classes: int) -> list[str]:
    if expected_classes <= 0:
        raise ValueError("expected_classes must be positive")
    blocks = parse_cfg(text)
    issues: list[str] = []
    net = next((props for name, props in blocks if name == "net"), None)
    if net is None:
        issues.append("missing [net] block")
    else:
        for axis in ("width", "height"):
            try:
                value = int(net.get(axis, ""))
                if value <= 0 or value % 32:
                    issues.append(f"[net] {axis} must be a positive multiple of 32")
            except ValueError:
                issues.append(f"[net] {axis} must be an integer")
    heads = [(i, block) for i, block in enumerate(blocks) if block[0] == "yolo"]
    if len(heads) != 3:
        issues.append(f"expected three [yolo] heads in full YOLOv3; got {len(heads)}")
    all_masks: list[int] = []
    for head_num, (i, (_, props)) in enumerate(heads, start=1):
        try:
            mask = _integers(props["mask"])
            anchors = [float(v.strip()) for v in props["anchors"].split(",") if v.strip()]
            classes = int(props["classes"])
        except (KeyError, ValueError) as exc:
            issues.append(f"head {head_num}: invalid mask/anchors/classes: {exc}")
            continue
        if len(mask) != 3 or len(set(mask)) != 3:
            issues.append(f"head {head_num}: expected three distinct mask indices")
        if len(anchors) != 18 or any(x <= 0 for x in anchors):
            issues.append(f"head {head_num}: expected nine positive anchor (w,h) pairs")
        if any(x < 0 or x >= len(anchors) // 2 for x in mask):
            issues.append(f"head {head_num}: mask references nonexistent anchor")
        if classes != expected_classes:
            issues.append(f"head {head_num}: classes={classes}, expected {expected_classes}")
        if i == 0 or blocks[i - 1][0] != "convolutional":
            issues.append(f"head {head_num}: preceding block must be [convolutional]")
        else:
            try:
                filters = int(blocks[i - 1][1]["filters"])
                target = len(mask) * (5 + expected_classes)
                if filters != target:
                    issues.append(f"head {head_num}: filters={filters}, expected {target}")
            except (ValueError, KeyError):
                issues.append(f"head {head_num}: preceding convolution missing valid filters")
        all_masks += mask
    if len(all_masks) != len(set(all_masks)):
        issues.append("anchor mask indices overlap across heads; inspect intentional reuse")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cfg", type=Path, help="Darknet cfg file path")
    parser.add_argument("--classes", type=int, required=True)
    args = parser.parse_args()
    errors = audit(args.cfg.read_text(encoding="utf-8"), args.classes)
    if errors:
        for message in errors:
            print("ERROR:", message)
        return 1
    print("PASS: three YOLOv3 heads, mask/class/filter and net dimensions are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
