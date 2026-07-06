from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


# Portable: output lands in the skill's assets folder.
SKILL_ROOT = Path(__file__).resolve().parent.parent
OUT = SKILL_ROOT / "assets"


def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_table(doc, headers, rows=3):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr[i].text = header
    for _ in range(rows):
        cells = table.add_row().cells
        for i in range(len(headers)):
            cells[i].text = ""
    doc.add_paragraph()
    return table


def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Elite SEO Audit and Growth Strategy")
    run.bold = True
    run.font.size = Pt(20)
    doc.add_paragraph("Client / Site: ______________________________")
    doc.add_paragraph("Prepared by: ________________________________")
    doc.add_paragraph("Date: _______________________________________")

    add_heading(doc, "1. Executive Summary")
    doc.add_paragraph(
        "The site has [strengths], but organic growth is currently limited by [top blockers]. "
        "The highest-impact work is [priority 1], [priority 2], and [priority 3]. "
        "If implemented in order, the expected outcome is [traffic/conversion/risk impact] over [time horizon]."
    )

    add_heading(doc, "2. SEO Health Scorecard")
    add_table(doc, ["Area", "Score / 10", "Status", "Notes"], rows=7)

    add_heading(doc, "3. What Is Working")
    add_bullets(doc, ["[Strength 1]", "[Strength 2]", "[Strength 3]"])

    add_heading(doc, "4. Biggest Blockers")
    add_table(doc, ["Priority", "Issue", "Evidence", "Impact", "Owner"], rows=5)

    add_heading(doc, "5. Biggest Growth Opportunities")
    add_table(doc, ["Priority", "Opportunity", "Search surface", "Expected payoff", "Owner"], rows=5)

    add_heading(doc, "6. Technical Findings")
    add_bullets(
        doc,
        [
            "Crawl/indexation:",
            "Rendering/JavaScript:",
            "Sitemap/robots/canonicals:",
            "Schema:",
            "Speed/page experience:",
            "Security/spam risk:",
        ],
    )

    add_heading(doc, "7. Content Findings")
    add_bullets(
        doc,
        [
            "Keyword and intent gaps:",
            "Cannibalization:",
            "Content decay:",
            "Topical authority:",
            "Internal links:",
            "Review/proof gaps:",
        ],
    )

    add_heading(doc, "8. Authority and Reputation Findings")
    add_bullets(
        doc,
        [
            "Backlinks:",
            "Unlinked mentions:",
            "Digital PR opportunities:",
            "Review hub:",
            "Branded SERP:",
            "Risk issues:",
        ],
    )

    add_heading(doc, "9. AI Search Findings")
    add_table(doc, ["Prompt type", "Current visibility", "Competitors cited", "Gap", "Action"], rows=6)

    add_heading(doc, "10. 30/60/90-Day Roadmap")
    add_table(doc, ["Timeframe", "Workstream", "Action", "Owner", "Success metric"], rows=9)

    add_heading(doc, "11. Appendix")
    add_bullets(
        doc,
        [
            "Master workbook: elite-seo-master-audit-workbook.xlsx",
            "Issue register export",
            "Keyword map export",
            "GSC export",
            "Crawl export",
            "AI visibility tracker",
            "Backlink/mention audit",
        ],
    )

    doc.save(OUT / "elite-seo-audit-report-template.docx")
    print(OUT / "elite-seo-audit-report-template.docx")


if __name__ == "__main__":
    main()
