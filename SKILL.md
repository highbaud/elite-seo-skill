---
name: elite-seo
description: Review, audit, or improve SEO for a page, a site, or a whole strategy (SaaS, local service, ecommerce, publisher, affiliate/review, marketplace, personal brand, YMYL). Use whenever the user asks to review SEO, improve SEO, audit SEO, do on-page or technical SEO, optimize a page for search, build an SEO or keyword/content plan, do link building or local SEO, improve AI search visibility (AEO/GEO, ChatGPT/Perplexity/AI Overviews citations), analyze content decay or cannibalization, or produce an SEO client report. Includes a 30-tab audit workbook, scored issue register, SOPs, site-type playbooks, GSC export analyzer, and client report templates.
---

# Elite SEO Operating Kit

A complete SEO audit and strategy operating system. Everything is self-contained in this folder: SOPs and strategy references in `references/`, ready-to-use templates in `assets/`, automation in `scripts/`.

## Core Rules (apply to every engagement)

1. **Evidence before advice.** Every finding gets a row in the Issue Register with Impact/Effort/Confidence/Risk/Speed scored 1-5. Priority = (Impact + Confidence + Risk + Speed) - Effort. Bands: 14+ fix now, 10-13 next sprint, 6-9 backlog, 5 or lower monitor.
2. **Grade every source.** A = primary docs (Google Search Central, OpenAI/Perplexity crawler docs). B = repeatable field practice. C = vendor claims (hypotheses only). D = social anecdotes. Red = policy-risk tactics. Never present C/D claims as facts.
3. **Red lines.** Never recommend: fake reviews, paid dofollow schemes, doorway pages, mass AI pages without unique value, cloaking, hidden text, competitor-domain impersonation, fake third-party review sites, inauthentic AI mentions, expired-domain abuse. Run `references/kit/08-red-team-risk-review.md` before any aggressive tactic.
4. **Triage order.** Fix access before content. Fix intent before links. Fix proof before conversion. Fix measurement before reporting wins.

## Workflow

1. **Intake** — follow `references/kit/00-audit-intake-and-triage.md`. Route by site type; apply the YMYL overlay for health/finance/legal/safety niches.
2. **Set up the workbook** — copy `assets/elite-seo-master-audit-workbook.xlsx` (or the CSVs in `assets/csv-templates/` for Sheets/Airtable/Notion). Fill `Site_Profile` first.
3. **Audit** — run the relevant SOPs:
   - Technical (crawl, indexation, rendering, canonicals, log files, IndexNow): `references/kit/02-technical-seo-sop.md`
   - Content, decay, cannibalization, topical authority: `references/kit/03-content-authority-sop.md`
   - AI search / AEO measurement and crawler policy: `references/kit/04-ai-search-aeo-sop.md`
   - Links, reviews, reputation, branded SERP: `references/kit/05-link-reputation-sop.md`
   - Quick wins first if the engagement needs fast proof: `references/kit/01-fast-wins-sop.md`
4. **Score and roadmap** — every finding into `Issue_Register`; build the 30/60/90 roadmap from the highest-scoring issues. Verify with `references/kit/11-master-checklist.md`.
5. **Deliver** — use `references/kit/07-client-report-template.md` (markdown) or `assets/elite-seo-audit-report-template.docx`, fronted by `references/kit/10-executive-scorecard.md`.

## AI Search Facts That Are Commonly Gotten Wrong

- Google AI Overviews/AI Mode are fed by normal Googlebot. Blocking `Google-Extended` opts out of Gemini training only; it does NOT remove AI Overviews visibility. Display controls are `nosnippet`, `max-snippet`, `data-nosnippet`.
- ChatGPT Search leans partly on Bing's index: Bing Webmaster Tools + IndexNow are AI-visibility work. `OAI-SearchBot` (search inclusion) is separate from `GPTBot` (training).
- Perplexity's user-triggered `Perplexity-User` fetches generally ignore robots.txt; control at the WAF if needed.
- `llms.txt` is optional agent usability, not a ranking lever and not required for Google AI features.
- FAQ rich results display only for authoritative gov/health sites; HowTo rich results are deprecated (both since 2023).
- AI answers are volatile: run each prompt 3+ times across days, log engine/region/account state, report mention/citation rates as fractions. Never claim "ranks #1 on ChatGPT" from one run.
- The full per-bot decision matrix (Google, OpenAI, Perplexity, Anthropic, Apple, Meta, Common Crawl, ByteDance) is the `Crawler_Access` workbook tab; every bot gets a deliberate Allow/Block decision.

## Automation

- **GSC analyzer** (no dependencies): `python scripts/seo_gsc_analyzer.py all previous.csv current.csv -o out/` converts GSC "Queries + Pages" exports into pre-filled rows for GSC_Opportunities (striking distance + position-adjusted low CTR), Cannibalization (queries split across pages), and Content_Decay (20%+ click drops).
- **Regenerate the kit** (needs `openpyxl`, `python-docx`): `python scripts/build_elite_seo_operating_kit.py` rebuilds the workbook, all CSV templates, and the SOP docs; `python scripts/build_seo_report_docx.py` rebuilds the DOCX report template. Paths are relative to this skill folder. Edit the generator scripts, never the generated files.

## Deep References

- `references/elite-seo-knowledge-plan.md` — the full operating system: layered authority model, 14 phases (baseline audit → measurement), 90-day execution plan, outranking playbooks, risk register.
- `references/elite-seo-audit-strategy-expansion.md` — the audit layer: 24 diagnostic modules (business, tracking, crawl, rendering, index control, IA, entities, cannibalization, CTR, decay, E-E-A-T, schema, ecommerce, local, international, multimodal, off-page, AI search, migration QA, page experience, security, deliverables, site-type roadmaps, final checklist).
- `references/kit/06-site-type-playbooks.md` — per-site-type priorities plus YMYL and enterprise overlays.
- `references/kit/09-elite-prompts.md` — copy-paste analysis prompts (SERP reverse engineering, refresh, cannibalization, AI visibility, linkable assets, risk review, log-file triage, internal links).

Load these on demand; do not read everything up front. For a quick engagement, SKILL.md + the relevant SOP + the workbook is enough.
