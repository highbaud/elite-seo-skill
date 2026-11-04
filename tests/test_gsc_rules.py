"""Tests for the GSC opportunity, cannibalization and decay rules."""

from __future__ import annotations

import seo_gsc_analyzer as gsc
from gsc_helpers import row


def test_striking_distance_bounds():
    rows = [row("in-lo", position=4.0), row("in-hi", position=15.0),
            row("below", position=3.9, clicks=500), row("above", position=15.1)]
    out = gsc.opportunity_rows(rows)
    assert {r["Query"] for r in out} == {"in-lo", "in-hi"}
    assert all(r["Opportunity Type"] == "Striking distance (pos 4-15)" for r in out)


def test_low_ctr_for_position_flagged_and_formatted():
    out = gsc.opportunity_rows([row("weak", clicks=10, impressions=1000, position=2.04)])
    assert out == [{"Query": "weak", "Page": "/a", "Clicks": 10, "Impressions": 1000,
                    "CTR": "1.00%", "Position": 2.0,
                    "Opportunity Type": "High impressions low CTR for position",
                    "Action": "Rewrite title/meta; log in Experiment_Log and judge CTR at stable position",
                    "Owner": "SEO"}]


def test_healthy_ctr_not_flagged():
    assert gsc.opportunity_rows([row(clicks=200, impressions=1000, position=2.0)]) == []


def test_min_impressions_excluded():
    rows = [row("low", impressions=gsc.MIN_IMPRESSIONS - 1), row("ok", impressions=gsc.MIN_IMPRESSIONS)]
    assert [r["Query"] for r in gsc.opportunity_rows(rows)] == ["ok"]


def test_opportunities_sorted_by_impressions_desc():
    rows = [row("a", impressions=200), row("b", impressions=900), row("c", impressions=500)]
    assert [r["Query"] for r in gsc.opportunity_rows(rows)] == ["b", "c", "a"]


def test_cannibalization_share_threshold():
    above = [row("hit", "/a", impressions=800), row("hit", "/b", impressions=200)]    # 20%
    below = [row("miss", "/a", impressions=810), row("miss", "/b", impressions=190)]  # 19%
    out = gsc.cannibalization_rows(above + below)
    assert [r["Keyword / Intent"] for r in out] == ["hit"]
    assert (out[0]["URL 1"], out[0]["URL 2"]) == ("/a", "/b")
    assert out[0]["Winning URL"] == "/a"


def test_cannibalization_ignores_single_page_and_noise_pages():
    rows = [row("solo", "/a", impressions=5000),
            row("noisy", "/a", impressions=1000), row("noisy", "/b", impressions=10)]
    assert gsc.cannibalization_rows(rows) == []


def test_cannibalization_duplicate_query_page_rows_do_not_self_conflict():
    rows = [row("dup", "/a", impressions=600), row("dup", "/a", impressions=400),
            row("dup", "/b", impressions=10)]
    assert gsc.cannibalization_rows(rows) == []


def test_cannibalization_aggregates_split_rows_before_noise_filter():
    # Each /b row is under MIN_IMPRESSIONS / 2 alone; together they clear it and the share.
    rows = [row("agg", "/a", impressions=600),
            row("agg", "/b", impressions=40), row("agg", "/b", impressions=40),
            row("agg", "/b", impressions=40), row("agg", "/b", impressions=40)]  # 160 total, 21%
    out = gsc.cannibalization_rows(rows)
    assert [(r["URL 1"], r["URL 2"]) for r in out] == [("/a", "/b")]


def test_cannibalization_sorted_by_query():
    rows = [row(q, p, impressions=500) for q in ("zeta", "alpha") for p in ("/a", "/b")]
    assert [r["Keyword / Intent"] for r in gsc.cannibalization_rows(rows)] == ["alpha", "zeta"]


def test_decay_drop_threshold():
    prev = [row(page="/hit", clicks=100), row(page="/miss", clicks=100)]
    cur = [row(page="/hit", clicks=80), row(page="/miss", clicks=81)]
    out = gsc.decay_rows(prev, cur)
    assert [r["URL"] for r in out] == ["/hit"]
    assert (out[0]["Clicks 90d"], out[0]["Clicks Previous 90d"], out[0]["Delta"]) == (80, 100, "-20%")


def test_decay_minimum_clicks_rule():
    prev = [row(page="/small", clicks=9), row(page="/edge", clicks=10)]
    cur = [row(page="/small", clicks=0), row(page="/edge", clicks=0)]
    assert [r["URL"] for r in gsc.decay_rows(prev, cur)] == ["/edge"]


def test_decay_dropped_out_when_no_current_impressions():
    prev = [row(page="/gone", clicks=50, position=3)]
    out = gsc.decay_rows(prev, [])
    assert out[0]["Rank Change"] == "dropped out"
    zero = gsc.decay_rows(prev, [row(page="/gone", clicks=0, impressions=0, position=3)])
    assert zero[0]["Rank Change"] == "dropped out"


def test_decay_rank_change_uses_weighted_position():
    prev = [row(page="/p", clicks=50, impressions=100, position=2),
            row("q2", "/p", clicks=50, impressions=300, position=6)]
    cur = [row(page="/p", clicks=10, impressions=100, position=9)]
    out = gsc.decay_rows(prev, cur)
    assert out[0]["Rank Change"] == "5.0 -> 9.0"


def test_decay_sorted_by_absolute_click_loss():
    prev = [row(page="/small", clicks=20), row(page="/big", clicks=500), row(page="/mid", clicks=100)]
    cur = [row(page="/small", clicks=0), row(page="/big", clicks=100), row(page="/mid", clicks=10)]
    assert [r["URL"] for r in gsc.decay_rows(prev, cur)] == ["/big", "/mid", "/small"]
