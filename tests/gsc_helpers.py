"""Shared row builders and CSV helpers for the GSC analyzer tests."""

from __future__ import annotations

import csv
from pathlib import Path

import seo_gsc_analyzer as gsc

HEADER = "query,page,clicks,impressions,ctr,position\n"


def row(query="q", page="/a", clicks=0, impressions=1000, position=5.0):
    return gsc.GscRow(query, page, float(clicks), float(impressions), float(position))


def write_export(path: Path, lines: list[str], header: str = HEADER, encoding: str = "utf-8") -> Path:
    path.write_text(header + "".join(line + "\n" for line in lines), encoding=encoding)
    return path


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))
