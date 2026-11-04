"""Keep the docs honest: the SOP index is complete and every cited file exists."""

from __future__ import annotations

import re

import pytest

from kit_common import SKILL_ROOT

KIT_DIR = SKILL_ROOT / "references" / "kit"
# Backticked repo paths such as `references/kit/02-technical-seo-sop.md` or `assets/csv-templates/`.
CITED_PATH = re.compile(r"`((?:references|assets|scripts|tests)/[^`\s*]*)`")


def test_kit_readme_indexes_every_sop() -> None:
    index = (KIT_DIR / "README.md").read_text(encoding="utf-8")
    sops = sorted(p.name for p in KIT_DIR.glob("[0-9][0-9]-*.md"))
    assert sops, "no SOP files found"
    missing = [name for name in sops if f"`{name}`" not in index]
    assert not missing, f"SOPs not listed in references/kit/README.md: {missing}"


def test_kit_readme_lists_only_existing_sops() -> None:
    index = (KIT_DIR / "README.md").read_text(encoding="utf-8")
    listed = re.findall(r"`(\d\d-[^`]+\.md)`", index)
    assert [name for name in listed if not (KIT_DIR / name).exists()] == []


@pytest.mark.parametrize("doc", ["README.md", "SKILL.md"])
def test_cited_paths_exist(doc: str) -> None:
    text = (SKILL_ROOT / doc).read_text(encoding="utf-8")
    cited = set(CITED_PATH.findall(text))
    assert cited, f"expected {doc} to cite repo paths"
    missing = sorted(path for path in cited if not (SKILL_ROOT / path).exists())
    assert not missing, f"{doc} cites missing paths: {missing}"


def test_kit_readme_asset_paths_exist() -> None:
    index = (KIT_DIR / "README.md").read_text(encoding="utf-8")
    relative = re.findall(r"`(\.\./\.\./[^`]+)`", index)
    assert relative
    assert [p for p in relative if not (KIT_DIR / p).resolve().exists()] == []
