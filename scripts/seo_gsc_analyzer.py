"""GSC export analyzer for the Elite SEO Operating Kit.

Turns raw Google Search Console performance exports into pre-filled rows for the
workbook tabs GSC_Opportunities, Cannibalization, and Content_Decay. Column
headers come from workbook_spec, so the output always matches the workbook.

Input format: CSV export with columns (case-insensitive, extra columns ignored):
    query, page, clicks, impressions, ctr, position
GSC's own "Queries + Pages" export works; so does any tool export with those headers.
Rows that are short, have unparsable numbers, or have a blank/non-positive position
(GSC positions start at 1) are skipped and reported on stderr. Blank clicks or
impressions count as 0.

Decay compares two equal-length periods (previous, then current). The workbook's
Content_Decay tab labels assume 90-day windows, so export 90 days for each.

Usage:
    python seo_gsc_analyzer.py opportunities current.csv -o out_dir
    python seo_gsc_analyzer.py cannibalization current.csv -o out_dir
    python seo_gsc_analyzer.py decay previous.csv current.csv -o out_dir
    python seo_gsc_analyzer.py all previous.csv current.csv -o out_dir

opportunities/cannibalization take exactly one file; decay/all take exactly two.

No third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

from kit_common import CellValue, write_csv
from workbook_spec import (
    TAB_CANNIBALIZATION,
    TAB_CONTENT_DECAY,
    TAB_GSC_OPPORTUNITIES,
    headers_for,
)

# Rough expected CTR by position bucket (industry-typical medians; used only to
# flag underperformers, never reported as a benchmark to clients).
EXPECTED_CTR: dict[int, float] = {1: 0.28, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
                                  6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.018}

MIN_IMPRESSIONS = 100          # ignore noise rows
STRIKING_DISTANCE: tuple[float, float] = (4.0, 15.0)
CTR_UNDERPERFORM_RATIO = 0.5   # flag if CTR < 50% of position-expected
CANNIBAL_SHARE = 0.20          # 2nd page needs >=20% of query impressions
DECAY_DROP = 0.20              # >=20% click drop flags decay
DECAY_MIN_PREV_CLICKS = 10     # too few previous clicks to judge decay

REQUIRED_COLUMNS: tuple[str, ...] = ("query", "page", "clicks", "impressions", "position")

MAX_PROBLEM_EXAMPLES = 5       # skipped-row reasons kept per file

Mode = Literal["opportunities", "cannibalization", "decay", "all"]

# One workbook row keyed by column header; columns the analyzer leaves blank are omitted.
TabRow = dict[str, CellValue]


class GscInputError(ValueError):
    """The GSC export is unusable (missing columns, undecodable file)."""


@dataclass(frozen=True)
class GscRow:
    query: str
    page: str
    clicks: float
    impressions: float
    position: float


@dataclass(frozen=True)
class ReadResult:
    rows: list[GscRow]
    skipped: int  # malformed rows that were dropped
    # First few skipped rows as (CSV file line number, reason); the header is line 1.
    problems: tuple[tuple[int, str], ...] = ()


@dataclass
class PageTotals:
    """Per-page aggregate over one period."""

    clicks: float = 0.0
    impressions: float = 0.0
    position_weighted_sum: float = 0.0  # sum of position * impressions

    def add(self, row: GscRow) -> None:
        self.clicks += row.clicks
        self.impressions += row.impressions
        self.position_weighted_sum += row.position * row.impressions

    @property
    def average_position(self) -> float:
        """Impression-weighted average position (0.0 when there are no impressions)."""
        return self.position_weighted_sum / self.impressions if self.impressions else 0.0


def _parse_number(cell: str | None, column: str, *, default: float | None) -> float:
    """Parse a numeric cell; blank uses ``default`` (None means blank is an error).

    Raises ValueError with a message naming ``column`` and the offending value.
    """
    if cell is None:
        raise ValueError(f"missing {column}")
    text = cell.strip()
    if not text:
        if default is None:
            raise ValueError(f"blank {column}")
        return default
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"unparsable number {text!r} in {column}") from None
    if not math.isfinite(value):
        raise ValueError(f"non-finite number {text!r} in {column}")
    return value


def read_rows(path: str | Path) -> ReadResult:
    """Read a GSC export. Raises GscInputError for missing columns, OSError for I/O."""
    rows: list[GscRow] = []
    skipped = 0
    problems: list[tuple[int, str]] = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            field_map = {name.strip().lower(): name for name in reader.fieldnames or []}
            missing = [c for c in REQUIRED_COLUMNS if c not in field_map]
            if missing:
                raise GscInputError(f"{path}: missing columns {missing}. Found: {reader.fieldnames}")
            for raw in reader:
                try:
                    query, page = raw[field_map["query"]], raw[field_map["page"]]
                    if query is None or page is None:
                        raise ValueError("short row")
                    position = _parse_number(raw[field_map["position"]], "position", default=None)
                    if position <= 0:
                        raise ValueError("position must be >= 1")
                    rows.append(GscRow(
                        query=query.strip(),
                        page=page.strip(),
                        clicks=_parse_number(raw[field_map["clicks"]], "clicks", default=0.0),
                        impressions=_parse_number(raw[field_map["impressions"]], "impressions", default=0.0),
                        position=position,
                    ))
                except ValueError as exc:
                    skipped += 1
                    if len(problems) < MAX_PROBLEM_EXAMPLES:
                        problems.append((reader.line_num, str(exc)))
    except UnicodeDecodeError as exc:
        raise GscInputError(f"{path}: not a UTF-8 CSV ({exc.reason})") from exc
    except csv.Error as exc:
        raise GscInputError(f"{path}: invalid CSV ({exc})") from exc
    return ReadResult(rows, skipped, tuple(problems))


def expected_ctr(position: float) -> float:
    bucket = min(10, max(1, round(position)))
    return EXPECTED_CTR[bucket]


def opportunity_rows(rows: Sequence[GscRow]) -> list[TabRow]:
    """Striking-distance and position-adjusted low-CTR rows for GSC_Opportunities."""
    found: list[tuple[int, TabRow]] = []
    lo, hi = STRIKING_DISTANCE
    striking_label = f"Striking distance (pos {lo:g}-{hi:g})"
    for r in rows:
        if r.impressions < MIN_IMPRESSIONS:
            continue
        ctr = r.clicks / r.impressions
        if lo <= r.position <= hi:
            opportunity, action = (striking_label,
                                   "Add internal links, improve answer block, refresh proof")
        # Low-CTR flagging covers positions above (better than) striking distance;
        # striking-distance rows are already reported by the branch above.
        elif r.position < lo and ctr < expected_ctr(r.position) * CTR_UNDERPERFORM_RATIO:
            opportunity, action = ("High impressions low CTR for position",
                                   "Rewrite title/meta; log in Experiment_Log and judge CTR at stable position")
        else:
            continue
        found.append((int(r.impressions), {
            "Query": r.query, "Page": r.page,
            "Clicks": int(r.clicks), "Impressions": int(r.impressions),
            "CTR": f"{ctr:.2%}", "Position": round(r.position, 1),
            "Opportunity Type": opportunity, "Action": action, "Owner": "SEO",
        }))
    found.sort(key=lambda item: -item[0])
    return [row for _, row in found]


def cannibalization_rows(rows: Sequence[GscRow]) -> list[TabRow]:
    """Queries where 2+ pages each hold a meaningful impression share."""
    by_query: defaultdict[str, list[GscRow]] = defaultdict(list)
    for r in rows:
        if r.impressions >= MIN_IMPRESSIONS / 2:
            by_query[r.query].append(r)
    found: list[tuple[str, TabRow]] = []
    for query, group in by_query.items():
        if len(group) < 2:
            continue
        total = sum(g.impressions for g in group)
        group.sort(key=lambda g: -g.impressions)
        top, second = group[0], group[1]
        if second.impressions / total >= CANNIBAL_SHARE:
            found.append((query, {
                "Keyword / Intent": query, "URL 1": top.page, "URL 2": second.page,
                "Conflict Type": "Review: true duplicate / intent split / format mismatch",
                "Winning URL": top.page,
                "Decision": "Diagnose with Cannibalization prompt before merging",
            }))
    found.sort(key=lambda item: item[0])
    return [row for _, row in found]


def _totals_by_page(rows: Sequence[GscRow]) -> dict[str, PageTotals]:
    totals: defaultdict[str, PageTotals] = defaultdict(PageTotals)
    for r in rows:
        totals[r.page].add(r)
    return totals


def decay_rows(prev_rows: Sequence[GscRow], cur_rows: Sequence[GscRow]) -> list[TabRow]:
    """Pages losing >=20% clicks period-over-period, for Content_Decay."""
    prev, cur = _totals_by_page(prev_rows), _totals_by_page(cur_rows)
    flagged: list[tuple[float, TabRow]] = []
    for page, before in prev.items():
        if before.clicks < DECAY_MIN_PREV_CLICKS:
            continue
        after = cur.get(page, PageTotals())
        drop = (before.clicks - after.clicks) / before.clicks
        if drop >= DECAY_DROP:
            if after.impressions > 0:
                rank_change = f"{before.average_position:.1f} -> {after.average_position:.1f}"
            else:
                rank_change = "dropped out"
            flagged.append((before.clicks - after.clicks, {
                "URL": page, "Clicks 90d": int(after.clicks),
                "Clicks Previous 90d": int(before.clicks), "Delta": f"{-drop:.0%}",
                "Rank Change": rank_change, "Freshness Need": "High", "Action": "Refresh",
            }))
    flagged.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in flagged]


def write_tab(out_dir: Path, title: str, rows: Sequence[Mapping[str, CellValue]]) -> Path:
    """Write ``rows`` under the workbook headers for tab ``title``; return the file path.

    Each row maps header name to value; headers a row omits are written blank. A key
    that is not a header of the tab raises ValueError.
    """
    headers = headers_for(title)
    known = set(headers)
    for row in rows:
        unknown = [key for key in row if key not in known]
        if unknown:
            raise ValueError(f"{title}: unknown column(s) {unknown}; headers are {headers}")
    path = out_dir / f"{title}_filled.csv"
    write_csv(path, headers, [[row.get(h, "") for h in headers] for row in rows])
    return path


def _load(path: str) -> list[GscRow]:
    result = read_rows(path)
    if result.skipped:
        print(f"{Path(path).name}: skipped {result.skipped} malformed row(s)", file=sys.stderr)
        for line_number, reason in result.problems:
            print(f"  line {line_number}: {reason}", file=sys.stderr)
    return result.rows


def generate_tabs(mode: Mode, files: Sequence[str], out_dir: Path) -> None:
    """Read the export(s) and write the filled CSV tab(s) selected by ``mode``."""
    if mode in ("decay", "all"):
        prev_rows, cur_rows = _load(files[0]), _load(files[1])
    else:
        prev_rows, cur_rows = [], _load(files[0])
    out_dir.mkdir(parents=True, exist_ok=True)

    if mode in ("opportunities", "all"):
        rows = opportunity_rows(cur_rows)
        write_tab(out_dir, TAB_GSC_OPPORTUNITIES, rows)
        print(f"opportunities: {len(rows)} rows")
    if mode in ("cannibalization", "all"):
        rows = cannibalization_rows(cur_rows)
        write_tab(out_dir, TAB_CANNIBALIZATION, rows)
        print(f"cannibalization: {len(rows)} queries")
    if mode in ("decay", "all"):
        rows = decay_rows(prev_rows, cur_rows)
        write_tab(out_dir, TAB_CONTENT_DECAY, rows)
        print(f"decay: {len(rows)} pages flagged")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse and validate the command line (argparse exits with 2 on usage errors)."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=get_args(Mode))
    ap.add_argument("files", nargs="+",
                    help="GSC export CSV(s): one file for opportunities/cannibalization; "
                         "previous then current for decay/all")
    ap.add_argument("-o", "--out-dir", dest="out_dir", type=Path, default=Path("."),
                    help="output directory (default: current directory)")
    ap.add_argument("--out", dest="out_dir", type=Path, help=argparse.SUPPRESS)  # deprecated alias
    args = ap.parse_args(argv)

    expected = 2 if args.mode in ("decay", "all") else 1
    if len(args.files) != expected:
        ap.error(f"{args.mode} takes exactly {expected} file(s), got {len(args.files)}"
                 + (" (previous.csv current.csv)" if expected == 2 else ""))
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point; returns the process exit code."""
    args = parse_args(argv)
    try:
        generate_tabs(args.mode, args.files, args.out_dir)
    except (GscInputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
