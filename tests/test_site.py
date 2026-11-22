from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.h1_count = 0
        self.article_count = 0
        self.main_count = 0
        self.svg_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"a", "link", "script", "img"}:
            value = attrs.get("href") or attrs.get("src")
            if value:
                self.links.append(value)
        if tag == "h1":
            self.h1_count += 1
        if tag == "article":
            self.article_count += 1
        if tag == "main":
            self.main_count += 1
        if tag == "svg":
            self.svg_count += 1


def read_page(path: Path) -> tuple[str, PageParser]:
    content = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(content)
    return content, parser


class SiteStructureTests(unittest.TestCase):
    def test_catalogue_has_28_canonical_chapters(self):
        data = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
        self.assertEqual(data["chapterCount"], 28)
        self.assertEqual(len(data["chapters"]), 28)
        self.assertEqual([c["num"] for c in data["chapters"]], [f"{i:02d}" for i in range(1, 29)])
        for chapter in data["chapters"]:
            target = ROOT / chapter["file"]
            self.assertTrue(target.is_file(), chapter["file"])
            self.assertTrue(chapter.get("stage"), chapter["num"])

    def test_homepage_is_static_and_has_all_chapter_cards(self):
        content, parser = read_page(ROOT / "index.html")
        self.assertEqual(content.count('class="chapter-card"'), 28)
        self.assertIn('id="chapter-search"', content)
        self.assertIn('id="stage-filter"', content)
        self.assertIn('id="empty-state" role="status" hidden', content)
        self.assertIn('src="assets/site.js"', content)
        self.assertNotIn("fetch(", content)
        self.assertTrue((ROOT / "assets/theme.css").is_file())
        self.assertTrue((ROOT / "assets/site.js").is_file())

    def test_every_local_html_link_resolves(self):
        pages = list(ROOT.glob("*.html")) + list((ROOT / "chapters").glob("*.html"))
        self.assertEqual(len(pages), 57)
        for page in pages:
            _, parser = read_page(page)
            for raw in parser.links:
                parsed = urlparse(raw)
                if parsed.scheme or raw.startswith("//") or raw.startswith("#"):
                    continue
                if raw.startswith(("javascript:", "data:", "mailto:", "tel:")):
                    continue
                target_path = parsed.path
                if not target_path:
                    continue
                target = (page.parent / target_path).resolve()
                self.assertTrue(target.exists(), f"{page.relative_to(ROOT)} -> {raw}")

    def test_root_chapter_urls_are_compatibility_redirects(self):
        for i in range(1, 29):
            num = f"{i:02d}"
            content = (ROOT / f"{num}.html").read_text(encoding="utf-8")
            self.assertIn(f'url=chapters/{num}.html', content)
            self.assertIn(f'href="chapters/{num}.html"', content)
            self.assertIn('name="robots" content="noindex"', content)

    def test_first_twenty_chapters_are_self_contained_articles(self):
        forbidden = ("大家好，我是你们的讲师", "上一章我们", "下一章我们", "讲义介绍了")
        for i in range(1, 21):
            num = f"{i:02d}"
            content, parser = read_page(ROOT / "chapters" / f"{num}.html")
            self.assertEqual(parser.h1_count, 1, num)
            self.assertEqual(parser.article_count, 1, num)
            self.assertEqual(parser.main_count, 1, num)
            self.assertGreaterEqual(parser.svg_count, 1, num)
            if i == 15:
                # Classic YOLOv5 v7.0 is specified by source tag rather than
                # an original Redmon-family research paper.
                self.assertIn("https://github.com/ultralytics/yolov5/blob/v7.0/", content, num)
            else:
                self.assertTrue("https://arxiv.org/abs/" in content or "https://docs.ultralytics.com/" in content or "https://www.ecva.net/" in content or "https://proceedings.neurips.cc/" in content or "https://cocodataset.org/" in content or "https://ieeexplore.ieee.org/" in content, num)
            for phrase in forbidden:
                self.assertNotIn(phrase, content, f"{num}: {phrase}")

    def test_first_twenty_inline_svgs_are_accessible_and_well_formed(self):
        for i in range(1, 16):
            num = f"{i:02d}"
            content = (ROOT / "chapters" / f"{num}.html").read_text(encoding="utf-8")
            figures = re.findall(r"<svg\b[\s\S]*?</svg>", content, flags=re.IGNORECASE)
            self.assertGreaterEqual(len(figures), 1, num)
            for svg in figures:
                root = ET.fromstring(svg)
                local_names = {node.tag.split("}")[-1] for node in root.iter()}
                self.assertIn("title", local_names, num)
                self.assertIn("desc", local_names, num)
                self.assertTrue(root.attrib.get("viewBox"), num)

    def test_no_remote_runtime_assets(self):
        for page in [ROOT / "index.html", *(ROOT / "chapters" / f"{i:02d}.html" for i in range(1, 16))]:
            _, parser = read_page(page)
            for raw in parser.links:
                if raw.startswith(("https://", "http://")):
                    self.assertNotIn(raw, [raw for raw in parser.links if raw.lower().endswith((".js", ".css"))])

    def test_mathml_is_accessible_and_outside_svg(self):
        for i in range(1, 16):
            num = f"{i:02d}"
            content = (ROOT / "chapters" / f"{num}.html").read_text(encoding="utf-8")
            math_attrs = re.findall(r"<math\b([^>]*)>", content, flags=re.IGNORECASE)
            for attrs in math_attrs:
                self.assertRegex(attrs, r'aria-label="[^"]+"', num)
            for svg in re.findall(r"<svg\b[\s\S]*?</svg>", content, flags=re.IGNORECASE):
                self.assertNotIn("<math", svg.lower(), num)
            equation_count = content.count('class="equation"')
            self.assertEqual(content.count('class="equation" tabindex="0"'), equation_count, num)

    def test_second_batch_article_labs_and_evidence(self):
        for i in range(6, 11):
            num = f"{i:02d}"
            content = (ROOT / "chapters" / f"{num}.html").read_text(encoding="utf-8")
            self.assertIn(f'data-chapter="{num}" aria-current="page"', content, num)
            self.assertIn('class="references"', content, num)
            ledger = json.loads((ROOT / "docs" / "evidence" / f"{num}.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["article"], f"chapters/{num}.html")
            self.assertGreaterEqual(len(ledger["claims"]), 5)
            for claim in ledger["claims"]:
                self.assertTrue(claim.get("source_url"), (num, claim))
                self.assertTrue(claim.get("locator"), (num, claim))
                self.assertIn(claim.get("status"), {"verified", "derived", "illustrative", "unverified"})

    def test_interactive_anchor_demo_has_local_script(self):
        content = (ROOT / "chapters" / "08.html").read_text(encoding="utf-8")
        self.assertIn('id="anchor-demo-select"', content)
        self.assertIn('id="anchor-demo-output"', content)
        self.assertIn('src="../assets/anchor-demo.js"', content)
        self.assertTrue((ROOT / "assets" / "anchor-demo.js").is_file())

    def test_standalone_svgs_match_inline_figures_for_reviewed_chapters(self):
        for i in range(6, 21):
            num = f"{i:02d}"
            content = (ROOT / "chapters" / f"{num}.html").read_text(encoding="utf-8")
            svgs = re.findall(r"<svg\b[\s\S]*?</svg>", content, flags=re.IGNORECASE)
            exported = sorted((ROOT / "assets" / "figures").glob(f"chapter-{num}-*.svg"))
            self.assertEqual(len(svgs), len(exported), num)
            for inline, path in zip(svgs, exported):
                self.assertEqual(inline, path.read_text(encoding="utf-8").strip(), path.name)
                root = ET.fromstring(path.read_text(encoding="utf-8"))
                self.assertTrue(root.attrib.get("viewBox"))
                tags = {node.tag.split("}")[-1] for node in root.iter()}
                self.assertIn("title", tags)
                self.assertIn("desc", tags)

    def test_third_batch_article_labs_evidence_and_navigation(self):
        for i in range(11, 16):
            num=f"{i:02d}"
            content,parser=read_page(ROOT / "chapters" / f"{num}.html")
            self.assertEqual(parser.h1_count,1,num)
            self.assertEqual(parser.article_count,1,num)
            self.assertEqual(parser.main_count,1,num)
            self.assertGreaterEqual(parser.svg_count,1,num)
            self.assertIn(f'data-chapter="{num}" aria-current="page"',content,num)
            self.assertIn('class="references"',content,num)
            ledger=json.loads((ROOT/"docs"/"evidence"/f"{num}.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["article"],f"chapters/{num}.html")
            self.assertGreaterEqual(len(ledger["claims"]),6,num)
            for claim in ledger["claims"]:
                self.assertTrue(claim.get("source_url"),(num,claim))
                self.assertTrue(claim.get("locator"),(num,claim))
                self.assertIn(claim.get("status"),{"verified","derived","illustrative","unverified"},claim)

    def test_fourth_batch_content_evidence_and_demo_controls(self):
        for i in range(16, 21):
            num = f"{i:02d}"
            content, parser = read_page(ROOT / "chapters" / f"{num}.html")
            self.assertEqual((parser.h1_count, parser.main_count, parser.article_count), (1, 1, 1), num)
            self.assertIn(f'data-chapter="{num}" aria-current="page"', content, num)
            self.assertIn('class="references"', content, num)
            self.assertIn(f'id="lab-input-{num}"', content, num)
            self.assertIn(f'id="lab-output-{num}" role="status" aria-live="polite"', content, num)
            self.assertIn('src="../assets/lab-16-20.js"', content, num)
            ledger = json.loads((ROOT / "docs" / "evidence" / f"{num}.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["article"], f"chapters/{num}.html")
            self.assertGreaterEqual(len(ledger["claims"]), 6, num)
            for claim in ledger["claims"]:
                self.assertTrue(claim.get("source_url"), claim)
                self.assertTrue(claim.get("locator"), claim)
                self.assertIn(claim.get("status"), {"verified", "derived", "illustrative", "unverified"})
        self.assertTrue((ROOT / "assets" / "lab-16-20.js").exists())

    def test_nms_demo_has_local_script_and_accessible_controls(self):
        content=(ROOT/"chapters"/"14.html").read_text(encoding="utf-8")
        self.assertIn('id="nms-threshold"',content)
        self.assertIn('id="nms-mode"',content)
        self.assertIn('id="nms-demo-output" aria-live="polite"',content)
        self.assertIn('src="../assets/nms-demo.js"',content)
        self.assertTrue((ROOT/"assets"/"nms-demo.js").is_file())

    def test_corrected_yolov3_large_object_ap_is_present(self):
        content = (ROOT / "chapters" / "05.html").read_text(encoding="utf-8")
        self.assertIn("41.9", content)
        self.assertIn("49.1 不是该模型对应的大目标 AP", content)


if __name__ == "__main__":
    unittest.main()
