"""GSC export analyzer for the Elite SEO Operating Kit.

Turns raw Google Search Console performance exports into pre-filled rows for the
workbook tabs GSC_Opportunities, Cannibalization, and Content_Decay.

Input format: CSV export with columns (case-insensitive, extra columns ignored):
    query, page, clicks, impressions, ctr, position
GSC's own "Queries + Pages" export works; so does any tool export with those headers.

Usage:
    python seo_gsc_analyzer.py opportunities current.csv -o out_dir
    python seo_gsc_analyzer.py cannibalization current.csv -o out_dir
    python seo_gsc_analyzer.py decay previous.csv current.csv -o out_dir
    python seo_gsc_analyzer.py all previous.csv current.csv -o out_dir

No third-party dependencies.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

# Rough expected CTR by position bucket (industry-typical medians; used only to
# flag underperformers, never reported as a benchmark to clients).
EXPECTED_CTR = {1: 0.28, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
                6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.018}

MIN_IMPRESSIONS = 100          # ignore noise rows
STRIKING_DISTANCE = (4.0, 15.0)
CTR_UNDERPERFORM_RATIO = 0.5   # flag if CTR < 50% of position-expected
CANNIBAL_SHARE = 0.20          # 2nd page needs >=20% of query impressions
DECAY_DROP = 0.20              # >=20% click drop flags decay


def read_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        field_map = {name.strip().lower(): name for name in reader.fieldnames or []}
        required = ["query", "page", "clicks", "impressions", "position"]
        missing = [c for c in required if c not in field_map]
        if missing:
            sys.exit(f"{path}: missing columns {missing}. Found: {reader.fieldnames}")
        for raw in reader:
            try:
                rows.append({
                    "query": raw[field_map["query"]].strip(),
                    "page": raw[field_map["page"]].strip(),
                    "clicks": float(raw[field_map["clicks"]] or 0),
                    "impressions": float(raw[field_map["impressions"]] or 0),
                    "position": float(raw[field_map["position"]] or 0),
                })
            except ValueError:
                continue
    return rows


def expected_ctr(position):
    bucket = min(10, max(1, round(position)))
    return EXPECTED_CTR[bucket]


def opportunities(rows, out_dir):
    """Striking-distance and position-adjusted low-CTR rows -> GSC_Opportunities."""
    out = []
    for r in rows:
        if r["impressions"] < MIN_IMPRESSIONS:
            continue
        ctr = r["clicks"] / r["impressions"] if r["impressions"] else 0
        lo, hi = STRIKING_DISTANCE
        if lo <= r["position"] <= hi:
            out.append([r["query"], r["page"], int(r["clicks"]), int(r["impressions"]),
                        f"{ctr:.2%}", round(r["position"], 1),
                        "Striking distance (pos 4-15)",
                        "Add internal links, improve answer block, refresh proof", "SEO"])
        elif r["position"] <= 10 and ctr < expected_ctr(r["position"]) * CTR_UNDERPERFORM_RATIO:
            out.append([r["query"], r["page"], int(r["clicks"]), int(r["impressions"]),
                        f"{ctr:.2%}", round(r["position"], 1),
                        "High impressions low CTR for position",
                        "Rewrite title/meta; log in Experiment_Log and judge CTR at stable position", "SEO"])
    out.sort(key=lambda x: -x[3])
    write_csv(out_dir / "GSC_Opportunities_filled.csv",
              ["Query", "Page", "Clicks", "Impressions", "CTR", "Position",
               "Opportunity Type", "Action", "Owner"], out)
    return len(out)


def cannibalization(rows, out_dir):
    """Queries where 2+ pages each hold a meaningful impression share -> Cannibalization."""
    by_query = defaultdict(list)
    for r in rows:
        if r["impressions"] >= MIN_IMPRESSIONS / 2:
            by_query[r["query"]].append(r)
    out = []
    for query, group in by_query.items():
        if len(group) < 2:
            continue
        total = sum(g["impressions"] for g in group)
        group.sort(key=lambda g: -g["impressions"])
        top, second = group[0], group[1]
        if second["impressions"] / total >= CANNIBAL_SHARE:
            out.append([query, top["page"], second["page"],
                        "Review: true duplicate / intent split / format mismatch",
                        top["page"],
                        "Diagnose with Cannibalization prompt before merging", ""])
    out.sort(key=lambda x: x[0])
    write_csv(out_dir / "Cannibalization_filled.csv",
              ["Keyword / Intent", "URL 1", "URL 2", "Conflict Type",
               "Winning URL", "Decision", "Redirect / Canonical / Rewrite"], out)
    return len(out)


def decay(prev_rows, cur_rows, out_dir):
    """Pages losing >=20% clicks period-over-period -> Content_Decay."""
    def by_page(rows):
        agg = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # clicks, impr, pos*impr, impr for pos
        for r in rows:
            a = agg[r["page"]]
            a[0] += r["clicks"]
            a[1] += r["impressions"]
            a[2] += r["position"] * r["impressions"]
            a[3] += r["impressions"]
        return agg

    prev, cur = by_page(prev_rows), by_page(cur_rows)
    out = []
    for page, p in prev.items():
        if p[0] < 10:  # too few clicks to judge decay
            continue
        c = cur.get(page, [0.0, 0.0, 0.0, 0.0])
        if p[0] == 0:
            continue
        drop = (p[0] - c[0]) / p[0]
        if drop >= DECAY_DROP:
            prev_pos = p[2] / p[3] if p[3] else 0
            cur_pos = c[2] / c[3] if c[3] else 0
            out.append([page, "", int(c[0]), int(p[0]), f"{-drop:.0%}",
                        f"{prev_pos:.1f} -> {cur_pos:.1f}" if cur_pos else "dropped out",
                        "High", "", "", "Refresh"])
    out.sort(key=lambda x: x[3] - x[2], reverse=True)
    write_csv(out_dir / "Content_Decay_filled.csv",
              ["URL", "Page Type", "Clicks 90d", "Clicks Previous 90d", "Delta",
               "Rank Change", "Freshness Need", "Backlinks", "Conversions", "Action"], out)
    return len(out)


def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["opportunities", "cannibalization", "decay", "all"])
    ap.add_argument("files", nargs="+", help="GSC export CSV(s); decay/all need previous then current")
    ap.add_argument("-o", "--out", default=".", help="output directory")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode in ("decay", "all") and len(args.files) < 2:
        sys.exit("decay/all need two files: previous.csv current.csv")

    if args.mode == "decay":
        prev_rows, cur_rows = read_rows(args.files[0]), read_rows(args.files[1])
        print(f"decay: {decay(prev_rows, cur_rows, out_dir)} pages flagged")
        return

    if args.mode == "all":
        prev_rows, cur_rows = read_rows(args.files[0]), read_rows(args.files[1])
        print(f"opportunities: {opportunities(cur_rows, out_dir)} rows")
        print(f"cannibalization: {cannibalization(cur_rows, out_dir)} queries")
        print(f"decay: {decay(prev_rows, cur_rows, out_dir)} pages flagged")
        return

    rows = read_rows(args.files[0])
    if args.mode == "opportunities":
        print(f"opportunities: {opportunities(rows, out_dir)} rows")
    else:
        print(f"cannibalization: {cannibalization(rows, out_dir)} queries")


if __name__ == "__main__":
    main()
