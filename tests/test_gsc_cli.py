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
    ["queue", "a.csv"],
    ["snapshot", "a.csv", "b.csv", "--url", "/a"],
    ["measure", "a.csv", "b.csv", "--checkpoint", "d28"],
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
                                         "decay: 2 pages flagged",
                                         "queue: 2 pages ranked, 0 dropped as low-visibility "
                                         "(<100 impressions)"]
    assert "previous.csv: skipped 1 malformed row(s)" in captured.err
    for title in ("GSC_Opportunities", "Cannibalization", "Content_Decay", "Edit_Queue"):
        rows = read_csv(out / f"{title}_filled.csv")
        assert rows[0] == headers_for(title)
    assert len(read_csv(out / "Content_Decay_filled.csv")) == 3
    decay = {r[0]: r for r in read_csv(out / "Content_Decay_filled.csv")[1:]}
    assert decay["/b"][5] == "dropped out"
    assert decay["/a"][5] == "5.0 -> 6.0"
    # /a lost 90 of 100 clicks (recover 90 beats ctr (0.04 - 0.005) * 2000 = 70);
    # /c is new, at position 8: ctr (0.025 - 0.01) * 1000 = 15.
    queue = [r[:6] for r in read_csv(out / "Edit_Queue_filled.csv")[1:]]
    assert queue == [["1", "/a", "recover", "Regression repair", "90", "Yes"],
                     ["2", "/c", "ctr", "Title / description rewrite", "15", "No"]]


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


@pytest.mark.parametrize("flag", ["-o", "--out-dir"])
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
    assert get_args(gsc.Mode) == ("opportunities", "cannibalization", "decay", "all",
                                  "queue", "snapshot", "measure")
    with pytest.raises(SystemExit) as exc:
        gsc.parse_args(["bogus", "a.csv"])
    assert exc.value.code == 2


def test_parse_args_defaults_and_path_type():
    args = gsc.parse_args(["opportunities", "a.csv"])
    assert args.out_dir == Path(".")
    assert gsc.parse_args(["decay", "a", "b", "--out-dir", "x"]).out_dir == Path("x")

    two = gsc.parse_args(["decay", "a", "b"])
    assert (two.mode, two.previous, two.current) == ("decay", Path("a"), Path("b"))
    one = gsc.parse_args(["cannibalization", "a"])
    assert (one.mode, one.previous, one.current) == ("cannibalization", None, Path("a"))


def test_needs_previous_is_the_arity_source_of_truth():
    assert gsc.NEEDS_PREVIOUS == {"decay", "all", "queue"}
    assert gsc.NEEDS_PREVIOUS <= set(get_args(gsc.Mode))


@pytest.mark.parametrize("flag", ["--out", "--ou"])
def test_removed_out_alias_and_abbreviations_rejected(flag, tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        gsc.main(["opportunities", "a.csv", flag, str(tmp_path)])
    assert exc.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


@pytest.mark.parametrize("mode", ["decay", "all", "queue"])
def test_generate_tabs_requires_previous_for_decay_and_all(mode, tmp_path):
    cur = write_export(tmp_path / "current.csv", ["q,/a,1,200,1%,5"])
    with pytest.raises(gsc.GscInputError, match="previous"):
        gsc.generate_tabs(mode, cur, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_generate_tabs_direct_call_single_file_mode(tmp_path):
    cur = write_export(tmp_path / "current.csv", ["q,/a,1,200,1%,5"])
    gsc.generate_tabs("opportunities", cur, tmp_path / "out")
    assert (tmp_path / "out" / "GSC_Opportunities_filled.csv").exists()
