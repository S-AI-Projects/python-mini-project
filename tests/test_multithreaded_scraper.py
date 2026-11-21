import copy
import csv
import json
import os
import random
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.multithreaded_scraper import MultithreadedScraper, HTMLParser, DataExporter
from utilities.multithreaded_scraper.main import main



SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page Title</title>
    <meta name="description" content="This is a test description." />
</head>
<body>
    <h1>Heading 1</h1>
    <h2>Heading 2</h2>
    <a href="/about">About Us</a>
    <a href="https://example.com/contact">Contact</a>
</body>
</html>
"""


def test_html_parser():
    parser = HTMLParser("https://example.com/test")
    res = parser.parse(SAMPLE_HTML)

    assert res["title"] == "Test Page Title"
    assert res["meta_description"] == "This is a test description."
    assert "Heading 1" in res["headings"]
    assert "Heading 2" in res["headings"]
    assert "https://example.com/about" in res["links"]
    assert "https://example.com/contact" in res["links"]


def test_exporter_json_and_csv():
    data = [{
        "url": "https://example.com",
        "title": "Example",
        "meta_description": "Desc",
        "headings": ["H1"],
        "links": ["https://example.com/1"]
    }]

    exporter = DataExporter()

    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "out.json")
        csv_file = os.path.join(tmpdir, "out.csv")

        exporter.export_json(data, json_file)
        assert os.path.exists(json_file)
        with open(json_file, 'r', encoding='utf-8') as f:
            read_json = json.load(f)
            assert len(read_json) == 1
            assert read_json[0]["title"] == "Example"

        exporter.export_csv(data, csv_file)
        assert os.path.exists(csv_file)


def test_scraper_mock_fetch(monkeypatch):
    def mock_fetch(self, url):
        return SAMPLE_HTML

    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", mock_fetch)

    scraper = MultithreadedScraper(
        start_urls=["https://example.com"],
        max_workers=2,
        max_depth=1,
        delay=0
    )

    results = scraper.run()
    assert len(results) == 1
    assert results[0]["title"] == "Test Page Title"


@pytest.mark.parametrize("url", ["file:///etc/hostname", "ftp://example.com/x", "data:text/html,hi"])
def test_scraper_rejects_non_http_schemes(monkeypatch, url):
    """Regression: file:// seeds were passed straight to urllib.request.urlopen."""
    import urllib.request

    def _fail(*args, **kwargs):
        raise AssertionError("urlopen must not be called for non-http(s) URLs")

    monkeypatch.setattr(urllib.request, "urlopen", _fail)
    scraper = MultithreadedScraper([url], delay=0)
    assert scraper._fetch_url(url) is None
    assert scraper.failed_urls and "scheme" in scraper.failed_urls[0]["error"]


# ── Task R26-T034: Invariant and Property Tests for main() ─────────────────

MOCK_HTML_PAGE = """<!DOCTYPE html>
<html>
<head><title>Test Page Title</title><meta name="description" content="Test description"></head>
<body><h1>Heading 1</h1><a href="/internal">Internal</a></body>
</html>"""


def _mock_controlled_fetch(self, url):
    return MOCK_HTML_PAGE


def test_main_smallest_valid_input(tmp_path, monkeypatch):
    """
    Smallest valid input: Single target URL, default worker/depth/delay settings.
    Precondition source line: Line 12 (parser.add_argument('urls', nargs='*')).
    Expected output:
      - Return value: None
      - Result file created with shape: 1 item containing required schema keys.
      - Input argv unmutated.
    """
    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", _mock_controlled_fetch)
    out_file = str(tmp_path / "smallest_out.json")

    argv = ["https://example.com/item0", "-o", out_file, "--delay", "0"]
    original_argv = list(argv)

    res = main(argv)

    assert res is None
    assert argv == original_argv, "Input argv was mutated"
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    expected_keys = {"url", "title", "meta_description", "headings", "links", "depth"}
    assert set(item.keys()) == expected_keys
    assert item["url"] == "https://example.com/item0"
    assert item["title"] == "Test Page Title"


def test_main_ordinary_input(tmp_path, monkeypatch):
    """
    Ordinary input: Multiple target URLs with explicit workers, depth, and output.
    Precondition source lines: Lines 12-16 (urls, -w, -d, -o, --format).
    Expected output:
      - Return value: None
      - Result file created with shape: entries for the seed URLs.
    """
    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", _mock_controlled_fetch)
    out_file = str(tmp_path / "ordinary_out.json")

    argv = [
        "https://example.com/page1",
        "https://example.com/page2",
        "-w", "2",
        "-d", "1",
        "-o", out_file,
        "--format", "json",
        "--delay", "0"
    ]
    original_argv = list(argv)

    res = main(argv)

    assert res is None
    assert argv == original_argv, "Input argv was mutated"
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) >= 2
    scraped_urls = {item["url"] for item in data}
    assert "https://example.com/page1" in scraped_urls
    assert "https://example.com/page2" in scraped_urls


def test_main_input_mutation_invariance(tmp_path, monkeypatch):
    """
    Invariant: main() must not mutate the passed argv list.
    """
    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", _mock_controlled_fetch)
    out_file = str(tmp_path / "mutation_test.json")

    argv = ["https://example.com/alpha", "https://example.com/beta", "-o", out_file, "--delay", "0"]
    argv_copy = copy.deepcopy(argv)

    main(argv)
    assert argv == argv_copy, "argv was modified during main() execution"


def test_main_fresh_equivalent_inputs_invariance(tmp_path, monkeypatch):
    """
    Invariant: Two fresh, identical input invocations under controlled external state
    must yield equivalent output data and schema shape.
    """
    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", _mock_controlled_fetch)
    out_a = str(tmp_path / "equiv_a.json")
    out_b = str(tmp_path / "equiv_b.json")

    argv_a = ["https://example.com/test", "-o", out_a, "--delay", "0"]
    argv_b = ["https://example.com/test", "-o", out_b, "--delay", "0"]

    main(argv_a)
    main(argv_b)

    with open(out_a, "r", encoding="utf-8") as fa, open(out_b, "r", encoding="utf-8") as fb:
        data_a = json.load(fa)
        data_b = json.load(fb)

    assert data_a == data_b, "Fresh equivalent inputs produced non-identical output data"


def test_main_property_100_bounded_valid_cases(tmp_path, monkeypatch):
    """
    Property test: Generate at least 100 bounded valid cases with fixed seed.
    Invariant:
      - All runs complete without unhandled exception (return None).
      - Input argv is strictly unmutated.
      - Output file exists and adheres to valid type/shape schema.
    """
    monkeypatch.setattr(MultithreadedScraper, "_fetch_url", _mock_controlled_fetch)

    rng = random.Random(42)
    url_pool = [f"https://example.com/resource_{i}" for i in range(25)]

    for idx in range(100):
        k_urls = rng.randint(1, 3)
        selected_urls = rng.sample(url_pool, k_urls)
        workers = rng.randint(1, 4)
        depth = rng.randint(1, 2)
        fmt = rng.choice(["json", "csv"])
        out_filename = str(tmp_path / f"prop_test_{idx}.{fmt}")

        argv = list(selected_urls) + [
            "-w", str(workers),
            "-d", str(depth),
            "-o", out_filename,
            "--format", fmt,
            "--delay", "0"
        ]
        argv_snapshot = list(argv)

        res = main(argv)

        # Invariant checks
        assert res is None, f"Case #{idx}: main did not return None"
        assert argv == argv_snapshot, f"Case #{idx}: argv was mutated"
        assert os.path.exists(out_filename), f"Case #{idx}: output file was not created"

        if fmt == "json":
            with open(out_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, list), f"Case #{idx}: JSON output is not a list"
            assert len(data) >= len(selected_urls), f"Case #{idx}: missing scraped items"
            for item in data:
                assert "url" in item and "title" in item
        else:
            with open(out_filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) >= len(selected_urls), f"Case #{idx}: missing CSV rows"
            for row in rows:
                assert "url" in row and "title" in row

