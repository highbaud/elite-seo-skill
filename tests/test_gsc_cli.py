"""Tests for the GSC analyzer CLI: parse_args, modes, main() end-to-end and error exits."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

import seo_gsc_analyzer as gsc
from gsc_helpers import read_csv, write_export
from workbook_spec import headers_for


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


@pytest.mark.parametrize("flag", ["-o", "--out", "--out-dir"])
def test_output_dir_flag_spellings(flag, tmp_path, capsys):
    cur = write_export(tmp_path / "current.csv", ["q1,/a,10,2000,0.5%,6"])
    out = tmp_path / flag.strip("-")
    gsc.main(["opportunities", str(cur), flag, str(out)])
    assert (out / "GSC_Opportunities_filled.csv").exists()


def test_skipped_row_examples_on_stderr(tmp_path, capsys):
    p = write_export(tmp_path / "x.csv", [
        "good,/a,5,100,5%,3",         # line 2
        "bad,/a,abc,100,1%,3",        # line 3
        "blank,/a,5,100,5%,",         # line 4
        "zero,/a,5,100,5%,0",         # line 5
    ])
    result = gsc.read_rows(p)
    assert result.problems == ((3, "unparsable number 'abc' in clicks"),
                               (4, "blank position"),
                               (5, "position must be >= 1"))
    gsc.main(["opportunities", str(p), "-o", str(tmp_path / "out")])
    err = capsys.readouterr().err
    assert "x.csv: skipped 3 malformed row(s)" in err
    assert "  line 3: unparsable number 'abc' in clicks" in err
    assert "  line 5: position must be >= 1" in err


def test_mode_choices_derived_from_mode_type():
    assert get_args(gsc.Mode) == ("opportunities", "cannibalization", "decay", "all")
    with pytest.raises(SystemExit) as exc:
        gsc.parse_args(["bogus", "a.csv"])
    assert exc.value.code == 2


def test_parse_args_defaults_and_path_type():
    args = gsc.parse_args(["opportunities", "a.csv"])
    assert args.out_dir == Path(".")
    assert gsc.parse_args(["decay", "a", "b", "--out", "x"]).out_dir == Path("x")
