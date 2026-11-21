"""
Tests for utilities/Markdown-PDF-Converter/markdown_to_pdf.py

Focus areas (Task R26-T032):
- Define the supported boundaries of setup_styles(theme).
- Precondition source lines and boundary table:
    * Valid Interior: ordinary full theme dict (lines 24-82, 85-189)
    * Valid Boundary 1: smallest supported input (minimal 8 required keys)
    * Valid Boundary 2: font branch boundary (line 163: Helvetica vs non-Helvetica)
    * Valid Boundary 3: optional BodyText presence (line 131: if 'BodyText' in styles)
    * Outside Boundary: missing required key -> KeyError (lines 90, 93, etc.)
    * Outside Boundary: non-subscriptable theme -> TypeError (line 90)
    * Outside Boundary: invalid hex color format -> ValueError (line 93)
- Source fixture / data anchors:
    * Line 201: self.story = []
    * Line 205: self.text_accumulator = []
- Assertion of explicit return values and mutation isolation.
- External I/O and libraries (reportlab, markdown2) mocked for hermetic execution.
"""

import copy
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Markdown-PDF-Converter"
    / "markdown_to_pdf.py"
)


class MockHexColor:
    """Mock reportlab.lib.colors.HexColor for isolated testing."""

    def __init__(self, hex_val):
        if not isinstance(hex_val, str) or not hex_val.startswith("#"):
            raise ValueError(f"Invalid hex color format: {hex_val}")
        self.hex_val = hex_val

    def __eq__(self, other):
        return isinstance(other, MockHexColor) and self.hex_val == other.hex_val

    def __repr__(self):
        return f"HexColor('{self.hex_val}')"


class MockParagraphStyle:
    """Mock reportlab.lib.styles.ParagraphStyle."""

    def __init__(self, name, parent=None, **kwargs):
        self.name = name
        self.parent = parent
        self.fontName = "Helvetica"
        self.fontSize = 10
        self.leading = 12
        self.textColor = None
        self.spaceBefore = 0
        self.spaceAfter = 0
        self.keepWithNext = False
        self.leftIndent = 0
        self.firstLineIndent = 0
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockStyleSheet:
    """Mock reportlab.lib.styles.getSampleStyleSheet."""

    def __init__(self, include_body_text=True):
        self._styles = {
            "Heading1": MockParagraphStyle("Heading1"),
            "Heading2": MockParagraphStyle("Heading2"),
            "Heading3": MockParagraphStyle("Heading3"),
            "Heading4": MockParagraphStyle("Heading4"),
            "Heading5": MockParagraphStyle("Heading5"),
            "Heading6": MockParagraphStyle("Heading6"),
            "Normal": MockParagraphStyle("Normal"),
        }
        if include_body_text:
            self._styles["BodyText"] = MockParagraphStyle("BodyText")

    def __getitem__(self, key):
        return self._styles[key]

    def __contains__(self, key):
        return key in self._styles

    def add(self, style):
        self._styles[style.name] = style


def load_md_to_pdf_module():
    """Load markdown_to_pdf with hermetic mock reportlab and markdown2."""
    mock_colors = MagicMock()
    mock_colors.HexColor = MockHexColor

    mock_styles = MagicMock()
    mock_styles.getSampleStyleSheet = MockStyleSheet
    mock_styles.ParagraphStyle = MockParagraphStyle

    mock_reportlab = MagicMock()
    mock_reportlab.lib.colors = mock_colors
    mock_reportlab.lib.styles = mock_styles

    mock_platypus = MagicMock()
    mock_platypus.Paragraph = lambda text, style: {"type": "Paragraph", "text": text, "style": style}
    mock_platypus.Spacer = lambda w, h: {"type": "Spacer", "width": w, "height": h}
    mock_platypus.HRFlowable = lambda **kw: {"type": "HRFlowable", **kw}

    sys.modules["reportlab"] = mock_reportlab
    sys.modules["reportlab.lib"] = mock_reportlab.lib
    sys.modules["reportlab.lib.colors"] = mock_colors
    sys.modules["reportlab.lib.pagesizes"] = MagicMock()
    sys.modules["reportlab.platypus"] = mock_platypus
    sys.modules["reportlab.platypus.flowables"] = mock_platypus
    sys.modules["reportlab.lib.styles"] = mock_styles
    sys.modules["markdown2"] = MagicMock()

    spec = importlib.util.spec_from_file_location("markdown_to_pdf", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["markdown_to_pdf"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def md_module():
    return load_md_to_pdf_module()


# ── Valid Interior: Ordinary Input ──────────────────────────────────────────

def test_setup_styles_ordinary_input(md_module):
    """
    Ordinary input: Full THEMES['Classic'] dictionary (16 keys).
    Precondition source lines: Line 25-43 (THEMES['Classic']), Lines 85-189 (setup_styles).
    Expected results:
      - Heading1 fontName is 'Times-Roman', fontSize 24, textColor HexColor('#1A365D')
      - Heading2 fontName is 'Times-Roman', fontSize 18, textColor HexColor('#2C3E50')
      - Heading3 fontName is 'Times-Roman', fontSize 14, textColor HexColor('#34495E')
      - Normal fontName is 'Helvetica', fontSize 10, textColor HexColor('#2C3E50')
      - CustomListItem leftIndent is 24, firstLineIndent is -12
      - CodeStyle fontName is 'Courier', fontSize 8.5
      - TableHeaderStyle fontName is 'Times-Roman', textColor HexColor('#FFFFFF')
    """
    theme = md_module.THEMES["Classic"]
    styles = md_module.setup_styles(theme)

    # Explicit expected value assertions
    assert styles["Heading1"].fontName == "Times-Roman"
    assert styles["Heading1"].fontSize == 24
    assert styles["Heading1"].leading == 28
    assert styles["Heading1"].textColor == MockHexColor("#1A365D")
    assert styles["Heading1"].keepWithNext is True

    assert styles["Heading2"].fontName == "Times-Roman"
    assert styles["Heading2"].fontSize == 18
    assert styles["Heading2"].textColor == MockHexColor("#2C3E50")

    assert styles["Heading3"].fontName == "Times-Roman"
    assert styles["Heading3"].fontSize == 14
    assert styles["Heading3"].textColor == MockHexColor("#34495E")

    for level in ("Heading4", "Heading5", "Heading6"):
        assert styles[level].fontName == "Times-Roman"
        assert styles[level].fontSize == 11.5
        assert styles[level].textColor == MockHexColor("#2C3E50")

    assert styles["Normal"].fontName == "Helvetica"
    assert styles["Normal"].fontSize == 10
    assert styles["Normal"].textColor == MockHexColor("#2C3E50")

    assert styles["CustomListItem"].leftIndent == 24
    assert styles["CustomListItem"].firstLineIndent == -12
    assert styles["CodeStyle"].fontName == "Courier"
    assert styles["CodeStyle"].fontSize == 8.5
    assert styles["TableHeaderStyle"].textColor == MockHexColor("#FFFFFF")


# ── Valid Boundary: Smallest Supported Input (Minimal Domain) ───────────────

def test_setup_styles_smallest_valid_input(md_module):
    """
    Smallest valid input: Dictionary with ONLY the 8 keys strictly required by setup_styles.
    Unused theme keys (background, accent, code_bg, quote_bg, table_header_bg, etc.) are omitted.
    Precondition source lines:
      Line 90: theme["font_family_headings"]
      Line 93: theme["h1"]
      Line 101: theme["h2"]
      Line 109: theme["h3"]
      Line 119: theme["text"]
      Line 125: theme["font_family_body"]
      Line 164: theme["quote_text"]
      Line 175: theme["table_header_text"]
    """
    minimal_theme = {
        "font_family_headings": "Helvetica-Bold",
        "font_family_body": "Helvetica",
        "h1": "#0F766E",
        "h2": "#115E59",
        "h3": "#134E4A",
        "text": "#1F2937",
        "quote_text": "#4B5563",
        "table_header_text": "#FFFFFF",
    }
    assert len(minimal_theme) == 8  # Smallest supported boundary size

    styles = md_module.setup_styles(minimal_theme)

    assert styles["Heading1"].fontName == "Helvetica-Bold"
    assert styles["Heading1"].textColor == MockHexColor("#0F766E")
    assert styles["Heading2"].textColor == MockHexColor("#115E59")
    assert styles["Heading3"].textColor == MockHexColor("#134E4A")
    assert styles["Normal"].fontName == "Helvetica"
    assert styles["Normal"].textColor == MockHexColor("#1F2937")
    assert styles["QuoteParaStyle"].textColor == MockHexColor("#4B5563")
    assert styles["TableHeaderStyle"].textColor == MockHexColor("#FFFFFF")


# ── Valid Boundary: Font Branch in QuoteParaStyle ───────────────────────────

def test_setup_styles_quote_font_helvetica_boundary(md_module):
    """
    Branch A: theme['font_family_body'] == 'Helvetica'.
    Precondition line: Line 163 (fontName='Helvetica-Oblique' if theme["font_family_body"] == 'Helvetica' else 'Times-Italic')
    Expected result: QuoteParaStyle.fontName == 'Helvetica-Oblique'
    """
    theme = {
        "font_family_headings": "Helvetica-Bold",
        "font_family_body": "Helvetica",
        "h1": "#111111",
        "h2": "#222222",
        "h3": "#333333",
        "text": "#444444",
        "quote_text": "#555555",
        "table_header_text": "#FFFFFF",
    }
    styles = md_module.setup_styles(theme)
    assert styles["QuoteParaStyle"].fontName == "Helvetica-Oblique"


def test_setup_styles_quote_font_non_helvetica_boundary(md_module):
    """
    Branch B: theme['font_family_body'] != 'Helvetica' (e.g. 'Times-Roman').
    Precondition line: Line 163 (fontName='Helvetica-Oblique' if theme["font_family_body"] == 'Helvetica' else 'Times-Italic')
    Expected result: QuoteParaStyle.fontName == 'Times-Italic'
    """
    theme = {
        "font_family_headings": "Times-Bold",
        "font_family_body": "Times-Roman",
        "h1": "#111111",
        "h2": "#222222",
        "h3": "#333333",
        "text": "#444444",
        "quote_text": "#555555",
        "table_header_text": "#FFFFFF",
    }
    styles = md_module.setup_styles(theme)
    assert styles["QuoteParaStyle"].fontName == "Times-Italic"


# ── Valid Boundary: Optional BodyText Key ───────────────────────────────────

def test_setup_styles_optional_body_text_handled(md_module, monkeypatch):
    """
    Precondition line: Line 131 (if 'BodyText' in styles:)
    Verifies that when the base stylesheet lacks 'BodyText', setup_styles
    completes without KeyError.
    """
    sheet_without_body_text = MockStyleSheet(include_body_text=False)
    monkeypatch.setattr(md_module, "getSampleStyleSheet", lambda: sheet_without_body_text)

    theme = md_module.THEMES["Classic"]
    styles = md_module.setup_styles(theme)
    assert "BodyText" not in styles
    assert styles["Normal"].fontName == "Helvetica"


# ── Mutation Behavior Isolation ─────────────────────────────────────────────

def test_setup_styles_mutation_isolation(md_module):
    """
    Verify setup_styles does not mutate the passed theme dictionary.
    """
    original_theme = copy.deepcopy(md_module.THEMES["Modern"])
    working_theme = copy.deepcopy(md_module.THEMES["Modern"])

    styles = md_module.setup_styles(working_theme)

    assert working_theme == original_theme, "theme dict was unexpectedly mutated"
    assert styles is not None


# ── Outside Supported Boundary (Explicit Error Behaviors) ───────────────────

def test_setup_styles_boundary_missing_required_key(md_module):
    """
    Precondition line: Line 90 (styles['Heading1'].fontName = theme["font_family_headings"])
    Outside supported boundary: dictionary missing required key raises KeyError.
    """
    incomplete_theme = {
        "font_family_body": "Helvetica",
        "h1": "#111111",
        "h2": "#222222",
        "h3": "#333333",
        "text": "#444444",
        "quote_text": "#555555",
        "table_header_text": "#FFFFFF",
        # Missing 'font_family_headings'
    }
    with pytest.raises(KeyError) as exc_info:
        md_module.setup_styles(incomplete_theme)
    assert "font_family_headings" in str(exc_info.value)


def test_setup_styles_boundary_none_input(md_module):
    """
    Precondition line: Line 90 (theme["font_family_headings"])
    Outside supported boundary: None or non-subscriptable object raises TypeError.
    """
    with pytest.raises(TypeError):
        md_module.setup_styles(None)


def test_setup_styles_boundary_invalid_color_format(md_module):
    """
    Precondition line: Line 93 (colors.HexColor(theme["h1"]))
    Outside supported boundary: Malformed hex color raises ValueError.
    """
    invalid_color_theme = {
        "font_family_headings": "Helvetica-Bold",
        "font_family_body": "Helvetica",
        "h1": "not-a-hex-color",
        "h2": "#222222",
        "h3": "#333333",
        "text": "#444444",
        "quote_text": "#555555",
        "table_header_text": "#FFFFFF",
    }
    with pytest.raises(ValueError) as exc_info:
        md_module.setup_styles(invalid_color_theme)
    assert "Invalid hex color format" in str(exc_info.value)


# ── Source Fixture & Data Anchors Integration ───────────────────────────────

def test_fixture_anchors_story_and_text_accumulator(md_module):
    """
    Source fixture/data anchors:
      Line 201: self.story = []
      Line 205: self.text_accumulator = []
    Verifies that HTMLToFlowablesParser initialized with styles from setup_styles:
      1. Instantiates self.story as empty list [].
      2. Instantiates self.text_accumulator as empty list [].
      3. Uses styles['Heading1'] when parsing <h1> to append flowable to self.story.
    """
    theme = md_module.THEMES["Classic"]
    styles = md_module.setup_styles(theme)
    parser = md_module.HTMLToFlowablesParser(styles, theme, printable_width=450)

    # Initial state assertion on source data anchors
    assert parser.story == [], "self.story was not initialized to empty list [] (Line 201)"
    assert parser.text_accumulator == [], "self.text_accumulator was not initialized to empty list [] (Line 205)"

    # Feed heading HTML
    parser.feed("<h1>Sample Heading</h1>")
    parser.close()

    # Verify flowable was generated and added to story
    assert len(parser.story) >= 1
    flowable = parser.story[0]
    assert flowable["type"] == "Paragraph"
    assert "Sample Heading" in flowable["text"]
    assert flowable["style"].name == "Heading1"
    assert flowable["style"].fontName == "Times-Roman"
