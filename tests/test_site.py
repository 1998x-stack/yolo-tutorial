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
        self.assertIn('src="assets/site.js"', content)
        self.assertNotIn("fetch(", content)
        self.assertTrue((ROOT / "assets/theme.css").is_file())
        self.assertTrue((ROOT / "assets/site.js").is_file())

    def test_every_local_html_link_resolves(self):
        pages = list(ROOT.glob("*.html")) + list((ROOT / "chapters").glob("*.html"))
        self.assertEqual(len(pages), 56)
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

    def test_first_five_chapters_are_self_contained_articles(self):
        forbidden = ("大家好，我是你们的讲师", "上一章我们", "下一章我们", "讲义介绍了")
        for i in range(1, 6):
            num = f"{i:02d}"
            content, parser = read_page(ROOT / "chapters" / f"{num}.html")
            self.assertEqual(parser.h1_count, 1, num)
            self.assertEqual(parser.article_count, 1, num)
            self.assertEqual(parser.main_count, 1, num)
            self.assertGreaterEqual(parser.svg_count, 1, num)
            self.assertIn("<math", content, num)
            self.assertIn("https://arxiv.org/abs/", content, num)
            for phrase in forbidden:
                self.assertNotIn(phrase, content, f"{num}: {phrase}")

    def test_first_five_inline_svgs_are_accessible_and_well_formed(self):
        for i in range(1, 6):
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
        for page in [ROOT / "index.html", *(ROOT / "chapters" / f"{i:02d}.html" for i in range(1, 6))]:
            _, parser = read_page(page)
            for raw in parser.links:
                if raw.startswith(("https://", "http://")):
                    self.assertNotIn(raw, [raw for raw in parser.links if raw.lower().endswith((".js", ".css"))])

    def test_mathml_is_accessible_and_outside_svg(self):
        for i in range(1, 6):
            num = f"{i:02d}"
            content = (ROOT / "chapters" / f"{num}.html").read_text(encoding="utf-8")
            math_attrs = re.findall(r"<math\b([^>]*)>", content, flags=re.IGNORECASE)
            for attrs in math_attrs:
                self.assertRegex(attrs, r'aria-label="[^"]+"', num)
            self.assertNotRegex(content, r"<svg\b[\s\S]*?<math\b", num)
            equation_count = content.count('class="equation"')
            self.assertEqual(content.count('class="equation" tabindex="0"'), equation_count, num)

    def test_corrected_yolov3_large_object_ap_is_present(self):
        content = (ROOT / "chapters" / "05.html").read_text(encoding="utf-8")
        self.assertIn("41.9", content)
        self.assertIn("49.1 不是该模型对应的大目标 AP", content)


if __name__ == "__main__":
    unittest.main()
