# Elite SEO Operating Kit

This folder turns the SEO knowledge plan into a working audit and execution system.

## Start Here

1. Open `../../assets/elite-seo-master-audit-workbook.xlsx`.
2. Fill `Site_Profile`.
3. Run the `00-audit-intake-and-triage.md` process.
4. Add every finding to `Issue_Register`.
5. Use the priority formula instead of guessing what matters.
6. Build the 30/60/90 roadmap from the highest-scoring issues.

## Files

- `../../assets/elite-seo-master-audit-workbook.xlsx`: master workbook with tabs, formulas, dropdowns, and starter rows.
- `../../assets/csv-templates/`: CSV versions of every workbook tab for Google Sheets, Airtable, Notion, or a database.
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

`scripts/seo_gsc_analyzer.py` (no dependencies) converts raw GSC "Queries + Pages" exports into pre-filled rows:

```text
python scripts/seo_gsc_analyzer.py all previous.csv current.csv -o out/
# -> GSC_Opportunities_filled.csv (striking distance + position-adjusted low CTR)
# -> Cannibalization_filled.csv   (queries split across 2+ pages)
# -> Content_Decay_filled.csv     (pages losing 20%+ clicks period-over-period)
# -> Edit_Queue_filled.csv        (one ranked work queue, see below)
```

Paste the outputs into the matching workbook tabs, then score survivors into `Issue_Register`.

### One queue instead of three lists

`queue` mode scores every page three ways against the previous window, in clicks,
so the three are comparable. The biggest number wins and names the fix:

- `recover` -> clicks genuinely lost against the previous window. Fix: regression repair.
- `ctr` -> page-one clicks the page did not earn for the position it holds. Fix: title and meta rewrite.
- `rank` -> clicks a page-two result would gain by landing on page one. Fix: content push.

Two guardrails. Pages under the impression floor are dropped, because no edit fixes
"nobody is searching for this". And a page with a real click loss sorts above every
estimate-only page, whatever the size of the estimate.

The `ctr` and `rank` numbers are soft. GSC average position blends every query a page
ranks for, so both over-count. Use them to ORDER the queue, never as a forecast.

### Measuring an edit against a control

A page can rise because your edit worked, or because the whole site rose. Without the
second number you cannot tell the two apart. `snapshot` records the page AND the totals
of the same export for the same dates; `measure` re-reads both at +28 and +56 days and
reports the difference between them.

```text
# when the edit goes live
python scripts/seo_gsc_analyzer.py snapshot current.csv --url https://site.com/post --change-type ctr --date 2026-08-26 -o out/

# 28 days later, then again at 56
python scripts/seo_gsc_analyzer.py measure fresh.csv --checkpoint d28 -o out/
python scripts/seo_gsc_analyzer.py measure fresh.csv --checkpoint d56 -o out/
# -> Edit_Measurement_filled.csv
```

The control is the total of THAT export, not a true property-wide total, because GSC
caps export rows. It only holds if every export is pulled the same way: same property,
same filters, same row limit. `measure` is safe to re-run; it fills only rows that are
due and not already read.

## Workbook Tabs Worth Knowing

Beyond the audit tabs, the workbook includes: `Crawler_Access` (per-bot policy matrix covering Google, OpenAI, Perplexity, Anthropic, Apple, Meta, Common Crawl, and ByteDance crawlers, with the blocking consequence of each), `Log_File_Analysis` (crawl-budget and bot-behavior evidence), `Rank_Tracking` (positions plus AI-answer presence per surface), `Experiment_Log` (hypothesis-driven tests with position-controlled CTR rules), `Competitors` (business vs SERP-only competitors, link gaps, AI citations), `Agent_Readability` (per-page extractability, freshness, authorship, and answer-structure scoring for AI agents), `Edit_Queue` (one ranked work queue where the winning lever names the fix type), and `Edit_Measurement` (before-snapshot plus a same-dates control, re-read at +28 and +56 days).

## Rule

Do not treat every issue as equal. A true elite audit turns evidence into priority. If a recommendation cannot be tied to crawl access, search demand, trust, authority, conversion, or risk reduction, it should not make the roadmap.
