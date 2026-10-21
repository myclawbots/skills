---
name: seo_tools
description: Analyze website SEO performance, track keyword rankings, audit pages for issues, and monitor backlinks and competitors.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: analytics
tags: [seo, keywords, backlinks, rankings]
suggested_template: marketing_strategist
---

# SEO Tools

This skill enables you to analyze SEO performance, research and track keywords, audit page-level issues, monitor backlinks, and keep tabs on competitors. You can identify quick wins, prioritize high-impact improvements, and track progress over time.

> **Dashboard Connection:** Link your SEO tool account (SEMrush, Ahrefs, Moz, or equivalent) to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- SEO tool account configured in the dashboard
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- Domain ownership or access verification completed in the dashboard
- Understanding of SEO metrics (Domain Authority, search volume, keyword difficulty, etc.)

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| SEO platform connected via dashboard | Yes | Enables domain analysis, keyword research, and audits |
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| `content-writer` skill | No | Optional: for implementing SEO recommendations |
| `google-workspace` skill | No | Optional: for saving reports to Google Drive |

**Pre-flight checks:**
- Verify SEO platform (SEMrush, Ahrefs, Moz, etc.) is configured in the dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Ensure domain ownership or access is verified in the dashboard
- If implementing recommendations: ensure `content-writer` skill is available
- If saving reports: ensure `google-workspace` skill is connected

## How It Works

This skill wraps an SEO analysis API that covers the full SEO landscape:
- Get a bird's-eye view of domain health and traffic potential
- Track keyword rankings and track changes over time
- Research new keywords by volume, competition, and CPC
- Audit individual pages for on-page SEO issues
- Monitor backlink profile and identify link opportunities
- Analyze competitor domains and their keywords
- Monitor SERP results for your target keywords
- Track long-term keyword position changes

All requests use the proxy endpoint format: `${PROXY_URL}/seo/...`

## Available Tools

**1. Get Domain SEO Overview**

```bash
curl -X GET "${PROXY_URL}/seo/overview?domain=example.com" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "domain": "example.com", "domain_authority": 42, "traffic_estimate": 15000, "top_keywords": [ { "keyword": "...", "position": 1, "volume": 500 }, ... ] }`

---

**2. Get Keyword Rankings**

```bash
curl -X GET "${PROXY_URL}/seo/keywords?domain=example.com&limit=50" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of ranked keywords with position, search volume, traffic, difficulty score

---

**3. Research Keywords**

```bash
curl -X GET "${PROXY_URL}/seo/keywords/research?query=project+management+software&limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of keyword ideas with search_volume, difficulty (0-100), cpc, intent (commercial/informational)

---

**4. Audit a Page for SEO Issues**

```bash
curl -X GET "${PROXY_URL}/seo/audit?url=example.com/blog/best-practices" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns audit report with title, meta_description, h1_count, word_count, images_missing_alt, issues (critical, warning, info)

---

**5. Get Backlink Profile**

```bash
curl -X GET "${PROXY_URL}/seo/backlinks?domain=example.com&limit=50" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of backlinks with source_domain, anchor_text, domain_authority, traffic_estimate, link_type

---

**6. Find Competitors**

```bash
curl -X GET "${PROXY_URL}/seo/competitors?domain=example.com" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of competitor domains ranked by keyword overlap and traffic

---

**7. Check SERP for a Query**

```bash
curl -X GET "${PROXY_URL}/seo/serp?query=best+project+management+tools" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns top 10 SERP results with rank, url, title, snippet, domain_authority

---

**8. Add Keyword to Tracking**

```bash
curl -X POST "${PROXY_URL}/seo/track" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "keyword": "project management software"
  }'
```

**Response:** Returns `{ "keyword": "...", "status": "tracking", "added_at": "2026-03-29T10:15:00Z" }`

---

**9. Get Tracked Keyword Positions Over Time**

```bash
curl -X GET "${PROXY_URL}/seo/tracked?domain=example.com" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of tracked keywords with current position, position_history (7d, 30d, 90d trends)

---

**10. Check Site Health**

```bash
curl -X GET "${PROXY_URL}/seo/site-health?domain=example.com" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "crawlability": "good", "broken_links": 3, "redirect_chains": 1, "missing_meta": 12, "crawled_pages": 487, "recommendations": [...] }`

---

## Important Rules

1. **Present data with context** — Never report raw metrics without explaining what they mean. Always compare to benchmarks or industry averages.
2. **Prioritize high-impact keywords** — Focus on keywords with high search volume, low difficulty, and clear commercial intent.
3. **Compare competitors** — When analyzing your domain, reference how competitors rank for the same keywords. Identify gaps.
4. **Flag critical audit issues** — Highlight on-page issues that directly impact rankings (missing title tags, broken links, mobile usability).
5. **Monitor position trends** — Track whether rankings are improving or declining. Sudden drops warrant investigation.
6. **Respect crawl limits** — Don't over-audit. Space audits across multiple days to avoid rate limiting.
7. **Validate backlink quality** — Not all backlinks are equal. Prioritize high-authority, relevant linking domains.
8. **Document strategy changes** — When you make improvements (new content, technical fixes), track their impact over 4+ weeks.

## Smart Strategy

- **Start with overview:** Check domain authority, traffic estimate, and top-performing keywords first. This identifies your current strengths.
- **Find quick wins:** Research keywords with moderate search volume (100–1000/month) and low difficulty (< 30). These convert faster than high-difficulty targets.
- **Audit problem pages:** If a page should rank but doesn't, run a page audit to identify on-page issues (missing title, thin content, no internal links).
- **Analyze competitor keywords:** Identify keywords competitors rank for but you don't. If relevant to your business, create content targeting these opportunities.
- **Track momentum:** Add your 20–30 highest-potential keywords to tracking. Review position changes weekly to validate that content/technical changes are working.
- **Monitor backlinks:** Review new backlinks monthly. If competitors get high-authority links, investigate the source and pitch for similar coverage.
- **Seasonal trends:** Flag keywords with seasonal search volume patterns. Plan content around predictable demand spikes.
- **Link building targets:** Use the backlink audit to identify which domains link to competitors but not you. Prioritize reaching out to them.
- **Content gaps:** If a competitor ranks for a topic and you don't, audit their top page and create better, more comprehensive content.
- **Track SERP evolution:** Monitor SERP results for your target keywords. Changes in featured snippets, ads, or result types may require content adjustments.
