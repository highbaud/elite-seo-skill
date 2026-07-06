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
