"""GSC export analyzer for the Elite SEO Operating Kit.

Turns raw Google Search Console performance exports into pre-filled rows for the
workbook tabs GSC_Opportunities, Cannibalization, Content_Decay, Edit_Queue, and
Edit_Measurement. Column headers come from workbook_spec, so the output always
matches the workbook.

Input format: CSV export with columns (case-insensitive, extra columns ignored):
    query, page, clicks, impressions, ctr, position
GSC's own "Queries + Pages" export works; so does any tool export with those headers.
A Pages-only export (no query column) works for every mode except cannibalization,
which needs the query column.
Rows that are short, have unparsable numbers, or have a blank/non-positive position
(GSC positions start at 1) are skipped and reported on stderr. Blank clicks or
impressions count as 0.

Decay and queue compare two equal-length periods (previous, then current). The
workbook's Content_Decay tab labels assume 90-day windows, so export 90 days for each.

Usage:
    python seo_gsc_analyzer.py opportunities current.csv -o out_dir
    python seo_gsc_analyzer.py cannibalization current.csv -o out_dir
    python seo_gsc_analyzer.py decay previous.csv current.csv -o out_dir
    python seo_gsc_analyzer.py all previous.csv current.csv -o out_dir

    # One ranked work queue: every page scored three ways, biggest lever wins
    # and names the fix type. "all" writes this queue too.
    python seo_gsc_analyzer.py queue previous.csv current.csv -o out_dir

    # Measurement with a control group.
    python seo_gsc_analyzer.py snapshot current.csv --url URL --change-type ctr \\
        --date 2026-08-26 --ledger out_dir/Edit_Measurement_filled.csv
    python seo_gsc_analyzer.py measure current.csv --checkpoint d28 \\
        --ledger out_dir/Edit_Measurement_filled.csv

decay/all/queue take exactly two files; every other mode takes exactly one.
snapshot/measure update the ledger (default <out_dir>/Edit_Measurement_filled.csv).

No third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal, cast, get_args

from kit_common import CellValue, write_csv
from workbook_spec import (
    TAB_CANNIBALIZATION,
    TAB_CONTENT_DECAY,
    TAB_EDIT_MEASUREMENT,
    TAB_EDIT_QUEUE,
    TAB_GSC_OPPORTUNITIES,
    headers_for,
)

# Rough expected CTR by position bucket (industry-typical medians; used only to
# flag underperformers, never reported as a benchmark to clients).
EXPECTED_CTR: dict[int, float] = {
    1: 0.28,
    2: 0.15,
    3: 0.10,
    4: 0.07,
    5: 0.05,
    6: 0.04,
    7: 0.03,
    8: 0.025,
    9: 0.02,
    10: 0.018,
}

MIN_IMPRESSIONS = 100  # ignore noise rows
STRIKING_DISTANCE: tuple[float, float] = (4.0, 15.0)
CTR_UNDERPERFORM_RATIO = 0.5  # flag if CTR < 50% of position-expected
CANNIBAL_SHARE = 0.20  # 2nd page needs >=20% of query impressions
DECAY_DROP = 0.20  # >=20% click drop flags decay
DECAY_MIN_PREV_CLICKS = 10  # too few previous clicks to judge decay
PAGE_ONE_POSITION = 10  # bottom of page one, used for the rank lever

CHECKPOINT_DAYS: dict[str, int] = {"d28": 28, "d56": 56}
DATE_FORMAT = "%Y-%m-%d"

# query is optional: a Pages-only export has no query column (cannibalization needs it).
REQUIRED_COLUMNS: tuple[str, ...] = ("page", "clicks", "impressions", "position")

MAX_PROBLEM_EXAMPLES = 5  # skipped-row reasons kept per file

Mode = Literal["opportunities", "cannibalization", "decay", "all", "queue", "snapshot", "measure"]

# Modes that compare two periods and so need a previous-period export; every other mode
# takes the current export alone. The single source of truth for mode-to-file arity.
NEEDS_PREVIOUS: frozenset[Mode] = frozenset({"decay", "all", "queue"})

# One workbook row keyed by column header; columns the analyzer leaves blank are omitted.
TabRow = dict[str, CellValue]


class GscInputError(Exception):
    """The run cannot proceed: unusable export (missing columns, undecodable file) or bad arguments.

    Deliberately not a ValueError: read_rows catches ValueError per row, and file-level
    failures must never be mistaken for a skippable malformed row.
    """


@dataclass(frozen=True)
class GscRow:
    """One parsed GSC export row."""

    query: str  # "" when the export has no query column
    page: str
    clicks: float
    impressions: float
    position: float


@dataclass(frozen=True)
class ReadResult:
    """Parsed rows plus a count and sample of the rows that were skipped."""

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

    @property
    def ctr(self) -> float:
        """Click-through rate (0.0 when there are no impressions)."""
        return self.clicks / self.impressions if self.impressions else 0.0


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


def _parse_row(raw: Mapping[str, str | None], field_map: Mapping[str, str]) -> GscRow:
    """Build a GscRow from one DictReader row; raises ValueError with the skip reason."""
    query = raw[field_map["query"]] if "query" in field_map else ""
    page = raw[field_map["page"]]
    if query is None or page is None:
        raise ValueError("short row")
    position = _parse_number(raw[field_map["position"]], "position", default=None)
    if position <= 0:
        raise ValueError("position must be >= 1")
    return GscRow(
        query=query.strip(),
        page=page.strip(),
        clicks=_parse_number(raw[field_map["clicks"]], "clicks", default=0.0),
        impressions=_parse_number(raw[field_map["impressions"]], "impressions", default=0.0),
        position=position,
    )


def read_rows(path: Path) -> ReadResult:
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
                    rows.append(_parse_row(raw, field_map))
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
    """Expected CTR for the position bucket (positions clamp to 1-10)."""
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
    # GSC exports split by device/country repeat (query, page); sum them first so a
    # page is never reported as conflicting with itself.
    impressions: defaultdict[str, dict[str, float]] = defaultdict(dict)
    for r in rows:
        pages = impressions[r.query]
        pages[r.page] = pages.get(r.page, 0.0) + r.impressions
    found: list[tuple[str, TabRow]] = []
    for query, pages in impressions.items():
        group = [(page, imp) for page, imp in pages.items() if imp >= MIN_IMPRESSIONS / 2]
        if len(group) < 2:
            continue
        total = sum(imp for _, imp in group)
        group.sort(key=lambda item: -item[1])
        (top_page, _), (second_page, second_imp) = group[0], group[1]
        if second_imp / total >= CANNIBAL_SHARE:
            found.append((query, {
                "Keyword / Intent": query, "URL 1": top_page, "URL 2": second_page,
                "Conflict Type": "Review: true duplicate / intent split / format mismatch",
                "Winning URL": top_page,
                "Decision": "Diagnose with Cannibalization prompt before merging",
            }))
    found.sort(key=lambda item: item[0])
    return [row for _, row in found]


def _totals_by_page(rows: Sequence[GscRow]) -> dict[str, PageTotals]:
    """Aggregate rows into per-page totals."""
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


# --------------------------------------------------------------------------
# Edit queue: one list, three levers, biggest lever names the fix.
# --------------------------------------------------------------------------

Lever = Literal["recover", "ctr", "rank"]

FIX_FOR_LEVER: dict[Lever, tuple[str, str]] = {
    "recover": ("Regression repair",
                "Find what changed: lost links, SERP feature, refreshed competitor. Restore or rewrite."),
    "ctr": ("Title / description rewrite",
            "Rewrite title and meta description only. Log in Experiment_Log and judge CTR at a stable position."),
    "rank": ("Content push to page one",
             "Deepen the answer, add internal links from strong pages, refresh proof and dates."),
}


@dataclass(frozen=True)
class LeverScores:
    """Three estimates of recoverable clicks for one page, plus the inputs behind them."""

    recover: float
    ctr: float
    rank: float
    real_loss: bool
    position: float
    actual_ctr: float
    impressions: float

    def estimate(self, lever: Lever) -> float:
        return {"recover": self.recover, "ctr": self.ctr, "rank": self.rank}[lever]


def score_levers(before: PageTotals, after: PageTotals) -> LeverScores:
    """Three estimates of recoverable clicks for one page.

    recover: clicks genuinely lost against the previous window (a regression).
    ctr: page-one clicks the page did not earn for the position it holds.
    rank: clicks a page-two result would gain by landing on page one.

    Every number is an estimate in clicks, so the three are comparable. They are
    soft: GSC average position blends every query a page ranks for, so the ctr
    and rank levers over-count. Use them to ORDER the queue, never as a forecast.
    """
    position, actual = after.average_position, after.ctr

    # recover: only a real loss counts, on both an absolute and a proportional test.
    recover, real_loss = 0.0, False
    if before.clicks >= DECAY_MIN_PREV_CLICKS:
        drop = (before.clicks - after.clicks) / before.clicks
        if drop >= DECAY_DROP:
            recover, real_loss = before.clicks - after.clicks, True

    # ctr: already on page one but under-clicked for its position.
    ctr_gap = 0.0
    if 0 < position <= PAGE_ONE_POSITION:
        ctr_gap = max(0.0, expected_ctr(position) - actual) * after.impressions

    # rank: on page two, within reach of page one.
    rank_gain = 0.0
    if PAGE_ONE_POSITION < position <= STRIKING_DISTANCE[1]:
        rank_gain = max(0.0, EXPECTED_CTR[PAGE_ONE_POSITION] - actual) * after.impressions

    return LeverScores(recover, ctr_gap, rank_gain, real_loss, position, actual, after.impressions)


def edit_queue_rows(prev_rows: Sequence[GscRow], cur_rows: Sequence[GscRow]) -> tuple[list[TabRow], int]:
    """Every page scored three ways, one ranked Edit_Queue; also returns the low-visibility count."""
    prev, cur = _totals_by_page(prev_rows), _totals_by_page(cur_rows)
    levers: tuple[Lever, ...] = get_args(Lever)

    scored: list[tuple[str, Lever, LeverScores, PageTotals, PageTotals]] = []
    low_visibility = 0
    for page, after in cur.items():
        # Guardrail 1: no edit fixes "nobody is searching for this".
        if after.impressions < MIN_IMPRESSIONS:
            low_visibility += 1
            continue
        before = prev.get(page, PageTotals())
        s = score_levers(before, after)
        lever = max(levers, key=s.estimate)  # ties go to the first lever, as listed
        if s.estimate(lever) <= 0:
            continue
        scored.append((page, lever, s, before, after))

    # Guardrail 2: a real click loss outranks any estimate, whatever its size.
    scored.sort(key=lambda item: (item[2].real_loss, item[2].estimate(item[1])), reverse=True)

    out: list[TabRow] = []
    for rank, (page, lever, s, before, after) in enumerate(scored, start=1):
        fix_type, action = FIX_FOR_LEVER[lever]
        out.append({
            "Rank": rank, "URL": page, "Winning Lever": lever, "Fix Type": fix_type,
            "Est. Recoverable Clicks": round(s.estimate(lever)),
            "Real Click Loss?": "Yes" if s.real_loss else "No",
            "Clicks (current)": int(after.clicks), "Clicks (previous)": int(before.clicks),
            "Impressions (current)": int(s.impressions), "Position": round(s.position, 1),
            "Actual CTR": f"{s.actual_ctr:.2%}",
            "Expected CTR": f"{expected_ctr(s.position):.2%}" if s.position else "",
            "Recover Est.": round(s.recover), "CTR Est.": round(s.ctr), "Rank Est.": round(s.rank),
            "Action": action, "Status": "Open",
        })
    return out, low_visibility


# --------------------------------------------------------------------------
# Measurement with a control group.
# --------------------------------------------------------------------------

LedgerRecord = dict[str, CellValue]


def make_edit_id(url: str, change_type: str, change_date: str) -> str:
    """Stable id for one edit, so re-running a snapshot updates rather than duplicates."""
    seed = f"{change_date}|{url}|{change_type}".encode()
    return hashlib.sha1(seed).hexdigest()[:10]


def read_ledger(path: Path) -> list[LedgerRecord]:
    """Ledger rows keyed by header; an absent ledger reads as empty."""
    if not path.exists():
        return []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return [dict(rec) for rec in csv.DictReader(f)]
    except UnicodeDecodeError as exc:
        raise GscInputError(f"{path}: not a UTF-8 CSV ({exc.reason})") from exc
    except csv.Error as exc:
        raise GscInputError(f"{path}: invalid CSV ({exc})") from exc


def write_ledger(path: Path, records: Sequence[LedgerRecord]) -> None:
    """Atomically write the ledger under the Edit_Measurement headers."""
    headers = headers_for(TAB_EDIT_MEASUREMENT)
    write_csv(path, headers, [[rec.get(h, "") for h in headers] for rec in records])


def site_totals(rows: Sequence[GscRow]) -> PageTotals:
    """Totals across every row in the export.

    This is the control group. It is the total of THIS export, not a true
    property-wide total, because GSC caps export rows. The control is only valid
    when the baseline and the checkpoint export are pulled the same way (same
    property, same filters, same row limit).
    """
    totals = PageTotals()
    for r in rows:
        totals.add(r)
    return totals


def pct_delta(now: float, before: float) -> float | None:
    """Percent change from ``before`` to ``now``; None when there is no positive baseline."""
    if before <= 0:
        return None
    return (now - before) / before * 100.0


def fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value:+.1f}%"


@dataclass(frozen=True)
class SnapshotResult:
    added: int
    updated: int
    missing: tuple[str, ...]  # requested URLs absent from the export


def snapshot(rows: Sequence[GscRow], urls: Sequence[str], change_type: str, change_date: str,
             window_label: str, ledger_path: Path) -> SnapshotResult:
    """Record the before-numbers for an edit, plus the control for the same dates."""
    pages = _totals_by_page(rows)
    site = site_totals(rows)

    records = read_ledger(ledger_path)
    index = {str(rec.get("Edit ID", "")): rec for rec in records}
    added, updated, missing = 0, 0, []

    for url in urls:
        page = pages.get(url)
        if page is None:
            missing.append(url)
            continue
        edit_id = make_edit_id(url, change_type, change_date)
        rec: LedgerRecord = {
            "Edit ID": edit_id, "URL": url, "Change Type": change_type,
            "Change Date": change_date, "Baseline Window": window_label,
            "Base Page Clicks": int(page.clicks),
            "Base Page Impressions": int(page.impressions),
            "Base Page CTR": f"{page.ctr:.2%}",
            "Base Page Position": round(page.average_position, 1),
            "Base Site Clicks": int(site.clicks),
            "Base Site Impressions": int(site.impressions),
            "Base Site CTR": f"{site.ctr:.2%}",
            "Base Site Position": round(site.average_position, 1),
            "Status": "baseline captured",
            "Notes": "Control = totals of this export. Pull later exports the same way.",
        }
        if edit_id in index:
            index[edit_id].update(rec)
            updated += 1
        else:
            records.append(rec)
            index[edit_id] = rec
            added += 1

    write_ledger(ledger_path, records)
    return SnapshotResult(added, updated, tuple(missing))


@dataclass(frozen=True)
class MeasureResult:
    filled: int
    not_due: int
    already: int
    missing: tuple[str, ...]  # "URL (reason)" for records that could not be read


def _baseline_clicks(rec: LedgerRecord, header: str) -> float:
    """A ledger baseline number; blank is 0. Raises ValueError when unparsable."""
    return float(str(rec.get(header) or 0))


def measure(rows: Sequence[GscRow], checkpoint: str, as_of: date, ledger_path: Path) -> MeasureResult:
    """Re-read a page and its control at +28 or +56 days, then compare the two."""
    days = CHECKPOINT_DAYS[checkpoint]
    pages = _totals_by_page(rows)
    site = site_totals(rows)

    records = read_ledger(ledger_path)
    if not records:
        raise GscInputError(f"{ledger_path}: no snapshots to measure. Run 'snapshot' first.")

    filled, not_due, already, missing = 0, 0, 0, []
    for rec in records:
        url = str(rec.get("URL") or "?")
        if rec.get(f"{checkpoint} Read Date"):
            already += 1
            continue
        try:
            change = datetime.strptime(str(rec.get("Change Date") or ""), DATE_FORMAT).date()
        except ValueError:
            missing.append(f"{url} (bad Change Date)")
            continue
        if change + timedelta(days=days) > as_of:
            not_due += 1
            continue

        page = pages.get(url)
        if page is None:
            missing.append(f"{url} (not in this export)")
            continue
        try:
            base_page = _baseline_clicks(rec, "Base Page Clicks")
            base_site = _baseline_clicks(rec, "Base Site Clicks")
        except ValueError:
            missing.append(f"{url} (bad baseline clicks)")
            continue

        page_pct = pct_delta(page.clicks, base_page)
        site_pct = pct_delta(site.clicks, base_site)
        lift = None if (page_pct is None or site_pct is None) else page_pct - site_pct

        rec[f"{checkpoint} Read Date"] = as_of.isoformat()
        rec[f"{checkpoint} Page Clicks"] = int(page.clicks)
        rec[f"{checkpoint} Page Impressions"] = int(page.impressions)
        rec[f"{checkpoint} Page Position"] = round(page.average_position, 1)
        rec[f"{checkpoint} Site Clicks"] = int(site.clicks)
        rec[f"{checkpoint} Page Delta %"] = fmt_pct(page_pct)
        rec[f"{checkpoint} Site Delta %"] = fmt_pct(site_pct)
        rec[f"{checkpoint} Lift vs Control %"] = fmt_pct(lift)
        rec["Status"] = f"{checkpoint} read"
        if page_pct is None:
            rec["Notes"] = "Zero baseline clicks; delta undefined. Judge on impressions."
        filled += 1

    write_ledger(ledger_path, records)
    return MeasureResult(filled, not_due, already, tuple(missing))


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


def _load(path: Path) -> list[GscRow]:
    """Read one export, reporting skipped rows on stderr."""
    result = read_rows(path)
    if result.skipped:
        print(f"{path.name}: skipped {result.skipped} malformed row(s)", file=sys.stderr)
        for line_number, reason in result.problems:
            print(f"  line {line_number}: {reason}", file=sys.stderr)
    return result.rows


def generate_tabs(mode: Mode, current: Path, out_dir: Path, previous: Path | None = None) -> None:
    """Read the export(s) and write the filled CSV tab(s) selected by ``mode``.

    ``previous`` is required for decay/all/queue (the earlier period) and ignored
    otherwise; ``current`` is always the latest period. Raises GscInputError if
    ``previous`` is missing for a mode that needs it, or if cannibalization/all is
    given a Pages-only export (no query column). snapshot/measure are not tab modes;
    run them through run_snapshot/run_measure.
    """
    if mode in ("snapshot", "measure"):
        raise GscInputError(f"{mode} writes the ledger; it is not a tab mode")
    prev_rows: list[GscRow] = []
    if mode in NEEDS_PREVIOUS:
        if previous is None:
            raise GscInputError(f"{mode} needs a previous-period export")
        prev_rows = _load(previous)
    cur_rows = _load(current)
    # Checked before any file is written, so a failed run leaves no partial output.
    if mode in ("cannibalization", "all") and not any(r.query for r in cur_rows):
        raise GscInputError(f"{current}: cannibalization needs a 'query' column; this export has none.")
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
    if mode in ("queue", "all"):
        rows, dropped = edit_queue_rows(prev_rows, cur_rows)
        write_tab(out_dir, TAB_EDIT_QUEUE, rows)
        print(f"queue: {len(rows)} pages ranked, {dropped} dropped as low-visibility "
              f"(<{MIN_IMPRESSIONS} impressions)")


def run_snapshot(args: CliArgs) -> None:
    """snapshot mode: record baselines for args.urls in the ledger and report."""
    result = snapshot(_load(args.current), args.urls, args.change_type,
                      args.change_date, args.window, args.ledger)
    print(f"snapshot: {result.added} new, {result.updated} updated -> {args.ledger}")
    for url in result.missing:
        print(f"  not in export, skipped: {url}")


def run_measure(args: CliArgs) -> None:
    """measure mode: fill the args.checkpoint reading for every due ledger record."""
    if args.checkpoint is None:
        raise GscInputError("measure needs --checkpoint d28 or d56")
    result = measure(_load(args.current), args.checkpoint, args.as_of, args.ledger)
    print(f"measure {args.checkpoint}: {result.filled} read, {result.not_due} not due yet, "
          f"{result.already} already recorded -> {args.ledger}")
    for item in result.missing:
        print(f"  skipped: {item}")


@dataclass(frozen=True)
class CliArgs:
    """Validated command line: the mode and the paths it maps onto."""

    mode: Mode
    current: Path
    out_dir: Path
    previous: Path | None = None  # set exactly for the modes in NEEDS_PREVIOUS
    # snapshot/measure options; every other mode ignores them.
    ledger: Path = Path("Edit_Measurement_filled.csv")
    urls: tuple[str, ...] = ()
    change_type: str = "edit"
    change_date: str = ""  # YYYY-MM-DD
    window: str = ""
    checkpoint: str | None = None
    as_of: date = field(default_factory=date.today)


def parse_args(argv: Sequence[str] | None = None) -> CliArgs:
    """Parse and validate the command line (argparse exits with 2 on usage errors)."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    parser.add_argument("mode", choices=get_args(Mode))
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="GSC export CSV(s): previous then current for decay/all/queue; "
        "one file for every other mode",
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        dest="out_dir",
        type=Path,
        default=Path("."),
        help="output directory (default: current directory)",
    )
    parser.add_argument("--url", action="append", default=[], help="snapshot: page URL (repeatable)")
    parser.add_argument("--change-type", default="edit", help="snapshot: recover | ctr | rank | edit")
    parser.add_argument("--date", help="snapshot: date the edit went live, YYYY-MM-DD (default today)")
    parser.add_argument("--window", default="",
                        help="snapshot: label for the baseline window, e.g. '28d to 2026-08-26'")
    parser.add_argument("--checkpoint", choices=sorted(CHECKPOINT_DAYS), help="measure: which reading")
    parser.add_argument("--as-of", help="measure: reading date, YYYY-MM-DD (default today)")
    parser.add_argument("--ledger", type=Path,
                        help="snapshot/measure: ledger CSV (default <out_dir>/Edit_Measurement_filled.csv)")
    args = parser.parse_args(argv)

    mode = cast(Mode, args.mode)  # argparse choices were derived from Mode
    files: list[Path] = args.files
    expected = 2 if mode in NEEDS_PREVIOUS else 1
    if len(files) != expected:
        parser.error(
            f"{mode} takes exactly {expected} file(s), got {len(files)}"
            + (" (previous.csv current.csv)" if expected == 2 else "")
        )
    if mode in NEEDS_PREVIOUS:
        return CliArgs(mode, current=files[1], out_dir=args.out_dir, previous=files[0])
    if mode == "snapshot" and not args.url:
        parser.error("snapshot needs at least one --url")
    if mode == "measure" and not args.checkpoint:
        parser.error("measure needs --checkpoint d28 or d56")

    def parse_date(text: str | None, flag: str) -> date:
        if text is None:
            return date.today()
        try:
            return datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            parser.error(f"{flag} must be YYYY-MM-DD, got {text!r}")

    if mode == "snapshot":
        parse_date(args.date, "--date")  # validation only
    return CliArgs(
        mode, current=files[0], out_dir=args.out_dir,
        ledger=args.ledger or args.out_dir / f"{TAB_EDIT_MEASUREMENT}_filled.csv",
        urls=tuple(args.url), change_type=args.change_type,
        # The raw --date text seeds the edit id, matching earlier ledgers byte for byte.
        change_date=(args.date or date.today().isoformat()) if mode == "snapshot" else "",
        window=args.window, checkpoint=args.checkpoint,
        as_of=parse_date(args.as_of, "--as-of") if mode == "measure" else date.today(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point; returns the process exit code."""
    args = parse_args(argv)
    try:
        if args.mode == "snapshot":
            run_snapshot(args)
        elif args.mode == "measure":
            run_measure(args)
        else:
            generate_tabs(args.mode, args.current, args.out_dir, args.previous)
    except (GscInputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
