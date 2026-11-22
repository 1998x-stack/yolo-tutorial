from __future__ import annotations
import unittest
from labs.modern_yolo_contract import (
    attention_relationship_counts, dfl_expected, dfl_target_weights,
    grid_positions, offset_box, raw_weight_bytes, tile_origins
)


class ModernYoloContractTests(unittest.TestCase):
    def test_anchor_free_grid_points(self):
        self.assertEqual(grid_positions(), 8400)

    def test_target_interpolation(self):
        l, r, wl, wr = dfl_target_weights(3.7)
        self.assertEqual((l, r), (3, 4))
        self.assertAlmostEqual(wl, .3)
        self.assertAlmostEqual(wr, .7)
        self.assertAlmostEqual(l*wl+r*wr, 3.7)

    def test_dfl_prediction_expectation(self):
        self.assertAlmostEqual(dfl_expected([0, .2, .8]), 1.8)
        with self.assertRaises(ValueError):
            dfl_expected([.1, .2])

    def test_attention_complexity_is_not_latency(self):
        self.assertEqual(attention_relationship_counts(256, 64), (65536, 16384))

    def test_memory_arithmetic_excludes_activations(self):
        self.assertEqual(raw_weight_bytes(10_000_000, 8), 10_000_000)
        self.assertEqual(raw_weight_bytes(10_000_000, 32), 40_000_000)

    def test_tiling_20_percent(self):
        starts = tile_origins(2048, 640, .2)
        self.assertEqual(starts, [0, 512, 1024, 1408])
        self.assertEqual(len(starts)**2, 16)

    def test_tiling_without_overlap(self):
        starts = tile_origins(1280, 640, 0)
        self.assertEqual(starts, [0, 640])
        self.assertEqual(tile_origins(640,640,.5), [0])

    def test_tiling_invalid(self):
        for args in [(2048,0,.2),(2048,640,1),(100,640,.2)]:
            with self.assertRaises(ValueError):
                tile_origins(*args)

    def test_global_offset(self):
        self.assertEqual(offset_box((20,30,84,110),(512,256)),(532,286,596,366))
        with self.assertRaises(ValueError):
            offset_box((5,5,0,3),(0,0))


if __name__ == "__main__":
    unittest.main()
