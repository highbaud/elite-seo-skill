# Elite SEO Skill

A portable, self-contained **SEO audit and strategy operating system** packaged as an [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills). Drop it into Claude Code (or any agent that reads `SKILL.md`) and it turns "review the SEO on this page" into a scored, evidence-backed audit with a 30/60/90 roadmap.

It works for SaaS, local service, ecommerce, publisher, affiliate/review, marketplace, personal-brand, and YMYL/regulated sites.

## What's inside

| Path | What it is |
| --- | --- |
| `SKILL.md` | Entry point: core rules, workflow, AI-search facts, routing |
| `references/elite-seo-knowledge-plan.md` | The full operating system — layered authority model, 14 phases, 90-day plan, outranking playbooks |
| `references/elite-seo-audit-strategy-expansion.md` | 24 diagnostic audit modules (crawl, rendering, index control, entities, cannibalization, CTR, decay, E-E-A-T, schema, ecommerce, local, international, migration QA, security, and more) |
| `references/kit/00-12*.md` | SOPs: intake/triage, fast wins, technical, content/authority, AI search/AEO, links/reputation, site-type playbooks, client report, red-team risk review, prompt pack, executive scorecard, master checklist, agent readability |
| `assets/elite-seo-master-audit-workbook.xlsx` | 31-tab audit workbook with a scored Issue Register, priority formulas, dropdowns, and a per-bot crawler-access matrix |
| `assets/csv-templates/` | Every workbook tab as a CSV for Google Sheets / Airtable / Notion / a database |
| `assets/elite-seo-audit-report-template.docx` | Client-ready audit report template |
| `scripts/seo_gsc_analyzer.py` | Dependency-free Google Search Console export analyzer |
| `scripts/build_*.py` | Regenerate the workbook, CSVs, and DOCX (tab definitions live in `scripts/workbook_spec.py`) |
| `tests/` | pytest suite for the analyzer, the generators, and the analyzer/workbook header contract |

## Design principles

- **Evidence before advice.** Every finding is scored (Impact + Confidence + Risk + Speed − Effort) and lands in the Issue Register, so priority comes from data, not vibes.
- **Sources are graded A–D / Red.** Primary docs vs. field practice vs. vendor claims vs. anecdotes vs. policy-risk tactics. C/D claims are never presented as facts.
- **Red lines are explicit.** No fake reviews, paid dofollow schemes, doorway pages, mass thin AI pages, cloaking, or impersonation.
- **AI search facts kept honest.** Correct handling of Google-Extended vs. AI Overviews, the Bing↔ChatGPT relationship, `llms.txt`, FAQ/HowTo rich-result deprecation, and prompt volatility.
- **Agent readability is a first-class audit.** A dedicated SOP and workbook tab for whether AI agents can extract, date, attribute, and parse a page (not just whether it ranks), with directional field benchmarks.

## Install

### Claude Code

```bash
git clone https://github.com/highbaud/elite-seo-skill.git ~/.claude/skills/elite-seo
```

It triggers automatically when you ask to review, audit, or improve SEO. For a project-local install, clone into `<project>/.claude/skills/elite-seo` instead.

### Any other agent

Point your agent at `SKILL.md`. It's plain Markdown with relative links; nothing is Claude-specific.

## Using the GSC analyzer

Export a Google Search Console "Queries + Pages" report for two periods, then:

```bash
python scripts/seo_gsc_analyzer.py all previous.csv current.csv -o out/
# -> GSC_Opportunities_filled.csv  (striking-distance + position-adjusted low CTR)
# -> Cannibalization_filled.csv    (queries split across pages)
# -> Content_Decay_filled.csv      (pages losing 20%+ clicks period-over-period)
```

Paste the output into the matching workbook tabs, then score survivors into the Issue Register.

## Regenerating the kit

The SOP docs in `references/` are plain Markdown: edit them directly.

The workbook, the CSV templates, and the DOCX report template are generated, so edit the generators, not the outputs. Every workbook tab (name, headers, starter rows, dropdowns) is declared once in `scripts/workbook_spec.py`; the GSC analyzer reads its output headers from the same spec, so the two can't drift apart.

```bash
pip install -r requirements.txt
python scripts/build_elite_seo_operating_kit.py   # workbook + CSV templates
python scripts/build_seo_report_docx.py           # DOCX report template
```

Both builders write into `assets/` by default; pass `--out-dir <dir>` to write somewhere else. All paths resolve relative to the skill folder, so it regenerates cleanly wherever it's cloned.

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
