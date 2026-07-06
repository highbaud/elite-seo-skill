# Elite SEO Skill

A portable, self-contained **SEO audit and strategy operating system** packaged as an [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills). Drop it into Claude Code (or any agent that reads `SKILL.md`) and it turns "review the SEO on this page" into a scored, evidence-backed audit with a 30/60/90 roadmap.

It works for SaaS, local service, ecommerce, publisher, affiliate/review, marketplace, personal-brand, and YMYL/regulated sites.

## What's inside

| Path | What it is |
| --- | --- |
| `SKILL.md` | Entry point: core rules, workflow, AI-search facts, routing |
| `references/elite-seo-knowledge-plan.md` | The full operating system — layered authority model, 14 phases, 90-day plan, outranking playbooks |
| `references/elite-seo-audit-strategy-expansion.md` | 24 diagnostic audit modules (crawl, rendering, index control, entities, cannibalization, CTR, decay, E-E-A-T, schema, ecommerce, local, international, migration QA, security, and more) |
| `references/kit/00-11*.md` | SOPs: intake/triage, fast wins, technical, content/authority, AI search/AEO, links/reputation, site-type playbooks, client report, red-team risk review, prompt pack, executive scorecard, master checklist |
| `assets/elite-seo-master-audit-workbook.xlsx` | 30-tab audit workbook with a scored Issue Register, priority formulas, dropdowns, and a per-bot crawler-access matrix |
| `assets/csv-templates/` | Every workbook tab as a CSV for Google Sheets / Airtable / Notion / a database |
| `assets/elite-seo-audit-report-template.docx` | Client-ready audit report template |
| `scripts/seo_gsc_analyzer.py` | Dependency-free Google Search Console export analyzer |
| `scripts/build_*.py` | Regenerate the workbook, CSVs, SOPs, and DOCX from source |

## Design principles

- **Evidence before advice.** Every finding is scored (Impact + Confidence + Risk + Speed − Effort) and lands in the Issue Register, so priority comes from data, not vibes.
- **Sources are graded A–D / Red.** Primary docs vs. field practice vs. vendor claims vs. anecdotes vs. policy-risk tactics. C/D claims are never presented as facts.
- **Red lines are explicit.** No fake reviews, paid dofollow schemes, doorway pages, mass thin AI pages, cloaking, or impersonation.
- **AI search facts kept honest.** Correct handling of Google-Extended vs. AI Overviews, the Bing↔ChatGPT relationship, `llms.txt`, FAQ/HowTo rich-result deprecation, and prompt volatility.

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

The workbook, CSVs, SOP docs, and DOCX are generated. Edit the generator scripts, not the outputs:

```bash
pip install openpyxl python-docx
python scripts/build_elite_seo_operating_kit.py   # workbook + CSVs + SOP docs
python scripts/build_seo_report_docx.py           # DOCX report template
```

All paths resolve relative to the skill folder, so it regenerates cleanly wherever it's cloned.

## License

MIT — see [LICENSE](LICENSE).
