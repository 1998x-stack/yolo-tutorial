/* Self-contained deterministic teaching demos for chapters 16–20. No remote resources. */
(function () {
  "use strict";
  const configs = {
    "16": (v) => {
      const t = Number(v), k = Math.floor(t), frac = t - k;
      return "目标 t=" + t.toFixed(1) + "；bin " + k + " 权重 " + (1-frac).toFixed(2) +
        "；bin " + (k+1) + " 权重 " + frac.toFixed(2) + "；两项加权期望为 " + t.toFixed(1) + "。";
    },
    "17": (v) => "教学示例：one-to-many 选 " + Number(v) +
      " 个正例；one-to-one 固定为 1 个。实际 YOLOv10 分配由匹配规则决定。 ",
    "18": (v) => {
      const w = Number(v), n = 256;
      return "N=" + n + "，W=" + w + "：全局关系 " + (n*n).toLocaleString("en-US") +
        "；区域关系约 " + (n*w).toLocaleString("en-US") +
        "；理论关系数比值 " + (n/w).toFixed(1) + "∶1（不等于速度比）。";
    },
    "19": (v) => {
      const bits = Number(v), params = 10e6, mb = params*bits/8/1e6;
      return "10M 参数 × " + bits + " bit = " + mb.toFixed(1) + " MB 原始权重；" +
        "FP32 同参数为 40.0 MB（不含激活与量化参数）。";
    },
    "20": (v) => {
      const overlap = Number(v)/100, L = 2048, tile = 640;
      const step = tile*(1-overlap);
      const origins = [];
      for (let x = 0; x < L-tile; x += step) {
        origins.push(Math.round(x));
      }
      origins.push(L-tile);
      const starts = [...new Set(origins)];
      return "重叠 " + Math.round(overlap*100) + "%；单轴 " + starts.length +
        " 片，双轴共 " + (starts.length**2) + " 片；x 起点约为 " + starts.join(", ") +
        "（像素；最后一片夹紧到图像边界）。";
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
