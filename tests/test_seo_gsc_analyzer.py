"""Tests for scripts/seo_gsc_analyzer.py using synthetic GSC exports."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

import seo_gsc_analyzer as gsc
from kit_common import CSV_TEMPLATE_DIR
from workbook_spec import headers_for

HEADER = "query,page,clicks,impressions,ctr,position\n"


def row(query="q", page="/a", clicks=0, impressions=1000, position=5.0):
    return gsc.GscRow(query, page, float(clicks), float(impressions), float(position))


def write_export(path: Path, lines: list[str], header: str = HEADER, encoding: str = "utf-8") -> Path:
    path.write_text(header + "".join(line + "\n" for line in lines), encoding=encoding)
    return path


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


# --- opportunities -------------------------------------------------------

def test_striking_distance_bounds():
    rows = [row("in-lo", position=4.0), row("in-hi", position=15.0),
            row("below", position=3.9, clicks=500), row("above", position=15.1)]
    out = gsc.opportunity_rows(rows)
    assert {r[0] for r in out} == {"in-lo", "in-hi"}
    assert all(r[6] == "Striking distance (pos 4-15)" for r in out)


def test_low_ctr_for_position_flagged_and_formatted():
    out = gsc.opportunity_rows([row("weak", clicks=10, impressions=1000, position=2.04)])
    assert out == [["weak", "/a", 10, 1000, "1.00%", 2.0,
                    "High impressions low CTR for position",
                    "Rewrite title/meta; log in Experiment_Log and judge CTR at stable position", "SEO"]]


def test_healthy_ctr_not_flagged():
    assert gsc.opportunity_rows([row(clicks=200, impressions=1000, position=2.0)]) == []


def test_min_impressions_excluded():
    rows = [row("low", impressions=gsc.MIN_IMPRESSIONS - 1), row("ok", impressions=gsc.MIN_IMPRESSIONS)]
    assert [r[0] for r in gsc.opportunity_rows(rows)] == ["ok"]


def test_opportunities_sorted_by_impressions_desc():
    rows = [row("a", impressions=200), row("b", impressions=900), row("c", impressions=500)]
    assert [r[0] for r in gsc.opportunity_rows(rows)] == ["b", "c", "a"]


# --- cannibalization -----------------------------------------------------

def test_cannibalization_share_threshold():
    above = [row("hit", "/a", impressions=800), row("hit", "/b", impressions=200)]    # 20%
    below = [row("miss", "/a", impressions=810), row("miss", "/b", impressions=190)]  # 19%
    out = gsc.cannibalization_rows(above + below)
    assert [r[0] for r in out] == ["hit"]
    assert out[0][1:3] == ["/a", "/b"]
    assert out[0][4] == "/a"


def test_cannibalization_ignores_single_page_and_noise_pages():
    rows = [row("solo", "/a", impressions=5000),
            row("noisy", "/a", impressions=1000), row("noisy", "/b", impressions=10)]
    assert gsc.cannibalization_rows(rows) == []


def test_cannibalization_sorted_by_query():
    rows = [row(q, p, impressions=500) for q in ("zeta", "alpha") for p in ("/a", "/b")]
    assert [r[0] for r in gsc.cannibalization_rows(rows)] == ["alpha", "zeta"]


# --- decay ---------------------------------------------------------------

def test_decay_drop_threshold():
    prev = [row(page="/hit", clicks=100), row(page="/miss", clicks=100)]
    cur = [row(page="/hit", clicks=80), row(page="/miss", clicks=81)]
    out = gsc.decay_rows(prev, cur)
    assert [r[0] for r in out] == ["/hit"]
    assert out[0][2:5] == [80, 100, "-20%"]


def test_decay_minimum_clicks_rule():
    prev = [row(page="/small", clicks=9), row(page="/edge", clicks=10)]
    cur = [row(page="/small", clicks=0), row(page="/edge", clicks=0)]
    assert [r[0] for r in gsc.decay_rows(prev, cur)] == ["/edge"]


def test_decay_dropped_out_when_no_current_impressions():
    prev = [row(page="/gone", clicks=50, position=3)]
    out = gsc.decay_rows(prev, [])
    assert out[0][5] == "dropped out"
    zero = gsc.decay_rows(prev, [row(page="/gone", clicks=0, impressions=0, position=3)])
    assert zero[0][5] == "dropped out"


def test_decay_rank_change_uses_weighted_position():
    prev = [row(page="/p", clicks=50, impressions=100, position=2),
            row("q2", "/p", clicks=50, impressions=300, position=6)]
    cur = [row(page="/p", clicks=10, impressions=100, position=9)]
    out = gsc.decay_rows(prev, cur)
    assert out[0][5] == "5.0 -> 9.0"


def test_decay_sorted_by_absolute_click_loss():
    prev = [row(page="/small", clicks=20), row(page="/big", clicks=500), row(page="/mid", clicks=100)]
    cur = [row(page="/small", clicks=0), row(page="/big", clicks=100), row(page="/mid", clicks=10)]
    assert [r[0] for r in gsc.decay_rows(prev, cur)] == ["/big", "/mid", "/small"]


# --- read_rows -----------------------------------------------------------

def test_read_rows_missing_column_raises(tmp_path):
    p = write_export(tmp_path / "x.csv", ["a,b,1,2"], header="query,page,clicks,impressions\n")
    with pytest.raises(gsc.GscInputError, match="position"):
        gsc.read_rows(p)


def test_read_rows_skips_and_counts_malformed(tmp_path):
    p = write_export(tmp_path / "x.csv", [
        "good,/a,5,100,5%,3.2",
        "short,/a,5",              # short row
        "bad,/a,abc,100,1%,3",     # unparsable number
        "blank,/a,5,100,5%,",      # blank position
        "zero,/a,5,100,5%,0",      # non-positive position
        "nan,/a,5,100,5%,nan",     # non-finite
    ])
    result = gsc.read_rows(p)
    assert [r.query for r in result.rows] == ["good"]
    assert result.skipped == 5


def test_read_rows_blank_clicks_and_impressions_default_to_zero(tmp_path):
    p = write_export(tmp_path / "x.csv", ["q,/a,,,,7"])
    result = gsc.read_rows(p)
    assert result.skipped == 0
    assert result.rows == [gsc.GscRow("q", "/a", 0.0, 0.0, 7.0)]


def test_read_rows_header_case_insensitive_and_bom(tmp_path):
    p = write_export(tmp_path / "x.csv", ["q,/a,1,10,10%,2"],
                     header=" Query , PAGE ,Clicks,Impressions,CTR,Position\n", encoding="utf-8-sig")
    assert gsc.read_rows(p).rows == [gsc.GscRow("q", "/a", 1.0, 10.0, 2.0)]


# --- CLI -----------------------------------------------------------------

@pytest.mark.parametrize("args", [
    ["opportunities", "a.csv", "b.csv"],
    ["cannibalization", "a.csv", "b.csv"],
    ["decay", "a.csv"],
    ["decay", "a.csv", "b.csv", "c.csv"],
    ["all", "a.csv"],
])
def test_wrong_file_counts_are_argparse_errors(args, tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        gsc.main([*args, "-o", str(tmp_path)])
    assert exc.value.code == 2
    assert "takes exactly" in capsys.readouterr().err


def test_all_mode_end_to_end(tmp_path, capsys):
    prev = write_export(tmp_path / "previous.csv", [
        "q1,/a,100,2000,5%,5",
        "q2,/b,100,1000,10%,2",
        "bad,/a,x,1,1%,1",
    ])
    cur = write_export(tmp_path / "current.csv", [
        "q1,/a,10,2000,0.5%,6",
        "q1,/c,10,1000,1%,8",
    ])
    out = tmp_path / "out"
    gsc.main(["all", str(prev), str(cur), "-o", str(out)])
    captured = capsys.readouterr()
    assert captured.out.splitlines() == ["opportunities: 2 rows", "cannibalization: 1 queries",
                                         "decay: 2 pages flagged"]
    assert "previous.csv: skipped 1 malformed row(s)" in captured.err
    for title in ("GSC_Opportunities", "Cannibalization", "Content_Decay"):
        rows = read_csv(out / f"{title}_filled.csv")
        assert rows[0] == headers_for(title)
    assert len(read_csv(out / "Content_Decay_filled.csv")) == 3
    decay = {r[0]: r for r in read_csv(out / "Content_Decay_filled.csv")[1:]}
    assert decay["/b"][5] == "dropped out"
    assert decay["/a"][5] == "5.0 -> 6.0"


def test_missing_input_file_is_clean_error(tmp_path, capsys):
    assert gsc.main(["opportunities", str(tmp_path / "nope.csv"), "-o", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error:") and "nope.csv" in err


def test_missing_columns_is_clean_error(tmp_path, capsys):
    p = write_export(tmp_path / "x.csv", [], header="foo,bar\n")
    assert gsc.main(["cannibalization", str(p), "-o", str(tmp_path)]) == 1
    assert "missing columns" in capsys.readouterr().err


def test_unwritable_output_dir_is_clean_error(tmp_path, capsys):
    p = write_export(tmp_path / "x.csv", ["q,/a,1,200,1%,5"])
    blocker = tmp_path / "file"
    blocker.write_text("x")
    assert gsc.main(["opportunities", str(p), "-o", str(blocker / "sub")]) == 1
    assert capsys.readouterr().err.startswith("error:")


# --- contract with csv templates -----------------------------------------

@pytest.mark.parametrize("title", ["GSC_Opportunities", "Cannibalization", "Content_Decay"])
def test_headers_match_csv_template(title):
    template = CSV_TEMPLATE_DIR / f"{title}.csv"
    with template.open(newline="", encoding="utf-8-sig") as f:
        assert headers_for(title) == next(csv.reader(f))


@pytest.mark.parametrize("flag", ["-o", "--out", "--out-dir"])
def test_output_dir_flag_spellings(flag, tmp_path, capsys):
    cur = write_export(tmp_path / "current.csv", ["q1,/a,10,2000,0.5%,6"])
    out = tmp_path / flag.strip("-")
    gsc.main(["opportunities", str(cur), flag, str(out)])
    assert (out / "GSC_Opportunities_filled.csv").exists()
