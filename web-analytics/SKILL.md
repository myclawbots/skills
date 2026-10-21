---
name: web_analytics
description: Access website traffic data, user behavior analytics, conversion funnels, and audience demographics from your connected analytics platform.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: analytics
tags: [analytics, traffic, funnels, audience]
suggested_template: data_analyst
---

# Web Analytics

> **Dashboard Connection Required**
> This skill requires an active analytics connection in your MyClawBots dashboard. Configure your provider (Google Analytics, Plausible, Mixpanel, Amplitude, or equivalent) before using these tools. Auth is handled by the proxy—provide `${PROXY_URL}` and `$PROXY_API_KEY` in curl requests.

## Prerequisites

- Connected analytics account in MyClawBots dashboard
- Analytics data already flowing (at least 24 hours of activity recommended)
- `${PROXY_URL}` environment variable set to your proxy endpoint
- `$PROXY_API_KEY` environment variable set to your API key

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Analytics platform connected via dashboard | Yes | Enables traffic data and visitor analytics |
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| `google-workspace` skill | No | Optional: for saving reports to Google Sheets |
| `slack` skill | No | Optional: for sending metric alerts |

**Pre-flight checks:**
- Verify analytics platform (Google Analytics, Plausible, Mixpanel, Amplitude, etc.) is configured in the dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Ensure at least 24 hours of analytics data is available
- If saving reports: ensure `google-workspace` skill is connected
- If sending alerts: ensure `slack` skill is connected

## How it works

The Web Analytics skill gives you programmatic access to your analytics platform without needing to log in to dashboards. Query visitor counts, traffic sources, page performance, device breakdowns, conversion events, and more. Use this to:

- Monitor real-time site activity and traffic patterns
- Identify your top-performing pages and content
- Analyze where your visitors come from
- Track conversion goals and funnel completion
- Compare performance across time periods
- Generate insights for optimization

All endpoints support flexible date ranges using standard period formats (`7d`, `30d`, `90d`, `12m`) or custom date ranges with `start_date` and `end_date` parameters.

## Available Tools

### 1. Dashboard Overview
Get high-level metrics for your site across a time period.

```bash
curl -X GET "${PROXY_URL}/analytics/overview?period=7d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: visitors (unique users), pageviews, bounce rate, average session duration, new vs returning ratio. Use this first to understand your current traffic health.

### 2. Top Pages
Identify which pages drive the most traffic.

```bash
curl -X GET "${PROXY_URL}/analytics/pages?period=30d&limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: page URL, views, unique visitors, avg time on page, bounce rate. Limit defaults to 20; adjust to see more/fewer pages.

### 3. Traffic Sources
Understand where visitors come from—referrers, search, social, direct.

```bash
curl -X GET "${PROXY_URL}/analytics/sources?period=30d&limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: source name (e.g., "google", "facebook.com", "direct"), visitor count, percentage of total traffic. Essential for attribution analysis.

### 4. Visitors by Country
See geographic distribution of your audience.

```bash
curl -X GET "${PROXY_URL}/analytics/countries?period=30d&limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: country, visitor count, percentage. Use to understand if your audience is global, regional, or concentrated.

### 5. Device Breakdown
Analyze mobile vs. desktop vs. tablet traffic.

```bash
curl -X GET "${PROXY_URL}/analytics/devices?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: device type (desktop, mobile, tablet), visitor count, percentage, bounce rate. Critical for mobile optimization decisions.

### 6. Real-Time Activity
See current active visitors and what pages they're on right now.

```bash
curl -X GET "${PROXY_URL}/analytics/realtime" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: active visitors (total), breakdown by page, traffic source. No period parameter—always current snapshot.

### 7. Conversion Events
Track goal completions, purchases, signups, or custom events you've defined.

```bash
curl -X GET "${PROXY_URL}/analytics/conversions?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: event name, conversion count, conversion rate, average value (if applicable). Essential for measuring business outcomes.

### 8. Funnel Analysis
Measure step-by-step completion through defined funnels (e.g., signup → verify email → upgrade).

```bash
curl -X GET "${PROXY_URL}/analytics/funnels/{id}?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Replace `{id}` with your funnel ID from dashboard. Returns: step name, users entering, users completing, drop-off rate. Use to identify conversion bottlenecks.

### 9. Time Series Data
Get metrics plotted over time for charting and trend analysis.

```bash
curl -X GET "${PROXY_URL}/analytics/timeseries?metric=visitors&period=30d&interval=day" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Parameters:
- `metric`: visitors, pageviews, bounce_rate, session_duration, conversions
- `interval`: hour, day, week, month

Returns: array of [timestamp, value] pairs. Perfect for creating trend charts.

### 10. Period-over-Period Comparison
Compare current performance to previous period to spot growth or decline.

```bash
curl -X GET "${PROXY_URL}/analytics/compare?period=30d&compare=previous" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Returns: current period metrics + previous period metrics + percent change for each metric. Options for `compare`: `previous`, `last_year`, or specify custom dates with `compare_start_date` and `compare_end_date`.

## Important Rules

1. **Always Present Context** — When reporting numbers, include comparisons (previous period, targets, industry benchmarks) so the data is actionable, not just informative.

2. **Flag Significant Changes** — If a metric moved more than 20% up or down, call it out explicitly. Investigate anomalies (traffic spikes, drops).

3. **Respect Date Ranges** — Use `period` parameter consistently. For daily monitoring, use `7d`. For trend analysis, use `30d` or `90d`. Don't mix different periods in one comparison without being clear.

4. **Understand Attribution Limits** — Analytics attribution (especially on traffic sources) has limitations. Cross-channel attribution may not be perfect. Always note "last-click" vs. "first-click" if relevant.

5. **Real-Time Lag** — Real-time data may have a 30-60 second delay. Historical data is finalized after 24-48 hours.

6. **Mobile-First Lens** — Many modern sites see 50%+ mobile traffic. Always review device breakdown and mobile-specific metrics.

7. **Conversion Clarity** — Ask "conversion to what?" when analyzing. Ensure events are properly instrumented on the site before drawing conclusions.

## Smart Strategy

1. **Start with Overview** — Call the dashboard overview endpoint first. Get a sense of your overall traffic, bounce rate, and session patterns. This gives you baseline context.

2. **Drill into Top Pages** — Identify which pages drive the most traffic. These are your high-value assets. Look for outliers (unexpectedly popular or underperforming pages).

3. **Understand Traffic Sources** — Segment your visitors by source. Organic search, direct, and referral typically have different characteristics. Paid traffic should show clear ROI.

4. **Check Device & Geographic Split** — Understand your audience composition. If 70% of traffic is mobile, mobile performance becomes critical. If traffic is global, consider regional differences.

5. **Compare Periods** — Always use the comparison endpoint for trend analysis. Growth rates matter more than absolute numbers.

6. **Monitor Conversions** — Link traffic back to business outcomes. High traffic + low conversions = optimization opportunity. High conversions + low traffic = scaling opportunity.

7. **Use Time Series for Narrative** — If explaining performance over time, generate a time series chart. Visual trends are easier to communicate than tables.

8. **Investigate Anomalies** — Unusual spikes or drops deserve investigation. Was there a PR campaign? A technical issue? A viral link? Understanding causation helps with future planning.
