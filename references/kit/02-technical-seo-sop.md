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
