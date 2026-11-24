"""report_lib.py - small helpers shared by build_report.py (data access + python-docx building blocks)."""
import csv, os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAPHS = os.path.join(ROOT, "graphs")

# ---------------------------------------------------------------- data access
_rows = {}
def load_data():
    with open(os.path.join(ROOT, "data", "all_stats.csv")) as f:
        for r in csv.DictReader(f):
            for k, v in list(r.items()):
                try:
                    r[k] = float(v)
                except (ValueError, TypeError):
                    pass
            _rows[(r["bench"], r["part"], r["label"])] = r

def v(b, p, l, k):
    return _rows[(b, p, l)][k]

def pct_change(a, b):
    return 100 * (b - a) / a

# ---------------------------------------------------------------- document setup
FONT = "Calibri"

def new_document():
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)         # A4
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2.0)
    st = d.styles["Normal"]
    st.font.name = FONT; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.12
    for name, size, color in (("Heading 1", 17, "1F3864"), ("Heading 2", 13.5, "1F3864"), ("Heading 3", 11.5, "2F5496")):
        h = d.styles[name]
        h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True
        h.font.color.rgb = RGBColor.from_string(color)
        h.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        h.paragraph_format.space_before = Pt(14 if name != "Heading 3" else 10)
        h.paragraph_format.space_after = Pt(5)
        h.paragraph_format.keep_with_next = True
    return d

def para(d, text="", bold=False, italic=False, size=None, align=None, after=None, color=None, keep_next=False):
    p = d.add_paragraph()
    add_runs(p, text, bold, italic, size, color)
    if align == "center": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if keep_next: p.paragraph_format.keep_with_next = True
    return p

def add_runs(p, text, bold=False, italic=False, size=None, color=None):
    """Supports **bold** pieces inside text."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1)
        r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = RGBColor.from_string(color)

def bullet(d, text):
    p = d.add_paragraph(style="List Bullet")
    add_runs(p, text)
    p.paragraph_format.space_after = Pt(2)
    return p

def code(d, text):
    p = d.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.3)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "F2F2F2")
    pPr.append(shd)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        r = p.add_run(line)
        r.font.name = "Consolas"; r.font.size = Pt(8.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        if i < len(lines) - 1:
            r.add_break()
    return p

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def table(d, header, rows, widths_cm, align_right_from=1, font=9.5, bold_rows=()):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(font)
        shade(c, "D9E2F3")
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val)); r.font.size = Pt(font)
            if ri in bold_rows: r.bold = True
            if i >= align_right_from:
                cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for i, w in enumerate(widths_cm):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        for i, w in enumerate(widths_cm):
            row.cells[i].width = Cm(w)
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
    # keep a small table on one page: rows never split, and every row stays with the next one
    for ri, row in enumerate(t.rows):
        trPr_ = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); trPr_.append(cs)
        if ri < len(t.rows) - 1 and len(t.rows) <= 14:
            for c in row.cells:
                for p_ in c.paragraphs:
                    p_.paragraph_format.keep_with_next = True
    # repeat header row
    trPr = t.rows[0]._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trPr.append(h)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

_fig = [0]
def figure(d, filename, caption, width_cm=15.0):
    _fig[0] += 1
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(os.path.join(GRAPHS, filename), width=Cm(width_cm))
    c = para(d, f"**Figure {_fig[0]}.** {caption}", size=9.5, align="center", after=8, color="404040")
    return c

def interp(d, text_paras):
    """Interpretation block: a shaded-left-border box of 1-2 short paragraphs."""
    if isinstance(text_paras, str):
        text_paras = [text_paras]
    for i, t in enumerate(text_paras):
        p = d.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.4)
        pPr = p._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr"); left = OxmlElement("w:left")
        left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "18"); left.set(qn("w:space"), "8"); left.set(qn("w:color"), "2F5496")
        bdr.append(left); pPr.append(bdr)
        if i == 0:
            r = p.add_run("Our interpretation. "); r.bold = True; r.font.color.rgb = RGBColor.from_string("2F5496")
        add_runs(p, t)
        p.paragraph_format.space_after = Pt(8)

def page_numbers(d, left_text):
    s = d.sections[0]
    fp = s.footer.paragraphs[0]
    fp.text = ""
    fp.add_run(left_text + "    |    Page ").font.size = Pt(8.5)
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        r = fp.add_run(); r.font.size = Pt(8.5)
        if tag:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), tag); r._r.append(f)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

def page_break(d):
    from docx.enum.text import WD_BREAK
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
