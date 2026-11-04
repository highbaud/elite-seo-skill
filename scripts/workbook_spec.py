"""Workbook tab definitions: the single source of truth for the master audit workbook.

Standard library only (no openpyxl), so the dependency-free GSC analyzer can import
it. The workbook builder renders these specs; the analyzer reads the headers of the
tabs it pre-fills, so the two can never drift apart.

Everything that points at a column (dashboard formulas, list validations, priority
formulas, conditional formatting) is resolved from header names through
``column_letter``, so reordering headers cannot silently break a formula.
"""

from __future__ import annotations

from dataclasses import dataclass

from kit_common import CellValue

Row = tuple[CellValue, ...]

# Tabs other scripts refer to by name (the GSC analyzer pre-fills these three).
TAB_GSC_OPPORTUNITIES = "GSC_Opportunities"
TAB_CANNIBALIZATION = "Cannibalization"
TAB_CONTENT_DECAY = "Content_Decay"

FIRST_DATA_ROW = 2  # row 1 holds the headers
LAST_DATA_ROW = 500  # validations, fill-down formulas and formatting run to this row

# Issue_Register priority bands: a score at or above each minimum lands in that band.
FIX_NOW_MIN = 14
NEXT_SPRINT_MIN = 10
BACKLOG_MIN = 6


@dataclass(frozen=True)
class ListValidation:
    """A dropdown applied to each column named in ``headers`` (rows 2..LAST_DATA_ROW)."""

    headers: tuple[str, ...]
    values: tuple[str, ...]


@dataclass(frozen=True)
class FillDown:
    """Formula written into ``header``'s column for rows first_row..last_row.

    ``template`` contains the literal token ``{row}``, replaced by each row number.
    """

    header: str
    first_row: int
    last_row: int
    template: str


@dataclass(frozen=True)
class ConditionalFill:
    """Fill ``fill`` (a colour name such as "red") on ``header``'s column where ``template`` holds.

    ``template`` is a rule formula containing ``{col}`` (the column letter) and ``{first}``
    (the first row of the range).
    """

    header: str
    template: str
    fill: str
    first_row: int = 2
    last_row: int = LAST_DATA_ROW


@dataclass(frozen=True)
class SheetSpec:
    """Declarative definition of one workbook tab."""

    title: str
    headers: tuple[str, ...]
    rows: tuple[Row, ...] = ()
    validations: tuple[ListValidation, ...] = ()
    widths: tuple[tuple[str, int], ...] = ()  # (header name, column width) overrides
    fills: tuple[FillDown, ...] = ()
    conditional: tuple[ConditionalFill, ...] = ()


# Header names of the tabs other specs refer to by column.
ISSUE_HEADERS: tuple[str, ...] = (
    "ID", "Module", "Issue", "Evidence", "Affected URL / Pattern", "Impact", "Effort",
    "Confidence", "Risk", "Speed", "Priority", "Priority Band", "Source Grade", "Owner",
    "Status", "Next Action", "Date Added",
)
DASHBOARD_HEADERS: tuple[str, ...] = ("Metric", "Formula / Value", "Notes")

_TABLES: dict[str, tuple[tuple[str, ...], tuple[Row, ...]]] = {
    'Site_Profile': (
        ('Field', 'Answer', 'Why it matters'),
        (
            ('Site / brand', '', 'Defines entity consistency across SEO and AI surfaces'),
            ('Business model', '', 'SaaS, local, ecommerce, publisher, affiliate, marketplace, lead gen'),
            ('Primary offer', '', 'SEO should support revenue, not vanity traffic'),
            ('Average order / contract value', '', 'Used to prioritize high-intent queries'),
            ('Top 5 competitors', '', 'Separate business competitors from SERP competitors'),
            ('Primary geography', '', 'Local, national, international, service area'),
            ('YMYL risk?', '', 'Medical, legal, finance, safety, civic, health, high-trust topics'),
            ('Tech stack / CMS', '', 'Impacts crawl/render/schema/migration fixes'),
            ('Primary conversion', '', 'Lead, call, trial, purchase, subscription, demo'),
            ('Analytics stack', '', 'GA4, CRM, call tracking, ecommerce, BI'),
            ('Existing SEO tools', '', 'GSC, Bing, Ahrefs, Semrush, Screaming Frog, Surfer, Search Atlas'),
            ('Risk tolerance', '', 'White-hat only, experimental allowed, no paid links, etc.'),
        ),
    ),
    'Source_Reliability': (
        ('Grade', 'Definition', 'Use', 'Examples'),
        (
            ('A', 'Primary documentation or first-party platform policy', 'Can be treated as the base rule', 'Google Search Central, OpenAI crawler docs, Perplexity docs'),
            ('B', 'Repeatable field practice with broad industry support', 'Use when it aligns with primary docs', 'Content pruning, internal linking, log analysis, earned link outreach'),
            ('C', 'Tool/vendor guidance or case study', 'Use as hypothesis; verify on the site', 'Surfer, Search Atlas, Ahrefs, agency studies'),
            ('D', 'Social post, anecdote, one-off tactic', 'Test only if low-risk and measurable', 'X threads, Instagram reels, isolated screenshots'),
            ('Red', 'Manipulative, deceptive, or policy-risk tactic', 'Do not execute for serious projects', 'Fake reviews, link schemes, doorway pages, inauthentic mentions'),
        ),
    ),
    'URL_Inventory': (
        ('URL', 'Status Code', 'Indexability', 'Canonical', 'Title', 'H1', 'Template', 'Organic Clicks 3m', 'Impressions 3m', 'Backlinks', 'Conversions', 'Action', 'Notes'),
        (
            ('/', 200, 'Indexable', '/', 'Homepage', 'Brand', 'Homepage', '', '', '', '', 'Keep', ''),
        ),
    ),
    'Keyword_Map': (
        ('Cluster', 'Keyword', 'Intent', 'Funnel Stage', 'Current URL', 'Target URL', 'Current Rank', 'SERP Format', 'Business Value', 'Difficulty', 'Required Asset', 'Action'),
        (
            ('Core category', '', 'Commercial', 'Consideration', '', '', '', 'Listicles / reviews / product pages', 5, 3, 'Comparison hub', 'Build'),
        ),
    ),
    TAB_GSC_OPPORTUNITIES: (
        ('Query', 'Page', 'Clicks', 'Impressions', 'CTR', 'Position', 'Opportunity Type', 'Action', 'Owner'),
        (
            ('', '', '', '', '', '', 'High impressions low CTR', 'Rewrite title/meta and improve first answer', 'SEO'),
        ),
    ),
    TAB_CONTENT_DECAY: (
        ('URL', 'Page Type', 'Clicks 90d', 'Clicks Previous 90d', 'Delta', 'Rank Change', 'Freshness Need', 'Backlinks', 'Conversions', 'Action'),
        (
            ('', 'Guide', '', '', '', '', 'High', '', '', 'Refresh'),
        ),
    ),
    TAB_CANNIBALIZATION: (
        ('Keyword / Intent', 'URL 1', 'URL 2', 'Conflict Type', 'Winning URL', 'Decision', 'Redirect / Canonical / Rewrite'),
        (
            ('', '', '', 'True duplicate / intent split / format mismatch', '', '', ''),
        ),
    ),
    'Technical_Crawl': (
        ('URL', 'Status', 'Indexability', 'Canonical Status', 'Depth', 'Inlinks', 'Outlinks', 'Response Time', 'Issue', 'Fix'),
        (
            ('', '', '', '', '', '', '', '', '', ''),
        ),
    ),
    'Indexation': (
        ('URL', 'GSC Status', 'Sitemap?', 'Canonical Declared', 'Canonical Selected', 'Robots', 'Noindex?', 'Action'),
        (
            ('', 'Crawled currently not indexed', '', '', '', '', '', ''),
        ),
    ),
    'JS_Rendering': (
        ('URL', 'Raw HTML Content Present?', 'Rendered Content Present?', 'Crawlable Links?', 'Canonical Stable?', 'Structured Data Stable?', 'Issue', 'Action'),
        (
            ('', '', '', '', '', '', '', ''),
        ),
    ),
    'Schema': (
        ('URL', 'Page Type', 'Schema Types', 'Valid?', 'Visible Content Match?', 'Warnings', 'Errors', 'Action'),
        (
            ('', 'Product / Article / Local / Video', '', '', '', '', '', ''),
        ),
    ),
    'Internal_Links': (
        ('Source URL', 'Target URL', 'Anchor Text', 'Link Location', 'Reason', 'Priority'),
        (
            ('', '', '', 'Body / nav / footer / related', '', ''),
        ),
    ),
    'Backlinks_Mentions': (
        ('Source Domain', 'Source URL', 'Target URL', 'Anchor / Mention', 'Follow Type', 'Relevance', 'Traffic', 'Risk', 'Action'),
        (
            ('', '', '', '', 'follow / nofollow / sponsored / ugc / unlinked', '', '', '', ''),
        ),
    ),
    'AI_Visibility': (
        ('Prompt', 'Engine', 'Date', 'Region', 'Brand Mentioned?', 'Site Cited?', 'Cited URL', 'Competitors Cited', 'Sentiment', 'Gap', 'Action'),
        (
            ('best [category] for [use case]', 'ChatGPT Search / Perplexity / Google AI', '', '', '', '', '', '', '', '', ''),
        ),
    ),
    'Reviews_Reputation': (
        ('Asset', 'URL / Source', 'Review Type', 'Permission?', 'Schema Eligible?', 'Used On Pages', 'Branded SERP Target', 'Action'),
        (
            ('', '', 'Text / video / screenshot / case study', '', '', '', '[brand] review', ''),
        ),
    ),
    'Local_SEO': (
        ('Location', 'GBP Status', 'Primary Category', 'NAP Consistent?', 'Review Count', 'Rating', 'Local Page', 'Citation Gaps', 'Local Link Targets'),
        (
            ('', '', '', '', '', '', '', '', ''),
        ),
    ),
    'Ecommerce': (
        ('URL / Template', 'Type', 'Product Data Complete?', 'Schema Valid?', 'Facet Risk', 'Index Rule', 'Merchant Feed Match?', 'Action'),
        (
            ('', 'Product / Category / Facet / Variant', '', '', '', '', '', ''),
        ),
    ),
    'International': (
        ('Locale URL', 'Language / Region', 'Canonical', 'Hreflang Return Tag?', 'x-default?', 'Localized Content?', 'Issue', 'Action'),
        (
            ('', '', '', '', '', '', '', ''),
        ),
    ),
    'Migration_QA': (
        ('Old URL', 'New URL', 'Old Traffic', 'Backlinks', 'Redirect Status', 'Canonical', 'Internal Links Updated?', 'QA Status'),
        (
            ('', '', '', '', '', '', '', ''),
        ),
    ),
    'Platform_Distribution': (
        ('Platform', 'Role', 'Asset', 'Canonical Owned URL', 'Platform URL', 'UTM', 'Risk Grade', 'Performance', 'Next Action'),
        (
            ('LinkedIn', 'B2B authority', '', '', '', '', 'B', '', ''),
        ),
    ),
    'Quick_Wins': (
        ('Window', 'Opportunity', 'Signal', 'Action', 'Owner', 'Expected Impact', 'Proof Needed'),
        (
            ('48 hours', 'Pages ranking 4-15', 'GSC positions', 'Improve title, internal links, answer block', 'SEO', 'Medium-high', 'Rank/CTR change'),
        ),
    ),
    'Roadmap_30_60_90': (
        ('Timeframe', 'Workstream', 'Action', 'Why It Matters', 'Owner', 'Success Metric', 'Status'),
        (
            ('30 days', 'Technical', 'Fix crawl/index blockers', 'Unlock existing demand', 'Dev/SEO', 'Indexed priority URLs', 'Open'),
            ('60 days', 'Content', 'Build comparison/review hub', 'Capture consideration searches', 'Content', 'Commercial clicks/leads', 'Open'),
            ('90 days', 'Authority', 'Launch data asset outreach', 'Earn links and citations', 'PR/SEO', 'Referring domains/mentions', 'Open'),
        ),
    ),
    'Risk_Register': (
        ('Tactic', 'Why Tempting', 'Risk', 'Risk Grade', 'Safer Alternative', 'Decision'),
        (
            ('Mass AI pages', 'Scales fast', 'Scaled content abuse if low-value', 'Red', 'Unique data pages with selective indexing', 'Avoid'),
            ('Inauthentic AI mentions', 'Looks like AEO shortcut', 'Spam/reputation risk', 'Red', 'Earn real third-party mentions and reviews', 'Avoid'),
            ('llms.txt for Google AI rankings', 'Popular current claim', 'Not needed for Google Search AI visibility', 'C', 'Use optional agent guide only', 'Optional'),
        ),
    ),
    'Crawler_Access': (
        ('Bot / User-agent', 'Operator', 'What It Feeds', 'Blocking Consequence', 'Policy Decision', 'Verified Access?', 'Notes'),
        (
            ('Googlebot', 'Google', 'Google Search, AI Overviews, AI Mode', 'Removed from Google Search AND its AI answer features', 'Allow', '', 'There is no separate crawler to block only AI Overviews; use nosnippet/max-snippet/data-nosnippet for display control'),
            ('Google-Extended', 'Google', 'Gemini training and grounding', 'Opts out of Gemini training; does NOT remove AI Overviews visibility', 'Undecided', '', 'Common misconception: blocking this does not affect Google Search or AI Overviews inclusion'),
            ('Bingbot', 'Microsoft', 'Bing, Copilot, and part of ChatGPT Search results', 'Weakens visibility in Copilot and ChatGPT answers', 'Allow', '', 'Bing indexation matters for AI answers; submit via IndexNow and Bing Webmaster Tools'),
            ('OAI-SearchBot', 'OpenAI', 'ChatGPT Search surfacing/citations', 'Site not eligible for ChatGPT Search summaries', 'Allow', '', 'Separate from GPTBot; OpenAI documents no guaranteed placement'),
            ('GPTBot', 'OpenAI', 'OpenAI model training', 'Content excluded from future model training', 'Undecided', '', 'Deliberate business decision; independent from search inclusion'),
            ('ChatGPT-User', 'OpenAI', 'User-triggered live page fetches', 'Users cannot pull the page into a chat', 'Allow', '', ''),
            ('PerplexityBot', 'Perplexity', 'Perplexity search surfacing/citations', 'Not surfaced in Perplexity results', 'Allow', '', ''),
            ('Perplexity-User', 'Perplexity', 'User-triggered live fetches', 'n/a', 'Monitor', '', 'Perplexity documents that user-triggered fetches generally ignore robots.txt; control at WAF level if needed'),
            ('ClaudeBot', 'Anthropic', 'Anthropic model training', 'Content excluded from Claude training', 'Undecided', '', ''),
            ('Claude-SearchBot / Claude-User', 'Anthropic', 'Claude search surfacing / user fetches', 'Not cited in Claude answers', 'Allow', '', ''),
            ('Applebot / Applebot-Extended', 'Apple', 'Siri, Spotlight / Apple AI training', 'Applebot-Extended only opts out of AI training', 'Undecided', '', ''),
            ('CCBot', 'Common Crawl', 'Open corpus used by many AI labs', 'Excluded from Common Crawl derived training sets', 'Undecided', '', ''),
            ('meta-externalagent', 'Meta', 'Meta AI training', 'Excluded from Meta training', 'Undecided', '', ''),
            ('Bytespider', 'ByteDance', 'ByteDance AI training', 'Excluded if it complies', 'Undecided', '', 'Widely reported to ignore robots.txt; enforce at CDN/WAF if blocking matters'),
        ),
    ),
    'Log_File_Analysis': (
        ('URL Pattern', 'Bot', 'Hits 30d', '% of Total Crawl', 'Status Mix', 'Indexable?', 'Crawl Value', 'Issue', 'Action'),
        (
            ('/collections?sort=*', 'Googlebot', '', '', '200', 'No', 'Waste', 'Parameter crawl trap', 'Canonical + robots strategy, then re-measure'),
            ('/guides/*', 'Googlebot', '', '', '200', 'Yes', 'Under-crawled', 'Important pages rarely hit', 'Add hub/internal links, include in sitemap'),
        ),
    ),
    'Rank_Tracking': (
        ('Keyword', 'Target URL', 'Engine / Surface', 'Date', 'Position', 'SERP Features', 'AI Answer Present?', 'Brand In AI Answer?', 'Notes'),
        (
            ('', '', 'Google / Bing / Google AI / Local pack / Video', '', '', '', '', '', ''),
        ),
    ),
    'Experiment_Log': (
        ('Experiment', 'Hypothesis', 'Page / Platform', 'Start Date', 'Change Made', 'Primary Metric', 'Baseline', 'Result', 'Position Stable?', 'Status', 'Decision / Next Action'),
        (
            ('Title rewrite test', 'Specific title lifts CTR at same position', '', '', '', 'CTR at position bucket', '', '', '', 'Running', 'Compare CTR only at stable positions; annotate change date'),
        ),
    ),
    'Competitors': (
        ('Competitor', 'Type', 'Domain', 'Top Pages / Clusters', 'Link Gap Targets', 'AI Citations Seen', 'Weaknesses', 'Action'),
        (
            ('', 'Business + SERP / SERP only', '', '', '', '', '', ''),
        ),
    ),
    'Agent_Readability': (
        ('URL', 'Meaningful Words (no JS)', 'Extractable Static?', 'Needs JS Render?', 'Visible Date?', 'Date Schema?', 'Author Signal?', 'Answer Capsule?', 'FAQ / Q&A?', 'Content Schema', 'llms.txt?', 'Sitemap Listed?', 'Gaps', 'Action'),
        (
            ('/', '', '', '', '', '', '', '', '', 'Article / Product / Organization / none', '', '', '', ''),
        ),
    ),

}

_HEADERS: dict[str, tuple[str, ...]] = {
    "Dashboard": DASHBOARD_HEADERS,
    "Issue_Register": ISSUE_HEADERS,
    **{title: headers for title, (headers, _rows) in _TABLES.items()},
}


def headers_for(title: str) -> list[str]:
    """Column headers of the workbook tab named ``title``. Raises KeyError for unknown tabs."""
    return list(_HEADERS[title])


def column_letter(title: str, header: str) -> str:
    """Spreadsheet column letter (A..Z, AA..) of ``header`` in tab ``title``.

    Raises KeyError for an unknown tab and ValueError for an unknown header.
    """
    headers = _HEADERS[title]
    if header not in headers:
        raise ValueError(f"Tab {title!r} has no column {header!r}")
    return column_letter_for_index(headers.index(header) + 1)


def column_letter_for_index(index: int) -> str:
    """Spreadsheet column letter for a 1-based column index (1 -> A, 27 -> AA)."""
    if index < 1:
        raise ValueError(f"Column index must be >= 1, got {index}")
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _whole_column(title: str, header: str) -> str:
    """Whole-column reference such as ``Issue_Register!O:O``."""
    letter = column_letter(title, header)
    return f"{title}!{letter}:{letter}"


def _count_if(title: str, header: str, value: str) -> str:
    return f'=COUNTIF({_whole_column(title, header)},"{value}")'


def _dashboard_rows() -> tuple[Row, ...]:
    issues = "Issue_Register"
    average = f'=IFERROR(ROUND(AVERAGE({_whole_column(issues, "Priority")}),1),"-")'
    return (
        ("Open issues", _count_if(issues, "Status", "Open"), "Total unresolved audit issues"),
        ("Fix-now issues", _count_if(issues, "Priority Band", "Fix now"), f"Priority band {FIX_NOW_MIN}+"),
        ("Technical issues", _count_if(issues, "Module", "Technical"), "Crawl/index/render/speed/schema"),
        ("Content issues", _count_if(issues, "Module", "Content"), "Intent, quality, decay, cannibalization"),
        ("Authority issues", _count_if(issues, "Module", "Authority"), "Links, mentions, PR, reputation"),
        ("AI visibility gaps", _count_if(issues, "Module", "AI Search"), "Mention/citation/crawler gaps"),
        ("Average priority", average, "Formula: impact + confidence + risk + speed - effort"),
        ("30-day actions", _count_if("Roadmap_30_60_90", "Timeframe", "30 days"), "Immediate execution load"),
        ("Critical red-line risks", _count_if("Risk_Register", "Risk Grade", "Red"), "Do not execute without explicit risk acceptance"),
        ("Experiments open", _count_if("Experiment_Log", "Status", "Running"), "Active tests with a decision pending"),
        ("Crawlers undecided", _count_if("Crawler_Access", "Policy Decision", "Undecided"), "Bot policies still needing a deliberate decision"),
        ("Agent-readability gaps", _count_if(issues, "Module", "Agent Readability"), "Extractability, dating, authorship, answer-structure gaps for AI agents"),
    )


def _priority_formula(guarded: bool) -> str:
    """Priority score template (``{row}`` placeholder); ``guarded`` blanks it for empty rows."""

    def col(header: str) -> str:
        return column_letter("Issue_Register", header) + "{row}"

    total = f"SUM({col('Impact')},{col('Risk')},{col('Speed')},{col('Confidence')})-{col('Effort')}"
    if guarded:
        return f'=IF({col("Issue")}="","",{total})'
    return f"={total}"


def _band_formula(guarded: bool) -> str:
    """Priority band template (``{row}`` placeholder); ``guarded`` blanks it for empty rows."""
    score = column_letter("Issue_Register", "Priority") + "{row}"
    band = (
        f'IF({score}>={FIX_NOW_MIN},"Fix now",IF({score}>={NEXT_SPRINT_MIN},"Next sprint",'
        f'IF({score}>={BACKLOG_MIN},"Backlog","Monitor")))'
    )
    return f'=IF({score}="","",{band})' if guarded else f"={band}"


def _issue_rows() -> tuple[Row, ...]:
    """Starter issues, keyed by header; Priority/Priority Band are filled with formulas."""
    seeds: tuple[dict[str, CellValue], ...] = (
        {"ID": "SEO-001", "Module": "Technical", "Issue": "Important pages missing from XML sitemap",
         "Evidence": "Sitemap vs crawl export mismatch", "Affected URL / Pattern": "/services/*",
         "Impact": 4, "Effort": 2, "Confidence": 4, "Risk": 3, "Speed": 4, "Source Grade": "A",
         "Owner": "Dev", "Status": "Open",
         "Next Action": "Regenerate sitemap with canonical indexable URLs only"},
        {"ID": "SEO-002", "Module": "Content", "Issue": "High-impression page has weak CTR",
         "Evidence": "GSC export", "Affected URL / Pattern": "/blog/example",
         "Impact": 3, "Effort": 1, "Confidence": 3, "Risk": 2, "Speed": 5, "Source Grade": "B",
         "Owner": "SEO", "Status": "Open",
         "Next Action": "Rewrite title/meta and add snippet-supporting answer block"},
        {"ID": "SEO-003", "Module": "AI Search", "Issue": "Competitors cited for category prompt but brand absent",
         "Evidence": "AI prompt tracker", "Affected URL / Pattern": "/compare/",
         "Impact": 4, "Effort": 3, "Confidence": 3, "Risk": 3, "Speed": 3, "Source Grade": "B",
         "Owner": "Content", "Status": "Open",
         "Next Action": "Build answer-ready comparison hub and verify crawler access"},
    )
    formulas = {"Priority": _priority_formula(False), "Priority Band": _band_formula(False)}
    rows: list[Row] = []
    for row_number, seed in enumerate(seeds, start=FIRST_DATA_ROW):
        values = {**seed, **{h: f.replace("{row}", str(row_number)) for h, f in formulas.items()}}
        unknown = set(values) - set(ISSUE_HEADERS)
        if unknown:
            raise ValueError(f"Issue_Register seed uses unknown headers: {sorted(unknown)}")
        rows.append(tuple(values.get(header, "") for header in ISSUE_HEADERS))
    return tuple(rows)


def _issue_register_spec() -> SheetSpec:
    seed_rows = _issue_rows()
    # Seed issues fill the first data rows; every row after them gets guarded fill-down formulas.
    guarded_start = FIRST_DATA_ROW + len(seed_rows)
    return SheetSpec(
        title="Issue_Register",
        headers=ISSUE_HEADERS,
        rows=seed_rows,
        validations=(
            ListValidation(
                ("Module",),
                ("Technical", "Content", "Authority", "AI Search", "Agent Readability", "Local",
                 "Ecommerce", "International", "Analytics", "Reputation", "Risk"),
            ),
            ListValidation(("Source Grade",), ("A", "B", "C", "D", "Red")),
            ListValidation(("Status",), ("Open", "In progress", "Blocked", "Done", "Won't do")),
            ListValidation(("Impact", "Effort", "Confidence", "Risk", "Speed"), ("1", "2", "3", "4", "5")),
        ),
        fills=(
            FillDown("Priority", guarded_start, LAST_DATA_ROW, _priority_formula(True)),
            FillDown("Priority Band", guarded_start, LAST_DATA_ROW, _band_formula(True)),
        ),
        conditional=(
            ConditionalFill("Priority Band", '${col}{first}="Fix now"', "red"),
            ConditionalFill("Priority Band", '${col}{first}="Next sprint"', "yellow"),
            ConditionalFill("Priority Band", '${col}{first}="Backlog"', "green"),
        ),
    )


_TABLE_VALIDATIONS: dict[str, tuple[ListValidation, ...]] = {
    "Roadmap_30_60_90": (
        ListValidation(("Timeframe",), ("30 days", "60 days", "90 days", "Backlog")),
        ListValidation(("Status",), ("Open", "In progress", "Blocked", "Done")),
    ),
    "Risk_Register": (ListValidation(("Risk Grade",), ("A", "B", "C", "D", "Red")),),
    "Crawler_Access": (
        ListValidation(("Policy Decision",), ("Allow", "Block", "Undecided", "Monitor")),
        ListValidation(("Verified Access?",), ("Yes", "No", "Not tested")),
    ),
    "Experiment_Log": (ListValidation(("Status",), ("Planned", "Running", "Done", "Abandoned")),),
    "Log_File_Analysis": (
        ListValidation(("Crawl Value",), ("High value", "Normal", "Under-crawled", "Waste")),
    ),
    "Agent_Readability": (
        ListValidation(
            ("Extractable Static?", "Needs JS Render?", "Visible Date?", "Date Schema?",
             "Author Signal?", "Answer Capsule?", "FAQ / Q&A?", "llms.txt?", "Sitemap Listed?"),
            ("Yes", "No", "Partial"),
        ),
    ),
}


def _table_spec(title: str) -> SheetSpec:
    headers, rows = _TABLES[title]
    return SheetSpec(title, headers, rows, validations=_TABLE_VALIDATIONS.get(title, ()))


def _build_specs() -> tuple[SheetSpec, ...]:
    dashboard = SheetSpec(
        "Dashboard",
        DASHBOARD_HEADERS,
        _dashboard_rows(),
        widths=(("Metric", 28), ("Formula / Value", 24), ("Notes", 72)),
    )
    leading = ("Site_Profile", "Source_Reliability")
    trailing = tuple(title for title in _TABLES if title not in leading)
    return (
        dashboard,
        *(_table_spec(title) for title in leading),
        _issue_register_spec(),
        *(_table_spec(title) for title in trailing),
    )


SHEETS: tuple[SheetSpec, ...] = _build_specs()
