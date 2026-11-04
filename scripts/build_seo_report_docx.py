"""Build the Elite SEO client report template as a Word document.

The DOCX is the Word rendering of references/kit/07-client-report-template.md:
a title block followed by eleven numbered sections (paragraphs, bullet lists and
blank tables) that you fill in per client.

Usage:
    python build_seo_report_docx.py
    python build_seo_report_docx.py --out-dir some/dir

Writes elite-seo-audit-report-template.docx (default: the skill's assets/ folder).
Requires python-docx (pip install -r requirements.txt).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from kit_common import ASSETS_DIR, atomic_write

try:
    from docx import Document
    from docx.document import Document as DocumentType
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt
    from docx.table import Table
except ImportError as exc:
    raise ImportError(
        "python-docx is required to build the report template. "
        "Install it with: pip install -r requirements.txt"
    ) from exc

OUTPUT_NAME = "elite-seo-audit-report-template.docx"

PAGE_MARGIN_INCHES = 0.7
BASE_FONT_NAME = "Arial"
BASE_FONT_SIZE_PT = 10
TITLE_FONT_SIZE_PT = 20

TITLE = "Elite SEO Audit and Growth Strategy"
TITLE_FIELDS: tuple[str, ...] = (
    "Client / Site: ______________________________",
    "Prepared by: ________________________________",
    "Date: _______________________________________",
)


@dataclass(frozen=True)
class ParagraphBody:
    """A single prose paragraph."""

    text: str


@dataclass(frozen=True)
class BulletsBody:
    """A bullet list, one item per entry."""

    items: tuple[str, ...]


@dataclass(frozen=True)
class TableBody:
    """A grid table: a header row plus ``blank_rows`` empty rows."""

    headers: tuple[str, ...]
    blank_rows: int


Body = Union[ParagraphBody, BulletsBody, TableBody]


@dataclass(frozen=True)
class SectionSpec:
    """One numbered report section."""

    heading: str
    body: Body


SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec(
        "1. Executive Summary",
        ParagraphBody(
            "The site has [strengths], but organic growth is currently limited by [top blockers]. "
            "The highest-impact work is [priority 1], [priority 2], and [priority 3]. "
            "If implemented in order, the expected outcome is [traffic/conversion/risk impact] "
            "over [time horizon]."
        ),
    ),
    SectionSpec(
        "2. SEO Health Scorecard",
        TableBody(("Area", "Score / 10", "Status", "Notes"), blank_rows=7),
    ),
    SectionSpec(
        "3. What Is Working",
        BulletsBody(("[Strength 1]", "[Strength 2]", "[Strength 3]")),
    ),
    SectionSpec(
        "4. Biggest Blockers",
        TableBody(("Priority", "Issue", "Evidence", "Impact", "Owner"), blank_rows=5),
    ),
    SectionSpec(
        "5. Biggest Growth Opportunities",
        TableBody(
            ("Priority", "Opportunity", "Search surface", "Expected payoff", "Owner"),
            blank_rows=5,
        ),
    ),
    SectionSpec(
        "6. Technical Findings",
        BulletsBody(
            (
                "Crawl/indexation:",
                "Rendering/JavaScript:",
                "Sitemap/robots/canonicals:",
                "Schema:",
                "Speed/page experience:",
                "Security/spam risk:",
            )
        ),
    ),
    SectionSpec(
        "7. Content Findings",
        BulletsBody(
            (
                "Keyword and intent gaps:",
                "Cannibalization:",
                "Content decay:",
                "Topical authority:",
                "Internal links:",
                "Review/proof gaps:",
            )
        ),
    ),
    SectionSpec(
        "8. Authority and Reputation Findings",
        BulletsBody(
            (
                "Backlinks:",
                "Unlinked mentions:",
                "Digital PR opportunities:",
                "Review hub:",
                "Branded SERP:",
                "Risk issues:",
            )
        ),
    ),
    SectionSpec(
        "9. AI Search Findings",
        TableBody(
            ("Prompt type", "Current visibility", "Competitors cited", "Gap", "Action"),
            blank_rows=6,
        ),
    ),
    SectionSpec(
        "10. 30/60/90-Day Roadmap",
        TableBody(
            ("Timeframe", "Workstream", "Action", "Owner", "Success metric"),
            blank_rows=9,
        ),
    ),
    SectionSpec(
        "11. Appendix",
        BulletsBody(
            (
                "Master workbook: elite-seo-master-audit-workbook.xlsx",
                "Issue register export",
                "Keyword map export",
                "GSC export",
                "Crawl export",
                "AI visibility tracker",
                "Backlink/mention audit",
            )
        ),
    ),
)


def add_bullets(doc: DocumentType, items: Sequence[str]) -> None:
    """Append one bulleted paragraph per item."""
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_table(doc: DocumentType, headers: Sequence[str], blank_rows: int) -> Table:
    """Append a grid table with a header row and ``blank_rows`` empty rows, then a spacer."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    header_cells = table.rows[0].cells
    for cell, header in zip(header_cells, headers):
        cell.text = header
    for _ in range(blank_rows):
        for cell in table.add_row().cells:
            cell.text = ""
    doc.add_paragraph()
    return table


def add_section(doc: DocumentType, section: SectionSpec) -> None:
    """Render one section: its heading, then its body."""
    doc.add_heading(section.heading, level=1)
    body = section.body
    if isinstance(body, ParagraphBody):
        doc.add_paragraph(body.text)
    elif isinstance(body, BulletsBody):
        add_bullets(doc, body.items)
    else:
        add_table(doc, body.headers, body.blank_rows)


def setup_page_and_title(doc: DocumentType) -> None:
    """Set margins and the base font, then write the title and client fields."""
    page = doc.sections[0]
    margin = Inches(PAGE_MARGIN_INCHES)
    page.top_margin = margin
    page.bottom_margin = margin
    page.left_margin = margin
    page.right_margin = margin

    normal = doc.styles["Normal"]
    normal.font.name = BASE_FONT_NAME
    normal.font.size = Pt(BASE_FONT_SIZE_PT)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(TITLE)
    run.bold = True
    run.font.size = Pt(TITLE_FONT_SIZE_PT)
    for field in TITLE_FIELDS:
        doc.add_paragraph(field)


def build_document() -> DocumentType:
    """Assemble the full report template in memory."""
    doc = Document()
    setup_page_and_title(doc)
    for section in SECTIONS:
        add_section(doc, section)
    return doc


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Elite SEO client report DOCX template.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ASSETS_DIR,
        help="directory to write the DOCX into (default: the skill's assets/ folder)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    path: Path = args.out_dir / OUTPUT_NAME
    doc = build_document()
    try:
        atomic_write(path, lambda tmp: doc.save(str(tmp)))
    except OSError as exc:
        sys.exit(f"error: could not write {path}: {exc}")
    print(path)


if __name__ == "__main__":
    main()
