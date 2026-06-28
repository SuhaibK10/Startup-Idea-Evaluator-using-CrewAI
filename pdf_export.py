"""Generate a downloadable PDF evaluation report using fpdf2."""

from __future__ import annotations

import datetime
import re
from typing import Optional

try:
    from fpdf import FPDF
    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe(text: str) -> str:
    """Strip characters that fpdf core fonts can't encode."""
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "--", "•": "*", "…": "...",
        "✓": "[x]", "✔": "[x]", "✅": "[OK]",
        "⚠": "[!]", "❌": "[X]", "⭐": "*",
        "🟢": "[Strong]", "🟡": "[Watchlist]", "🟠": "[Needs Work]", "🔴": "[Pass]",
        "✅": "[done]", "⚠️": "[warn]", "📊": "", "💼": "", "🔍": "",
        "📄": "", "⭐": "*",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_md(text: str) -> str:
    """Light markdown-to-plain-text conversion for PDF body."""
    text = re.sub(r"#{1,6}\s+", "", text)           # headings
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)    # bold
    text = re.sub(r"\*(.+?)\*",   r"\1", text)      # italic
    text = re.sub(r"`(.+?)`",     r"\1", text)      # inline code
    text = re.sub(r"^\s*[-*]\s+", "  * ", text, flags=re.MULTILINE)  # bullets
    text = re.sub(r"\|.*\|", lambda m: m.group().replace("|", "  "), text)  # tables
    return text


# ── PDF class ─────────────────────────────────────────────────────────────────

class _Report(FPDF):
    _title: str = "Startup Evaluation Report"

    def header(self) -> None:
        self.set_fill_color(10, 22, 40)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(147, 197, 253)
        self.set_xy(0, 3)
        self.cell(0, 8, "  VentureScope AI  |  Startup Evaluation Report", align="L")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(160, 160, 160)
        date_str = datetime.date.today().strftime("%B %d, %Y")
        self.cell(0, 6, f"Generated {date_str}  |  Page {self.page_no()}", align="C")

    def section_header(self, title: str) -> None:
        self.ln(4)
        self.set_fill_color(10, 22, 40)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, f"  {_safe(title)}", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 41, 59)
        cleaned = _safe(_strip_md(text))
        self.multi_cell(0, 5.5, cleaned)


# ── Public function ───────────────────────────────────────────────────────────

def generate_pdf(
    idea: str,
    target: str,
    region: str,
    score_data: Optional[dict],
    outputs: dict[str, str],
) -> bytes:
    if not _FPDF_AVAILABLE:
        raise RuntimeError(
            "fpdf2 is not installed. Run: pip install fpdf2"
        )

    pdf = _Report()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── Cover page ────────────────────────────────────────────────────────────
    pdf.add_page()

    # Big banner
    pdf.set_fill_color(10, 22, 40)
    pdf.rect(0, 14, 210, 60, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(0, 24)
    pdf.cell(0, 10, "STARTUP EVALUATION REPORT", align="C", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(147, 197, 253)
    pdf.cell(0, 8, "Powered by VentureScope AI  |  5-Agent Analysis", align="C", ln=True)

    # Idea block
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 88)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "EVALUATED IDEA", ln=True)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(180, 6, _safe(idea))
    pdf.ln(4)

    # Meta row
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(15)
    pdf.cell(60, 6, f"Target: {_safe(target or 'N/A')}")
    pdf.cell(60, 6, f"Region: {_safe(region or 'N/A')}")
    pdf.cell(60, 6, f"Date: {datetime.date.today().strftime('%b %d, %Y')}", ln=True)

    # Score badge
    if score_data:
        pdf.ln(8)
        score = score_data.get("overall_score", 0)
        v_label = score_data.get("verdict", "N/A")
        pdf.set_fill_color(240, 247, 255)
        pdf.set_draw_color(193, 215, 245)
        pdf.rounded_rect(15, pdf.get_y(), 180, 32, 5, "FD")
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(10, 22, 40)
        pdf.set_xy(15, pdf.get_y() + 4)
        pdf.cell(90, 12, f"Score: {score}/100", align="C")
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(90, 12, f"Verdict: {_safe(v_label)}", align="C", ln=True)

        # Dimension scores
        dims = score_data.get("dimensions", {})
        dim_labels = {
            "problem":   "Problem",
            "market":    "Market",
            "biz_model": "Biz Model",
            "execution": "Execution",
            "moat":      "Moat",
        }
        if dims:
            pdf.ln(6)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 116, 139)
            pdf.set_x(15)
            for k, lbl in dim_labels.items():
                pdf.cell(36, 6, f"{lbl}: {dims.get(k, '-')}/10", align="C")
            pdf.ln()

    # ── Agent sections ────────────────────────────────────────────────────────
    sections = [
        ("1. PROBLEM VALIDATION",        outputs.get("validate", "")),
        ("2. MARKET RESEARCH",            outputs.get("research", "")),
        ("3. BUSINESS MODEL & GTM",       outputs.get("bizmodel", "")),
        ("4. RISK & MOAT ANALYSIS",       outputs.get("risks",    "")),
        ("5. VC INVESTMENT MEMO",         outputs.get("memo",     "")),
    ]

    for title, content in sections:
        if not content.strip():
            continue
        pdf.add_page()
        pdf.section_header(title)
        pdf.body_text(content)

    return bytes(pdf.output())
