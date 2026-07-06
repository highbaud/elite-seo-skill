from pathlib import Path
import csv
from textwrap import dedent

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import FormulaRule
from openpyxl import load_workbook


# Portable: all paths resolve relative to the skill folder this script lives in.
SKILL_ROOT = Path(__file__).resolve().parent.parent
OUT = SKILL_ROOT / "assets"
CSV_DIR = OUT / "csv-templates"
DOCS = SKILL_ROOT / "references" / "kit"


BLUE = "1F4E79"
LIGHT_BLUE = "D9EAF7"
GREEN = "E2F0D9"
YELLOW = "FFF2CC"
RED = "F4CCCC"
GRAY = "E7E6E6"
WHITE = "FFFFFF"
BLACK = "000000"


def ensure_dirs():
    OUT.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)


def style_sheet(ws):
    header_fill = PatternFill("solid", fgColor=BLUE)
    header_font = Font(color=WHITE, bold=True)
    thin = Side(border_style="thin", color="D9D9D9")
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for column_cells in ws.columns:
        col_letter = get_column_letter(column_cells[0].column)
        max_len = 12
        for cell in column_cells:
            if cell.value is not None:
                max_len = max(max_len, min(len(str(cell.value)) + 2, 48))
        ws.column_dimensions[col_letter].width = max_len


def add_sheet(wb, title, headers, rows=None):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for row in rows or []:
        ws.append(row)
    style_sheet(ws)
    return ws


def add_list_validation(ws, col, values, start_row=2, end_row=500):
    formula = '"' + ",".join(values) + '"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}{start_row}:{col}{end_row}")


def build_workbook():
    wb = Workbook()
    wb.remove(wb.active)

    dashboard = add_sheet(
        wb,
        "Dashboard",
        ["Metric", "Formula / Value", "Notes"],
        [
            ["Open issues", '=COUNTIF(Issue_Register!O:O,"Open")', "Total unresolved audit issues"],
            ["Fix-now issues", '=COUNTIF(Issue_Register!L:L,"Fix now")', "Priority band 14+"],
            ["Technical issues", '=COUNTIF(Issue_Register!B:B,"Technical")', "Crawl/index/render/speed/schema"],
            ["Content issues", '=COUNTIF(Issue_Register!B:B,"Content")', "Intent, quality, decay, cannibalization"],
            ["Authority issues", '=COUNTIF(Issue_Register!B:B,"Authority")', "Links, mentions, PR, reputation"],
            ["AI visibility gaps", '=COUNTIF(Issue_Register!B:B,"AI Search")', "Mention/citation/crawler gaps"],
            ["Average priority", '=IFERROR(ROUND(AVERAGE(Issue_Register!K:K),1),"-")', "Formula: impact + confidence + risk + speed - effort"],
            ["30-day actions", '=COUNTIF(Roadmap_30_60_90!A:A,"30 days")', "Immediate execution load"],
            ["Critical red-line risks", '=COUNTIF(Risk_Register!D:D,"Red")', "Do not execute without explicit risk acceptance"],
            ["Experiments open", '=COUNTIF(Experiment_Log!J:J,"Running")', "Active tests with a decision pending"],
            ["Crawlers undecided", '=COUNTIF(Crawler_Access!E:E,"Undecided")', "Bot policies still needing a deliberate decision"],
            ["Agent-readability gaps", '=COUNTIF(Issue_Register!B:B,"Agent Readability")', "Extractability, dating, authorship, answer-structure gaps for AI agents"],
        ],
    )
    dashboard.column_dimensions["A"].width = 28
    dashboard.column_dimensions["B"].width = 24
    dashboard.column_dimensions["C"].width = 72

    add_sheet(
        wb,
        "Site_Profile",
        ["Field", "Answer", "Why it matters"],
        [
            ["Site / brand", "", "Defines entity consistency across SEO and AI surfaces"],
            ["Business model", "", "SaaS, local, ecommerce, publisher, affiliate, marketplace, lead gen"],
            ["Primary offer", "", "SEO should support revenue, not vanity traffic"],
            ["Average order / contract value", "", "Used to prioritize high-intent queries"],
            ["Top 5 competitors", "", "Separate business competitors from SERP competitors"],
            ["Primary geography", "", "Local, national, international, service area"],
            ["YMYL risk?", "", "Medical, legal, finance, safety, civic, health, high-trust topics"],
            ["Tech stack / CMS", "", "Impacts crawl/render/schema/migration fixes"],
            ["Primary conversion", "", "Lead, call, trial, purchase, subscription, demo"],
            ["Analytics stack", "", "GA4, CRM, call tracking, ecommerce, BI"],
            ["Existing SEO tools", "", "GSC, Bing, Ahrefs, Semrush, Screaming Frog, Surfer, Search Atlas"],
            ["Risk tolerance", "", "White-hat only, experimental allowed, no paid links, etc."],
        ],
    )

    add_sheet(
        wb,
        "Source_Reliability",
        ["Grade", "Definition", "Use", "Examples"],
        [
            ["A", "Primary documentation or first-party platform policy", "Can be treated as the base rule", "Google Search Central, OpenAI crawler docs, Perplexity docs"],
            ["B", "Repeatable field practice with broad industry support", "Use when it aligns with primary docs", "Content pruning, internal linking, log analysis, earned link outreach"],
            ["C", "Tool/vendor guidance or case study", "Use as hypothesis; verify on the site", "Surfer, Search Atlas, Ahrefs, agency studies"],
            ["D", "Social post, anecdote, one-off tactic", "Test only if low-risk and measurable", "X threads, Instagram reels, isolated screenshots"],
            ["Red", "Manipulative, deceptive, or policy-risk tactic", "Do not execute for serious projects", "Fake reviews, link schemes, doorway pages, inauthentic mentions"],
        ],
    )

    issue_headers = [
        "ID",
        "Module",
        "Issue",
        "Evidence",
        "Affected URL / Pattern",
        "Impact",
        "Effort",
        "Confidence",
        "Risk",
        "Speed",
        "Priority",
        "Priority Band",
        "Source Grade",
        "Owner",
        "Status",
        "Next Action",
        "Date Added",
    ]
    issue_rows = [
        ["SEO-001", "Technical", "Important pages missing from XML sitemap", "Sitemap vs crawl export mismatch", "/services/*", 4, 2, 4, 3, 4, "=SUM(F2,I2,J2,H2)-G2", '=IF(K2>=14,"Fix now",IF(K2>=10,"Next sprint",IF(K2>=6,"Backlog","Monitor")))', "A", "Dev", "Open", "Regenerate sitemap with canonical indexable URLs only", ""],
        ["SEO-002", "Content", "High-impression page has weak CTR", "GSC export", "/blog/example", 3, 1, 3, 2, 5, "=SUM(F3,I3,J3,H3)-G3", '=IF(K3>=14,"Fix now",IF(K3>=10,"Next sprint",IF(K3>=6,"Backlog","Monitor")))', "B", "SEO", "Open", "Rewrite title/meta and add snippet-supporting answer block", ""],
        ["SEO-003", "AI Search", "Competitors cited for category prompt but brand absent", "AI prompt tracker", "/compare/", 4, 3, 3, 3, 3, "=SUM(F4,I4,J4,H4)-G4", '=IF(K4>=14,"Fix now",IF(K4>=10,"Next sprint",IF(K4>=6,"Backlog","Monitor")))', "B", "Content", "Open", "Build answer-ready comparison hub and verify crawler access", ""],
    ]
    issue_ws = add_sheet(wb, "Issue_Register", issue_headers, issue_rows)
    for row in range(5, 501):
        issue_ws[f"K{row}"] = f"=IF(C{row}=\"\",\"\",SUM(F{row},I{row},J{row},H{row})-G{row})"
        issue_ws[f"L{row}"] = f"=IF(K{row}=\"\",\"\",IF(K{row}>=14,\"Fix now\",IF(K{row}>=10,\"Next sprint\",IF(K{row}>=6,\"Backlog\",\"Monitor\"))))"
    add_list_validation(issue_ws, "B", ["Technical", "Content", "Authority", "AI Search", "Agent Readability", "Local", "Ecommerce", "International", "Analytics", "Reputation", "Risk"])
    add_list_validation(issue_ws, "M", ["A", "B", "C", "D", "Red"])
    add_list_validation(issue_ws, "O", ["Open", "In progress", "Blocked", "Done", "Won't do"])
    for col in ["F", "G", "H", "I", "J"]:
        add_list_validation(issue_ws, col, ["1", "2", "3", "4", "5"])

    tables = {
        "URL_Inventory": [
            ["URL", "Status Code", "Indexability", "Canonical", "Title", "H1", "Template", "Organic Clicks 3m", "Impressions 3m", "Backlinks", "Conversions", "Action", "Notes"],
            ["/", 200, "Indexable", "/", "Homepage", "Brand", "Homepage", "", "", "", "", "Keep", ""],
        ],
        "Keyword_Map": [
            ["Cluster", "Keyword", "Intent", "Funnel Stage", "Current URL", "Target URL", "Current Rank", "SERP Format", "Business Value", "Difficulty", "Required Asset", "Action"],
            ["Core category", "", "Commercial", "Consideration", "", "", "", "Listicles / reviews / product pages", 5, 3, "Comparison hub", "Build"],
        ],
        "GSC_Opportunities": [
            ["Query", "Page", "Clicks", "Impressions", "CTR", "Position", "Opportunity Type", "Action", "Owner"],
            ["", "", "", "", "", "", "High impressions low CTR", "Rewrite title/meta and improve first answer", "SEO"],
        ],
        "Content_Decay": [
            ["URL", "Page Type", "Clicks 90d", "Clicks Previous 90d", "Delta", "Rank Change", "Freshness Need", "Backlinks", "Conversions", "Action"],
            ["", "Guide", "", "", "", "", "High", "", "", "Refresh"],
        ],
        "Cannibalization": [
            ["Keyword / Intent", "URL 1", "URL 2", "Conflict Type", "Winning URL", "Decision", "Redirect / Canonical / Rewrite"],
            ["", "", "", "True duplicate / intent split / format mismatch", "", "", ""],
        ],
        "Technical_Crawl": [
            ["URL", "Status", "Indexability", "Canonical Status", "Depth", "Inlinks", "Outlinks", "Response Time", "Issue", "Fix"],
            ["", "", "", "", "", "", "", "", "", ""],
        ],
        "Indexation": [
            ["URL", "GSC Status", "Sitemap?", "Canonical Declared", "Canonical Selected", "Robots", "Noindex?", "Action"],
            ["", "Crawled currently not indexed", "", "", "", "", "", ""],
        ],
        "JS_Rendering": [
            ["URL", "Raw HTML Content Present?", "Rendered Content Present?", "Crawlable Links?", "Canonical Stable?", "Structured Data Stable?", "Issue", "Action"],
            ["", "", "", "", "", "", "", ""],
        ],
        "Schema": [
            ["URL", "Page Type", "Schema Types", "Valid?", "Visible Content Match?", "Warnings", "Errors", "Action"],
            ["", "Product / Article / Local / Video", "", "", "", "", "", ""],
        ],
        "Internal_Links": [
            ["Source URL", "Target URL", "Anchor Text", "Link Location", "Reason", "Priority"],
            ["", "", "", "Body / nav / footer / related", "", ""],
        ],
        "Backlinks_Mentions": [
            ["Source Domain", "Source URL", "Target URL", "Anchor / Mention", "Follow Type", "Relevance", "Traffic", "Risk", "Action"],
            ["", "", "", "", "follow / nofollow / sponsored / ugc / unlinked", "", "", "", ""],
        ],
        "AI_Visibility": [
            ["Prompt", "Engine", "Date", "Region", "Brand Mentioned?", "Site Cited?", "Cited URL", "Competitors Cited", "Sentiment", "Gap", "Action"],
            ["best [category] for [use case]", "ChatGPT Search / Perplexity / Google AI", "", "", "", "", "", "", "", "", ""],
        ],
        "Reviews_Reputation": [
            ["Asset", "URL / Source", "Review Type", "Permission?", "Schema Eligible?", "Used On Pages", "Branded SERP Target", "Action"],
            ["", "", "Text / video / screenshot / case study", "", "", "", "[brand] review", ""],
        ],
        "Local_SEO": [
            ["Location", "GBP Status", "Primary Category", "NAP Consistent?", "Review Count", "Rating", "Local Page", "Citation Gaps", "Local Link Targets"],
            ["", "", "", "", "", "", "", "", ""],
        ],
        "Ecommerce": [
            ["URL / Template", "Type", "Product Data Complete?", "Schema Valid?", "Facet Risk", "Index Rule", "Merchant Feed Match?", "Action"],
            ["", "Product / Category / Facet / Variant", "", "", "", "", "", ""],
        ],
        "International": [
            ["Locale URL", "Language / Region", "Canonical", "Hreflang Return Tag?", "x-default?", "Localized Content?", "Issue", "Action"],
            ["", "", "", "", "", "", "", ""],
        ],
        "Migration_QA": [
            ["Old URL", "New URL", "Old Traffic", "Backlinks", "Redirect Status", "Canonical", "Internal Links Updated?", "QA Status"],
            ["", "", "", "", "", "", "", ""],
        ],
        "Platform_Distribution": [
            ["Platform", "Role", "Asset", "Canonical Owned URL", "Platform URL", "UTM", "Risk Grade", "Performance", "Next Action"],
            ["LinkedIn", "B2B authority", "", "", "", "", "B", "", ""],
        ],
        "Quick_Wins": [
            ["Window", "Opportunity", "Signal", "Action", "Owner", "Expected Impact", "Proof Needed"],
            ["48 hours", "Pages ranking 4-15", "GSC positions", "Improve title, internal links, answer block", "SEO", "Medium-high", "Rank/CTR change"],
        ],
        "Roadmap_30_60_90": [
            ["Timeframe", "Workstream", "Action", "Why It Matters", "Owner", "Success Metric", "Status"],
            ["30 days", "Technical", "Fix crawl/index blockers", "Unlock existing demand", "Dev/SEO", "Indexed priority URLs", "Open"],
            ["60 days", "Content", "Build comparison/review hub", "Capture consideration searches", "Content", "Commercial clicks/leads", "Open"],
            ["90 days", "Authority", "Launch data asset outreach", "Earn links and citations", "PR/SEO", "Referring domains/mentions", "Open"],
        ],
        "Risk_Register": [
            ["Tactic", "Why Tempting", "Risk", "Risk Grade", "Safer Alternative", "Decision"],
            ["Mass AI pages", "Scales fast", "Scaled content abuse if low-value", "Red", "Unique data pages with selective indexing", "Avoid"],
            ["Inauthentic AI mentions", "Looks like AEO shortcut", "Spam/reputation risk", "Red", "Earn real third-party mentions and reviews", "Avoid"],
            ["llms.txt for Google AI rankings", "Popular current claim", "Not needed for Google Search AI visibility", "C", "Use optional agent guide only", "Optional"],
        ],
        "Crawler_Access": [
            ["Bot / User-agent", "Operator", "What It Feeds", "Blocking Consequence", "Policy Decision", "Verified Access?", "Notes"],
            ["Googlebot", "Google", "Google Search, AI Overviews, AI Mode", "Removed from Google Search AND its AI answer features", "Allow", "", "There is no separate crawler to block only AI Overviews; use nosnippet/max-snippet/data-nosnippet for display control"],
            ["Google-Extended", "Google", "Gemini training and grounding", "Opts out of Gemini training; does NOT remove AI Overviews visibility", "Undecided", "", "Common misconception: blocking this does not affect Google Search or AI Overviews inclusion"],
            ["Bingbot", "Microsoft", "Bing, Copilot, and part of ChatGPT Search results", "Weakens visibility in Copilot and ChatGPT answers", "Allow", "", "Bing indexation matters for AI answers; submit via IndexNow and Bing Webmaster Tools"],
            ["OAI-SearchBot", "OpenAI", "ChatGPT Search surfacing/citations", "Site not eligible for ChatGPT Search summaries", "Allow", "", "Separate from GPTBot; OpenAI documents no guaranteed placement"],
            ["GPTBot", "OpenAI", "OpenAI model training", "Content excluded from future model training", "Undecided", "", "Deliberate business decision; independent from search inclusion"],
            ["ChatGPT-User", "OpenAI", "User-triggered live page fetches", "Users cannot pull the page into a chat", "Allow", "", ""],
            ["PerplexityBot", "Perplexity", "Perplexity search surfacing/citations", "Not surfaced in Perplexity results", "Allow", "", ""],
            ["Perplexity-User", "Perplexity", "User-triggered live fetches", "n/a", "Monitor", "", "Perplexity documents that user-triggered fetches generally ignore robots.txt; control at WAF level if needed"],
            ["ClaudeBot", "Anthropic", "Anthropic model training", "Content excluded from Claude training", "Undecided", "", ""],
            ["Claude-SearchBot / Claude-User", "Anthropic", "Claude search surfacing / user fetches", "Not cited in Claude answers", "Allow", "", ""],
            ["Applebot / Applebot-Extended", "Apple", "Siri, Spotlight / Apple AI training", "Applebot-Extended only opts out of AI training", "Undecided", "", ""],
            ["CCBot", "Common Crawl", "Open corpus used by many AI labs", "Excluded from Common Crawl derived training sets", "Undecided", "", ""],
            ["meta-externalagent", "Meta", "Meta AI training", "Excluded from Meta training", "Undecided", "", ""],
            ["Bytespider", "ByteDance", "ByteDance AI training", "Excluded if it complies", "Undecided", "", "Widely reported to ignore robots.txt; enforce at CDN/WAF if blocking matters"],
        ],
        "Log_File_Analysis": [
            ["URL Pattern", "Bot", "Hits 30d", "% of Total Crawl", "Status Mix", "Indexable?", "Crawl Value", "Issue", "Action"],
            ["/collections?sort=*", "Googlebot", "", "", "200", "No", "Waste", "Parameter crawl trap", "Canonical + robots strategy, then re-measure"],
            ["/guides/*", "Googlebot", "", "", "200", "Yes", "Under-crawled", "Important pages rarely hit", "Add hub/internal links, include in sitemap"],
        ],
        "Rank_Tracking": [
            ["Keyword", "Target URL", "Engine / Surface", "Date", "Position", "SERP Features", "AI Answer Present?", "Brand In AI Answer?", "Notes"],
            ["", "", "Google / Bing / Google AI / Local pack / Video", "", "", "", "", "", ""],
        ],
        "Experiment_Log": [
            ["Experiment", "Hypothesis", "Page / Platform", "Start Date", "Change Made", "Primary Metric", "Baseline", "Result", "Position Stable?", "Status", "Decision / Next Action"],
            ["Title rewrite test", "Specific title lifts CTR at same position", "", "", "", "CTR at position bucket", "", "", "", "Running", "Compare CTR only at stable positions; annotate change date"],
        ],
        "Competitors": [
            ["Competitor", "Type", "Domain", "Top Pages / Clusters", "Link Gap Targets", "AI Citations Seen", "Weaknesses", "Action"],
            ["", "Business + SERP / SERP only", "", "", "", "", "", ""],
        ],
        "Agent_Readability": [
            ["URL", "Meaningful Words (no JS)", "Extractable Static?", "Needs JS Render?", "Visible Date?", "Date Schema?", "Author Signal?", "Answer Capsule?", "FAQ / Q&A?", "Content Schema", "llms.txt?", "Sitemap Listed?", "Gaps", "Action"],
            ["/", "", "", "", "", "", "", "", "", "Article / Product / Organization / none", "", "", "", ""],
        ],
    }

    for name, data in tables.items():
        ws = add_sheet(wb, name, data[0], data[1:])
        if name == "Roadmap_30_60_90":
            add_list_validation(ws, "A", ["30 days", "60 days", "90 days", "Backlog"])
            add_list_validation(ws, "G", ["Open", "In progress", "Blocked", "Done"])
        if name == "Risk_Register":
            add_list_validation(ws, "D", ["A", "B", "C", "D", "Red"])
        if name == "Crawler_Access":
            add_list_validation(ws, "E", ["Allow", "Block", "Undecided", "Monitor"])
            add_list_validation(ws, "F", ["Yes", "No", "Not tested"])
        if name == "Experiment_Log":
            add_list_validation(ws, "J", ["Planned", "Running", "Done", "Abandoned"])
        if name == "Log_File_Analysis":
            add_list_validation(ws, "G", ["High value", "Normal", "Under-crawled", "Waste"])
        if name == "Agent_Readability":
            for col in ["C", "D", "E", "F", "G", "H", "I", "K", "L"]:
                add_list_validation(ws, col, ["Yes", "No", "Partial"])

    # Basic conditional formatting on issue priority bands.
    issue_ws.conditional_formatting.add("L2:L500", FormulaRule(formula=['$L2="Fix now"'], fill=PatternFill("solid", fgColor=RED)))
    issue_ws.conditional_formatting.add("L2:L500", FormulaRule(formula=['$L2="Next sprint"'], fill=PatternFill("solid", fgColor=YELLOW)))
    issue_ws.conditional_formatting.add("L2:L500", FormulaRule(formula=['$L2="Backlog"'], fill=PatternFill("solid", fgColor=GREEN)))

    workbook_path = OUT / "elite-seo-master-audit-workbook.xlsx"
    wb.save(workbook_path)
    return workbook_path


def export_csvs(workbook_path):
    wb = load_workbook(workbook_path, data_only=False)
    for ws in wb.worksheets:
        path = CSV_DIR / f"{ws.title}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(["" if value is None else value for value in row])


def write_text(path, content):
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def build_docs():
    write_text(
        DOCS / "README.md",
        """
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
        """,
    )

    write_text(
        DOCS / "00-audit-intake-and-triage.md",
        """
        # 00 Audit Intake and Triage

        ## Objective

        Turn a vague request like "improve SEO" into a scoped search strategy tied to revenue, risk, and execution.

        ## Intake Questions

        - What is the business model?
        - What is the primary conversion?
        - What is the average order value, contract value, or lead value?
        - What markets and languages matter?
        - Which products/services have the best margin?
        - Which pages already generate traffic or leads?
        - Which keywords are strategically important even if volume is low?
        - Which competitors win sales, and which competitors only win SERPs?
        - Is the site local, ecommerce, SaaS, publisher, affiliate, marketplace, personal brand, or hybrid?
        - Is the niche YMYL: health, finance, law, safety, civic, employment, or high-stakes advice?
        - What tactics are off limits?

        ## Site-Type Routing

        | Site type | Audit modules to prioritize |
        | --- | --- |
        | SaaS | Category, use case, integrations, alternatives, docs, reviews, security/compliance |
        | Local service | GBP, local pages, reviews, citations, local links, service-area proof |
        | Ecommerce | Product/category crawlability, facets, feeds, product schema, reviews, buying guides |
        | Publisher | Topic hubs, authors, freshness, Discover, video/image, pruning, ad experience |
        | Affiliate/review | First-hand proof, methodology, disclosures, comparison tables, trust |
        | Marketplace | Supply/demand pages, indexation controls, UGC moderation, location/category architecture |
        | Personal brand | Entity SERP, expertise proof, platform distribution, newsletter, branded search |
        | YMYL / regulated | Everything above PLUS expert review workflow, citation standards, compliance sign-off, disclaimer/disclosure audit |

        ## First 90 Minutes

        1. Fill `Site_Profile`.
        2. Verify GSC, Bing, analytics, and conversion tracking.
        3. Crawl the site.
        4. Export top GSC pages and queries.
        5. Search branded, review, comparison, and category terms manually.
        6. Run 10 AI search prompts and record mentions/citations.
        7. Inspect robots.txt, sitemap, canonicals, and noindex patterns.
        8. Pick the first 10 findings for `Issue_Register`.

        ## Triage Rule

        Fix access before content. Fix intent before links. Fix proof before conversion. Fix measurement before reporting wins.
        """,
    )

    write_text(
        DOCS / "01-fast-wins-sop.md",
        """
        # 01 Fast Wins SOP

        ## 48-Hour Wins

        - Add internal links to pages ranking positions 4-15.
        - Rewrite titles/meta for high-impression low-CTR pages.
        - Fix accidental noindex/canonical conflicts.
        - Submit cleaned sitemap.
        - Fix broken links on high-value pages.
        - Add review proof to money pages.
        - Add answer blocks to pages already earning impressions.
        - Replace old years in titles/body where the content is current.
        - Fix missing H1/title duplicates on priority templates.
        - Add clear CTAs to informational pages with commercial intent.

        ## 7-Day Wins

        - Refresh 5-10 decaying pages.
        - Consolidate obvious cannibalization.
        - Build a branded review hub v1.
        - Build one comparison or alternatives page.
        - Add schema to eligible templates.
        - Create a quick YouTube/video transcript asset for the highest-value FAQ.
        - Reclaim unlinked brand mentions.
        - Fix top crawl waste patterns.

        ## 30-Day Wins

        - Build one topic cluster around the highest-value category.
        - Launch one linkable asset.
        - Build a platform distribution pack for LinkedIn, YouTube, Reddit, Medium, GitHub, or Substack.
        - Run outreach to relevant resource/listicle/comparison pages.
        - Build AI visibility baseline and improve pages competitors are cited for.

        ## Measurement Discipline

        - Log every title/meta rewrite in `Experiment_Log` with the change date.
        - Judge CTR changes only at comparable positions. A page that moved from 8 to 4 will show higher CTR regardless of the new title; compare CTR within the same position bucket before and after.
        - Give changes 14-28 days and check seasonality before declaring a win.
        - Batch changes per template, not per page, so you can attribute movement.

        ## Scoring

        Every quick win still goes in `Issue_Register`. If it cannot score, it is not a quick win; it is a distraction.
        """,
    )

    write_text(
        DOCS / "02-technical-seo-sop.md",
        """
        # 02 Technical SEO SOP

        ## Crawl Setup

        Crawl with both normal HTML and JavaScript rendering when the site depends on JS. Export all URLs, status codes, titles, meta descriptions, H1s, canonicals, indexability, inlinks, depth, structured data, and response times.

        ## Access Checks

        - Googlebot can fetch HTML, CSS, JS, images, and video thumbnails.
        - Bingbot can fetch important pages.
        - OAI-SearchBot can access public pages meant for ChatGPT Search.
        - PerplexityBot can access public pages meant for Perplexity.
        - GPTBot policy is intentional because it is separate from OAI-SearchBot.
        - WAF/CDN rules do not block verified search crawlers.

        ## Index-Control Checks

        - XML sitemaps include only canonical indexable URLs.
        - Canonicals point to 200 indexable URLs.
        - Robots.txt is not blocking pages that need crawler-readable noindex.
        - Sort/search/session/cart/account URLs are controlled.
        - Facets with demand are handled as static indexable URLs; junk combinations are controlled.

        ## JavaScript Checks

        - Main content exists in raw or reliably rendered HTML.
        - Links are real `<a href>` links.
        - Canonicals do not change between raw and rendered DOM.
        - Structured data matches visible content.
        - Infinite scroll exposes crawlable pagination.

        ## Log-File Quick Pass

        Even a 30-day sample from server or CDN logs answers questions a crawler cannot:

        1. Rank URL patterns by Googlebot hits. Flag the top crawl-waste patterns (parameters, redirects, 404s, session URLs).
        2. Cross-reference priority pages against crawl frequency. Important pages Googlebot rarely visits need internal links and sitemap presence, not more content.
        3. Compare status codes served to bots vs users. Mismatches are rendering, WAF, or cloaking-adjacent bugs.
        4. Record which AI crawlers actually hit the site; this validates the `Crawler_Access` policy instead of assuming it.

        Record findings in `Log_File_Analysis` and score crawl-waste fixes in `Issue_Register`.

        ## Indexing Speed

        For Bing and everything downstream of it (Copilot, part of ChatGPT Search), implement IndexNow or use Bing Webmaster Tools URL submission. It is cheap, supported, and shortens discovery for new/changed pages. Google has no equivalent for normal sites; rely on sitemaps, internal links, and (sparingly) URL Inspection.

        ## Schema Checks

        Validate by template, not random samples. Product, Article, LocalBusiness, VideoObject, Organization, BreadcrumbList, FAQPage, Dataset, Course, Event, and JobPosting all have different eligibility rules. Schema is a clarification layer, not a way to invent facts.

        Rich-result reality check (both changed in 2023 and much older advice ignores it):

        - FAQ rich results now display only for well-known, authoritative government and health sites. FAQPage markup elsewhere is harmless but should not be sold as a SERP feature win.
        - HowTo rich results were deprecated entirely. Do not add HowTo markup expecting display.

        ## Output

        Add every issue to `Issue_Register` with affected URL pattern, evidence, owner, and priority score.
        """,
    )

    write_text(
        DOCS / "03-content-authority-sop.md",
        """
        # 03 Content and Authority SOP

        ## Content Audit Workflow

        1. Export all URLs.
        2. Join crawl data, GSC data, backlink data, and conversion data.
        3. Classify each URL by page type and intent.
        4. Assign action: keep, refresh, expand, merge, redirect, noindex, delete, repurpose, add links, or build links.
        5. Prioritize pages with impressions, links, conversions, or strategic value.

        ## Cannibalization Rules

        - If two pages answer the same intent, consolidate.
        - If one page serves two intents badly, split.
        - If a blog ranks for a money query, strengthen the money page and link between them.
        - If Reddit/forums dominate, add lived experience, examples, quotes, screenshots, and FAQs.

        ## Topic Cluster Build

        A complete cluster has:

        - Core category page.
        - Use-case pages.
        - Problem/solution guides.
        - Comparison and alternatives pages.
        - Reviews/proof pages.
        - FAQ/support pages.
        - Data/tool/template asset.
        - Internal links between all relevant nodes.

        ## Refresh Standard

        A refresh is not changing the date. A real refresh updates facts, examples, screenshots, proof, internal links, SERP fit, title/meta, schema, and CTAs.
        """,
    )

    write_text(
        DOCS / "04-ai-search-aeo-sop.md",
        """
        # 04 AI Search and AEO SOP

        ## Principle

        For Google AI features, good SEO is still the base. Google says site owners do not need special AI files such as `llms.txt`, content chunking, AI-only markup, or inauthentic mentions to appear in generative AI search. Treat AEO as a measurement and content-clarity layer, not a hack layer.

        ## Measurement Layers

        - Mention: does the answer name the brand?
        - Citation: does it link or cite the site?
        - Prominence: is the brand first, buried, or framed as an alternative?
        - Sentiment: positive, neutral, negative, inaccurate.
        - Impact: referrals, leads, assisted conversions, sales-call mentions.

        ## Prompt Set

        - `[brand] review`
        - `is [brand] legit`
        - `[brand] pricing`
        - `[brand] vs [competitor]`
        - `[competitor] alternatives`
        - `best [category] for [use case]`
        - `what should I know before buying [category]`
        - `best [service] in [city]`

        ## Crawler Policy

        Use the `Crawler_Access` workbook tab as the full per-bot decision matrix. The rules that prevent the most common mistakes:

        - Google AI Overviews and AI Mode are fed by normal Googlebot crawling. There is no crawler that blocks only Google's AI features; `nosnippet`, `max-snippet`, and `data-nosnippet` are the display controls.
        - Blocking `Google-Extended` opts out of Gemini training/grounding. It does NOT remove the site from AI Overviews. Do not sell it as either protection from or a lever for Google AI visibility.
        - ChatGPT Search leans partly on Bing's index. Bing Webmaster Tools verification and IndexNow are AI-visibility work, not optional extras.
        - Allow OAI-SearchBot for public pages you want eligible for ChatGPT Search. Decide GPTBot separately; it only affects training.
        - Allow PerplexityBot for Perplexity discovery. Note Perplexity documents that user-triggered `Perplexity-User` fetches generally ignore robots.txt; if that matters, control it at the WAF.
        - Do not expose private/member/account paths to any crawler.

        ## Volatility Protocol

        AI answers vary by model version, account state, region, phrasing, and day. A single prompt run is an anecdote, not a baseline.

        - Run each prompt at least 3 times across different days before recording a baseline, and re-run the full set monthly.
        - Log engine, date, region, and logged-in/logged-out state with every run.
        - Report mention/citation rates as fractions ("cited in 2 of 6 runs"), never as "we rank #1 on ChatGPT".
        - Treat competitor citation patterns that persist across runs as signal; one-off appearances as noise.

        ## Answer-Ready Page Pattern

        - Clear entity/category sentence.
        - Direct answer in the first section.
        - Comparison table where useful.
        - Proof: reviews, screenshots, data, demos, case studies.
        - Current date and reviewer/author.
        - Crawlable HTML.
        - Third-party corroboration where possible.

        ## llms.txt Position

        Optional for agent usability. Not a Google Search AI requirement. If used, make it a short map to canonical resources, not a second SEO website.
        """,
    )

    write_text(
        DOCS / "05-link-reputation-sop.md",
        """
        # 05 Link, Reputation, and Review SOP

        ## Link Quality Standard

        Score links by topical relevance, editorial standards, placement context, indexation, traffic, referral potential, and brand safety. DR alone is not a strategy.

        ## Linkable Assets

        - Original data report.
        - Calculator.
        - Template/checklist.
        - Open-source tool.
        - Visual explainer.
        - Industry statistics page.
        - Comparison database.
        - Local resource.
        - Expert survey.

        ## Outreach Targets

        - Broken competitor links.
        - Outdated resources.
        - Relevant listicles.
        - Partner/vendor pages.
        - Customer pages.
        - Local associations.
        - Podcasts/newsletters.
        - Journalists covering the niche.

        ## Review System

        Every real review should become:

        - Review database entry.
        - Review hub asset.
        - Relevant money page proof.
        - Social post.
        - Video/testimonial if possible.
        - Sales proof asset.
        - Branded SERP support.

        Never fake reviews, undisclosed incentives, or third-party-looking review sites controlled by the brand.
        """,
    )

    write_text(
        DOCS / "06-site-type-playbooks.md",
        """
        # 06 Site-Type Playbooks

        ## SaaS

        Build category, use-case, industry, role, integration, alternatives, vs, pricing, security, docs, API, template, and case-study clusters. The fastest wins usually come from comparison pages, integration pages, and proof-heavy category pages.

        ## Local Service

        Prioritize Google Business Profile, reviews, service/location pages, local proof, citations, local links, photos, cost pages, and emergency/near-me intent where legitimate.

        ## Ecommerce

        Prioritize crawlable product/category templates, controlled facets, product schema, Merchant Center feed quality, unique category copy, review content, buying guides, product images, and out-of-stock handling.

        ## Publisher

        Prioritize author expertise, topic hubs, freshness, internal links, Discover/image/video optimization, archive rules, ad experience, and original reporting.

        ## Affiliate / Review Site

        Prioritize first-hand testing proof, transparent methodology, pros/cons, update dates, disclosures, comparison tables, author trust, and avoiding thin rewrites of vendor pages.

        ## Marketplace

        Prioritize supply/demand page architecture, location/category indexation, UGC moderation, duplicate controls, crawl traps, marketplace trust, and conversion paths for both sides.

        ## Personal Brand

        Prioritize entity SERP, about page, credentials, social profiles, podcast/video presence, newsletter capture, speaking/press mentions, branded review/reputation queries, and owned hub content.

        ## YMYL / Regulated (overlay on any type above)

        Health, finance, legal, safety, and civic topics get judged on trust evidence, not volume. Add on top of the base playbook:

        - Named, credentialed authors and a documented expert-review workflow with visible review dates.
        - Citations to primary sources for every factual or statistical claim.
        - Compliance/legal sign-off in the publish pipeline, not after publication.
        - Disclosure and disclaimer audit: affiliate, sponsorship, advisory, and regulatory disclosures present and accurate.
        - Slower cadence, higher bar: one reviewed, sourced page beats five unreviewed ones in these niches.

        ## Enterprise / Multi-Team (overlay for large orgs)

        - SEO QA gate in the release process: title/meta/canonical/index-directive/schema checks run before deploy, not discovered after.
        - A named owner per workstream (`Issue_Register` Owner column is the contract; no unowned issues).
        - Crawl-budget review quarterly from logs (`Log_File_Analysis`), because template bugs at scale dwarf page-level wins.
        - Change annotations: every template change, migration, and robots edit gets a dated log entry so traffic moves can be attributed.
        """,
    )

    write_text(
        DOCS / "07-client-report-template.md",
        """
        # 07 SEO Audit Report Template

        ## Executive Summary

        The site has [strengths], but organic growth is limited by [top blockers]. The highest-impact work is [priority 1], [priority 2], and [priority 3]. If implemented in order, the expected outcome is [traffic/conversion/risk impact] over [time horizon].

        ## What Is Working

        - [Strength 1]
        - [Strength 2]
        - [Strength 3]

        ## Biggest Blockers

        | Priority | Issue | Evidence | Impact | Owner |
        | --- | --- | --- | --- | --- |

        ## Biggest Opportunities

        | Priority | Opportunity | Why it matters | Expected metric |
        | --- | --- | --- | --- |

        ## Technical Findings

        Summarize crawl, indexation, rendering, canonical, sitemap, schema, speed, migration, and security findings.

        ## Content Findings

        Summarize intent gaps, cannibalization, decay, topical authority, content quality, review proof, and internal links.

        ## Authority and Reputation Findings

        Summarize backlinks, mentions, reviews, branded SERP, digital PR assets, and risk.

        ## AI Search Findings

        Summarize prompt coverage, mentions, citations, competitors cited, crawler access, and answer-ready content gaps.

        ## 30/60/90 Roadmap

        | Timeframe | Workstream | Action | Owner | Success metric |
        | --- | --- | --- | --- | --- |

        ## Appendix

        Attach crawl exports, GSC exports, AI prompt tracker, issue register, keyword map, and content audit.
        """,
    )

    write_text(
        DOCS / "08-red-team-risk-review.md",
        """
        # 08 Red-Team Risk Review

        Run this before executing any aggressive tactic.

        ## Red-Line Tactics

        - Fake reviews.
        - Inauthentic Reddit/forum participation.
        - Paid dofollow link schemes.
        - Doorway city pages.
        - Mass AI pages without unique value.
        - Expired-domain abuse.
        - Parasite content that exists only to exploit host authority.
        - Competitor-domain impersonation.
        - Hidden links/text.
        - Cloaking.
        - Scraped or spun content.
        - Fake third-party review sites.
        - Inauthentic AI mentions.

        ## Risk Questions

        - Would this help a real user if search engines did not exist?
        - Is the brand pretending to be someone else?
        - Is compensation or control hidden?
        - Is the same page being mass-produced with shallow swaps?
        - Would we be comfortable showing this tactic to Google, a customer, or a journalist?
        - Is there a safer way to get the same business outcome?

        ## Decision

        If any answer creates serious reputational, legal, or policy risk, mark the tactic `Red` in `Risk_Register` and replace it with the safer alternative.
        """,
    )

    write_text(
        DOCS / "09-elite-prompts.md",
        """
        # 09 Elite SEO Prompts

        ## SERP Reverse Engineering

        ```text
        Analyze the top search results for [keyword]. Classify search intent, page type, SERP features, proof used, freshness, content gaps, backlink/authority signals, and what a page would need to do to deserve to rank. Separate verified observations from hypotheses.
        ```

        ## Content Refresh

        ```text
        Given this page and its target queries, identify what is outdated, what search intent is under-served, what proof is missing, what internal links should be added, what title/meta changes may improve CTR, and what sections should be merged, removed, or expanded.
        ```

        ## Cannibalization Diagnosis

        ```text
        These URLs all receive impressions for [keyword/intent]. Determine whether this is true cannibalization, intent split, SERP mismatch, or healthy multi-page coverage. Recommend keep, merge, redirect, rewrite, or differentiate.
        ```

        ## AI Visibility Test

        ```text
        For the prompt [prompt], compare the answer across ChatGPT Search, Perplexity, Google AI results, and Bing/Copilot. Track brand mention, citation, prominence, sentiment, competitors cited, missing proof, and the next content action.
        ```

        ## Linkable Asset Ideation

        ```text
        For [industry/site], propose 10 linkable assets that journalists, bloggers, partners, and communities would have a real reason to cite. Include data required, production effort, outreach targets, and expected link angle.
        ```

        ## Risk Review

        ```text
        Red-team this SEO tactic: [tactic]. Identify policy risk, reputational risk, legal risk, user value, safer alternatives, and whether it should be graded A, B, C, D, or Red.
        ```

        ## Log-File Triage

        ```text
        Here is a summary of bot hits by URL pattern from the last 30 days [paste]. Identify crawl waste, under-crawled priority sections, bot/user status-code mismatches, and AI crawlers present. Rank the top 5 crawl-budget fixes by expected impact and state the evidence for each.
        ```

        ## Internal Link Opportunities

        ```text
        Given this list of pages with their topics, traffic, and current inlink counts [paste], propose the 20 highest-value internal links to add. For each: source URL, target URL, suggested anchor, and why it helps (ranking support, conversion path, or crawl discovery). Prefer links from high-traffic or high-authority pages to under-linked money and cluster pages.
        ```
        """,
    )

    write_text(
        DOCS / "10-executive-scorecard.md",
        """
        # 10 Executive SEO Scorecard

        Use this as the first page of an audit report or weekly operating review.

        ## SEO Health Snapshot

        | Area | Score / 10 | Status | Notes |
        | --- | ---: | --- | --- |
        | Technical access |  | Green / Yellow / Red | Crawlability, indexation, rendering, sitemap, canonicals |
        | Content quality |  | Green / Yellow / Red | Intent fit, helpfulness, proof, freshness |
        | Authority |  | Green / Yellow / Red | Links, mentions, PR, topical trust |
        | Reputation |  | Green / Yellow / Red | Reviews, branded SERP, testimonials, trust evidence |
        | AI visibility |  | Green / Yellow / Red | Mentions, citations, crawler access, answer-ready pages |
        | Local/ecommerce/international |  | Green / Yellow / Red | Only score modules that apply |
        | Measurement |  | Green / Yellow / Red | GSC, Bing, GA4, CRM, conversions, dashboards |

        ## Top 5 Fixes

        | Priority | Fix | Why it matters | Owner | Deadline |
        | ---: | --- | --- | --- | --- |
        | 1 |  |  |  |  |
        | 2 |  |  |  |  |
        | 3 |  |  |  |  |
        | 4 |  |  |  |  |
        | 5 |  |  |  |  |

        ## Top 5 Growth Bets

        | Priority | Opportunity | Search surface | Expected payoff | Owner |
        | ---: | --- | --- | --- | --- |
        | 1 |  | Google / Bing / AI / Local / Video / Image |  |  |
        | 2 |  | Google / Bing / AI / Local / Video / Image |  |  |
        | 3 |  | Google / Bing / AI / Local / Video / Image |  |  |
        | 4 |  | Google / Bing / AI / Local / Video / Image |  |  |
        | 5 |  | Google / Bing / AI / Local / Video / Image |  |  |

        ## This Week

        - Ship:
        - Measure:
        - Decide:
        - Blocked by:

        ## Executive Decision Needed

        State the decision, options, recommendation, risk, and cost of waiting.
        """,
    )

    write_text(
        DOCS / "11-master-checklist.md",
        """
        # 11 Master SEO Audit Checklist

        ## Intake

        - [ ] Business model defined.
        - [ ] Primary conversion defined.
        - [ ] Site type selected.
        - [ ] Target markets selected.
        - [ ] Competitors separated into business competitors and SERP competitors.
        - [ ] Risk tolerance documented.
        - [ ] YMYL/high-trust risk documented.

        ## Measurement

        - [ ] Google Search Console verified.
        - [ ] Bing Webmaster Tools verified.
        - [ ] IndexNow implemented or consciously skipped.
        - [ ] GA4 installed once.
        - [ ] Primary conversions tracked.
        - [ ] CRM/source attribution checked.
        - [ ] AI referral filters created.
        - [ ] UTM rules documented.

        ## Technical

        - [ ] Crawl complete.
        - [ ] JavaScript rendering checked.
        - [ ] Indexation states mapped.
        - [ ] Robots.txt reviewed.
        - [ ] XML sitemaps reviewed.
        - [ ] Canonicals reviewed.
        - [ ] Redirect chains checked.
        - [ ] Broken links checked.
        - [ ] Page templates speed checked.
        - [ ] Structured data validated.
        - [ ] Mobile rendering checked.
        - [ ] Log-file quick pass done (or logged as unavailable).
        - [ ] Bot access checked for Googlebot, Bingbot, OAI-SearchBot, and PerplexityBot where relevant.
        - [ ] `Crawler_Access` tab decisions made for every listed bot.

        ## Content

        - [ ] Keyword map complete.
        - [ ] Search intent mapped.
        - [ ] SERP format mapped.
        - [ ] Cannibalization identified.
        - [ ] Content decay identified.
        - [ ] Refresh queue built.
        - [ ] Internal link opportunities mapped.
        - [ ] Comparison/review/pricing/support gaps identified.
        - [ ] E-E-A-T evidence gaps documented.

        ## Authority

        - [ ] Backlink profile reviewed.
        - [ ] Link risks identified.
        - [ ] Lost/broken links identified.
        - [ ] Unlinked mentions identified.
        - [ ] Competitor link gaps identified.
        - [ ] Digital PR asset selected.
        - [ ] Outreach targets built.

        ## Reputation

        - [ ] Review hub exists or is scoped.
        - [ ] Customer proof collected.
        - [ ] Branded SERP checked.
        - [ ] Negative/incorrect claims checked.
        - [ ] Testimonials have permission.
        - [ ] Review schema eligibility checked.

        ## AI Search

        - [ ] Prompt set created.
        - [ ] Each prompt run at least 3 times across days before baselining.
        - [ ] ChatGPT Search tested.
        - [ ] Perplexity tested.
        - [ ] Google AI results checked where available.
        - [ ] Mentions and citations separated.
        - [ ] Competitors cited recorded.
        - [ ] Answer-ready content gaps identified.
        - [ ] Crawler policy documented.
        - [ ] `llms.txt` treated as optional agent usability, not Google AI ranking requirement.

        ## Site-Type Modules

        - [ ] Local SEO module complete if location matters.
        - [ ] Ecommerce module complete if products/inventory matter.
        - [ ] International module complete if multiple languages/countries matter.
        - [ ] Publisher module complete if freshness/news/Discover matters.
        - [ ] SaaS module complete if product-led/category/comparison search matters.
        - [ ] Affiliate/review module complete if recommendations drive revenue.
        - [ ] YMYL overlay applied if the niche is health, finance, legal, safety, or civic.

        ## Roadmap

        - [ ] Every finding added to Issue_Register.
        - [ ] Impact, effort, confidence, risk, and speed scored.
        - [ ] 30/60/90 roadmap built.
        - [ ] Owners assigned.
        - [ ] Success metrics assigned.
        - [ ] Experiments logged in Experiment_Log with baselines.
        - [ ] Agent-readability pass done on priority pages (see 12).
        - [ ] Red-team risk review complete.
        """,
    )

    write_text(
        DOCS / "12-agent-readability-sop.md",
        """
        # 12 Agent Readability and Agentic SEO SOP

        ## Why This Exists

        Search is no longer only humans and classic crawlers. AI agents and agentic browsers fetch a page, try to extract text fast, and then decide whether the page is usable as an answer or citation. A page can rank fine for humans yet be nearly invisible to an agent because it cannot be extracted, dated, attributed, or parsed into answer units.

        This overlaps with but is distinct from `04-ai-search-aeo-sop.md`. That SOP measures whether you get cited. This SOP fixes whether an agent can even read and trust the page in the first place. Do this pass on priority money, comparison, and proof pages; agent readability is worth most where a citation converts.

        ## The 10 Agent-Readability Gaps

        The benchmark column is from a field measurement of company sites (aggregate and directional, Source Grade B/C, not Google-official). Use it to judge whether a client is better or worse than typical, not as a hard target.

        | # | Gap | Typical benchmark | Why it matters for agents | How to check | Fix |
        | --- | --- | --- | --- | --- | --- |
        | 1 | Thin / non-extractable pages | ~36% of pages | If an agent can fetch but not extract meaningful text, the page effectively disappears | Fetch raw HTML, strip boilerplate, count meaningful words; flag under ~150-200 | Real content in semantic HTML; move key copy out of images/canvas/embeds |
        | 2 | Static extraction gaps / JS dependency | ~21% | Agents often extract static text before rendering; JS-only content is missed | Diff raw HTML text vs rendered DOM text | SSR/prerender the primary copy and answer into initial HTML |
        | 3 | Browser rendering required | ~13% | Full-render-only pages cost latency, so agents inspect them less | Load with JS disabled; is core content present? | Server-render primary content and structured data |
        | 4 | Undated content | ~77% | Agents use freshness to trust recommendations | Visible date plus datePublished/dateModified schema | Add visible last-updated and accurate Article date schema |
        | 5 | Missing authorship / ownership | only ~21% had author signals | Agents want to know who makes the claim; anonymous pages are weaker citations | Byline, Person/Organization schema, author/about page | Named authors, author schema, sameAs to profiles |
        | 6 | Weak FAQ / answer structure | ~63% had zero FAQ schema, ~57% zero FAQ sections | Agents reward direct answers; answers buried in prose are harder to use | Look for question-shaped headings and FAQPage markup | Add real Q&A blocks with concise answers (structure helps agents even where FAQ rich results are gated) |
        | 7 | Weak article/content schema | only ~20% had article schema | Structured content helps agents classify what a page is | Crawl schema types by template | Add Article/BlogPosting/Product/Organization schema matching visible content |
        | 8 | No answer capsules | ~50% had zero answer capsules | Agents prefer concise, quotable answer blocks | Is there a 40-60 word standalone answer near the top? | Add answer capsules to key pages |
        | 9 | Incomplete agent-facing discovery files | llms.txt ~48%, llms-full.txt ~24%, ai.txt ~11% | Cheap "agent welcome mats," though not magic | Fetch /llms.txt and /ai.txt | Add a short llms.txt mapping canonical resources |
        | 10 | Sitemap / discovery gaps | sitemap ~77%, robots ~90% | Agents need clean crawl paths, not just human nav | Fetch /robots.txt and /sitemap.xml; validate canonical URLs | Clean XML sitemap plus robots with a sitemap directive |

        ## Honesty Guardrails

        - `llms.txt` and `ai.txt` are optional and not proven ranking factors. The durable wins are gaps 1-8: extractable content, freshness, authorship, and answer structure. Do not sell discovery files as a ranking lever.
        - FAQ rich results are gated to authoritative gov/health sites and HowTo rich results are deprecated, but the underlying Q&A and answer-capsule structure still improves agent extraction. Recommend the structure for extractability, not for a SERP feature.
        - Benchmarks are directional field data. Report them as "typical sites," not as thresholds Google enforces.

        ## Quick Scan

        1. Fetch raw HTML with JS disabled. Count meaningful words. Flag thin pages (gap 1).
        2. Diff raw vs rendered text to find JS-dependency (gaps 2-3).
        3. Check visible date plus date schema (gap 4).
        4. Check author byline plus Person/Organization schema (gap 5).
        5. Grep schema types; confirm they match visible content (gaps 6-7).
        6. Look for a top-of-page answer capsule and question-shaped headings (gaps 6, 8).
        7. Fetch /llms.txt, /ai.txt, /sitemap.xml, /robots.txt (gaps 9-10).

        ## Output

        Record per-page findings in the `Agent_Readability` workbook tab. Add each failing gap to `Issue_Register` with Module = `Agent Readability`. Extractability (gaps 1-3) and freshness/authorship (gaps 4-5) usually score the highest impact for AI visibility, so they tend to reach the "Fix now" band first.
        """,
    )


def main():
    ensure_dirs()
    workbook_path = build_workbook()
    export_csvs(workbook_path)
    build_docs()
    print(f"Created kit at {OUT}")
    print(f"Workbook: {workbook_path}")
    print(f"CSV templates: {CSV_DIR}")


if __name__ == "__main__":
    main()
