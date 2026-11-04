"""Tests for GSC export parsing: read_rows skipping, defaults and problem line numbers."""

from __future__ import annotations

import pytest

import seo_gsc_analyzer as gsc
from gsc_helpers import write_export


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


def test_skipped_row_examples_capped(tmp_path):
    p = write_export(tmp_path / "x.csv", [f"q{i},/a,x,100,1%,3" for i in range(9)])
    result = gsc.read_rows(p)
    assert result.skipped == 9
    assert len(result.problems) == gsc.MAX_PROBLEM_EXAMPLES == 5
    assert result.problems[0][0] == 2
