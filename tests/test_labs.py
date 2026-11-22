from __future__ import annotations

import math
import subprocess
import sys
import unittest

from labs.anchor_clusters import cluster, shape_iou
from labs.box_geometry import variants
from labs.darknet_cfg_audit import audit
from labs.fpn_shapes import add_features, concat_channels, shape_map, upsample2


class LabContracts(unittest.TestCase):
    def test_shape_iou_and_deterministic_clusters(self):
        self.assertAlmostEqual(shape_iou((10, 20), (10, 20)), 1.0)
        self.assertAlmostEqual(shape_iou((10, 10), (5, 5)), 0.25)
        data = [(20, 30), (21, 31), (90, 70), (88, 72), (50, 140), (52, 138)]
        first = cluster(data, k=3, seed=7)
        self.assertEqual(first, cluster(data, k=3, seed=7))
        self.assertEqual(len(first[0]), 3)
        self.assertGreater(first[1], 0.9)
        with self.assertRaises(ValueError):
            cluster(data, k=0)
        with self.assertRaises(ValueError):
            shape_iou((0, 1), (2, 3))

    def test_iou_variants_basic_invariants(self):
        a = (0, 0, 2, 2)
        same = variants(a, a)
        for k in ("iou", "giou", "diou", "ciou"):
            self.assertAlmostEqual(same[k], 1.0, places=9)
        disjoint = variants(a, (3, 0, 5, 2))
        self.assertAlmostEqual(disjoint["iou"], 0.0)
        self.assertAlmostEqual(disjoint["giou"], -0.2, places=9)
        self.assertAlmostEqual(disjoint["diou"], -9 / 29, places=9)
        self.assertAlmostEqual(disjoint["ciou"], disjoint["diou"], places=9)
        self.assertAlmostEqual(disjoint["ciou_loss"], 1 + 9 / 29, places=9)
        ab = variants((0, 0, 2, 3), (1, 1, 3, 2))
        ba = variants((1, 1, 3, 2), (0, 0, 2, 3))
        for k in ab:
            self.assertAlmostEqual(ab[k], ba[k], places=9)
        with self.assertRaises(ValueError):
            variants((0, 0, 0, 4), (0, 0, 2, 2))
        with self.assertRaises(ValueError):
            variants((0, 0, math.inf, 4), (0, 0, 2, 2))

    def test_feature_fusion_shape_contracts(self):
        stages = shape_map(416)
        self.assertEqual(stages["C3"], (1, 256, 52, 52))
        self.assertEqual(stages["C4"], (1, 512, 26, 26))
        self.assertEqual(stages["C5"], (1, 1024, 13, 13))
        projected_deep = (1, 256, 13, 13)
        self.assertEqual(
            concat_channels(stages["C4"], upsample2(projected_deep)),
            (1, 768, 26, 26),
        )
        self.assertEqual(
            add_features((1, 256, 26, 26), upsample2(projected_deep)),
            (1, 256, 26, 26),
        )
        with self.assertRaises(ValueError):
            add_features(stages["C4"], upsample2(projected_deep))
        with self.assertRaises(ValueError):
            shape_map(417)

    def test_darknet_cfg_full_three_heads(self):
        anchors = "10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326"
        text = "[net]\nwidth=416\nheight=416\n"
        for mask in ("6,7,8", "3,4,5", "0,1,2"):
            text += f"[convolutional]\nfilters=21\n[yolo]\nclasses=2\nmask={mask}\nanchors={anchors}\n"
        self.assertEqual(audit(text, expected_classes=2), [])
        invalid = text.replace("filters=21", "filters=24", 1)
        self.assertTrue(any("filters=24" in item for item in audit(invalid, 2)))
        invalid = text.replace("height=416", "height=415")
        self.assertTrue(any("height" in item for item in audit(invalid, 2)))

    def test_opencv_cli_help_requires_no_optional_imports(self):
        result = subprocess.run(
            [sys.executable, "-m", "labs.yolov3_opencv", "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--weights", result.stdout)


if __name__ == "__main__":
    unittest.main()
