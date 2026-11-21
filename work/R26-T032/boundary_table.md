# Task R26-T032: Boundary Definition for `setup_styles` (`utilities/Markdown-PDF-Converter/markdown_to_pdf.py`)

## 1. Function Analysis & Contract

### Public Interface
```python
def setup_styles(theme)
```
- **Target Location**: `utilities/Markdown-PDF-Converter/markdown_to_pdf.py` (lines 85–189).
- **Public Inputs**:
  - `theme` (`dict`): Configuration dictionary providing typography families and hex colors.
- **Return Value**:
  - `styles` (`reportlab.lib.styles.StyleSheet1`): StyleSheet populated with configured standard styles (`Heading1` through `Heading6`, `Normal`, `BodyText`) and custom added styles (`CustomListItem`, `CodeStyle`, `QuoteParaStyle`, `TableHeaderStyle`, `TableCellStyle`).
- **Mutation Behavior**:
  - Pure with respect to caller inputs: `theme` is never modified.
- **External Dependencies**:
  - `reportlab.lib.styles.getSampleStyleSheet`, `ParagraphStyle`
  - `reportlab.lib.colors.HexColor`

---

## 2. Boundary Table

| Partition | Input Description | Precondition Source Lines | Expected Behavior | Tested Boundary Condition |
| :--- | :--- | :--- | :--- | :--- |
| **Valid Interior** | Full theme dict (e.g., `THEMES["Classic"]` with 16 keys) | Lines 25–43, 85–189 | Successfully configures all 12 styles with exact font families, sizes, leading, and colors | Standard ordinary input |
| **Valid Boundary 1** | Smallest supported input (minimal 8 keys accessed) | Lines 90, 93, 101, 109, 119, 125, 164, 175 | All styles generated successfully; unused theme keys omitted without error | Lower boundary of required theme keys |
| **Valid Boundary 2A**| `theme["font_family_body"] == "Helvetica"` | Line 163 | `QuoteParaStyle.fontName == "Helvetica-Oblique"` | Helvetica oblique font branch |
| **Valid Boundary 2B**| `theme["font_family_body"] != "Helvetica"` (e.g. `"Times-Roman"`) | Line 163 | `QuoteParaStyle.fontName == "Times-Italic"` | Non-Helvetica italic font branch |
| **Valid Boundary 3** | Base stylesheet without `'BodyText'` | Line 131 | `if 'BodyText' in styles:` cleanly skips without error | Optional key existence in base sheet |
| **Outside Boundary 1**| Missing mandatory key (e.g. `'font_family_headings'`) | Line 90 | Raises `KeyError('font_family_headings')` | Incomplete input dictionary |
| **Outside Boundary 2**| `theme = None` or non-subscriptable object | Line 90 | Raises `TypeError` | Type error boundary |
| **Outside Boundary 3**| Malformed hex color (e.g. `"not-a-hex"`) | Line 93 | Raises `ValueError` | Value error boundary |

---

## 3. Source Fixture & Data Anchors

- **Source Line 201**: `self.story = []`
- **Source Line 205**: `self.text_accumulator = []`
- **Verification**:
  - An instance of `HTMLToFlowablesParser(styles, theme, printable_width)` initialized with styles from `setup_styles(theme)` initializes `story` and `text_accumulator` to empty lists `[]`.
  - Feeding HTML blocks (such as `<h1>Title</h1>`) consumes text and accumulates flowables into `story` using the configured heading styles.
