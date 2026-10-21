---
name: reddit_leads
description: Search relevant Reddit discussions to find potential customers. Identify leads, track conversations, and push qualified leads to your CRM.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [reddit, leads, prospecting, listening]
suggested_template: sales_sdr
---

# Reddit Leads Generator

> **IMPORTANT:** This skill searches Reddit and drafts replies. NEVER spam or promote without adding genuine value. All drafted replies must be reviewed and approved by a human before posting. The proxy handles Reddit API access — you just use the `${PROXY_URL}` and `$PROXY_API_KEY` headers. Reddit requires authentic, helpful engagement.

## Prerequisites — MUST READ

1. **Product Knowledge**: Deeply understand your product, ideal customer, and when it solves problems.
2. **Target Subreddits**: Identify 5-10 relevant subreddits where your audience hangs out.
3. **Keywords**: Prepare keywords your ideal customer would search (not product names, but problem statements).
4. **CRM Connection**: Link your CRM (Salesforce, HubSpot, Pipedrive) to auto-push qualified leads.
5. **Authenticity**: Be genuinely helpful. Never spam or promote. Authentic engagement only.
6. **API Key**: Your `$PROXY_API_KEY` is configured in your environment.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Reddit access connected via dashboard | Yes | The proxy needs Reddit API access to search discussions and post replies |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the Reddit proxy endpoints |
| `crm` skill | No | Optional; use to push qualified leads to your CRM (HubSpot, Salesforce, Pipedrive) |
| `slack` skill | No | Optional; use to send lead notifications to Slack channels |

**Pre-flight checks:**
- Verify Reddit access is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test searching Reddit with sample keywords to verify connectivity

## How it works

This skill finds high-intent prospects on Reddit by searching for discussions about problems your product solves. It identifies threads where real people ask for solutions, drafts helpful replies (never pushy), lets you review before posting, and qualifies leads based on intent signals. Push qualified prospects directly to your CRM and track conversion.

The workflow:
1. Search Reddit for keyword/subreddit combinations
2. Review discovered discussions and identify high-intent threads
3. Draft helpful, value-first replies that address the person's problem
4. Review and approve all drafted replies before posting
5. Engage authentically in the community
6. Qualify leads based on conversation and intent
7. Push qualified leads to CRM
8. Track conversion from lead to customer

## Available Tools

### 1. Search Reddit Discussions

Find relevant Reddit discussions where your ideal customers are asking questions.

```bash
curl -X POST ${PROXY_URL}/reddit/search \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": [
      "project management alternatives",
      "remote team collaboration",
      "asana vs monday"
    ],
    "subreddits": [
      "r/productivity",
      "r/remotework",
      "r/startups",
      "r/entrepreneur"
    ],
    "min_score": 10,
    "period": "month",
    "sort": "relevance"
  }'
```

**Period**: `day`, `week`, `month`, `year`.

**Sort**: `relevance`, `hot`, `new`. For lead gen, prefer `new` (recent questions).

**Response**: Returns `job_id` for search processing.

### 2. Get Search Results

Retrieve discussions found from your search query.

```bash
curl -X GET ${PROXY_URL}/reddit/search/{job_id} \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Array of relevant threads with title, subreddit, author, score, comments, intent_score (0-100), link.

### 3. Set Up Keyword Monitoring

Watch for new discussions matching your keywords and get notified in real-time.

```bash
curl -X POST ${PROXY_URL}/reddit/monitor \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": [
      "project management tool",
      "team collaboration software"
    ],
    "subreddits": [
      "r/startups",
      "r/smallbusiness",
      "r/entrepreneur"
    ],
    "notify_via": "email",
    "frequency": "daily"
  }'
```

**notify_via**: `email`, `slack` (requires integration).

**frequency**: `realtime` (instant), `daily`, `weekly`.

### 4. List Active Monitors

See all keyword monitors you've set up.

```bash
curl -X GET ${PROXY_URL}/reddit/monitors \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Array of monitors with keywords, subreddits, frequency, last_notification, next_check.

### 5. Remove Monitor

Stop monitoring specific keywords.

```bash
curl -X DELETE ${PROXY_URL}/reddit/monitors/{id} \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Confirmation that monitor has been deleted.

### 6. List Identified Leads

Retrieve leads discovered from Reddit discussions, filtered by status.

```bash
curl -X GET "${PROXY_URL}/reddit/leads?limit=20&status=new" \
  -H "x-api-key: $PROXY_API_KEY"
```

**Status**: `new` (just found), `qualified` (high intent), `contacted` (message sent), `converted` (customer).

**Response**: Array of leads with username, subreddit, discussion_link, intent_score, status, notes.

### 7. Qualify a Lead

Mark a lead as qualified and add notes about their intent/fit.

```bash
curl -X POST ${PROXY_URL}/reddit/leads/{id}/qualify \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Looking for affordable project management tool for 5-person startup. Budget-conscious but willing to pay for quality.",
    "score": 8
  }'
```

**Score**: 1-10 (10 = perfect fit, 1 = poor fit).

**Response**: Updated lead status and qualification details.

### 8. Push Lead to CRM

Send a qualified Reddit lead to your connected CRM (HubSpot, Salesforce, Pipedrive, etc.).

```bash
curl -X POST ${PROXY_URL}/reddit/leads/{id}/push-to-crm \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_data": {
      "first_name": "Sarah",
      "email": "sarah.email@example.com",
      "company": "TechStartup Inc",
      "interest": "Project management tool",
      "source": "reddit",
      "notes": "Found in r/startups, looking for team collaboration solution"
    }
  }'
```

**Response**: Confirmation of CRM push, deal_id, and CRM link.

### 9. Draft a Reply

Create a helpful, value-first reply to a Reddit thread. ALWAYS review before posting.

```bash
curl -X POST ${PROXY_URL}/reddit/draft-reply \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "abc123",
    "context": "Person asking about best project management tool for remote team",
    "product_info": {
      "name": "TeamFlow",
      "strength": "Real-time collaboration and async-friendly workflows"
    },
    "tone": "helpful"
  }'
```

**Tone**: `helpful` (solution-focused), `casual` (friendly peer), `expert` (authority).

**Response**: Drafted reply text. REVIEW before submitting. Confirm it adds value without being salesy.

### 10. Get Analytics

Track your Reddit lead generation performance over time.

```bash
curl -X GET "${PROXY_URL}/reddit/analytics?period=30d" \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Leads found, leads qualified, leads contacted, conversion_rate, average_intent_score, top_keywords, top_subreddits.

## Important Rules

1. **NEVER spam Reddit** — always add genuine value. Spam gets you banned and harms your reputation.
2. **Draft replies must add value** — solve the person's problem first, mention your product second (if at all).
3. **Show all drafted replies before posting** — human review is mandatory. Never auto-post.
4. **Respect subreddit rules** — read the rules. Some prohibit self-promotion. Follow them strictly.
5. **Focus on genuine fit** — only engage in threads where your product genuinely solves the problem.
6. **Be honest about limitations** — acknowledge what your product doesn't do. Honesty builds trust.
7. **Track conversion thoroughly** — monitor leads from search → qualified → contacted → customer.
8. **Avoid fake accounts** — use your real identity. Authenticity is Reddit's core value.

## Smart Strategy

1. **Define target keywords**: Brainstorm 20+ keywords your ideal customer searches (problems, not product names).
2. **Pick 5-10 relevant subreddits**: r/startups, r/entrepreneur, r/productivity, r/remotework, r/smallbusiness, etc.
3. **Search and review**: Find high-intent threads where people ask for solutions you provide.
4. **Draft helpful replies**: Address their specific problem. Mention your product only if genuinely relevant. Always include context/experience.
5. **Human approves all replies**: Review every draft. Make sure it's helpful, not salesy.
6. **Engage authentically**: Answer follow-up questions. Build real relationships. Be part of the community.
7. **Qualify high-intent leads**: Mark people as qualified if they express interest or fit your ideal customer profile.
8. **Push to CRM**: Move qualified leads into your sales pipeline for follow-up.
9. **Track and optimize**: Monitor conversion rate from Reddit lead → customer. Double down on what works.
