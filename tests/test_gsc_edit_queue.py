"""Tests for the Edit_Queue: lever choice, guardrails, ordering, and the queue CLI mode.

Expected values are worked by hand from EXPECTED_CTR (pos 2 = 15%, pos 6 = 4%,
pos 10+ = 1.8%), not recomputed with the analyzer's formulas.
"""

from __future__ import annotations

import seo_gsc_analyzer as gsc
from gsc_helpers import read_csv, row, write_export
from workbook_spec import headers_for

PREVIOUS = [row(page="/loss", clicks=100, impressions=1000, position=6)]
CURRENT = [
    # Lost 80 of 100 clicks. recover 80 beats ctr (0.04 - 0.02) * 1000 = 20.
    row(page="/loss", clicks=20, impressions=1000, position=6),
    # New page on page one, badly under-clicked: ctr (0.15 - 0.002) * 5000 = 740.
    row(page="/ctr", clicks=10, impressions=5000, position=2),
    # Page two: rank (0.018 - 0.0025) * 2000 = 31.
    row(page="/rank", clicks=5, impressions=2000, position=12),
    # Below the 100-impression floor: dropped and counted.
    row(page="/low", clicks=0, impressions=50, position=3),
    # Above expected CTR at position 1, nothing to recover: no lever, not counted.
    row(page="/fine", clicks=300, impressions=1000, position=1),
]


def test_real_loss_outranks_bigger_estimates_and_floor_drops_low_visibility():
    rows, dropped = gsc.edit_queue_rows(PREVIOUS, CURRENT)
    assert dropped == 1
    assert [(r["Rank"], r["URL"], r["Winning Lever"], r["Est. Recoverable Clicks"], r["Real Click Loss?"])
            for r in rows] == [
        (1, "/loss", "recover", 80, "Yes"),
        (2, "/ctr", "ctr", 740, "No"),
        (3, "/rank", "rank", 31, "No"),
    ]


def test_queue_row_columns_and_formatting():
    rows, _ = gsc.edit_queue_rows(PREVIOUS, CURRENT)
    assert rows[0] == {
        "Rank": 1, "URL": "/loss", "Winning Lever": "recover", "Fix Type": "Regression repair",
        "Est. Recoverable Clicks": 80, "Real Click Loss?": "Yes",
        "Clicks (current)": 20, "Clicks (previous)": 100, "Impressions (current)": 1000,
        "Position": 6.0, "Actual CTR": "2.00%", "Expected CTR": "4.00%",
        "Recover Est.": 80, "CTR Est.": 20, "Rank Est.": 0,
        "Action": "Find what changed: lost links, SERP feature, refreshed competitor. Restore or rewrite.",
        "Status": "Open",
    }
    assert (rows[2]["Expected CTR"], rows[2]["Actual CTR"], rows[2]["Fix Type"]) == (
        "1.80%", "0.25%", "Content push to page one")


def test_biggest_lever_wins_even_with_a_real_loss():
    # Lost 40 of 100 clicks (real loss), but the ctr gap (0.15 - 0.06) * 1000 = 90 is bigger.
    rows, _ = gsc.edit_queue_rows([row(page="/a", clicks=100, position=2)],
                                  [row(page="/a", clicks=60, impressions=1000, position=2)])
    assert [(r["Winning Lever"], r["Est. Recoverable Clicks"], r["Real Click Loss?"], r["Recover Est."])
            for r in rows] == [("ctr", 90, "Yes", 40)]


def test_small_drop_is_not_a_real_loss():
    # 15% drop is under the 20% decay line; 9 previous clicks is under the 10-click floor.
    s = gsc.score_levers(gsc.PageTotals(clicks=100), gsc.PageTotals(clicks=85, impressions=1000,
                                                                    position_weighted_sum=1000))
    assert (s.recover, s.real_loss) == (0.0, False)
    s = gsc.score_levers(gsc.PageTotals(clicks=9), gsc.PageTotals(clicks=0, impressions=1000,
                                                                  position_weighted_sum=1000))
    assert (s.recover, s.real_loss) == (0.0, False)


def test_impression_floor_is_inclusive_at_100():
    rows, dropped = gsc.edit_queue_rows([], [row(page="/edge", clicks=0, impressions=100, position=2),
                                             row(page="/under", clicks=0, impressions=99, position=2)])
    assert ([r["URL"] for r in rows], dropped) == (["/edge"], 1)


def test_queue_mode_end_to_end(tmp_path, capsys):
    prev = write_export(tmp_path / "previous.csv", ["q,/loss,100,1000,,6"])
    cur = write_export(tmp_path / "current.csv", [
        "q,/loss,20,1000,,6",
        "q,/ctr,10,5000,,2",
        "q,/low,0,50,,3",
    ])
    out = tmp_path / "out"
    assert gsc.main(["queue", str(prev), str(cur), "-o", str(out)]) == 0
    assert capsys.readouterr().out == "queue: 2 pages ranked, 1 dropped as low-visibility (<100 impressions)\n"
    rows = read_csv(out / "Edit_Queue_filled.csv")
    assert rows[0] == headers_for("Edit_Queue")
    assert [r[:6] for r in rows[1:]] == [["1", "/loss", "recover", "Regression repair", "80", "Yes"],
                                         ["2", "/ctr", "ctr", "Title / description rewrite", "740", "No"]]
    assert not (out / "GSC_Opportunities_filled.csv").exists()
