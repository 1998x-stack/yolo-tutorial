/* Progressive enhancement for the Chapter 08 shape-IoU explainer.
 * All geometry is in SVG-local reference units; no network access needed.
 */
(() => {
  "use strict";
  const select = document.querySelector("#anchor-demo-select");
  const box = document.querySelector("#anchor-target-box");
  const output = document.querySelector("#anchor-demo-output");
  const shapes = {
    square: [76, 66],
    tall: [58, 140],
    wide: [142, 54],
  };
  const anchors = [[70, 60], [60, 150], [150, 60]];
  const names = ["① 方形先验", "② 竖长先验", "③ 横长先验"];
  if (!select || !box || !output) return;

  function shapeIoU(first, second) {
    const intersection = Math.min(first[0], second[0]) * Math.min(first[1], second[1]);
    const union = first[0] * first[1] + second[0] * second[1] - intersection;
    return union > 0 ? intersection / union : 0;
  }

  function render() {
    const target = shapes[select.value] || shapes.square;
    box.setAttribute("x", String(187 - target[0] / 2));
    box.setAttribute("y", String(150 - target[1] / 2));
    box.setAttribute("width", String(target[0]));
    box.setAttribute("height", String(target[1]));
    const scores = anchors.map(anchor => shapeIoU(target, anchor));
    const best = scores.indexOf(Math.max(...scores));
    for (let i = 0; i < anchors.length; i++) {
      const candidate = document.querySelector("#anchor-candidate-" + i);
      if (!candidate) continue;
      candidate.setAttribute("stroke-width", i === best ? "4" : "2");
      candidate.setAttribute("stroke-dasharray", i === best ? "none" : "6 5");
    }
    output.textContent = "最匹配：" + names[best] +
      "；形状 IoU ≈ " + scores[best].toFixed(3) +
      "（目标 " + target[0] + " × " + target[1] + "）";
  }

  select.addEventListener("change", render);
  render();
})();
