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
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from kit_common import CsvValue, write_csv
from workbook_spec import headers_for

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

TAB_OPPORTUNITIES = "GSC_Opportunities"
TAB_CANNIBALIZATION = "Cannibalization"
TAB_DECAY = "Content_Decay"

TabRow = list[CsvValue]


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


def _parse_number(cell: str | None, *, default: float | None) -> float:
    """Parse a numeric cell; blank uses ``default`` (None means blank is an error)."""
    if cell is None:
        raise ValueError("missing cell")
    text = cell.strip()
    if not text:
        if default is None:
            raise ValueError("blank cell")
        return default
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def read_rows(path: str | Path) -> ReadResult:
    """Read a GSC export. Raises GscInputError for missing columns, OSError for I/O."""
    rows: list[GscRow] = []
    skipped = 0
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
                    position = _parse_number(raw[field_map["position"]], default=None)
                    if position <= 0:
                        raise ValueError("position must be >= 1")
                    rows.append(GscRow(
                        query=query.strip(),
                        page=page.strip(),
                        clicks=_parse_number(raw[field_map["clicks"]], default=0.0),
                        impressions=_parse_number(raw[field_map["impressions"]], default=0.0),
                        position=position,
                    ))
                except ValueError:
                    skipped += 1
    except UnicodeDecodeError as exc:
        raise GscInputError(f"{path}: not a UTF-8 CSV ({exc.reason})") from exc
    except csv.Error as exc:
        raise GscInputError(f"{path}: invalid CSV ({exc})") from exc
    return ReadResult(rows, skipped)


def expected_ctr(position: float) -> float:
    bucket = min(10, max(1, round(position)))
    return EXPECTED_CTR[bucket]


def opportunity_rows(rows: Sequence[GscRow]) -> list[TabRow]:
    """Striking-distance and position-adjusted low-CTR rows for GSC_Opportunities."""
    out: list[TabRow] = []
    lo, hi = STRIKING_DISTANCE
    for r in rows:
        if r.impressions < MIN_IMPRESSIONS:
            continue
        ctr = r.clicks / r.impressions
        if lo <= r.position <= hi:
            out.append([r.query, r.page, int(r.clicks), int(r.impressions),
                        f"{ctr:.2%}", round(r.position, 1),
                        "Striking distance (pos 4-15)",
                        "Add internal links, improve answer block, refresh proof", "SEO"])
        elif r.position <= 10 and ctr < expected_ctr(r.position) * CTR_UNDERPERFORM_RATIO:
            out.append([r.query, r.page, int(r.clicks), int(r.impressions),
                        f"{ctr:.2%}", round(r.position, 1),
                        "High impressions low CTR for position",
                        "Rewrite title/meta; log in Experiment_Log and judge CTR at stable position", "SEO"])
    out.sort(key=lambda row: -int(row[3] or 0))
    return out


def cannibalization_rows(rows: Sequence[GscRow]) -> list[TabRow]:
    """Queries where 2+ pages each hold a meaningful impression share."""
    by_query: defaultdict[str, list[GscRow]] = defaultdict(list)
    for r in rows:
        if r.impressions >= MIN_IMPRESSIONS / 2:
            by_query[r.query].append(r)
    out: list[TabRow] = []
    for query, group in by_query.items():
        if len(group) < 2:
            continue
        total = sum(g.impressions for g in group)
        group.sort(key=lambda g: -g.impressions)
        top, second = group[0], group[1]
        if second.impressions / total >= CANNIBAL_SHARE:
            out.append([query, top.page, second.page,
                        "Review: true duplicate / intent split / format mismatch",
                        top.page,
                        "Diagnose with Cannibalization prompt before merging", ""])
    out.sort(key=lambda row: str(row[0]))
    return out


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
            flagged.append((before.clicks - after.clicks,
                            [page, "", int(after.clicks), int(before.clicks), f"{-drop:.0%}",
                             rank_change, "High", "", "", "Refresh"]))
    flagged.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in flagged]


def write_tab(out_dir: Path, title: str, rows: Sequence[TabRow]) -> Path:
    """Write ``rows`` under the workbook headers for tab ``title``; return the file path."""
    path = out_dir / f"{title}_filled.csv"
    write_csv(path, headers_for(title), rows)
    return path


def _load(path: str) -> list[GscRow]:
    result = read_rows(path)
    if result.skipped:
        print(f"{Path(path).name}: skipped {result.skipped} malformed row(s)", file=sys.stderr)
    return result.rows


def _run(mode: str, files: Sequence[str], out_dir: Path) -> None:
    if mode in ("decay", "all"):
        prev_rows, cur_rows = _load(files[0]), _load(files[1])
    else:
        prev_rows, cur_rows = [], _load(files[0])
    out_dir.mkdir(parents=True, exist_ok=True)

    if mode in ("opportunities", "all"):
        rows = opportunity_rows(cur_rows)
        write_tab(out_dir, TAB_OPPORTUNITIES, rows)
        print(f"opportunities: {len(rows)} rows")
    if mode in ("cannibalization", "all"):
        rows = cannibalization_rows(cur_rows)
        write_tab(out_dir, TAB_CANNIBALIZATION, rows)
        print(f"cannibalization: {len(rows)} queries")
    if mode in ("decay", "all"):
        rows = decay_rows(prev_rows, cur_rows)
        write_tab(out_dir, TAB_DECAY, rows)
        print(f"decay: {len(rows)} pages flagged")


def main(argv: Sequence[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["opportunities", "cannibalization", "decay", "all"])
    ap.add_argument("files", nargs="+",
                    help="GSC export CSV(s): one file for opportunities/cannibalization; "
                         "previous then current for decay/all")
    ap.add_argument("-o", "--out-dir", "--out", dest="out", default=".",
                    help="output directory (default: current directory)")
    args = ap.parse_args(argv)

    expected = 2 if args.mode in ("decay", "all") else 1
    if len(args.files) != expected:
        ap.error(f"{args.mode} takes exactly {expected} file(s), got {len(args.files)}"
                 + (" (previous.csv current.csv)" if expected == 2 else ""))

    try:
        _run(args.mode, args.files, Path(args.out))
    except (GscInputError, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
