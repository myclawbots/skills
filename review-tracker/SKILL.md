---
name: review_tracker
description: Monitor customer reviews across Google, Yelp, Trustpilot, and social media. Get real-time alerts, sentiment analysis, and AI-drafted responses.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: analytics
tags: [reviews, reputation, sentiment, alerts]
suggested_template: customer_support
---

# Review Tracker

This skill enables you to monitor customer reviews across multiple platforms (Google, Yelp, Trustpilot), analyze sentiment, set up alerts for negative reviews, and draft professional responses. All requests are handled through a proxy-wrapped review monitoring API.

> **Dashboard Connection:** Connect your Google Business, Yelp, and Trustpilot accounts to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- Business accounts on review platforms (Google, Yelp, Trustpilot) connected in dashboard
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- Access to respond on connected platforms

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Review platforms connected via dashboard | Yes | The proxy needs connected accounts (Google, Yelp, Trustpilot) to monitor reviews |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the review proxy endpoints |
| `slack` skill | No | Optional; use to send alerts for negative reviews to Slack channels |
| `google-workspace` | No | Optional; use to save review reports and analytics to Google Sheets |

**Pre-flight checks:**
- Verify review platforms are connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test listing connected accounts to verify connectivity before creating alerts

## How It Works

This skill wraps a review aggregation and monitoring API. You can:
- Monitor reviews across Google, Yelp, Trustpilot, and social media in real-time
- Analyze sentiment trends and identify common themes in reviews
- Set up alerts for new reviews, rating drops, or negative feedback
- View competitor reviews for benchmarking
- Automatically draft professional responses to reviews
- Track response rates and review trends over time
- Extract frequently mentioned keywords and pain points

All requests use the proxy endpoint format: `${PROXY_URL}/reviews/...`

## Available Tools

**1. List Connected Review Accounts**

```bash
curl -X GET "${PROXY_URL}/reviews/accounts" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of connected platforms with business names and status.

---

**2. Get Recent Reviews**

```bash
curl -X GET "${PROXY_URL}/reviews/recent?platform=all&limit=20&min_rating=1&max_rating=5" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns reviews with text, rating, reviewer name, platform, date, and sentiment score.

---

**3. Get Review Analytics**

```bash
curl -X GET "${PROXY_URL}/reviews/analytics?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "avg_rating": 4.6, "total_reviews": 150, "sentiment_trend": "positive", "rating_distribution": {...} }`

---

**4. List Active Alerts**

```bash
curl -X GET "${PROXY_URL}/reviews/alerts" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of alert rules with conditions, thresholds, and notification channels.

---

**5. Create an Alert**

```bash
curl -X POST "${PROXY_URL}/reviews/alerts" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "negative_review",
    "threshold": 3,
    "notify_via": "email",
    "target": "manager@company.com"
  }'
```

**Response:** Returns `{ "alert_id": "...", "status": "active", "created_at": "..." }`

---

**6. Update an Alert**

```bash
curl -X PUT "${PROXY_URL}/reviews/alerts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold": 2,
    "notify_via": "slack"
  }'
```

**Response:** Returns updated alert object.

---

**7. Delete an Alert**

```bash
curl -X DELETE "${PROXY_URL}/reviews/alerts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "deleted": true, "alert_id": "..." }`

---

**8. Draft a Response**

```bash
curl -X POST "${PROXY_URL}/reviews/respond" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "review_id": "12345",
    "tone": "professional"
  }'
```

**Response:** Returns `{ "draft_response": "Thank you for your feedback...", "tone": "professional" }`

---

**9. Send a Response**

```bash
curl -X POST "${PROXY_URL}/reviews/respond/send" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "review_id": "12345",
    "response_text": "Thank you for your feedback. We appreciate you choosing us..."
  }'
```

**Response:** Returns `{ "sent": true, "response_id": "...", "platform": "google" }`

---

**10. Compare with Competitors**

```bash
curl -X GET "${PROXY_URL}/reviews/competitors?competitor_ids=comp1,comp2" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns comparative metrics: your avg rating vs competitors, total review counts, sentiment distribution.

---

**11. Extract Keywords**

```bash
curl -X GET "${PROXY_URL}/reviews/keywords?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of frequently mentioned keywords with frequency, sentiment association, and review count.

---

## Important Rules

1. **Always show drafted responses** — Preview any AI-drafted response to the user before sending.
2. **Flag negative reviews immediately** — Set up alerts to catch 1–3 star reviews instantly.
3. **Never argue with reviewers** — Responses should be professional, empathetic, and solution-focused.
4. **Respond professionally** — All responses must maintain brand voice and avoid defensive language.
5. **Track response rates** — Monitor how many reviews you respond to (aim for 80%+).
6. **Confirm before sending** — Get explicit user approval before publishing any response.
7. **Address themes** — Identify common complaints and work to resolve underlying issues.
8. **Monitor trends** — Watch for rating drops that signal quality or service issues.

## Smart Strategy

- **Connect all platforms:** Ensure Google, Yelp, and Trustpilot are connected for full visibility.
- **Set up alerts:** Create alerts for negative reviews (≤3 stars) to respond quickly.
- **Review trends:** Check analytics weekly to identify sentiment trends and problem areas.
- **Draft responses:** Use the tone parameter to match your brand voice (professional, friendly, apologetic).
- **Respond quickly:** Aim to respond within 24–48 hours of new reviews, especially negative ones.
- **Extract themes:** Review the keywords endpoint to identify most-mentioned strengths and weaknesses.
- **Benchmark competitors:** Compare your ratings and review counts to competitors monthly.
- **Close the loop:** When customers mention specific issues, follow up to confirm resolution and ask for updated reviews.
