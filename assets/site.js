(function () {
  "use strict";
  const search = document.querySelector("#chapter-search");
  const stage = document.querySelector("#stage-filter");
  const cards = Array.from(document.querySelectorAll(".chapter-card"));
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty-state");
  if (!search || !stage || cards.length === 0) return;

  function applyFilters() {
    const query = search.value.trim().toLocaleLowerCase("zh-CN");
    const selectedStage = stage.value;
    let visible = 0;
    for (const card of cards) {
      const text = (card.dataset.search || card.textContent).toLocaleLowerCase("zh-CN");
      const stageMatches = selectedStage === "all" || card.dataset.stage === selectedStage;
      const queryMatches = !query || text.includes(query);
      const show = stageMatches && queryMatches;
      card.hidden = !show;
      if (show) visible += 1;
    }
    for (const group of document.querySelectorAll(".chapter-group")) {
      group.hidden = !group.querySelector(".chapter-card:not([hidden])");
    }
    if (count) count.textContent = "显示 " + visible + " / " + cards.length + " 篇";
    if (empty) empty.hidden = visible !== 0;
  }
  search.addEventListener("input", applyFilters);
  stage.addEventListener("change", applyFilters);
  applyFilters();
})();