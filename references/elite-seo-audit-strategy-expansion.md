# Elite SEO Audit and Strategy Expansion

Date: 2026-07-06

> **Scope:** the audit layer: 24 diagnostic modules, site-type roadmaps, prioritization, and the delivery format for an audit. It assumes the strategy and operating model in `elite-seo-knowledge-plan.md` and does not repeat it; for step-by-step execution, use the SOPs indexed in `kit/README.md`.

It adds what the knowledge plan leaves out: diagnostic depth, more site-type modules, stronger prioritization, better AI search measurement, and a cleaner delivery format for client or internal strategy work.

## What Was Missing From the First Plan

The original plan was strong on content, reviews, platform distribution, links, AI search, and operating cadence. The main missing pieces were:

- Log-file and bot-behavior analysis.
- JavaScript/rendering validation.
- Faceted navigation, filters, sorting, and URL parameter governance.
- Ecommerce product data, Merchant Center, variants, inventory, and shopping surface optimization.
- International SEO and hreflang.
- Migration/redesign QA.
- Content cannibalization and intent-conflict mapping.
- Snippet/title rewrite diagnostics and CTR testing.
- E-E-A-T/reputation evidence lockers for brand, people, and pages.
- Schema inventory by page type, not just generic structured data advice.
- AI visibility measurement methodology, including prompt volatility and citation/mention split.
- `llms.txt` nuance: useful as a machine-readable guide for some agents, not a ranking lever and not a crawler-control file.
- Governance: SEO QA before releases, continuous monitoring, ownership, and scoring.
- Audit deliverable templates: issue register, impact scoring, roadmap, and executive summary format.

## Additional Verified Source Notes

Use these sources alongside the sources in the first plan:

- Google canonicalization: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Google sitemap guidance: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Google title links: https://developers.google.com/search/docs/appearance/title-link
- Google robots meta and X-Robots-Tag: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
- Google JavaScript SEO basics: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google ecommerce URL structure: https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites
- Google ecommerce pagination/infinite scroll: https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading
- Google product structured data: https://developers.google.com/search/docs/appearance/structured-data/product
- Google review snippet structured data: https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- Google local business structured data: https://developers.google.com/search/docs/appearance/structured-data/local-business
- Google video SEO: https://developers.google.com/search/docs/appearance/video
- Google international/hreflang: https://developers.google.com/search/docs/specialty/international/localized-versions
- Google site moves: https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
- Google debugging traffic drops: https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops
- Surfer AI visibility metrics: https://surferseo.com/blog/best-ai-visibility-tools/
- Ahrefs content audit process: https://ahrefs.com/blog/content-audit/
- Ahrefs E-E-A-T audit framing: https://ahrefs.com/blog/eeat-audit/
- FatJoe unlinked brand mentions: https://fatjoe.com/blog/how-to-get-backlinks/
- Search Atlas topical/entity framework, treated as vendor guidance rather than official ranking documentation: https://searchatlas.com/blog/topical-authority-framework/

## Audit Philosophy

A serious SEO audit has to answer five questions:

1. Can search systems access, render, crawl, index, and understand the site?
2. Does the site deserve to rank for the topics it wants to own?
3. Does the wider web confirm the brand, people, products, and claims?
4. Is the site earning traffic that can turn into revenue or strategic value?
5. Is there a process to keep improving after the audit is delivered?

The audit should not be a dump of crawler warnings. It should be a decision document. Every issue needs an owner, evidence, impact, effort, confidence level, and next action.

## Audit Scoring Model

Use this scoring model for every issue and opportunity.

| Field | Scale | Meaning |
| --- | --- | --- |
| Impact | 1-5 | Expected effect on traffic, revenue, indexation, crawl efficiency, or risk reduction |
| Effort | 1-5 | Time, engineering complexity, content effort, approval friction |
| Confidence | 1-5 | Strength of evidence that this change matters |
| Risk | 1-5 | Risk if ignored, including revenue loss, index loss, manual action, legal/reputation impact |
| Speed | 1-5 | How quickly the change can show signal |

Priority score:

```text
((Impact + Confidence + Risk + Speed) - Effort) = Priority
```

Priority bands:

- 14-19: Fix now.
- 10-13: Schedule in next sprint.
- 6-9: Backlog or bundle with related work.
- 5 or lower (scores can go negative when effort outweighs everything): Monitor, do not distract the team.

## The Complete Audit Framework

### Module 1: Business, Revenue, and Search Objective Audit

Most SEO audits start too low in the stack. Start with the business.

Collect:

- Business model.
- Primary offer.
- Average order value or contract value.
- Gross margin.
- Sales cycle.
- Geographic targets.
- Customer segments.
- Main competitors.
- Top objections.
- Top acquisition channels.
- Best converting pages.
- Highest value products/services.
- Non-negotiable brand/legal constraints.

Questions:

- Which searches are actually worth winning?
- Which keywords create pipeline, not just traffic?
- Which pages support sales even if they do not rank?
- Which queries indicate high purchase intent?
- Which competitors are SEO competitors but not business competitors?
- Which offers need reputation support before they can convert?

Output:

| Search objective | Business value | Current visibility | Required asset | Metric |
| --- | ---: | --- | --- | --- |
| Own branded review queries | High | Weak | Review hub + video proof | Branded SERP coverage |
| Rank for commercial category | High | Medium | Comparison hub | SQLs from organic |
| Reduce support friction | Medium | Weak | FAQ/troubleshooting cluster | Support deflection |

### Module 2: Tracking, Analytics, and Attribution Audit

Before changing SEO, prove that measurement works.

Check:

- Google Search Console verified for all variants.
- Bing Webmaster Tools verified.
- GA4 installed once, not duplicated.
- Consent mode/cookie banner does not break critical tracking.
- Key events configured.
- Form submissions tracked.
- Calls tracked where relevant.
- Ecommerce purchases tracked.
- CRM/source attribution captured.
- UTM governance documented.
- AI search referral filters created.
- Bot/internal traffic filtered.
- Landing page reports separated from channel reports.
- Organic assisted conversions visible.

AI and answer-engine tracking:

- Track `utm_source=chatgpt.com` in analytics.
- Track referrals from `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`, and other AI surfaces where available.
- Keep prompt visibility tracking separate from traffic tracking. AI answers may mention a brand without sending a click.
- Store prompt tests with date, engine, region, account state, and citation list because AI answers vary by model, interface, region, and time.

Minimum GA4 events:

- `generate_lead`
- `sign_up`
- `purchase`
- `book_call`
- `click_phone`
- `click_email`
- `download_asset`
- `view_pricing`
- `start_trial`
- `watch_video_50_percent`
- `copy_code` for developer docs
- `use_calculator` for tools

Output:

| Tracking item | Status | Problem | Fix | Owner |
| --- | --- | --- | --- | --- |
| GSC domain property | Missing | Data split across http/www variants | Verify domain property | Marketing ops |
| Lead form events | Partial | Thank-you page not always triggered | Add form submit event | Dev |

### Module 3: Crawl, Indexation, and Bot Access Audit

This is the access layer.

Data sources:

- Screaming Frog/Sitebulb/LibreCrawl crawl.
- Google Search Console Pages report.
- URL Inspection samples.
- Bing Webmaster Tools.
- XML sitemaps.
- Robots.txt.
- Server logs or CDN logs.
- Edge/firewall rules.

Check crawl states:

- 200 indexable.
- 200 noindex.
- 3xx redirect.
- 4xx error.
- 5xx error.
- Soft 404.
- Canonicalized.
- Duplicate without canonical.
- Crawled, currently not indexed.
- Discovered, currently not indexed.
- Alternate page with proper canonical.
- Blocked by robots.txt.
- Blocked by noindex.
- Blocked by authentication.
- Blocked by WAF/CDN.

Bot access checklist:

- Googlebot can access HTML, CSS, JS, images, and video files needed for rendering.
- Bingbot can access important pages.
- OAI-SearchBot can access public pages intended for ChatGPT Search.
- PerplexityBot can access public pages intended for Perplexity.
- GPTBot policy is deliberately set based on training preference, not accidentally blocked/allowed.
- Firewall does not block verified search crawlers.
- Bot traps are blocked or controlled: infinite calendars, faceted combinations, internal search, session URLs, sort URLs, tracking parameters.

Server-log questions:

- Which pages does Googlebot crawl most?
- Which important pages are rarely crawled?
- How much crawl is wasted on parameters, redirects, 404s, duplicate pages, or static files?
- Are important new pages discovered quickly?
- Are AI crawlers hitting the site?
- Are bots receiving different status codes than users?
- Are 5xx spikes correlated with crawl drops?

Output:

| URL pattern | Googlebot hits | Status | Index state | Issue | Action |
| --- | ---: | --- | --- | --- | --- |
| `/collections?sort=*` | High | 200 | Mostly not indexed | Crawl waste | Canonical/noindex/robots strategy |
| `/guides/*` | Low | 200 | Indexed | Underlinked | Add hub links |

### Module 4: Rendering and JavaScript SEO Audit

Modern sites often fail because content exists only after user-triggered JavaScript.

Check:

- View source vs rendered DOM.
- Main content appears in initial HTML or is reliably rendered.
- Title/meta/canonical are stable in raw HTML and rendered DOM.
- JavaScript does not inject conflicting canonicals.
- Links use crawlable `<a href>` tags.
- Pagination and load-more expose crawlable URLs.
- Product grids render without user interaction.
- Reviews/testimonials are visible in rendered HTML.
- Structured data appears in rendered HTML and matches visible content.
- Lazy-loaded images have crawlable `src`/fallback.
- Critical pages work when JS is delayed or blocked.
- Hydration errors do not remove content.

Google-specific note: Google can process JavaScript, but JavaScript adds complexity. Google documentation warns to use robots meta carefully and avoid conflicting canonical signals, especially when JavaScript changes tags after load.

Testing stack:

- URL Inspection rendered HTML.
- Rich Results Test.
- Mobile-Friendly/PageSpeed rendering snapshots.
- Screaming Frog JavaScript rendering crawl.
- Browser devtools with JS disabled.
- Server logs to compare crawler behavior.

Red flags:

- Internal links are buttons with click handlers only.
- Infinite scroll has no paginated URLs.
- Product descriptions load only after interaction.
- Reviews are embedded from a third-party script and not visible to crawlers.
- Canonical differs between raw and rendered HTML.
- Noindex flashes during hydration.

### Module 5: Sitemap, Robots, Canonical, and Index-Control Audit

Sitemaps help discovery; they do not force indexing. Google says sitemaps are most useful for large, new, poorly linked, or media-heavy sites.

Sitemap checklist:

- Includes only canonical, indexable URLs.
- Excludes redirected, 404, noindex, duplicate, filtered, sort, search, cart, account, staging, and parameter junk.
- `lastmod` is accurate and changes only when meaningful page content changes.
- Sitemap index used for large sites.
- Image/video/news extensions used only when relevant.
- Sitemap path included in robots.txt.
- Submitted in Search Console and Bing Webmaster Tools.

Robots.txt checklist:

- Does not block important CSS/JS needed to render pages.
- Does not block pages that need crawler-readable noindex tags.
- Blocks crawl traps where appropriate.
- Does not attempt to remove indexed pages by robots-blocking them. Use noindex or removals where appropriate.
- Includes sitemap location.

Canonical checklist:

- One canonical per page.
- Canonical target is indexable and returns 200.
- Canonical target is not blocked by robots.txt.
- Internal links point to canonical versions.
- Sitemap includes canonical versions.
- hreflang points to canonical equivalents.
- Canonical is not used to hide unrelated duplicate doorway pages.

Index-control decision table:

| Page type | Recommended handling |
| --- | --- |
| Thin tag pages | Noindex or improve into real hubs |
| Internal search pages | Usually noindex/block crawl strategy |
| Useful filtered pages with demand | Index selectively with static URLs |
| Sort-only URLs | Canonical or noindex |
| Paginated category pages | Crawlable links, self-canonical in most cases |
| Staging pages | Auth block and noindex before launch |
| Expired products | Keep, redirect, or 410 based on substitutes/backlinks/search demand |

### Module 6: Information Architecture and Internal Link Equity Audit

Search engines and users infer importance from structure.

Map:

- Homepage.
- Primary category/service hubs.
- Subcategory pages.
- Product/service detail pages.
- Support content.
- Comparison content.
- Proof content.
- Local pages.
- Blog/resources.
- Tools/templates.

Check:

- Important pages are reachable within 3 clicks where practical.
- Hubs link to all major subtopics.
- Supporting articles link back to money pages.
- Related articles link laterally inside clusters.
- Breadcrumbs are present.
- Navigation does not bury core revenue pages.
- Footer links are not the only links to important pages.
- Anchor text is descriptive and varied naturally.
- Orphan pages are fixed or removed.
- High-authority pages pass internal links to strategic pages.

Internal link opportunity report:

| Source URL | Target URL | Suggested anchor | Reason |
| --- | --- | --- | --- |
| High-traffic guide | Money page | `[service] for [use case]` | Converts informational traffic |
| Case study | Comparison page | `[brand] vs alternatives` | Supports buyer research |

### Module 7: Topical Authority and Entity Map Audit

A site needs to look complete around the topics it wants to own.

Build an entity map for each target cluster:

- Core entity.
- Related entities.
- Attributes.
- Problems.
- Jobs-to-be-done.
- Alternatives.
- Integrations.
- Locations.
- Regulations.
- Tools.
- People/roles.
- Metrics.
- Processes.
- Risks.
- Decision criteria.

Example for a SaaS CRM:

```text
Core entity: CRM for roofing contractors
Related entities: estimates, storm restoration, insurance claims, job costing, dispatch, sales pipeline, QuickBooks, HubSpot, ServiceTitan
Buyer roles: owner, sales manager, office manager
Decision queries: best CRM for roofers, roofing CRM alternatives, roofing CRM pricing
Proof needed: case studies, workflow screenshots, integrations, migration process
```

Cluster scoring:

| Cluster | Coverage | Internal links | Proof | Commercial page | Comparison page | AI citation readiness |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Core category | 70% | Medium | Weak | Yes | No | Medium |
| Integrations | 30% | Weak | Medium | Partial | No | Low |

Expansion rule:

Do not publish more random posts. Fill missing nodes in the cluster that support the buyer journey or entity understanding.

### Module 8: Keyword, SERP, Intent, and Cannibalization Audit

Keyword research alone is not enough. You need query-to-page clarity.

For every keyword cluster, record:

- Query.
- Intent.
- Funnel stage.
- Current ranking URL.
- Best target URL.
- SERP features.
- Ranking competitors.
- Page type required.
- Existing content fit.
- Cannibalizing URLs.
- Refresh/build/consolidate decision.

Cannibalization types:

- True duplicate: multiple pages target same intent.
- Intent split: one page tries to serve two different intents.
- SERP mismatch: page type does not match ranking page types.
- Branded conflict: support/review/comparison pages compete awkwardly.
- Locale conflict: country/city pages not separated correctly.
- Format conflict: article ranking attempt when SERP wants product/category/video/forum.

Decision table:

| Problem | Action |
| --- | --- |
| Two weak pages serve same intent | Consolidate and redirect weaker page |
| Strong guide and weak service page both rank | Differentiate intent and link between them |
| Blog ranks for product term but does not convert | Add CTA or build/strengthen product page |
| Category page blocked by filters | Fix crawlable category path |
| Forum/Reddit dominates SERP | Add lived-experience section, quotes, FAQs, examples |

### Module 9: On-Page, Snippet, and CTR Audit

Google may rewrite title links and snippets, but your HTML title, headings, visible text, and internal anchors still matter.

Check each priority page:

- Title is unique, descriptive, concise, and aligned with intent.
- H1 is clear and matches page purpose.
- Meta description earns the click without false promises.
- First 100 words answer the query or explain the offer.
- Page has visible author/source/proof where needed.
- Subheadings reflect real user questions.
- Images support the topic.
- Tables or bullets help comparison queries.
- CTA matches intent.
- Dates are accurate.
- Pricing/availability claims are current.

CTR improvement workflow:

1. Export GSC queries/pages with high impressions and low CTR.
2. Check actual SERP: ads, AI overview, local pack, videos, competitor snippets.
3. Rewrite title/meta to match intent and improve specificity.
4. Add page content that supports a better snippet.
5. Request recrawl only for high-priority pages.
6. Measure 14-28 days, accounting for seasonality.

Snippet test log:

| URL | Query | Old title | New title | Date changed | CTR before | CTR after | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |

### Module 10: Content Quality, Decay, and Refresh Audit

Use the Ahrefs-style content audit concept: collect URLs, merge crawl/GSC/backlink/conversion data, then decide page by page.

Collect per URL:

- URL.
- Page type.
- Publish date.
- Last modified date.
- Organic clicks 3/6/12 months.
- Impressions 3/6/12 months.
- Backlinks.
- Internal links.
- Conversions.
- Revenue/assisted revenue.
- Target keyword.
- Current rank.
- Word count.
- Content quality score.
- SERP fit.
- Freshness need.
- Action.

Actions:

- Keep.
- Refresh.
- Expand.
- Merge.
- Redirect.
- Noindex.
- Delete.
- Repurpose.
- Add internal links.
- Build links.
- Change intent/page type.

Content refresh checklist:

- Update facts, dates, screenshots, pricing, policies, and examples.
- Add missing entities and subtopics.
- Add first-hand experience.
- Add customer proof or expert commentary.
- Improve internal links.
- Fix broken outbound links.
- Add schema if appropriate.
- Improve title/meta.
- Add visuals/video if the SERP rewards them.
- Remove obsolete sections.

Decay triggers:

- Clicks down 20%+ over 90 days.
- Rankings drift from top 3 to 4-10.
- Impressions rising but CTR falling.
- Competitors added newer data.
- Query intent changed.
- AI answers now satisfy the old simple answer.
- Product/pricing changed.

### Module 11: E-E-A-T, Reputation, and Trust Evidence Audit

Google says quality rater guidelines do not directly influence ranking, but they are useful for understanding what reliable, helpful content looks like. Treat E-E-A-T as an evidence system, not a badge you add.

Audit three entities:

1. Brand/organization.
2. People/authors/experts.
3. Pages/content assets.

Brand trust checklist:

- About page names the company and people.
- Contact information is visible.
- Legal pages are current.
- Policies are visible: privacy, terms, returns, warranties, disclaimers.
- Customer support path is clear.
- Business registrations/licenses/certifications shown where relevant.
- Press mentions collected.
- Reviews and testimonials are real and sourced.
- Social profiles are consistent.
- Brand SERP is clean and controlled.
- Organization schema uses consistent sameAs links.

People trust checklist:

- Author bios exist where content needs expertise.
- Credentials are real and verifiable.
- LinkedIn/social profiles align.
- Author pages list relevant work.
- Medical/legal/financial/YMYL content has expert review.
- Review dates are visible.
- Conflicts/affiliate relationships are disclosed.

Page trust checklist:

- Purpose is clear.
- Claims are sourced.
- Experience is visible.
- Screenshots/photos are original when possible.
- Dates are accurate.
- The page says who is responsible.
- The page does not overstate certainty.
- Affiliate/commercial relationships are disclosed.

Evidence locker structure:

```text
/reputation/
  licenses/
  certifications/
  expert-bios/
  customer-permissions/
  reviews-screenshots/
  press-mentions/
  awards/
  case-study-proof/
  original-data/
```

### Module 12: Structured Data and Schema Audit

Schema should clarify visible content. It should not claim things the page does not show.

Inventory by page type:

| Page type | Recommended schema |
| --- | --- |
| Homepage | Organization, WebSite, WebPage |
| Article/guide | Article or BlogPosting, BreadcrumbList, Person/Organization author |
| Product page | Product, Offer, AggregateRating if eligible, variant markup if needed |
| Ecommerce category | CollectionPage, BreadcrumbList, ItemList where appropriate |
| Local page | LocalBusiness if it describes that business/location, BreadcrumbList |
| Review hub | Review only when eligible; avoid self-serving local/org review stars |
| Video page | VideoObject, Clip or SeekToAction where appropriate |
| FAQ/support | FAQPage only when eligible and visible; do not expect rich result display for every site |
| Software/SaaS | SoftwareApplication, Product where appropriate, Organization |
| Course | Course/CourseInstance if applicable |
| Dataset/report | Dataset |
| Event | Event |
| Job page | JobPosting |

Validation process:

1. Crawl all structured data.
2. Validate templates in Rich Results Test.
3. Compare schema to visible content.
4. Check required and recommended fields.
5. Check image URLs are crawlable/indexable.
6. Check duplicate or conflicting schema entities.
7. Check Organization/Person identity consistency.
8. Monitor Search Console enhancement reports.

Review schema warning:

Google's review snippet guidelines say pages using `LocalBusiness` or `Organization` structured data are ineligible for star review features when the reviewed entity controls reviews about itself. Keep review content useful to buyers, but do not rely on self-serving review stars for local/org pages.

### Module 13: Ecommerce and Marketplace SEO Audit

Ecommerce requires its own audit layer.

Product page checklist:

- Product name clear.
- Unique description beyond manufacturer copy.
- Price visible.
- Availability visible.
- Shipping/returns visible.
- Product images high quality.
- Variants crawlable and understandable.
- Reviews visible.
- FAQs visible.
- Related products linked.
- Breadcrumbs present.
- Product schema valid.
- Merchant Center feed accurate if used.
- Canonicals correct across variants.
- Out-of-stock handling defined.

Category page checklist:

- Category intro is useful, not boilerplate.
- Product grid crawlable.
- Pagination/load-more crawlable.
- Filters do not create infinite crawl spaces.
- Valuable filtered pages have static indexable URLs.
- Sort-only/filter-no-demand URLs controlled.
- Internal links to related categories and buying guides.
- Unique title/H1/meta.
- No index bloat from parameters.

Faceted navigation strategy:

| Facet type | Search demand? | Unique inventory? | Index? | Handling |
| --- | --- | --- | --- | --- |
| Color | Sometimes | Yes | Selectively | Static pages for demand terms |
| Size | Sometimes | Yes | Usually no | Noindex/canonical unless demand exists |
| Sort price high-low | No | No | No | Canonical/block crawl |
| Brand | Often | Yes | Yes for demand | Static brand/category pages |
| Availability | Rare | No | No | Noindex/canonical |
| Location | Often | Yes | Yes if local intent | Static local inventory pages |

Out-of-stock decision table:

| Scenario | Action |
| --- | --- |
| Temporarily out of stock | Keep page, show availability, allow back-in-stock signup |
| Permanently discontinued with replacement | 301 to replacement or keep page with replacement link if search demand remains |
| Discontinued with backlinks/search demand | Keep informational page and recommend alternatives |
| No demand/no links/no replacement | 410 or 404 |

Google product surface checklist:

- Product structured data.
- Merchant listing fields where users can buy.
- Merchant Center feed where relevant.
- Product identifiers: GTIN/MPN/brand where available.
- Return policy.
- Shipping policy.
- Availability.
- Price.
- Product variants.
- High-quality product images.

### Module 14: Local SEO Deep Audit

Local SEO has three layers: Google Business Profile, location landing pages, and local prominence.

GBP checklist:

- Correct primary category.
- Useful secondary categories.
- Accurate NAP.
- Service area/location settings correct.
- Hours and holiday hours current.
- Services/products filled out.
- Photos added regularly.
- Reviews requested ethically.
- Reviews responded to.
- Q&A monitored.
- Booking/contact links work.
- UTM tags on website links.

Citation audit:

- Name consistency.
- Address consistency.
- Phone consistency.
- Website consistency.
- Duplicate listings.
- Wrong categories.
- Closed/moved listings.
- Major directories.
- Industry directories.
- Local chamber/association pages.

Local landing page proof:

- Real local projects.
- Local photos.
- Local testimonials.
- Local staff/service area details.
- Driving/service-area context.
- Local FAQs.
- Local links.
- Embedded map only if helpful.
- Clear service + city intent.

Local authority sources:

- Sponsorships.
- Local PR.
- Community events.
- Local podcasts.
- Supplier pages.
- Local associations.
- School/nonprofit partnerships.
- Local resource guides.

### Module 15: International and Multilingual SEO Audit

Use when the site targets multiple languages, countries, or regions.

Check:

- Separate URLs for each locale where possible.
- Correct `hreflang` annotations.
- Reciprocal hreflang links.
- `x-default` where appropriate.
- Canonicals point to same-language/country equivalents, not always to one global page.
- Language is not changed only by cookies or browser settings.
- Translations are localized, not just machine-translated literal copies.
- Currency, units, shipping, legal terms, and examples match market.
- Local backlinks/citations exist for important markets.
- Search Console properties/subfolders tracked by locale.

Common failures:

- English canonical on every translated page.
- Missing return hreflang tags.
- Same content served from one URL based on IP.
- Mixed language navigation.
- Auto-redirecting users and bots by IP in a way that blocks crawl access.

### Module 16: Image, Video, and Multimodal Audit

Images and videos are search assets.

Image audit:

- Important images are in `<img>` elements, not only CSS backgrounds.
- Fallback `src` exists for responsive images.
- Filenames are descriptive.
- Alt text explains the image in context.
- Captions or surrounding text support the image.
- Images are compressed without becoming blurry.
- Hero/product images are high resolution.
- Open Graph image is representative, not generic.
- `primaryImageOfPage` or page schema image is set where useful.
- Image sitemap used for image-heavy sites.
- Product images align with product schema/feed.
- IPTC/license metadata considered for licensable assets.

Video audit:

- Video is on a dedicated watch/landing page when search visibility matters.
- Google can fetch video bytes if hosted on site.
- Video URL is stable.
- Thumbnail URL is crawlable.
- VideoObject structured data is valid.
- Transcript is visible.
- Chapters/key moments are added.
- YouTube descriptions include timestamps and landing page links.
- Expiration dates are not accidentally set in the past.
- Video sitemap used for large video libraries.

Multimodal content opportunities:

- Turn comparison pages into tables and videos.
- Turn process guides into diagrams.
- Turn original data into charts.
- Turn testimonials into clips with transcripts.
- Turn demos into annotated screenshots.
- Turn complex decision pages into calculators.

### Module 17: Off-Page, Links, Mentions, and Digital PR Audit

Separate link quality from link quantity.

Backlink audit fields:

- Linking domain.
- Linking URL.
- Target URL.
- Anchor text.
- Follow/nofollow/sponsored/ugc.
- Topical relevance.
- Placement context.
- Estimated traffic.
- Indexation.
- Link risk.
- Relationship source.
- Referral traffic.

Risk patterns:

- Sitewide footer links.
- Irrelevant high-DR links.
- Obvious paid guest post networks.
- Exact-match anchors repeated unnaturally.
- Foreign-language spam unrelated to market.
- Links to redirected/dead pages.
- Links to pages that should be consolidated.

Opportunity types:

- Unlinked brand mentions.
- Broken competitor links.
- Outdated competitor resources.
- Expert quote requests.
- Podcast appearances.
- Data reports.
- Integration partner pages.
- Customer/vendor pages.
- Local sponsorships.
- Best-of/listicle inclusion.
- Tool/template promotion.

Mention audit fields:

- Brand mention URL.
- Sentiment.
- Linked/unlinked.
- Entity accuracy.
- Context.
- AI citation likelihood.
- Outreach action.

### Module 18: AI Search, AEO, and Agent Readiness Audit

AI search needs its own measurement because rankings, mentions, citations, and traffic are different things.

Measure four layers:

1. Mention: does the brand appear in the answer?
2. Citation: is the site cited or linked?
3. Position/prominence: is it first, buried, or only mentioned as an alternative?
4. Impact: does it drive traffic, leads, assisted conversions, or sales calls?

Prompt set design:

- Branded: `[brand] review`, `is [brand] legit`, `[brand] pricing`.
- Category: `best [category] for [use case]`.
- Comparison: `[brand] vs [competitor]`.
- Alternatives: `[competitor] alternatives`.
- Problem: `how to solve [pain]`.
- Local: `best [service] in [city]`.
- Support: `how do I [task] with [product/category]`.
- Purchase: `what should I know before buying [category]`.

Prompt tracking table:

| Prompt | Engine | Date | Region | Mention? | Citation? | Cited URL | Competitors | Notes | Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

AI citation readiness checklist:

- Page has a direct answer block.
- Page has clear entity/category language.
- Page has current facts.
- Page has proof.
- Page has citations where needed.
- Page has visible author/reviewer.
- Page loads without heavy JS dependency.
- Page allows relevant AI search crawlers.
- Page has structured sections and tables.
- Page is mentioned or linked from third-party sources.

Crawler-policy nuances that are commonly gotten wrong:

- Google AI Overviews and AI Mode are fed by normal Googlebot crawling. Blocking `Google-Extended` opts a site out of Gemini training/grounding but does NOT remove it from AI Overviews; the only AI-display controls for Google Search are `nosnippet`, `max-snippet`, and `data-nosnippet`.
- ChatGPT Search leans partly on Bing's index, so Bing Webmaster Tools and IndexNow are AI-visibility work.
- Perplexity documents that user-triggered `Perplexity-User` fetches generally ignore robots.txt; control at the CDN/WAF if that matters.
- The full per-bot decision matrix (OpenAI, Perplexity, Anthropic, Apple, Meta, Common Crawl, ByteDance) lives in the workbook's `Crawler_Access` tab; every bot should get a deliberate Allow/Block decision, not a default.

Measurement volatility: run each prompt at least 3 times across different days before recording a baseline, log region and account state, and report mention/citation rates as fractions across runs. Single-run "we rank on ChatGPT" claims are anecdotes.

`llms.txt` guidance:

- Use `robots.txt` and crawler-specific user agents for crawler control.
- Treat `llms.txt` as an optional machine-readable content guide, not a blocking mechanism and not a proven ranking factor.
- If implemented, keep it short and point to the best canonical resources, docs, pricing, product pages, API docs, comparison pages, and contact paths.
- Do not rely on it instead of crawlable HTML, sitemaps, schema, and strong content.

Example `llms.txt`:

```text
# Brand Name

> One-sentence description of the company/product.

## Core Resources
- Product overview: https://example.com/product/
- Pricing: https://example.com/pricing/
- Documentation: https://example.com/docs/
- Reviews: https://example.com/reviews/
- Comparisons: https://example.com/compare/
- Contact: https://example.com/contact/

## Policies
- Privacy: https://example.com/privacy/
- Terms: https://example.com/terms/
```

### Module 19: Migration, Redesign, and Release QA

SEO often gets damaged during redesigns and CMS migrations.

Pre-migration inventory:

- All current URLs.
- Organic traffic by URL.
- Backlinks by URL.
- Current rankings.
- Canonicals.
- Redirects.
- Titles/meta/H1s.
- Schema.
- Internal links.
- Sitemaps.
- Robots.txt.
- Media URLs.
- hreflang.

Migration checklist:

- One-to-one redirect map.
- No redirect chains.
- No mass redirect to homepage.
- Staging blocked from indexing.
- Production not accidentally noindexed.
- Canonicals updated.
- Internal links updated.
- XML sitemaps updated.
- Analytics preserved.
- GSC/Bing verified.
- Change of Address used for domain moves where applicable.
- Top pages manually tested.
- 404 monitoring active.
- Rankings/traffic monitored daily for first 2 weeks.

Release SEO QA:

- Title present.
- Meta description present.
- H1 present.
- Canonical correct.
- Index directive correct.
- Status code 200.
- Page in sitemap if indexable.
- Internal links present.
- Schema valid.
- Images have alt text.
- Mobile layout usable.
- Core CTA works.
- Tracking works.

### Module 20: Page Experience, Performance, and UX Audit

Google's guidance is clear that page experience should not be reduced to one metric. Audit the full experience.

Check:

- Core Web Vitals templates.
- Mobile usability.
- Intrusive interstitials/popups.
- Ad density.
- Layout shift.
- Font loading.
- Image/video weight.
- Third-party scripts.
- Server response time.
- Navigation clarity.
- Readability.
- Accessibility basics.
- Form friction.
- Trust cues.
- CTA clarity.

SEO/CRO overlap:

- If visitors cannot understand the offer in 5 seconds, rankings will not fix conversion.
- If review proof is hidden, consideration-stage traffic leaks.
- If pricing is impossible to find in a price-sensitive SERP, users bounce to competitors.
- If the page answers informational intent but has no next step, traffic does not compound into revenue.

### Module 21: Security, Spam, and Reputation Risk Audit

Search visibility can be hurt by security and trust failures.

Check:

- HTTPS everywhere.
- Mixed content.
- Malware/security warnings.
- Hacked pages.
- Spammy user-generated content.
- Open comments/forms abused by bots.
- Search pages indexed with spam queries.
- Thin affiliate pages.
- Fake reviews.
- Expired domain abuse risk.
- Doorway pages.
- Cloaking or accidental crawler/user mismatch.
- Legal removals/DMCA reputation issues.
- Privacy/legal compliance for claims and testimonials.

User-generated content controls:

- Moderation queue.
- Spam detection.
- `rel="ugc"` for user-added links.
- Noindex low-quality UGC sections until moderated.
- Rate limits.
- Captcha/honeypot where appropriate.

### Module 22: Audit Report Deliverable Format

A strong audit report should be structured like this:

1. Executive summary.
2. What is working.
3. Biggest blockers.
4. Biggest opportunities.
5. Risk register.
6. Priority roadmap.
7. Technical audit.
8. Content audit.
9. Authority/reputation audit.
10. AI search audit.
11. Local/ecommerce/international modules if relevant.
12. Measurement plan.
13. 30/60/90-day roadmap.
14. Appendix with raw exports and issue register.

Executive summary template:

```text
The site has [strengths], but organic growth is currently limited by [top blockers]. The highest-impact work is [priority 1], [priority 2], and [priority 3]. If implemented in order, the expected outcome is [traffic/conversion/risk impact] over [time horizon].
```

Issue register template:

| ID | Category | Issue | Evidence | Impact | Effort | Confidence | Risk | Priority | Owner | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |

Roadmap template:

| Timeframe | Workstream | Action | Why it matters | Owner | Success metric |
| --- | --- | --- | --- | --- | --- |
| Week 1-2 | Technical | Fix noindex/canonical conflicts | Recover indexability | Dev | Indexed priority URLs |
| Week 3-4 | Content | Refresh pages ranking 4-15 | Fast traffic lift | SEO/content | Clicks/rankings |
| Month 2 | Authority | Launch data asset outreach | Earn links/mentions | PR/SEO | Referring domains |
| Month 3 | AI search | Build comparison/review hub | Improve AI citations | SEO/content | Mention/citation rate |

### Module 23: Strategy Roadmap by Site Type

#### SaaS

Priorities:

- Category page.
- Use-case pages.
- Integration pages.
- Alternatives and vs pages.
- Pricing page.
- Demo pages.
- Customer proof.
- Docs/API SEO.
- Security/compliance pages.
- Product-led templates/tools.

Must-have clusters:

- Problem cluster.
- Solution/category cluster.
- Industry cluster.
- Role cluster.
- Integration cluster.
- Alternative/comparison cluster.
- Review/proof cluster.
- Support/docs cluster.

#### Local Service

Priorities:

- Google Business Profile.
- Service pages.
- Location pages.
- Review acquisition.
- Local photos/proof.
- Local citations.
- Local backlinks.
- Cost/pricing pages.
- Emergency/near-me pages if relevant.
- FAQ based on real calls.

#### Ecommerce

Priorities:

- Product/category crawlability.
- Faceted navigation control.
- Product data/schema/feed.
- Unique category copy.
- Product image SEO.
- Review content.
- Buying guides.
- Comparison pages.
- Out-of-stock handling.
- Internal links from guides to categories/products.

#### Publisher/Media

Priorities:

- News/topic hubs.
- Author expertise.
- Freshness.
- Internal links.
- Discover/image/video optimization.
- Content pruning.
- Archive/canonical rules.
- Ad experience.
- Newsletter capture.
- Original reporting.

#### Affiliate/Review Site

Priorities:

- First-hand testing proof.
- Transparent methodology.
- Review update dates.
- Pros/cons.
- Alternatives.
- Comparison tables.
- Affiliate disclosures.
- Product schema eligibility.
- Brand trust and author credentials.
- Avoid thin rewrites of manufacturer/vendor pages.

### Module 24: The Final Audit Checklist

Use this as the master pass before delivering strategy.

Technical:

- Crawl complete.
- Indexation states mapped.
- Robots and noindex reviewed.
- Canonicals reviewed.
- Sitemaps cleaned.
- Rendering tested.
- JS links checked.
- Logs reviewed if available.
- Core templates speed checked.
- Structured data validated.
- Broken links/redirect chains fixed or logged.

Content:

- Keyword map built.
- Search intent mapped.
- Cannibalization identified.
- Content decay identified.
- Refresh queue built.
- New page opportunities prioritized.
- E-E-A-T evidence gaps documented.
- Review/proof gaps documented.
- Internal links mapped.

Authority:

- Backlink profile reviewed.
- Link risks identified.
- Lost/broken links identified.
- Unlinked mentions found.
- Competitor link gaps found.
- Digital PR assets defined.
- Platform distribution plan created.

AI search:

- Crawler access checked.
- Prompt set built.
- Mention/citation baseline recorded.
- Competitor AI visibility recorded.
- Answer-ready content gaps identified.
- Analytics AI referral tracking set.

Business:

- SEO priorities tied to revenue.
- Conversion paths tested.
- Roadmap scored.
- Owners assigned.
- Reporting cadence defined.

## Final Recommendation

Add this expansion as the audit layer of the original plan. The original document explains how to build SEO growth. This document explains how to diagnose a specific site, choose the highest-value actions, prevent damage, and keep the strategy accountable.

The best SEO strategy for any project should end with four artifacts:

1. A site health audit.
2. A search demand and content map.
3. An authority/reputation plan.
4. A 30/60/90-day execution roadmap with owners, metrics, and priority scores.
