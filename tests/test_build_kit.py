"""Tests for the operating-kit builder and its declarative workbook spec."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("openpyxl")

import build_elite_seo_operating_kit as builder  # noqa: E402
import kit_common  # noqa: E402
import workbook_spec as spec  # noqa: E402
from openpyxl import load_workbook  # noqa: E402


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out_dir = tmp_path_factory.mktemp("kit")
    builder.build_kit(out_dir)
    return out_dir


def _validations(ws) -> dict[str, str]:
    """Map each validated range to its list formula."""
    return {str(dv.sqref): dv.formula1 for dv in ws.data_validations.dataValidation}


def test_csvs_match_committed_templates(built: Path) -> None:
    committed = sorted(kit_common.CSV_TEMPLATE_DIR.glob("*.csv"))
    assert committed
    generated = {p.name for p in (built / "csv-templates").glob("*.csv")}
    assert generated == {p.name for p in committed}
    for path in committed:
        assert (built / "csv-templates" / path.name).read_bytes() == path.read_bytes(), path.name


def test_sheet_titles_order_and_headers_match_specs(built: Path) -> None:
    wb = load_workbook(built / builder.WORKBOOK_NAME)
    assert wb.sheetnames == [s.title for s in spec.SHEETS]
    for sheet in spec.SHEETS:
        header_row = [c.value for c in wb[sheet.title][1]]
        assert header_row == list(sheet.headers)


def test_headers_for_matches_specs() -> None:
    for sheet in spec.SHEETS:
        assert spec.headers_for(sheet.title) == list(sheet.headers)
    with pytest.raises(KeyError):
        spec.headers_for("Nope")


def test_column_letter() -> None:
    assert spec.column_letter("Issue_Register", "ID") == "A"
    assert spec.column_letter("Issue_Register", "Status") == "O"
    assert spec.column_letter("Dashboard", "Metric") == "A"
    with pytest.raises(ValueError):
        spec.column_letter("Issue_Register", "Missing")
    with pytest.raises(KeyError):
        spec.column_letter("Missing_Tab", "ID")


def test_column_letter_for_index_wraps_past_z() -> None:
    assert spec.column_letter_for_index(1) == "A"
    assert spec.column_letter_for_index(26) == "Z"
    assert spec.column_letter_for_index(27) == "AA"
    assert spec.column_letter_for_index(52) == "AZ"
    assert spec.column_letter_for_index(703) == "AAA"
    with pytest.raises(ValueError):
        spec.column_letter_for_index(0)


def test_issue_register_guarded_rows_start_after_seeds() -> None:
    sheet = next(s for s in spec.SHEETS if s.title == "Issue_Register")
    assert {fill.first_row for fill in sheet.fills} == {spec.FIRST_DATA_ROW + len(sheet.rows)}


def test_dashboard_formulas_point_at_correct_columns(built: Path) -> None:
    ws = load_workbook(built / builder.WORKBOOK_NAME)["Dashboard"]
    formulas = {row[0].value: row[1].value for row in ws.iter_rows(min_row=2)}
    status = spec.column_letter("Issue_Register", "Status")
    band = spec.column_letter("Issue_Register", "Priority Band")
    priority = spec.column_letter("Issue_Register", "Priority")
    assert formulas["Open issues"] == f'=COUNTIF(Issue_Register!{status}:{status},"Open")'
    assert formulas["Fix-now issues"] == f'=COUNTIF(Issue_Register!{band}:{band},"Fix now")'
    assert f"Issue_Register!{priority}:{priority}" in formulas["Average priority"]
    decision = spec.column_letter("Crawler_Access", "Policy Decision")
    assert formulas["Crawlers undecided"] == f'=COUNTIF(Crawler_Access!{decision}:{decision},"Undecided")'


def test_validations_land_on_intended_headers(built: Path) -> None:
    wb = load_workbook(built / builder.WORKBOOK_NAME)
    issues = _validations(wb["Issue_Register"])
    status = spec.column_letter("Issue_Register", "Status")
    assert issues[f"{status}2:{status}500"] == '"Open,In progress,Blocked,Done,Won\'t do"'
    for header in ("Impact", "Effort", "Confidence", "Risk", "Speed"):
        letter = spec.column_letter("Issue_Register", header)
        assert issues[f"{letter}2:{letter}500"] == '"1,2,3,4,5"'
    crawler = _validations(wb["Crawler_Access"])
    decision = spec.column_letter("Crawler_Access", "Policy Decision")
    assert crawler[f"{decision}2:{decision}500"] == '"Allow,Block,Undecided,Monitor"'


def test_issue_register_formulas_and_formatting(built: Path) -> None:
    ws = load_workbook(built / builder.WORKBOOK_NAME)["Issue_Register"]
    priority = spec.column_letter("Issue_Register", "Priority")
    band = spec.column_letter("Issue_Register", "Priority Band")
    assert ws[f"{priority}2"].value == "=SUM(F2,I2,J2,H2)-G2"
    assert ws[f"{priority}500"].value.startswith('=IF(C500="","",SUM(F500')
    assert ws[f"{band}500"].value.startswith(f'=IF({priority}500="",""')
    ranges = {str(rng.sqref) for rng in ws.conditional_formatting}
    assert ranges == {f"{band}2:{band}500"}


def test_unwritable_out_dir_is_clean_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x")
    assert builder.main(["--out-dir", str(blocker)]) == 1
    assert capsys.readouterr().err.startswith("error: could not write the kit to")


def _sheet_snapshot(ws) -> dict[str, object]:
    """Everything about a sheet that the builder controls, in comparable form."""
    return {
        "values": [[cell.value for cell in row] for row in ws.iter_rows()],
        "header_style": [(c.fill.fgColor.rgb, c.font.b, c.alignment.horizontal) for c in ws[1]],
        "freeze_panes": ws.freeze_panes,
        "auto_filter": ws.auto_filter.ref,
        "widths": {key: dim.width for key, dim in ws.column_dimensions.items()},
        "validations": sorted(_validations(ws).items()),
        "conditional": [
            (str(rng.sqref), [(rule.type, rule.formula) for rule in rng.rules])
            for rng in ws.conditional_formatting
        ],
    }


def test_committed_workbook_matches_builder_output(built: Path) -> None:
    committed = load_workbook(kit_common.ASSETS_DIR / builder.WORKBOOK_NAME)
    fresh = load_workbook(built / builder.WORKBOOK_NAME)
    assert committed.sheetnames == fresh.sheetnames
    for title in committed.sheetnames:
        assert _sheet_snapshot(committed[title]) == _sheet_snapshot(fresh[title]), title


def test_missing_openpyxl_is_clean_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.setattr(builder, "MISSING_DEPENDENCY", "openpyxl is not installed")
    assert builder.main(["-o", str(tmp_path)]) == 1
    assert capsys.readouterr().err == "error: openpyxl is not installed\n"
    assert not any(tmp_path.iterdir())
