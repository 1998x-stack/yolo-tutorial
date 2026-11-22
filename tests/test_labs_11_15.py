"""Cross-validate chapters 11-15 against their deterministic teaching labs."""
from __future__ import annotations
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from labs.augmentation_geometry import flip_horizontal, crop_xyxy, resize_translate_clip
from labs.backbone_cost import conv_cost, verify_folding, fold_linear_branches
from labs.neck_head_contract import (
    max_pool_same, assert_sppf_equivalence, concat_channels, anchor_head_shape,
)
from labs.nms_reference import Detection, iou, suppress, sample_boxes
from labs.yolov5_contract import sigmoid, decode_v7, candidates, audit_labels

ROOT = Path(__file__).resolve().parents[1]


class ThirdBatchLabs(unittest.TestCase):
    def test_augmentation_flip_and_crop_local_coordinates(self):
        box = (120, 80, 280, 240)
        self.assertEqual(flip_horizontal(box, 640), (360, 80, 520, 240))
        self.assertEqual(
            flip_horizontal(flip_horizontal(box, 640), 640),
            tuple(map(float, box)),
        )
        self.assertEqual(
            crop_xyxy((100, 50, 340, 290), (150, 70, 320, 280), 0.2),
            (0, 0, 170, 210),
        )
        self.assertIsNone(crop_xyxy((0, 0, 5, 5), (10, 10, 30, 30)))
        self.assertIsNone(crop_xyxy((0, 0, 100, 100), (99, 99, 101, 101), 0.1))

    def test_mosaic_coordinate_transform_and_bad_boxes(self):
        self.assertEqual(
            resize_translate_clip((0, 0, 10, 10), 2, 2, 10, 5, (0, 0, 30, 30)),
            (10, 5, 30, 25),
        )
        with self.assertRaises(ValueError):
            flip_horizontal((20, 0, 10, 8), 640)
        with self.assertRaises(ValueError):
            crop_xyxy((1, 1, 2, 2), (0, 0, 2, 2), min_visible=1.1)
        with self.assertRaises(ValueError):
            resize_translate_clip((1,1,2,2), -1, 1, 0, 0, (0,0,10,10))

    def test_conv_macs_and_linear_branch_equivalence(self):
        self.assertEqual(conv_cost(80, 80, 32, 64, 3), (18432, 117964800))
        self.assertEqual(conv_cost(80, 80, 32, 64, 3, groups=32), (576, 3686400))
        folded = fold_linear_branches([[0,0,0],[0,2,0],[0,0,0]], 0.5, 1.0)
        self.assertAlmostEqual(folded[1][1], 3.5)
        self.assertEqual(len(verify_folding()), 3)
        with self.assertRaises(ValueError):
            conv_cost(80,80,15,64,3,groups=4)

    def test_sppf_pooling_every_cell_and_head_shapes(self):
        matrix = [[float((y*11+x*3)%19 - 10) for x in range(7)] for y in range(7)]
        self.assertTrue(assert_sppf_equivalence(matrix))
        self.assertEqual(max_pool_same([[1.,-2.],[3.,4.]], 3), [[4.,4.],[4.,4.]])
        self.assertEqual(anchor_head_shape(1,2,3,80,80), (1,21,80,80))
        self.assertEqual(concat_channels(*[(1,64,20,20)]*4), (1,256,20,20))
        with self.assertRaises(ValueError):
            concat_channels((1,3,20,20),(1,5,20,21))
        with self.assertRaises(ValueError):
            max_pool_same([[1]], 4)

    def test_hard_nms_is_classwise_and_threshold_sensitive(self):
        boxes = sample_boxes()
        self.assertAlmostEqual(iou(boxes[0].box, boxes[1].box), 8100/11900)
        self.assertEqual([d.id for d in suppress(boxes, .5, .25, "hard")], ["A","D","C"])
        self.assertEqual([d.id for d in suppress(boxes, .9, .25, "hard")], ["A","B","D","C"])
        self.assertEqual(suppress([], .5, .25), [])
        with self.assertRaises(ValueError):
            suppress([Detection("X","cat",1.2,(0,0,1,1))])

    def test_soft_nms_preserves_overlapping_with_decayed_score(self):
        results=suppress(sample_boxes(),.5,.25,"soft-linear")
        self.assertEqual([d.id for d in results], ["A","D","C","B"])
        b=next(d for d in results if d.id=="B")
        self.assertAlmostEqual(b.score, .88*(1-8100/11900))
        self.assertEqual([d.id for d in suppress(sample_boxes(), .5, .30, "soft-linear")],
                         ["A","D","C"])

    def test_yolov5_v7_geometry_and_candidate_count(self):
        self.assertEqual(candidates(640), 25200)
        self.assertEqual(candidates(416), 10647)
        self.assertEqual(decode_v7((0,0,0,0),(4,6),32,(116,90)), (144,208,116,90))
        self.assertAlmostEqual(sigmoid(-2000), 0)
        self.assertAlmostEqual(sigmoid(2000), 1)
        with self.assertRaises(ValueError):
            candidates(650)
        with self.assertRaises(ValueError):
            decode_v7((0,0,math.inf,0),(4,6),32,(116,90))

    def test_yolov5_label_audit_valid_and_invalid(self):
        good=audit_labels(ROOT/"labs"/"sample-yolov5-labels", 2)
        self.assertEqual(good.files,1)
        self.assertEqual(good.objects,2)
        self.assertEqual(good.errors,[])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.txt"
            path.write_text("2 0.5 0.5 0.3 0.4\n0 0.1 0.5 0.5 0.2\n1 0.5 0.5 0 0.2\n",encoding="utf-8")
            bad=audit_labels(Path(tmp),2)
            self.assertEqual(bad.objects,0)
            self.assertEqual(len(bad.errors),3)

    def test_yolov5_audit_cli_without_external_deps(self):
        result=subprocess.run(
            [sys.executable, "-m", "labs.yolov5_contract",
             "--labels", str(ROOT/"labs"/"sample-yolov5-labels"), "--classes","2"],
            capture_output=True,text=True,check=False,
        )
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("valid objects=2",result.stdout)


if __name__ == "__main__":
    unittest.main()
