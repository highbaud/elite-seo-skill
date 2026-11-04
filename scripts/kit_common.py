"""Shared paths and file helpers for the Elite SEO kit scripts.

Standard library only, so the dependency-free GSC analyzer can import it too.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

# Portable: every path resolves relative to the skill folder these scripts live in.
SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
CSV_TEMPLATE_DIR = ASSETS_DIR / "csv-templates"

CellValue = str | int | float | None  # one spreadsheet/CSV cell; None renders as empty


def atomic_write(path: Path, write: Callable[[Path], None]) -> None:
    """Write ``path`` via a sibling temp file so readers never see a partial file.

    ``write`` receives the temp path and must create it. On success the temp file
    replaces ``path`` in one rename; on failure it is removed and ``path`` is untouched.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        write(tmp_path)
        os.replace(tmp_path, path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def write_csv(
    path: Path,
    headers: Sequence[str],
    rows: Iterable[Sequence[CellValue]],
    *,
    lineterminator: str = "\r\n",
) -> None:
    """Atomically write a UTF-8 CSV with a header row. ``None`` cells become empty strings.

    The default line ending is the csv module's CRLF. The committed templates under
    assets/csv-templates/ use LF, so the workbook builder passes ``lineterminator="\n"``.
    """

    def _write(tmp_path: Path) -> None:
        with tmp_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator=lineterminator)
            writer.writerow(headers)
            writer.writerows(["" if value is None else value for value in row] for row in rows)

    atomic_write(path, _write)


def run_builder(
    argv: Sequence[str] | None,
    *,
    description: str,
    out_dir_help: str,
    missing_dependency: str | None,
    build: Callable[[Path], Sequence[Path]],
) -> int:
    """Shared CLI for the asset builders; returns the process exit code.

    Parses ``-o/--out-dir`` (default: the skill's assets/ folder), reports a missing
    dependency or an unwritable output location as a one-line ``error:`` message,
    otherwise runs ``build(out_dir)`` and prints each path it reports writing.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-o", "--out-dir", type=Path, default=ASSETS_DIR, help=out_dir_help)
    out_dir: Path = parser.parse_args(argv).out_dir
    if missing_dependency:
        print(f"error: {missing_dependency}", file=sys.stderr)
        return 1
    try:
        written = build(out_dir)
    except OSError as exc:
        print(f"error: could not write to {out_dir}: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(f"wrote {path}")
    return 0
