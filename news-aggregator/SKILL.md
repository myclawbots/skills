---
name: news_aggregator
description: Curate and deliver personalized news from 7000+ sources based on topics, industries, and interests. Deliver summaries via email, Slack, or Discord.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: analytics
tags: [news, curation, digest, monitoring]
suggested_template: research_agent
---

# News Aggregator

This skill enables you to curate personalized news feeds from thousands of sources, create topic-based subscriptions, and deliver daily or weekly digests via email, Slack, or Discord. All requests are handled through a proxy-wrapped news aggregation API.

> **Dashboard Connection:** Connect your email, Slack, or Discord account to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- Email account, Slack workspace, or Discord server configured in dashboard
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- Topic or industry interests defined

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the news aggregation proxy endpoints |
| `slack` skill | No | Optional; use to deliver news digests to Slack channels |
| `google-workspace` | No | Optional; use to deliver news digests via email through Gmail |

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test fetching a curated news feed to verify connectivity before creating subscriptions

## How It Works

This skill wraps a news aggregation API covering 7000+ sources. You can:
- Pull curated news feeds filtered by topics and industries
- Identify trending articles and topics
- Create recurring news subscriptions with delivery schedules
- Summarize multiple articles into brief digests
- Deliver news to email, Slack, or Discord channels
- Customize sources and topics per subscription
- Track what news resonates with your audience

All requests use the proxy endpoint format: `${PROXY_URL}/news/...`

## Available Tools

**1. Get Curated News Feed**

```bash
curl -X GET "${PROXY_URL}/news/feed?topics=ai,startups&limit=20&period=24h" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of news articles with title, source, url, summary, published_at, relevance_score.

---

**2. Get Trending News**

```bash
curl -X GET "${PROXY_URL}/news/trending?category=technology&limit=10" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns trending articles by category (technology, business, finance, healthcare, etc.).

---

**3. Create a News Subscription**

```bash
curl -X POST "${PROXY_URL}/news/subscribe" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Tech News",
    "topics": ["ai", "startups", "saas"],
    "sources": ["techcrunch", "theverge", "ycombinator"],
    "frequency": "daily",
    "delivery": {
      "channel": "email",
      "target": "user@example.com"
    }
  }'
```

**Response:** Returns `{ "subscription_id": "...", "status": "active", "next_delivery": "..." }`

---

**4. List Active Subscriptions**

```bash
curl -X GET "${PROXY_URL}/news/subscriptions" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of active subscriptions with names, topics, frequencies, and delivery details.

---

**5. Update a Subscription**

```bash
curl -X PUT "${PROXY_URL}/news/subscriptions/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["ai", "mlops"],
    "frequency": "weekly"
  }'
```

**Response:** Returns updated subscription object.

---

**6. Delete a Subscription**

```bash
curl -X DELETE "${PROXY_URL}/news/subscriptions/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "deleted": true, "subscription_id": "..." }`

---

**7. Summarize Articles**

```bash
curl -X POST "${PROXY_URL}/news/summarize" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "article_urls": ["https://example.com/article1", "https://example.com/article2"],
    "format": "bullet_points"
  }'
```

**Response:** Returns summarized key points from the articles.

---

**8. List Available Sources**

```bash
curl -X GET "${PROXY_URL}/news/sources" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns full list of 7000+ available news sources with categories and languages.

---

**9. Generate a Digest**

```bash
curl -X POST "${PROXY_URL}/news/digest" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["ai", "startups"],
    "period": "7d",
    "format": "detailed"
  }'
```

**Response:** Returns formatted digest with curated articles, summaries, and key takeaways.

---

## Important Rules

1. **Provide balanced coverage** — Include sources from multiple perspectives on each topic.
2. **Always cite sources** — Every article should include the source name, publication date, and URL.
3. **Summarize, don't copy** — Create original summaries rather than republishing full articles.
4. **Respect copyright** — Use brief excerpts with proper attribution, never full article text.
5. **Flag breaking news** — Immediately alert users to breaking or urgent news relevant to their topics.
6. **Let users customize** — Always allow customization of sources, topics, and delivery frequency.
7. **Monitor delivery** — Ensure subscriptions deliver consistently and on schedule.
8. **Avoid duplicate news** — Filter out duplicate stories across multiple sources.

## Smart Strategy

- **Understand interests:** Ask the user what topics, industries, and news sources matter most.
- **Create targeted subscriptions:** Set up subscriptions for each major topic with preferred frequency (daily, weekly, realtime).
- **Test delivery:** Send a test digest before automating to ensure quality and relevance.
- **Refine over time:** Track user feedback and adjust topics/sources based on engagement.
- **Combine with other skills:** Repurpose curated news into LinkedIn posts, blog articles, or email newsletters.
- **Set up alerts:** Use subscriptions for breaking news on critical topics (product launches, competitor moves, etc.).
- **Generate weekly summaries:** Create curated digests for leadership teams or stakeholder communications.
- **Archive and reference:** Maintain subscription history for future content research and trend identification.
