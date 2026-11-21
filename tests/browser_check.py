from __future__ import annotations

import json
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
                page.locator("#chapter-search").fill("")
                page.locator("#stage-filter").select_option("foundation")
                assert page.locator(".chapter-card:visible").count() == 5
                page.locator("#stage-filter").select_option("all")

                for width in results["viewports"]:
                    page.set_viewport_size({"width": width, "height": 1000})
                    page.goto(base + "/index.html", wait_until="networkidle")
                    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
                    assert not overflow, f"homepage horizontal overflow at {width}px"
                    if width in (1440, 390):
                        page.screenshot(path=str(Path(temp) / f"home-{width}.png"), full_page=True)

                    for chapter in range(1, 6):
                        num = f"{chapter:02d}"
                        page.goto(base + f"/chapters/{num}.html", wait_until="networkidle")
                        assert page.locator("main article h1").count() == 1, num
                        assert page.locator("article svg").count() >= 1, num
                        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
                        assert not overflow, f"chapter {num} horizontal overflow at {width}px"
                        assert page.locator("article svg").first.is_visible(), num
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
                            results["chapters_checked"].append(num)

                assert not results["browser_errors"], results["browser_errors"]
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
