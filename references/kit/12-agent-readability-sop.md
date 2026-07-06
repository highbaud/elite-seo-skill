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
