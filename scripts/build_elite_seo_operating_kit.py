"""Build the Elite SEO Operating Kit spreadsheet assets.

Renders the tab definitions in workbook_spec.py into the master audit workbook
(elite-seo-master-audit-workbook.xlsx) and one CSV template per tab. The SOP
markdown under references/kit/ is hand-edited and is not generated here.

Usage:
    python build_elite_seo_operating_kit.py
    python build_elite_seo_operating_kit.py --out-dir /path/to/assets

Outputs (under --out-dir, default: the skill's assets/ folder):
    elite-seo-master-audit-workbook.xlsx
    csv-templates/<Tab>.csv

Requires openpyxl: pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

# A missing dependency is reported by main() as a one-line error rather than a traceback.
MISSING_DEPENDENCY: str | None = None
try:
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.worksheet.worksheet import Worksheet
except ImportError:
    MISSING_DEPENDENCY = "openpyxl is not installed; run: pip install -r requirements.txt"

from kit_common import ASSETS_DIR, CellValue, atomic_write, write_csv
from workbook_spec import LAST_DATA_ROW, SHEETS, SheetSpec, column_letter

WORKBOOK_NAME = "elite-seo-master-audit-workbook.xlsx"
CSV_SUBDIR = "csv-templates"
TEMPLATE_LINE_ENDING = "\n"  # the committed CSV templates use LF

BLUE = "1F4E79"
LIGHT_BLUE = "D9EAF7"
GREEN = "E2F0D9"
YELLOW = "FFF2CC"
RED = "F4CCCC"
GRAY = "E7E6E6"
WHITE = "FFFFFF"
BLACK = "000000"

FILL_COLORS: dict[str, str] = {"red": RED, "yellow": YELLOW, "green": GREEN}


def style_sheet(ws: Worksheet) -> None:
    """Apply header styling, borders, freeze pane, auto-filter, and column widths."""
    header_fill = PatternFill("solid", fgColor=BLUE)
    header_font = Font(color=WHITE, bold=True)
    thin = Side(border_style="thin", color="D9D9D9")
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for column_cells in ws.columns:
        col_letter = get_column_letter(column_cells[0].column)
        max_len = 12
        for cell in column_cells:
            if cell.value is not None:
                max_len = max(max_len, min(len(str(cell.value)) + 2, 48))
        ws.column_dimensions[col_letter].width = max_len


def add_list_validation(
    ws: Worksheet, col: str, values: Sequence[str], start_row: int = 2, end_row: int = LAST_DATA_ROW
) -> None:
    """Add a dropdown list validation on ``col`` rows start_row..end_row."""
    formula = '"' + ",".join(values) + '"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}{start_row}:{col}{end_row}")


def apply_validations(ws: Worksheet, spec: SheetSpec) -> None:
    """Add the spec's dropdowns, resolving column letters from header names."""
    for validation in spec.validations:
        for header in validation.headers:
            add_list_validation(ws, column_letter(spec.title, header), validation.values)


def apply_fills(ws: Worksheet, spec: SheetSpec) -> None:
    """Write fill-down formulas (after styling, so these cells stay unstyled as before)."""
    for fill in spec.fills:
        letter = column_letter(spec.title, fill.header)
        for row in range(fill.first_row, fill.last_row + 1):
            ws[f"{letter}{row}"] = fill.template.replace("{row}", str(row))


def apply_conditional_formatting(ws: Worksheet, spec: SheetSpec) -> None:
    """Add the spec's conditional fills on their header columns."""
    for rule in spec.conditional:
        letter = column_letter(spec.title, rule.header)
        formula = rule.template.replace("{col}", letter).replace("{first}", str(rule.first_row))
        cell_range = f"{letter}{rule.first_row}:{letter}{rule.last_row}"
        fill = PatternFill("solid", fgColor=FILL_COLORS[rule.fill])
        ws.conditional_formatting.add(cell_range, FormulaRule(formula=[formula], fill=fill))


def render_sheet(wb: Workbook, spec: SheetSpec) -> Worksheet:
    """Create the tab for ``spec`` in ``wb`` with data, styling, validations and rules."""
    ws = wb.create_sheet(spec.title)
    ws.append(list(spec.headers))
    for row in spec.rows:
        ws.append(list(row))
    style_sheet(ws)
    for header, width in spec.widths:
        ws.column_dimensions[column_letter(spec.title, header)].width = width
    apply_fills(ws, spec)
    apply_validations(ws, spec)
    apply_conditional_formatting(ws, spec)
    return ws


def build_workbook(specs: Sequence[SheetSpec] = SHEETS) -> Workbook:
    """Render every spec, in order, into a new in-memory workbook."""
    wb = Workbook()
    wb.remove(wb.active)
    for spec in specs:
        render_sheet(wb, spec)
    return wb


def export_csvs(wb: Workbook, csv_dir: Path) -> list[Path]:
    """Write one CSV per tab of the in-memory workbook and return the written paths."""
    paths: list[Path] = []
    for ws in wb.worksheets:
        rows: list[tuple[CellValue, ...]] = list(ws.iter_rows(values_only=True))
        path = csv_dir / f"{ws.title}.csv"
        write_csv(path, rows[0], rows[1:], lineterminator=TEMPLATE_LINE_ENDING)
        paths.append(path)
    return paths


def build_kit(out_dir: Path) -> tuple[Path, Path]:
    """Build the workbook and CSV templates under ``out_dir``; return (workbook, csv_dir)."""
    wb = build_workbook()
    workbook_path = out_dir / WORKBOOK_NAME
    atomic_write(workbook_path, lambda tmp: wb.save(tmp))
    csv_dir = out_dir / CSV_SUBDIR
    export_csvs(wb, csv_dir)
    return workbook_path, csv_dir


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build the Elite SEO Operating Kit workbook and CSV templates.")
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=ASSETS_DIR,
        help="output directory (default: the skill's assets/ folder); CSVs go to <out-dir>/csv-templates/",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point; returns the process exit code."""
    args = parse_args(argv)
    if MISSING_DEPENDENCY:
        print(f"error: {MISSING_DEPENDENCY}", file=sys.stderr)
        return 1
    try:
        workbook_path, csv_dir = build_kit(args.out_dir)
    except OSError as exc:
        print(f"error: could not write the kit to {args.out_dir}: {exc}", file=sys.stderr)
        return 1
    print(f"Created kit at {args.out_dir}")
    print(f"Workbook: {workbook_path}")
    print(f"CSV templates: {csv_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
