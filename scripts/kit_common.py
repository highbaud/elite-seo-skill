"""Shared paths and file helpers for the Elite SEO kit scripts.

Standard library only, so the dependency-free GSC analyzer can import it too.
"""

from __future__ import annotations

import csv
import os
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Union

# Portable: every path resolves relative to the skill folder these scripts live in.
SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
CSV_TEMPLATE_DIR = ASSETS_DIR / "csv-templates"

CsvValue = Union[str, int, float, None]


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
    headers: Sequence[CsvValue],
    rows: Iterable[Sequence[CsvValue]],
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
            writer.writerow(["" if value is None else value for value in headers])
            writer.writerows(["" if value is None else value for value in row] for row in rows)

    atomic_write(path, _write)
