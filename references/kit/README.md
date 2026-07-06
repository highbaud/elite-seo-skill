# Elite SEO Operating Kit

This folder turns the SEO knowledge plan into a working audit and execution system.

## Start Here

1. Open `elite-seo-master-audit-workbook.xlsx`.
2. Fill `Site_Profile`.
3. Run the `00-audit-intake-and-triage.md` process.
4. Add every finding to `Issue_Register`.
5. Use the priority formula instead of guessing what matters.
6. Build the 30/60/90 roadmap from the highest-scoring issues.

## Files

- `elite-seo-master-audit-workbook.xlsx`: master workbook with tabs, formulas, dropdowns, and starter rows.
- `csv-templates/`: CSV versions of every workbook tab for Google Sheets, Airtable, Notion, or a database.
- `00-audit-intake-and-triage.md`: how to start an audit and route it by site type.
- `01-fast-wins-sop.md`: 48-hour, 7-day, and 30-day quick-win process.
- `02-technical-seo-sop.md`: crawl, indexation, rendering, canonical, sitemap, and schema workflow.
- `03-content-authority-sop.md`: topical authority, decay, refresh, cannibalization, and content strategy.
- `04-ai-search-aeo-sop.md`: AI visibility measurement without chasing fake AEO hacks.
- `05-link-reputation-sop.md`: links, mentions, reviews, PR, and branded SERP defense.
- `06-site-type-playbooks.md`: SaaS, local, ecommerce, publisher, affiliate, marketplace, and personal-brand modules.
- `07-client-report-template.md`: finished audit report template.
- `08-red-team-risk-review.md`: risk screen for tactics that can hurt a serious site.
- `09-elite-prompts.md`: copy-paste prompts for audits, briefs, refreshes, and AI search testing.
- `10-executive-scorecard.md`: one-page health snapshot for report covers and weekly operating reviews.
- `11-master-checklist.md`: the master pass before any strategy is delivered.
- `12-agent-readability-sop.md`: whether AI agents/browsers can extract, date, attribute, and parse pages, with field benchmarks.

## Automation

`scripts/seo_gsc_analyzer.py` (no dependencies) converts raw GSC "Queries + Pages" exports into pre-filled rows for three tabs:

```text
python scripts/seo_gsc_analyzer.py all previous.csv current.csv -o out/
# -> GSC_Opportunities_filled.csv (striking distance + position-adjusted low CTR)
# -> Cannibalization_filled.csv   (queries split across 2+ pages)
# -> Content_Decay_filled.csv     (pages losing 20%+ clicks period-over-period)
```

Paste the outputs into the matching workbook tabs, then score survivors into `Issue_Register`.

## Workbook Tabs Worth Knowing

Beyond the audit tabs, the workbook includes: `Crawler_Access` (per-bot policy matrix covering Google, OpenAI, Perplexity, Anthropic, Apple, Meta, Common Crawl, and ByteDance crawlers, with the blocking consequence of each), `Log_File_Analysis` (crawl-budget and bot-behavior evidence), `Rank_Tracking` (positions plus AI-answer presence per surface), `Experiment_Log` (hypothesis-driven tests with position-controlled CTR rules), `Competitors` (business vs SERP-only competitors, link gaps, AI citations), and `Agent_Readability` (per-page extractability, freshness, authorship, and answer-structure scoring for AI agents).

## Rule

Do not treat every issue as equal. A true elite audit turns evidence into priority. If a recommendation cannot be tied to crawl access, search demand, trust, authority, conversion, or risk reduction, it should not make the roadmap.
