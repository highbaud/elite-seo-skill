# AI search page playbook (SEO, AEO, GEO)

Use this when you build, rewrite, or audit any page meant to rank in Google or get cited by
ChatGPT, Perplexity, Claude, Copilot, or Google AI Overviews.

**Sources.** Two public items: a "10 traits of pages ranked #1 in LLMs" list
(it claims a study of 10K sites and publishes no method) and the infographic "The anatomy
of a page that wins Google and AI search" (Ryze AI, after Rob Hoffman's SOP). Every numeric
target below (word counts, link counts, placement depth) comes from those two sources. They
are working heuristics, not proven ranking factors. The one research-backed number is the
Princeton GEO paper (Aggarwal et al., KDD 2024): adding citations, quotations, and
statistics raised visibility in generative answers by up to about 40% on its benchmark.
That is a lab benchmark, not a live-traffic study.

**Overlaps.** `kit/04-ai-search-aeo-sop.md`, `kit/12-agent-readability-sop.md`, and the
`Agent_Readability` and `Crawler_Access` workbook tabs. This file adds the page anatomy, the
order, and the conversion placements.

## House rules that win over this playbook

1. **FAQ markup earns nothing in Google.** FAQ rich results were removed from Search on
   May 7, 2026. Keep the FAQ content, because answer engines lift it. Add `FAQPage` markup
   only as a harmless extra, never as a promised win. `kit/02` still says FAQ results show
   for gov and health sites; that line is stale.
2. **Never invent the proof.** Original data, stats, expert quotes, client examples, case
   studies, and sources must be real and checkable. If the owner has no data yet, leave a
   visible `[TODO: source]` and say so. Do not fill the slot.
3. **Regulated pages go through compliance first.** For financial, insurance, health, or
   legal sites, client results with numbers, scores and verdicts, "best" picks, expert
   quotes, and comparisons against competitors can be performance advertising,
   testimonials, or endorsements (for example under the SEC Marketing Rule; insurance copy
   falls under NAIC rules instead). Get compliance review before publishing. CTAs on those
   pages get the same review.
4. **Bylines must be true.** A real named person with their own profile, in a role they
   actually hold. Use current, correct entity names only.
5. **`llms.txt` and the markdown copy are cheap extras, not ranking levers.** Google says it
   needs no special AI files. Add them when it is cheap. Never rank them above crawlable
   HTML, dates, authorship, and answer structure. Give the markdown copy an HTTP
   `Link: <html-url>; rel="canonical"` header so it does not compete with the HTML page.
6. **Earn mentions; never fake them.** No scripted Reddit, review-site, or social
   engagement. Each platform's house rules still apply.
7. **Medium is not a citation surface for the ChatGPT or Claude crawls.** Medium's
   robots.txt blocks GPTBot and ClaudeBot. The quotable canonical copy lives on an owned site.
8. **All copy still passes your own writing and brand-voice rules.**

Many generic AI-SEO guides overstate `FAQPage` schema and `llms.txt`. Where they
conflict with this file, this file wins.

## The page, top to bottom

Tags: **[R]** retrieval and citation signal, **[S]** page structure, **[C]** conversion
placement. Skip an element only when the page type has no use for it (a definition page has
no comparison table).

### Top of the page

1. **Title tag and H1 [R].** Match the exact query and one intent. Pattern:
   `[Topic]: What It Is, How It Works and What It Costs (2026)`. 55-60 characters. Add the
   year only when the answer changes each year. The H1 uses the same phrase. Slug: 2-4
   words, no dates. *Miss:* a clever title nobody searches for.
2. **Named author with credentials [R].** A real person with a LinkedIn profile and a full
   author page. Mark up as `Person` with `sameAs` links. Add a named expert reviewer on
   money, health, or legal topics. The profile, the page, and the schema show the same name
   and dates. *Miss:* "By Admin" or "Marketing Team." Pages with no author look like
   content farms.
3. **Visible dates that match the schema [R].** Print Published and Updated near the title.
   Use the same dates in `datePublished` and `dateModified`. Change the date only when a
   fact on the page changes. *Miss:* bumping the date with no real change.
4. **Sticky CTA [C].** A bar pinned to the top and a tab pinned to the end. One action
   ("Book a 15-min demo"). Show it after the first scroll, never on load. Same words as the
   final CTA. *Miss:* a pop-up on load.
5. **Answer first [R].** The first paragraph is the reply AI lifts word for word.
   Definition first, a number second, both inside the first 50 words; the full answer runs
   40-60 words. Sentence 3 says who it is for. It must stay true and complete when read
   alone. *Miss:* "In this article we will..." or a three-paragraph story first.
6. **Bottom line with clear outcomes [R].** Right under the intro, 3 rows: "Pick A if...,
   pick B if..., skip C unless...". Each row has a result plus a time or number.
   *Miss:* "It depends on your needs."
7. **Image CTA with a button [C].** Before the first long section. Speak to the outcome.
   Under the button: time, price, risk ("15 minutes, free"). Make it look like an offer,
   not body text.
8. **Key facts [R].** 5 bullets. Each is one complete fact under 20 words with a number,
   price, time, %, or count. The last bullet says when the data was checked. *Miss:*
   "saves time."

### Body

9. **Define the entity [S].** 200-300 words on what it is and what it is not. A one-line
   definition, then the 3 terms people confuse it with. Link the entity in schema with
   `about` and `sameAs` (Wikipedia, Wikidata). Use one name for the topic on the whole
   page. *Miss:* switching between three names.
10. **Lead magnet link [C].** An in-text link about 10% down to a file people would pay
    for (template, calculator, checklist). Name the thing, not the form ("Free download:
    the 14-point checklist"). Track it as its own conversion. *Miss:* "Subscribe to our
    newsletter."
11. **Video embed [C].** About 30% down. 2-4 minutes, screen and face, the result in the
    first 20 seconds. A full transcript under it so AI can read what is said.
    `VideoObject` schema with chapters. *Miss:* a video with no transcript.
12. **Original data [R].** The strongest citation magnet. The first page to publish
    "43% of X" gets cited; the hundred pages that repeat it do not. Count something in
    your own data. State the sample, date range, and method. Publish it as an HTML table
    plus a downloadable file. *Miss:* someone else's stat as the headline. House rule 2.
13. **Steps as H3s [S].** One numbered H3 per step, so the order survives copying. Each
    step: the action, a time estimate, what you need, and a "done when" line. *Miss:*
    steps buried in paragraphs.
14. **Mistakes with a price tag [S].** 3 mistakes. Name each one, put a cost on it ($,
    weeks, %), and give a one-line fix. *Miss:* "Don't ignore SEO."
15. **Comparison table in HTML [R].** A real `<table>`, never an image or a screenshot.
    AI cannot read a table inside an image, and "X vs Y" answers are built from table
    cells. Rows are options; columns are cost, time, effort, best for. Real numbers, not
    checkmarks. Highlight the row you recommend and say why under the table.
16. **How the options were chosen [R].** 4-5 criteria with weights that add to 100%, and
    how each was measured, on what, and when. A disclosure line if you sell one of the
    options. *Miss:* "We picked the best tools."
17. **A verdict for every reader [C].** Best overall, best on a budget, best for one
    segment. A score out of 10 for each and one line on who it fits and when it fails.
    Your own product appears only where it honestly wins. *Miss:* ranking yourself #1 for
    everyone. House rule 3 for regulated sites.
18. **Segment sections [S].** A short section per audience, 4-6 of them. For each: where
    to start and the risk to watch. Use the segment name exactly as people type it.
19. **Who this is not for [S].** 2-3 segments or budgets it does not fit, the reason in
    one line, and a better option for each. It makes the rest believable.
20. **Sources and expert quotes [R].** Link primary sources inline, right next to the
    number each one backs. 2-3 named experts, each with a specific claim. *Miss:* a
    sources list at the bottom that no claim connects to.
21. **Examples with numbers [S].** 2-3 real examples in the form
    `+[X]% [metric] for [client] in [weeks]`, each linked to its full case study, with
    mixed client sizes. *Miss:* "Our clients see great results." House rules 2 and 3.
22. **FAQ from real prompts [R].** 6-8 questions buyers really ask. Ask ChatGPT what your
    buyers ask, then add Reddit threads, sales calls, and tracked prompts. Phrase each one
    the way people type it. Each answer is 2-3 sentences and starts with the direct answer.
    *Miss:* "Why is [brand] the best?" House rule 1 for the markup.
23. **Visible changelog [R].** Dated lines, newest first, real changes only (prices,
    scores, new sections). The latest date matches `dateModified`. It proves freshness
    and gives crawlers a reason to return. *Miss:* a new date with nothing else changed.
24. **Related pages [S].** 3-6 links to the subtopic guides and tools in the same
    cluster. The anchor text is the exact query each page targets. At least one tool
    (calculator, checker, template). Every child page links back with the same anchor.
    *Miss:* "You may also like" widgets with random posts.

### End of the page

25. **In-text CTA [C].** A plain link in the last paragraph, written as the outcome ("We'll
    show you which pages lose AI traffic"). The same offer as the sticky bar.
26. **Final image CTA [C].** The last thing on the page. Headline = the outcome, one offer,
    plus time and risk. The only dark block on the page.
27. **Structured data [R].** `Article` with author, dates, and `about`, plus
    `BreadcrumbList`, `HowTo`, `VideoObject`, or `Dataset` where they fit (`FAQPage` per
    house rule 1). The schema says exactly what the page says. Validate every template in
    the Rich Results Test. *Miss:* schema that claims ratings or reviews the page does not
    show.

## Technical layer (the part most pages skip)

| Item | Rule | Check |
|---|---|---|
| Crawlable by every engine | Server-rendered HTML and a self-referencing canonical. robots.txt allows `OAI-SearchBot`, `PerplexityBot`, and `Claude-SearchBot`, plus the user-fetch agents `ChatGPT-User`, `Claude-User`, and `Perplexity-User`. Training bots (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`) are a separate owner decision. AI Overviews run on plain Googlebot. | Load the page with JavaScript off. If the answer is gone, most AI crawlers cannot see it either. |
| Indexed in Google and Bing | Submit through Search Console and Bing Webmaster Tools. Ping IndexNow on every update. ChatGPT search leans partly on Bing's index. | Search `site:yourdomain.com/[slug]` on Bing. No result means a ChatGPT citation is unlikely. |
| Linked and mentioned | Links in from 3+ related outside pages. Earned mentions on Reddit, G2, and comparison sites, which models cross-check before they recommend. | Ask ChatGPT for the best options in the category and open every page it cites. That is the mention list. |
| Consistent facts everywhere | Price, plan limits, and ratings match across the page, the pricing page, the schema, and third-party listings. Conflicting numbers are a common reason a page stops being cited. | Put the page, G2, and schema values side by side. They must be identical. |
| Refreshed on a schedule | Re-check prices and ratings each month. Update `dateModified` only on real changes, each with a changelog line. | A visible "Updated [date]: what changed" line. |
| Measured by citations | Each month, track the 10-20 prompts the page should win in ChatGPT, Perplexity, and AI Overviews, beside rankings and traffic. Run each prompt 3+ times across days, because answers vary. | If you cannot name the page's prompts, the page is not built for any of them. |
| Agent copy (optional) | A clean markdown copy of the page, listed in `llms.txt`, with no scripts, menus, or pop-ups in the way. House rule 5. | Fetch `/llms.txt` and the `.md` URL. Check the canonical header. |
| Agent-completable sign-up (SaaS only) | AI agents now sign up for tools on behalf of their users, and many stop at the login wall. An agent must be able to finish the flow without a human. | Run an agent through sign-up on a test environment and fix each place it stops. |
