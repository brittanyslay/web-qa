#!/usr/bin/env python3
"""
Test suite for qa-scan.py.

Two things are tested, and the second matters more than the first:
  1. The scanner FINDS the defects planted in examples/demo-site/index.html.
  2. The scanner does NOT invent findings on examples/demo-site/about/index.html,
     which is deliberately correct. A noisy QA tool gets ignored, and an ignored
     QA tool catches nothing.

Run:  python3 tests/test_qa_scan.py
"""
import json, os, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "scripts", "qa-scan.py")
DEMO = os.path.join(ROOT, "examples", "demo-site")


def ensure_fixtures():
    subprocess.run([sys.executable, os.path.join(DEMO, "generate-fixtures.py")],
                   capture_output=True)


def scan(path, *args):
    ensure_fixtures()
    r = subprocess.run([sys.executable, SCAN, path, "--json", *args],
                       capture_output=True, text=True)
    return json.loads(r.stdout), r.returncode


class TestFindsPlantedDefects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.code = scan(DEMO)
        cls.f = cls.data["findings"]
        cls.broken = [x for x in cls.f if x["page"] == "index.html"]

    def issues(self, page=None):
        return " | ".join(x["issue"] + " " + x["detail"]
                          for x in self.f if page is None or x["page"] == page)

    def test_exit_code_is_1_when_blockers_exist(self):
        self.assertEqual(self.code, 1)

    def test_scanned_all_demo_pages(self):
        self.assertEqual(self.data["pages_scanned"], 3)

    def test_finds_broken_internal_link(self):
        self.assertIn("/pricing.html", self.issues("index.html"))

    def test_finds_missing_image_file(self):
        self.assertIn("missing-image.png", self.issues("index.html"))

    def test_finds_oversized_image(self):
        self.assertIn("hero.jpg", self.issues("index.html"))

    def test_finds_missing_viewport(self):
        self.assertIn("viewport", self.issues("index.html").lower())

    def test_finds_missing_alt(self):
        self.assertIn("alt", self.issues("index.html").lower())

    def test_finds_stripe_secret_key(self):
        self.assertIn("Stripe live secret key", self.issues("leaked-key.html"))

    def test_finds_localhost_url(self):
        self.assertIn("localhost", self.issues("index.html"))

    def test_finds_insecure_form_action(self):
        self.assertIn("insecure http", self.issues("index.html").lower())

    def test_finds_target_blank_without_noopener(self):
        self.assertIn("noopener", self.issues("index.html"))

    def test_finds_duplicate_ids(self):
        self.assertIn("Duplicate id", self.issues("index.html"))

    def test_finds_unlabelled_input(self):
        self.assertIn("label", self.issues("index.html").lower())

    def test_finds_placeholder_copy(self):
        self.assertIn("placeholder", self.issues("index.html").lower())

    def test_finds_dead_anchor_target(self):
        self.assertIn("nonexistent-section", self.issues("index.html"))

    def test_finds_vague_link_text(self):
        self.assertIn("click here", self.issues("index.html").lower())

    def test_finds_skipped_heading_level(self):
        self.assertIn("Heading level skipped", self.issues("index.html"))

    def test_finds_sitewide_robots_block(self):
        self.assertIn("robots.txt blocks the entire site", self.issues())


class TestDoesNotInventFindings(unittest.TestCase):
    """The clean page must produce no blockers and no majors."""

    @classmethod
    def setUpClass(cls):
        cls.data, _ = scan(DEMO)
        cls.clean = [x for x in cls.data["findings"]
                     if x["page"] == os.path.join("about", "index.html")]

    def test_no_blockers_on_clean_page(self):
        bad = [x["issue"] for x in self.clean if x["severity"] == "BLOCKER"]
        self.assertEqual(bad, [], f"False-positive blockers: {bad}")

    def test_no_majors_on_clean_page(self):
        bad = [x["issue"] for x in self.clean if x["severity"] == "MAJOR"]
        self.assertEqual(bad, [], f"False-positive majors: {bad}")


class TestRobotsParsing(unittest.TestCase):
    """A `Disallow: /` under an AI-crawler agent is intentional, not a defect."""

    def setUp(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("qa_scan", SCAN)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)

    def test_wildcard_disallow_all_is_a_block(self):
        self.assertTrue(self.m.robots_blocks_everything("User-agent: *\nDisallow: /"))

    def test_ai_crawler_block_is_not_a_sitewide_block(self):
        txt = ("User-agent: *\nAllow: /\n\n"
               "User-agent: GPTBot\nDisallow: /\n\n"
               "User-agent: CCBot\nDisallow: /\n")
        self.assertFalse(self.m.robots_blocks_everything(txt))

    def test_path_disallow_is_not_a_sitewide_block(self):
        self.assertFalse(self.m.robots_blocks_everything("User-agent: *\nDisallow: /admin/"))

    def test_comments_are_ignored(self):
        self.assertFalse(self.m.robots_blocks_everything("# Disallow: /\nUser-agent: *\nAllow: /"))


class TestIgnoreGlobs(unittest.TestCase):
    def test_ignore_reduces_page_count(self):
        full, _ = scan(DEMO)
        less, _ = scan(DEMO, "--ignore", "about")
        self.assertLess(less["pages_scanned"], full["pages_scanned"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
