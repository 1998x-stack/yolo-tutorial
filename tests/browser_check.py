from __future__ import annotations

import json
import shutil
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    failures: list[str] = []
    results = {"home_cards": 0, "chapters_checked": [], "viewports": [1440, 768, 390, 360], "browser_errors": []}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
            page.route("https://**/*", lambda route: route.abort())
            page.on("pageerror", lambda error: results["browser_errors"].append(str(error)))
            page.on("console", lambda message: results["browser_errors"].append("console: " + message.text) if message.type == "error" else None)

            with TemporaryDirectory(prefix="yolo-browser-qa-") as temp:
                page.goto(base + "/index.html", wait_until="networkidle")
                assert "YOLO 目标检测教程" in page.title()
                results["home_cards"] = page.locator(".chapter-card").count()
                assert results["home_cards"] == 28

                page.locator("#chapter-search").fill("YOLO9000")
                assert page.locator(".chapter-card:visible").count() >= 1
                page.locator("#chapter-search").fill("no-matching-chapter-xyz")
                assert page.locator(".chapter-card:visible").count() == 0
                assert page.locator("#empty-state").is_visible()
                page.locator("#chapter-search").fill("")
                assert not page.locator("#empty-state").is_visible()
                page.locator("#stage-filter").select_option("foundation")
                assert page.locator(".chapter-card:visible").count() == 5
                page.locator("#stage-filter").select_option("all")

                # A real chapter-level interaction: shape changes the chosen anchor.
                page.goto(base + "/chapters/08.html", wait_until="networkidle")
                assert "方形先验" in page.locator("#anchor-demo-output").inner_text()
                page.locator("#anchor-demo-select").select_option("tall")
                assert "竖长先验" in page.locator("#anchor-demo-output").inner_text()
                assert page.locator("#anchor-target-box").get_attribute("height") == "140"
                page.locator("#anchor-demo-select").select_option("wide")
                assert "横长先验" in page.locator("#anchor-demo-output").inner_text()


                # Chapter 14 tests threshold control, score decay and class-aware suppression.
                page.goto(base + "/chapters/14.html", wait_until="networkidle")
                assert "Hard NMS" in page.locator("#nms-demo-output").inner_text()
                assert "B(cat" not in page.locator("#nms-demo-output").inner_text()
                page.locator("#nms-threshold").focus()
                page.keyboard.press("End")
                assert "B(cat" in page.locator("#nms-demo-output").inner_text()
                page.keyboard.press("Home")
                assert "B(cat" not in page.locator("#nms-demo-output").inner_text()
                page.locator("#nms-mode").select_option("soft")
                assert "Soft-NMS" in page.locator("#nms-demo-output").inner_text()
                assert "B(cat" in page.locator("#nms-demo-output").inner_text()

                # New teaching interaction, one value change per architecture/deployment chapter.
                for num, phrase in [("16", "bin"), ("17", "one-to-many"), ("18", "N=256"), ("19", "MB"), ("20", "16 片")]:
                    page.goto(base + "/chapters/" + num + ".html", wait_until="networkidle")
                    slider = page.locator("#lab-input-" + num)
                    output = page.locator("#lab-output-" + num)
                    before = output.inner_text()
                    assert before and (phrase in before), (num, before)
                    slider.focus()
                    page.keyboard.press("End")
                    after = output.inner_text()
                    assert after != before, (num, before, after)

                # Batch 05 (21–28): same range-control contract, driven by assets/lab-21-28.js.
                for chapter in range(21, 29):
                    num = f"{chapter:02d}"
                    page.goto(base + "/chapters/" + num + ".html", wait_until="networkidle")
                    slider = page.locator("#lab-input-" + num)
                    output = page.locator("#lab-output-" + num)
                    before = output.inner_text()
                    assert before, (num, before)
                    slider.focus()
                    page.keyboard.press("End")
                    assert output.inner_text() != before, (num, before)

                for width in results["viewports"]:
                    page.set_viewport_size({"width": width, "height": 1000})
                    page.goto(base + "/index.html", wait_until="networkidle")
                    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
                    assert not overflow, f"homepage horizontal overflow at {width}px"
                    if width in (1440, 390):
                        page.screenshot(path=str(Path(temp) / f"home-{width}.png"), full_page=True)

                    for chapter in range(1, 29):
                        num = f"{chapter:02d}"
                        page.goto(base + f"/chapters/{num}.html", wait_until="networkidle")
                        assert page.locator("main article h1").count() == 1, num
                        assert page.locator("article svg").count() >= 1, num
                        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
                        assert not overflow, f"chapter {num} horizontal overflow at {width}px"
                        assert page.locator("article svg").first.is_visible(), num
                        if width in (360, 390) and chapter >= 6:
                            figure_scroll = page.locator("article .diagram").first.evaluate(
                                "(el) => ({inner: el.clientWidth, total: el.scrollWidth, focusable: el.tabIndex === 0})"
                            )
                            assert figure_scroll["total"] > figure_scroll["inner"], (num, width, figure_scroll)
                            assert figure_scroll["focusable"], (num, width)
                        math_data = page.locator("article math").evaluate_all("""els => els.map(el => ({
                          namespace: el.namespaceURI,
                          label: el.getAttribute('aria-label'),
                          width: el.getBoundingClientRect().width,
                          height: el.getBoundingClientRect().height
                        }))""")
                        for item in math_data:
                            assert item["namespace"] == "http://www.w3.org/1998/Math/MathML", (num, item)
                            assert item["label"], (num, item)
                            assert item["width"] > 0 and item["height"] > 0, (num, item)
                        if page.locator(".equation").count():
                            assert page.locator(".equation").first.evaluate("(el) => el.tabIndex === 0"), num
                            page.locator(".equation").first.focus()
                            assert page.evaluate("document.activeElement.classList.contains('equation')"), num
                        page.emulate_media(media="print")
                        assert page.locator("article h1").is_visible(), num
                        page.emulate_media(media="screen")
                        if width in (1440, 390):
                            page.screenshot(path=str(Path(temp) / f"chapter-{num}-{width}.png"), full_page=True)
                        if width == 1440:
                            assert page.locator('article .diagram').first.get_attribute("tabindex") == "0", num

                            results["chapters_checked"].append(num)

                assert not results["browser_errors"], results["browser_errors"]
                report_dir = ROOT / "reports" / "browser"
                report_dir.mkdir(parents=True, exist_ok=True)
                shutil.copytree(temp, report_dir, dirs_exist_ok=True)
                (report_dir / "report.json").write_text(
                    json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
