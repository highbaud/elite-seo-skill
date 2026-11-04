"""Tests for scripts/build_seo_report_docx.py against the committed template."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytest.importorskip("docx")

from docx import Document  # noqa: E402

import build_seo_report_docx as mod  # noqa: E402
from kit_common import ASSETS_DIR, SKILL_ROOT  # noqa: E402

COMMITTED = ASSETS_DIR / mod.OUTPUT_NAME


def _paragraphs(path: Path) -> list[tuple[str, str, object]]:
    doc = Document(str(path))
    return [(p.text, p.style.name, p.alignment) for p in doc.paragraphs]


def _tables(path: Path) -> list[tuple[str, list[list[str]]]]:
    doc = Document(str(path))
    return [(t.style.name, [[c.text for c in r.cells] for r in t.rows]) for t in doc.tables]


@pytest.fixture()
def built(tmp_path: Path) -> Path:
    mod.main(["--out-dir", str(tmp_path)])
    path = tmp_path / mod.OUTPUT_NAME
    assert path.exists()
    return path


def test_paragraphs_match_committed(built: Path) -> None:
    assert _paragraphs(built) == _paragraphs(COMMITTED)


def test_headings_match_committed(built: Path) -> None:
    def headings(path: Path) -> list[str]:
        return [t for t, style, _ in _paragraphs(path) if style.startswith("Heading")]

    assert headings(built) == headings(COMMITTED)


def test_tables_match_committed(built: Path) -> None:
    assert _tables(built) == _tables(COMMITTED)


def test_page_setup_and_title_match_committed(built: Path) -> None:
    new, old = Document(str(built)), Document(str(COMMITTED))
    ns, os_ = new.sections[0], old.sections[0]
    for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        assert getattr(ns, attr) == getattr(os_, attr)
    assert new.styles["Normal"].font.name == old.styles["Normal"].font.name
    assert new.styles["Normal"].font.size == old.styles["Normal"].font.size
    nr, orr = new.paragraphs[0].runs[0], old.paragraphs[0].runs[0]
    assert (nr.bold, nr.font.size) == (orr.bold, orr.font.size)


def test_no_temp_files_left(built: Path) -> None:
    assert [p.name for p in built.parent.iterdir()] == [mod.OUTPUT_NAME]


def test_section_headings_numbered_sequentially() -> None:
    for expected, section in enumerate(mod.SECTIONS, start=1):
        match = re.match(r"(\d+)\. ", section.heading)
        assert match, section.heading
        assert int(match.group(1)) == expected


def test_table_specs_have_headers() -> None:
    tables = [s.body for s in mod.SECTIONS if isinstance(s.body, mod.TableBody)]
    assert tables
    for body in tables:
        assert len(body.headers) >= 1
        assert body.blank_rows >= 0


def test_unwritable_out_dir_is_clean_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x")
    assert mod.main(["--out-dir", str(blocker)]) == 1
    assert capsys.readouterr().err.startswith("error: could not write")


def _markdown_sections(path: Path) -> list[tuple[str, list[list[str]]]]:
    """(H2 heading, tables) pairs from a Markdown file; each table is its header row only."""
    sections: list[tuple[str, list[list[str]]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif sections and line.startswith("|") and not set(line) <= set("|- "):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            tables = sections[-1][1]
            if not tables:  # first table row is the header
                tables.append(cells)
    return sections


def test_markdown_template_matches_docx_sections() -> None:
    markdown = _markdown_sections(SKILL_ROOT / "references" / "kit" / "07-client-report-template.md")
    docx_headings = [re.sub(r"^\d+\.\s*", "", section.heading) for section in mod.SECTIONS]
    assert [heading for heading, _ in markdown] == docx_headings
    for (heading, tables), section in zip(markdown, mod.SECTIONS):
        if tables and isinstance(section.body, mod.TableBody):
            assert tables[0] == list(section.body.headers), heading
