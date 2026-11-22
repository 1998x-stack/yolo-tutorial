"""Backbone arithmetic and a minimal RepVGG-style linear branch equivalence.

Counting convention: one multiply-accumulate is 1 MAC, not 1 or 2 measured
GPU FLOPs. This tiny kernel-folding proof has one input/output channel, stride 1,
same zero padding, NO BN or branch nonlinearity. Real Rep blocks additionally
fold each branch's frozen BN first and must match all stride/groups.
"""
from __future__ import annotations


def conv_cost(h: int, w: int, cin: int, cout: int, kernel: int, groups: int = 1) -> tuple[int, int]:
    if min(h, w, cin, cout, kernel, groups) <= 0:
        raise ValueError("dimensions must be positive")
    if cin % groups or cout % groups:
        raise ValueError("channel counts must be divisible by groups")
    weights = cout * (cin // groups) * kernel * kernel
    macs = h * w * weights
    return weights, macs


def fold_linear_branches(kernel3: list[list[float]], kernel1: float, identity: float):
    if len(kernel3) != 3 or any(len(row) != 3 for row in kernel3):
        raise ValueError("the demonstration requires a 3x3 kernel")
    out = [[float(v) for v in row] for row in kernel3]
    out[1][1] += float(kernel1) + float(identity)
    return out


def conv2d_same(image: list[list[float]], kernel: list[list[float]]):
    h = len(image)
    if not h or not image[0] or any(len(row) != len(image[0]) for row in image):
        raise ValueError("input needs a nonempty rectangular matrix")
    if len(kernel) != 3 or any(len(row) != 3 for row in kernel):
        raise ValueError("kernel must be 3x3")
    w = len(image[0])
    # Deep-learning convention: cross correlation, not kernel-flipped convolution.
    return [[sum(
        (image[y + dy - 1][x + dx - 1]
         if 0 <= y + dy - 1 < h and 0 <= x + dx - 1 < w else 0.0)
        * kernel[dy][dx]
        for dy in range(3) for dx in range(3))
        for x in range(w)] for y in range(h)]


def verify_folding():
    image = [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]
    kernel3 = [[0., 1., 0.], [1., 2., -1.], [0., -1., 0.]]
    kernel1, residual_scale = 0.5, 1.0
    three = conv2d_same(image, kernel3)
    multi = [[three[y][x] + kernel1 * image[y][x] + residual_scale * image[y][x]
              for x in range(3)] for y in range(3)]
    folded = conv2d_same(image, fold_linear_branches(kernel3, kernel1, residual_scale))
    if any(abs(multi[y][x] - folded[y][x]) > 1e-9 for y in range(3) for x in range(3)):
        raise AssertionError("linear kernel fold changed output")
    return folded


if __name__ == "__main__":
    params, macs = conv_cost(80, 80, 32, 64, 3)
    print(f"3x3 conv no bias: {params:,} weights, {macs:,} MACs")
    print("linear branch fold passes:", verify_folding())
