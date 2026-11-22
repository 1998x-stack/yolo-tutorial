/* Offline interactive companion to Chapter 14's deterministic NMS example. */
(() => {
  "use strict";
  const slider = document.querySelector("#nms-threshold");
  const indicator = document.querySelector("#nms-threshold-value");
  const select = document.querySelector("#nms-mode");
  const output = document.querySelector("#nms-demo-output");
  if (!slider || !indicator || !select || !output) return;

  const boxes = [
    {id:"A", cls:"cat", score:0.95, b:[40,40,140,140]},
    {id:"B", cls:"cat", score:0.88, b:[50,50,150,150]},
    {id:"C", cls:"cat", score:0.72, b:[190,40,290,140]},
    {id:"D", cls:"dog", score:0.80, b:[40,40,140,140]}
  ];
  function iou(a,b) {
    const inter = Math.max(0,Math.min(a[2],b[2])-Math.max(a[0],b[0])) *
                  Math.max(0,Math.min(a[3],b[3])-Math.max(a[1],b[1]));
    const area = b => (b[2]-b[0])*(b[3]-b[1]);
    return inter/(area(a)+area(b)-inter);
  }
  function run(t, mode) {
    const out = [];
    const classes = [...new Set(boxes.map(b=>b.cls))].sort();
    for (const cls of classes) {
      let pending = boxes.filter(b=>b.cls===cls).map(b=>({...b}));
      while (pending.length) {
        pending.sort((a,b)=>b.score-a.score || a.id.localeCompare(b.id));
        const first = pending.shift();
        out.push(first);
        pending = pending.flatMap(b=>{
          const overlap = iou(b.b,first.b);
          if (mode==="hard" && overlap>t) return [];
          const score = mode==="soft" && overlap>t ? b.score*(1-overlap) : b.score;
          return score>=0.25 ? [{...b,score}] : [];
        });
      }
    }
    return out.sort((a,b)=>b.score-a.score || a.id.localeCompare(b.id));
  }
  function render() {
    const t = Number(slider.value);
    const mode = select.value;
    indicator.textContent = t.toFixed(2);
    const retained = run(t,mode);
    output.textContent = (mode==="soft"?"Soft-NMS":"Hard NMS") +
      "：保留 " + retained.map(b=>b.id+"("+b.cls+", "+b.score.toFixed(3)+")").join("、") +
      "；共 "+retained.length+" 个检测（分数下限 0.25）。";
  }
  slider.addEventListener("input",render);
  select.addEventListener("change",render);
  render();
})();
