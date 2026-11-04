"""Tests for GSC CSV output: write_tab behavior and header contract with csv-templates."""

from __future__ import annotations

import csv

import pytest

import seo_gsc_analyzer as gsc
from gsc_helpers import read_csv, row
from kit_common import CSV_TEMPLATE_DIR
from workbook_spec import headers_for


def test_write_tab_orders_by_header_and_fills_missing(tmp_path):
    headers = headers_for("Content_Decay")
    given = {"Action": "Refresh", "URL": "/x"}
    path = gsc.write_tab(tmp_path, "Content_Decay", [given])
    assert read_csv(path) == [headers, [given.get(h, "") for h in headers]]


def test_write_tab_rejects_unknown_keys(tmp_path):
    with pytest.raises(ValueError, match="Bogus"):
        gsc.write_tab(tmp_path, "Cannibalization", [{"URL 1": "/a", "Bogus": "x"}])
    assert not (tmp_path / "Cannibalization_filled.csv").exists()


@pytest.mark.parametrize("title", ["GSC_Opportunities", "Cannibalization", "Content_Decay",
                                   "Edit_Queue", "Edit_Measurement"])
def test_headers_match_csv_template(title):
    template = CSV_TEMPLATE_DIR / f"{title}.csv"
    with template.open(newline="", encoding="utf-8-sig") as f:
        assert headers_for(title) == next(csv.reader(f))


def test_every_row_builder_key_is_a_workbook_header():
    # Both opportunity branches: striking distance (pos 8) and low CTR at pos 1.
    cur = [row("q", "/a", clicks=0, impressions=500, position=1.0),
           row("q", "/b", impressions=500, position=8.0)]
    opp = gsc.opportunity_rows(cur)
    assert {r["Opportunity Type"] for r in opp} == {
        "High impressions low CTR for position", "Striking distance (pos 4-15)"}
    built = {
        "GSC_Opportunities": opp,
        "Cannibalization": gsc.cannibalization_rows(cur),
        "Content_Decay": gsc.decay_rows([row(clicks=100)], [row(clicks=10)]),
    }
    for title, rows in built.items():
        assert rows, title
        keys = set().union(*rows)
        assert keys <= set(headers_for(title)), (title, keys - set(headers_for(title)))
