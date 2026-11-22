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
