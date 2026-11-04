"""Workbook tab definitions: the single source of truth for tab names and column headers.

Standard library only. The workbook builder renders these specs; the GSC analyzer
reads the headers of the tabs it pre-fills, so the two can never drift apart.

TEMPORARY STUB: only the three tabs the analyzer fills are defined here so far.
The workbook builder refactor moves every tab definition into this module.
"""

from __future__ import annotations

_HEADERS: dict[str, tuple[str, ...]] = {
    "GSC_Opportunities": (
        "Query", "Page", "Clicks", "Impressions", "CTR", "Position",
        "Opportunity Type", "Action", "Owner",
    ),
    "Cannibalization": (
        "Keyword / Intent", "URL 1", "URL 2", "Conflict Type",
        "Winning URL", "Decision", "Redirect / Canonical / Rewrite",
    ),
    "Content_Decay": (
        "URL", "Page Type", "Clicks 90d", "Clicks Previous 90d", "Delta",
        "Rank Change", "Freshness Need", "Backlinks", "Conversions", "Action",
    ),
}


def headers_for(title: str) -> list[str]:
    """Column headers of the workbook tab named ``title``. Raises KeyError for unknown tabs."""
    return list(_HEADERS[title])
