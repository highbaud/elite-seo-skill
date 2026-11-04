"""Tests for snapshot/measure (the Edit_Measurement ledger) and Pages-only exports."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import seo_gsc_analyzer as gsc
from gsc_helpers import write_export
from workbook_spec import headers_for

PAGES_HEADER = "page,clicks,impressions,ctr,position\n"
EDIT_ID = "b1b0044c81"  # sha1("2026-08-01|/a|ctr")[:10], worked once by hand


def _ledger(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _snapshot(baseline: Path, ledger: Path, *urls: str) -> int:
    args = ["snapshot", str(baseline), "--change-type", "ctr", "--date", "2026-08-01",
            "--window", "28d to 2026-08-01", "--ledger", str(ledger)]
    for url in urls:
        args += ["--url", url]
    return gsc.main(args)


def _measure(export: Path, ledger: Path, as_of: str) -> int:
    return gsc.main(["measure", str(export), "--checkpoint", "d28", "--as-of", as_of,
                     "--ledger", str(ledger)])


@pytest.fixture
def baseline(tmp_path: Path) -> Path:
    # Site control: 100 clicks, 5000 impressions, CTR 2.00%, position (5*1000 + 3*4000) / 5000 = 3.4.
    return write_export(tmp_path / "baseline.csv", ["q1,/a,20,1000,,5", "q2,/b,80,4000,,3"])


def test_snapshot_records_page_and_control_baseline(baseline, tmp_path, capsys):
    ledger = tmp_path / "ledger" / "Edit_Measurement_filled.csv"
    assert _snapshot(baseline, ledger, "/a", "/missing") == 0
    out = capsys.readouterr().out
    assert out == f"snapshot: 1 new, 0 updated -> {ledger}\n  not in export, skipped: /missing\n"
    (rec,) = _ledger(ledger)
    assert list(rec) == headers_for("Edit_Measurement")
    assert {k: v for k, v in rec.items() if v} == {
        "Edit ID": EDIT_ID, "URL": "/a", "Change Type": "ctr", "Change Date": "2026-08-01",
        "Baseline Window": "28d to 2026-08-01",
        "Base Page Clicks": "20", "Base Page Impressions": "1000", "Base Page CTR": "2.00%",
        "Base Page Position": "5.0",
        "Base Site Clicks": "100", "Base Site Impressions": "5000", "Base Site CTR": "2.00%",
        "Base Site Position": "3.4",
        "Status": "baseline captured",
        "Notes": "Control = totals of this export. Pull later exports the same way.",
    }


def test_snapshot_rerun_updates_in_place(baseline, tmp_path, capsys):
    ledger = tmp_path / "ledger.csv"
    _snapshot(baseline, ledger, "/a")
    _snapshot(baseline, ledger, "/a")
    assert capsys.readouterr().out.splitlines()[-1] == f"snapshot: 0 new, 1 updated -> {ledger}"
    assert [r["Edit ID"] for r in _ledger(ledger)] == [EDIT_ID]


def test_measure_d28_not_due_then_due_then_idempotent(baseline, tmp_path, capsys):
    ledger = tmp_path / "ledger.csv"
    _snapshot(baseline, ledger, "/a")
    # Pages-only export: /a 20 -> 30 clicks (+50.0%), site 100 -> 110 (+10.0%), lift +40.0 points.
    later = write_export(tmp_path / "later.csv", ["/a,30,1200,,4", "/b,80,4000,,3"], header=PAGES_HEADER)
    capsys.readouterr()

    # 2026-08-01 + 28 days = 2026-08-29, so the day before is not due.
    assert _measure(later, ledger, "2026-08-28") == 0
    assert capsys.readouterr().out == f"measure d28: 0 read, 1 not due yet, 0 already recorded -> {ledger}\n"
    assert _ledger(ledger)[0]["d28 Read Date"] == ""

    assert _measure(later, ledger, "2026-08-29") == 0
    assert capsys.readouterr().out == f"measure d28: 1 read, 0 not due yet, 0 already recorded -> {ledger}\n"
    (rec,) = _ledger(ledger)
    assert {k: rec[k] for k in rec if k.startswith("d28")} == {
        "d28 Read Date": "2026-08-29", "d28 Page Clicks": "30", "d28 Page Impressions": "1200",
        "d28 Page Position": "4.0", "d28 Site Clicks": "110", "d28 Page Delta %": "+50.0%",
        "d28 Site Delta %": "+10.0%", "d28 Lift vs Control %": "+40.0%",
    }
    assert rec["Status"] == "d28 read"
    assert all(rec[k] == "" for k in rec if k.startswith("d56"))

    before = ledger.read_bytes()
    assert _measure(later, ledger, "2026-09-30") == 0
    assert capsys.readouterr().out == f"measure d28: 0 read, 0 not due yet, 1 already recorded -> {ledger}\n"
    assert ledger.read_bytes() == before


def test_measure_zero_baseline_and_missing_page(tmp_path, capsys):
    zero = write_export(tmp_path / "zero.csv", ["q,/z,0,500,,4", "q,/gone,5,500,,4"])
    ledger = tmp_path / "ledger.csv"
    gsc.main(["snapshot", str(zero), "--url", "/z", "--url", "/gone", "--date", "2026-01-01",
              "--ledger", str(ledger)])
    later = write_export(tmp_path / "later.csv", ["q,/z,4,500,,4"])
    capsys.readouterr()
    assert _measure(later, ledger, "2026-03-01") == 0
    out = capsys.readouterr().out.splitlines()
    assert out[1:] == ["  skipped: /gone (not in this export)"]
    z = next(r for r in _ledger(ledger) if r["URL"] == "/z")
    assert (z["d28 Page Delta %"], z["d28 Lift vs Control %"]) == ("", "")
    assert z["Notes"] == "Zero baseline clicks; delta undefined. Judge on impressions."


def test_measure_without_snapshots_is_clean_error(baseline, tmp_path, capsys):
    assert _measure(baseline, tmp_path / "none.csv", "2026-09-01") == 1
    assert "no snapshots to measure" in capsys.readouterr().err


@pytest.mark.parametrize("args, message", [
    (["snapshot", "a.csv"], "needs at least one --url"),
    (["measure", "a.csv"], "needs --checkpoint"),
    (["snapshot", "a.csv", "--url", "/a", "--date", "08/01/2026"], "--date must be YYYY-MM-DD"),
    (["measure", "a.csv", "--checkpoint", "d28", "--as-of", "tomorrow"], "--as-of must be YYYY-MM-DD"),
    (["measure", "a.csv", "--checkpoint", "d90"], "invalid choice"),
])
def test_snapshot_measure_usage_errors(args, message, capsys):
    with pytest.raises(SystemExit) as exc:
        gsc.main(args)
    assert exc.value.code == 2
    assert message in capsys.readouterr().err


def test_default_ledger_lives_in_out_dir():
    args = gsc.parse_args(["snapshot", "a.csv", "--url", "/a", "-o", "out"])
    assert args.ledger == Path("out") / "Edit_Measurement_filled.csv"


def test_pages_only_export_reads_with_blank_query(tmp_path):
    p = write_export(tmp_path / "pages.csv", ["/a,1,10,10%,2"], header=PAGES_HEADER)
    assert gsc.read_rows(p).rows == [gsc.GscRow("", "/a", 1.0, 10.0, 2.0)]


def test_pages_only_export_works_for_opportunities(tmp_path):
    p = write_export(tmp_path / "pages.csv", ["/a,10,2000,,6"], header=PAGES_HEADER)
    out = tmp_path / "out"
    assert gsc.main(["opportunities", str(p), "-o", str(out)]) == 0
    assert (out / "GSC_Opportunities_filled.csv").exists()


@pytest.mark.parametrize("mode", ["cannibalization", "all"])
def test_pages_only_export_rejected_for_cannibalization(mode, tmp_path, capsys):
    p = write_export(tmp_path / "pages.csv", ["/a,10,2000,,6"], header=PAGES_HEADER)
    files = [str(p), str(p)] if mode == "all" else [str(p)]
    out = tmp_path / "out"
    assert gsc.main([mode, *files, "-o", str(out)]) == 1
    assert "cannibalization needs a 'query' column" in capsys.readouterr().err
    assert not out.exists()
