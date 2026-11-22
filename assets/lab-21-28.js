/* Self-contained deterministic teaching demos for chapters 21–28. No remote resources. */
(function () {
  "use strict";
  const configs = {
    "21": (v) => {
      const b = Number(v), a = 5, c = 2.5;
      const lat = a + c * b, fps = 1000 * b / lat, baseFps = 1000 / (a + c);
      return "batch=" + b + "：单次延迟≈" + lat.toFixed(1) + " ms；吞吐≈" + fps.toFixed(1) +
        " FPS；单帧延迟为 batch=1 的 " + (lat / (a + c)).toFixed(2) +
        "×，吞吐相对 batch=1 为 " + (fps / baseFps).toFixed(1) + "×。";
    },
    "22": (v) => {
      const q = Number(v), e = 120;
      const f = q * 1000 / e, f2 = q * 1000 / (e / 2);
      return "散热上限 " + q + " W；若每帧能耗 " + (e / 1000).toFixed(3) + " J，可持续帧率≈" +
        f.toFixed(1) + " FPS；每帧能耗减半到 " + (e / 2000).toFixed(3) +
        " J 时，同功耗下可持续≈" + f2.toFixed(1) + " FPS。";
    },
    "23": (v) => {
      const cx = Number(v) / 100, nw = 0.10, nh = 0.15, W = 640, H = 480;
      const x = (cx - nw / 2) * W, y = (0.5 - nh / 2) * H, w = nw * W, h = nh * H;
      return "cx=" + cx.toFixed(2) + "：YOLO 行 = 0 " + cx.toFixed(2) + " 0.50 " +
        nw.toFixed(2) + " " + nh.toFixed(2) + "；COCO bbox=[" + x.toFixed(1) + ", " +
        y.toFixed(1) + ", " + w.toFixed(1) + ", " + h.toFixed(1) + "]（像素）；VOC xmin=" +
        x.toFixed(1) + " ymin=" + y.toFixed(1) + " xmax=" + (x + w).toFixed(1) +
        " ymax=" + (y + h).toFixed(1) + "。";
    },
    "24": (v) => {
      const b = Number(v), N = 4, k = 1, B0 = 16, eta0 = 0.01;
      const Beff = b * N * k, eta = eta0 * Beff / B0;
      return "每卡 batch=" + b + "，设备 " + N + "，累积 " + k + "：有效批大小 = " + Beff +
        "；按线性缩放 η = " + eta0 + "×" + Beff + "/" + B0 + " = " + eta.toFixed(4) +
        "（教学示意，需在自有数据上重新验证）。";
    },
    "25": (v) => {
      const R = Number(v) / 100, P = 0.8;
      const F1 = 2 * P * R / (P + R);
      return "P=0.80，R=" + R.toFixed(2) + "：F1 = 2×0.80×" + R.toFixed(2) + " / (0.80+" +
        R.toFixed(2) + ") = " + F1.toFixed(3) + "（教学示意值）。";
    }
  };
  for (const [id, render] of Object.entries(configs)) {
    const slider = document.getElementById("lab-input-" + id);
    const output = document.getElementById("lab-output-" + id);
    if (!slider || !output) continue;
    const update = () => { output.textContent = render(slider.value); };
    slider.addEventListener("input", update);
    update();
  }
})();
