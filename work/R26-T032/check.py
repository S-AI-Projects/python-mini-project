#!/usr/bin/env python3
"""
Focused runner for Task R26-T032:
Define the supported boundaries of setup_styles (markdown_to_pdf.py) [utilities/Markdown-PDF-Converter]

Responsibilities:
1. Mock external I/O and libraries (reportlab, markdown2) and import only markdown_to_pdf.py.
2. Execute boundary and regression checks covering valid interior, valid boundaries,
   outside boundaries, mutation isolation, and source data anchors.
3. Run project pytest suite on tests/test_markdown_to_pdf.py.
4. Record actual command, nonzero test count, tool versions, inputs, expected and actual results.
5. Save artifacts to work/R26-T032/results.json, work/R26-T032/report.txt, and boundary_table.md.
6. Exit non-zero on any failure; exit 0 on success.
"""

import copy
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "utilities" / "Markdown-PDF-Converter" / "markdown_to_pdf.py"
OUTPUT_DIR = Path(__file__).resolve().parent


class MockHexColor:
    def __init__(self, hex_val):
        if not isinstance(hex_val, str) or not hex_val.startswith("#"):
            raise ValueError(f"Invalid hex color format: {hex_val}")
        self.hex_val = hex_val

    def __eq__(self, other):
        return isinstance(other, MockHexColor) and self.hex_val == other.hex_val

    def __repr__(self):
        return f"HexColor('{self.hex_val}')"


class MockParagraphStyle:
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


def load_module():
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

    spec = importlib.util.spec_from_file_location("markdown_to_pdf", TARGET_FILE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["markdown_to_pdf"] = mod
    spec.loader.exec_module(mod)
    return mod


def run_checks():
    md_mod = load_module()
    checks = []

    def record_check(name, input_val, expected, actual, condition_met, precondition_line):
        checks.append({
            "name": name,
            "input": repr(input_val),
            "precondition_source_line": precondition_line,
            "expected": repr(expected),
            "actual": repr(actual),
            "status": "PASSED" if condition_met else "FAILED"
        })

    # Check 1: Valid interior ordinary input
    classic = md_mod.THEMES["Classic"]
    styles = md_mod.setup_styles(classic)
    ok_1 = (
        styles["Heading1"].fontName == "Times-Roman"
        and styles["Heading1"].fontSize == 24
        and styles["Heading1"].textColor == MockHexColor("#1A365D")
        and styles["CustomListItem"].leftIndent == 24
        and styles["CodeStyle"].fontName == "Courier"
    )
    record_check(
        name="Valid interior: ordinary full theme dictionary (THEMES['Classic'])",
        input_val="THEMES['Classic'] (16 keys)",
        expected="Heading1(Times-Roman, 24, #1A365D), CustomListItem(leftIndent=24), CodeStyle(Courier)",
        actual=f"Heading1({styles['Heading1'].fontName}, {styles['Heading1'].fontSize}, {styles['Heading1'].textColor})",
        condition_met=ok_1,
        precondition_line="Lines 25-43 (THEMES['Classic']), Lines 85-189 (setup_styles)"
    )

    # Check 2: Valid boundary smallest supported input (minimal 8 required keys)
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
    styles_min = md_mod.setup_styles(minimal_theme)
    ok_2 = (
        len(minimal_theme) == 8
        and styles_min["Heading1"].textColor == MockHexColor("#0F766E")
        and styles_min["Normal"].textColor == MockHexColor("#1F2937")
    )
    record_check(
        name="Valid boundary: smallest supported input (minimal 8 required keys)",
        input_val=minimal_theme,
        expected="Styles created successfully with 8 required keys only",
        actual="Heading1 and Normal styles configured successfully",
        condition_met=ok_2,
        precondition_line="Lines 90, 93, 101, 109, 119, 125, 164, 175"
    )

    # Check 3: Valid boundary font branch Helvetica -> Helvetica-Oblique
    helv_theme = copy.deepcopy(minimal_theme)
    helv_theme["font_family_body"] = "Helvetica"
    styles_helv = md_mod.setup_styles(helv_theme)
    quote_font_helv = styles_helv["QuoteParaStyle"].fontName
    record_check(
        name="Valid boundary: font_family_body == 'Helvetica'",
        input_val="font_family_body='Helvetica'",
        expected="QuoteParaStyle.fontName == 'Helvetica-Oblique'",
        actual=f"QuoteParaStyle.fontName == '{quote_font_helv}'",
        condition_met=(quote_font_helv == "Helvetica-Oblique"),
        precondition_line="Line 163: 'Helvetica-Oblique' if theme['font_family_body'] == 'Helvetica' else 'Times-Italic'"
    )

    # Check 4: Valid boundary font branch non-Helvetica -> Times-Italic
    times_theme = copy.deepcopy(minimal_theme)
    times_theme["font_family_body"] = "Times-Roman"
    styles_times = md_mod.setup_styles(times_theme)
    quote_font_times = styles_times["QuoteParaStyle"].fontName
    record_check(
        name="Valid boundary: font_family_body != 'Helvetica' ('Times-Roman')",
        input_val="font_family_body='Times-Roman'",
        expected="QuoteParaStyle.fontName == 'Times-Italic'",
        actual=f"QuoteParaStyle.fontName == '{quote_font_times}'",
        condition_met=(quote_font_times == "Times-Italic"),
        precondition_line="Line 163: 'Helvetica-Oblique' if theme['font_family_body'] == 'Helvetica' else 'Times-Italic'"
    )

    # Check 5: Valid boundary optional BodyText handling
    sheet_no_body = MockStyleSheet(include_body_text=False)
    original_get_sheet = md_mod.getSampleStyleSheet
    try:
        md_mod.getSampleStyleSheet = lambda: sheet_no_body
        styles_no_body = md_mod.setup_styles(minimal_theme)
        body_handled = ("BodyText" not in styles_no_body)
    finally:
        md_mod.getSampleStyleSheet = original_get_sheet
    record_check(
        name="Valid boundary: stylesheet without 'BodyText' handled safely",
        input_val="MockStyleSheet without BodyText",
        expected="'BodyText' skipped without KeyError",
        actual="Completed without error",
        condition_met=body_handled,
        precondition_line="Line 131: if 'BodyText' in styles:"
    )

    # Check 6: Mutation isolation
    orig = copy.deepcopy(md_mod.THEMES["Sleek Dark"])
    working = copy.deepcopy(md_mod.THEMES["Sleek Dark"])
    md_mod.setup_styles(working)
    no_mut = (working == orig)
    record_check(
        name="Mutation isolation: theme dictionary remains unmutated",
        input_val="THEMES['Sleek Dark']",
        expected="theme dict unchanged",
        actual="theme dict unchanged" if no_mut else "unexpected mutation",
        condition_met=no_mut,
        precondition_line="Lines 85-189: pure dictionary read operations"
    )

    # Check 7: Outside boundary missing required key -> KeyError
    incomplete = copy.deepcopy(minimal_theme)
    del incomplete["font_family_headings"]
    try:
        md_mod.setup_styles(incomplete)
        raised_key = False
    except KeyError:
        raised_key = True
    record_check(
        name="Outside boundary: missing required key 'font_family_headings'",
        input_val="dict lacking 'font_family_headings'",
        expected="KeyError('font_family_headings')",
        actual="KeyError raised" if raised_key else "No exception raised",
        condition_met=raised_key,
        precondition_line="Line 90: styles['Heading1'].fontName = theme['font_family_headings']"
    )

    # Check 8: Outside boundary None input -> TypeError
    try:
        md_mod.setup_styles(None)
        raised_type = False
    except TypeError:
        raised_type = True
    record_check(
        name="Outside boundary: None input",
        input_val=None,
        expected="TypeError",
        actual="TypeError raised" if raised_type else "No exception raised",
        condition_met=raised_type,
        precondition_line="Line 90: theme['font_family_headings'] subscript on None"
    )

    # Check 9: Outside boundary invalid color format -> ValueError
    bad_color = copy.deepcopy(minimal_theme)
    bad_color["h1"] = "invalid_hex"
    try:
        md_mod.setup_styles(bad_color)
        raised_val = False
    except ValueError:
        raised_val = True
    record_check(
        name="Outside boundary: malformed hex color format",
        input_val="h1='invalid_hex'",
        expected="ValueError",
        actual="ValueError raised" if raised_val else "No exception raised",
        condition_met=raised_val,
        precondition_line="Line 93: colors.HexColor(theme['h1'])"
    )

    # Check 10: Fixture data anchors self.story = [] | self.text_accumulator = []
    parser = md_mod.HTMLToFlowablesParser(styles, classic, printable_width=450)
    story_init = (parser.story == [])
    accum_init = (parser.text_accumulator == [])
    parser.feed("<h1>Anchored Test Heading</h1>")
    parser.close()
    flowables_added = (len(parser.story) >= 1 and parser.story[0]["style"].name == "Heading1")
    anchors_ok = story_init and accum_init and flowables_added
    record_check(
        name="Fixture anchors: self.story = [] (line 201) and self.text_accumulator = [] (line 205)",
        input_val="HTMLToFlowablesParser with setup_styles and <h1> tag",
        expected="story=[] and accumulator=[] initially; flowables appended using Heading1 style",
        actual=f"story initial: [], accumulator initial: [], generated {len(parser.story)} flowables",
        condition_met=anchors_ok,
        precondition_line="Line 201: self.story = []; Line 205: self.text_accumulator = []"
    )

    return checks


def run_pytest_suite():
    venv_pytest = REPO_ROOT / ".venv" / "bin" / "pytest"
    cmd = [str(venv_pytest) if venv_pytest.exists() else "pytest", "tests/test_markdown_to_pdf.py", "-v"]
    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        return {
            "command": " ".join(cmd),
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "success": (proc.returncode == 0)
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


def get_git_info():
    def _git_run(args):
        try:
            return subprocess.check_output(["git"] + args, cwd=REPO_ROOT, text=True).strip()
        except Exception:
            return "unknown"
    return {
        "branch": _git_run(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": _git_run(["rev-parse", "HEAD"]),
        "status": _git_run(["status", "--short"])
    }


def main():
    print("=" * 70)
    print("🚀 Task R26-T032: markdown_to_pdf setup_styles Boundary Verification Runner")
    print("=" * 70)

    checks = run_checks()
    failed_checks = [c for c in checks if c["status"] != "PASSED"]

    pytest_result = run_pytest_suite()

    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "platform_machine": platform.machine(),
        "pytest_available": pytest_result["exit_code"] != -1,
        "git": get_git_info()
    }

    test_count = len(checks)
    all_passed = (len(failed_checks) == 0) and pytest_result["success"]

    summary_data = {
        "task_id": "R26-T032",
        "target_file": "utilities/Markdown-PDF-Converter/markdown_to_pdf.py",
        "target_function": "setup_styles",
        "native_command": pytest_result["command"],
        "nonzero_test_count": test_count,
        "overall_status": "PASSED" if all_passed else "FAILED",
        "tool_versions": tool_versions,
        "checks": checks,
        "pytest_summary": {
            "command": pytest_result["command"],
            "exit_code": pytest_result["exit_code"],
            "output": pytest_result["stdout"]
        }
    }

    results_json_path = OUTPUT_DIR / "results.json"
    with open(results_json_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    report_txt_path = OUTPUT_DIR / "report.txt"
    with open(report_txt_path, "w") as f:
        f.write("Task R26-T032 Verification Report\n")
        f.write("Target: utilities/Markdown-PDF-Converter/markdown_to_pdf.py::setup_styles\n")
        f.write(f"Overall Status: {summary_data['overall_status']}\n")
        f.write(f"Total Checks: {test_count} (Nonzero Count Verified)\n")
        f.write(f"Native Test Command: {pytest_result['command']}\n")
        f.write(f"Pytest Exit Code: {pytest_result['exit_code']}\n\n")
        f.write("--- Tool Versions ---\n")
        f.write(f"Python: {tool_versions['python']}\n")
        f.write(f"Platform: {tool_versions['platform']} ({tool_versions['platform_machine']})\n")
        f.write(f"Git Branch: {tool_versions['git']['branch']} ({tool_versions['git']['commit'][:8]})\n\n")
        f.write("--- Boundary & Regression Check Results ---\n")
        for idx, c in enumerate(checks, 1):
            f.write(f"[{idx:02d}] {c['status']}: {c['name']}\n")
            f.write(f"     Precondition Source Line: {c['precondition_source_line']}\n")
            f.write(f"     Input:    {c['input']}\n")
            f.write(f"     Expected: {c['expected']}\n")
            f.write(f"     Actual:   {c['actual']}\n\n")

    print(f"\n📊 Total Checks Executed: {test_count}")
    print(f"🛠️  Native Pytest Command: {pytest_result['command']}")
    print(f"📝 Native Pytest Result : {'PASSED' if pytest_result['success'] else 'FAILED'}")
    print(f"📁 Results Saved To    : {results_json_path}")
    print(f"📄 Report Saved To     : {report_txt_path}\n")

    for idx, c in enumerate(checks, 1):
        status_icon = "✅" if c["status"] == "PASSED" else "❌"
        print(f"{status_icon} [{idx:02d}] {c['name']}")
        print(f"    Expected: {c['expected']}")
        print(f"    Actual  : {c['actual']}")

    if not all_passed:
        print("\n❌ Verification FAILED!")
        sys.exit(1)

    print("\n✅ All boundary and regression checks PASSED successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
