"""YOLOv3 Darknet COCO inference via OpenCV DNN, with per-class NMS.

External resources (not redistributed here): cfg, weights, class names, image.
Dependencies: pip install -r labs/requirements-inference.txt

Usage:
 python -m labs.yolov3_opencv --cfg yolov3.cfg --weights yolov3.weights \
   --names coco.names --image dog.jpg --out predictions.jpg --size 416
"""
from __future__ import annotations
import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cfg", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--names", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("predictions.jpg"))
    parser.add_argument("--size", type=int, default=416)
    parser.add_argument("--score", type=float, default=0.25)
    parser.add_argument("--nms", type=float, default=0.45)
    args = parser.parse_args()
    if args.size <= 0 or args.size % 32:
        parser.error("--size must be a positive multiple of 32")
    if not (0.0 < args.score < 1.0 and 0.0 < args.nms < 1.0):
        parser.error("--score and --nms must lie strictly between 0 and 1")
    for item in (args.cfg, args.weights, args.names, args.image):
        if not item.is_file():
            parser.error(f"missing file: {item}")

    import cv2  # optional dependency, imported only after CLI validation
    import numpy as np

    image = cv2.imread(str(args.image))
    if image is None:
        parser.error(f"OpenCV cannot read image: {args.image}")
    height, width = image.shape[:2]
    names = [line.strip() for line in args.names.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not names:
        parser.error("class name file is empty")

    net = cv2.dnn.readNetFromDarknet(str(args.cfg), str(args.weights))
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    # OpenCV resizes to a square WITHOUT letterboxing (crop=False).
    # Coordinates are mapped back with independent x/y scale factors.
    blob = cv2.dnn.blobFromImage(
        image, scalefactor=1 / 255.0, size=(args.size, args.size),
        swapRB=True, crop=False
    )
    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    boxes_by_class: dict[int, list[list[int]]] = {}
    scores_by_class: dict[int, list[float]] = {}
    for tensor in outputs:
        for detection in tensor:
            objectness = float(detection[4])
            if objectness <= 0:
                continue
            scores = np.asarray(detection[5:], dtype=np.float32) * objectness
            # YOLOv3's independent sigmoid scores are not mutually exclusive.
            for class_id in np.flatnonzero(scores >= args.score):
                class_id = int(class_id)
                if class_id >= len(names):
                    continue
                cx, cy, bw, bh = map(float, detection[:4])
                x1 = max(0, int(round((cx - bw / 2) * width)))
                y1 = max(0, int(round((cy - bh / 2) * height)))
                x2 = min(width, int(round((cx + bw / 2) * width)))
                y2 = min(height, int(round((cy + bh / 2) * height)))
                if x2 <= x1 or y2 <= y1:
                    continue
                boxes_by_class.setdefault(class_id, []).append([x1, y1, x2 - x1, y2 - y1])
                scores_by_class.setdefault(class_id, []).append(float(scores[class_id]))

    total = 0
    for class_id, boxes in boxes_by_class.items():
        scores = scores_by_class[class_id]
        keep = cv2.dnn.NMSBoxes(boxes, scores, args.score, args.nms)
        if keep is None:
            continue
        for idx in np.asarray(keep).reshape(-1):
            x, y, w, h = boxes[int(idx)]
            confidence = scores[int(idx)]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 175, 120), 2)
            cv2.putText(image, f"{names[class_id]} {confidence:.2f}",
                        (x, max(16, y - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.52, (0, 90, 60), 2)
            total += 1
    if not cv2.imwrite(str(args.out), image):
        raise OSError(f"cannot write output image to {args.out}")
    print(f"saved {total} detections to {args.out}")
    print("Scores use objectness * class probability; class-wise NMS is applied.")


if __name__ == "__main__":
    main()
