---
name: crm
description: Manage contacts, companies, deals, and sales pipelines. Track interactions, log notes, and monitor deal progress.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [crm, contacts, deals, pipeline]
suggested_template: sales_sdr
---

# CRM

This skill enables you to manage your sales pipeline, track customer relationships, log interactions, and monitor deal progress. You can create and update contacts and companies, move deals through stages, record notes, and generate pipeline reports.

> **Dashboard Connection:** Link your CRM instance (HubSpot, Salesforce, Pipedrive, or equivalent) to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- CRM account configured in the dashboard
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- Familiarity with your sales pipeline stages and deal values
- Contact and company records (may already exist in your CRM)

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the CRM proxy endpoints |
| `google-workspace` | No | Optional; use to sync contacts and save reports to Google Sheets |
| `email-outreach` skill | No | Optional; use to send emails to contacts directly from the CRM |
| `slack` skill | No | Optional; use to send deal notifications and pipeline updates to Slack |

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test listing contacts to verify CRM connectivity before creating new records

## How It Works

This skill wraps a CRM API to manage all aspects of your sales process:
- Create and search contacts and companies
- Create and track deals through your sales pipeline
- Move deals between stages as they progress
- Log notes and interactions against contacts and deals
- View activity timelines and pipeline metrics
- Generate dashboard summaries for pipeline visibility

All requests use the proxy endpoint format: `${PROXY_URL}/crm/...`

## Available Tools

**1. List Contacts**

```bash
curl -X GET "${PROXY_URL}/crm/contacts?limit=50&offset=0" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns paginated array of contacts with id, email, first_name, last_name, phone, company_id, tags, created_at

---

**2. Create a Contact**

```bash
curl -X POST "${PROXY_URL}/crm/contacts" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contact@company.com",
    "first_name": "Sarah",
    "last_name": "Chen",
    "phone": "+1-555-0123",
    "company_id": "acme-corp-001",
    "tags": ["decision-maker", "tech-buyer"]
  }'
```

**Response:** Returns created contact object with auto-assigned `id`

---

**3. Get Contact Details**

```bash
curl -X GET "${PROXY_URL}/crm/contacts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns full contact profile including notes, associated deals, and activity log

---

**4. Update a Contact**

```bash
curl -X PUT "${PROXY_URL}/crm/contacts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1-555-0456",
    "tags": ["decision-maker", "vip"]
  }'
```

**Response:** Returns updated contact object

---

**5. Search Contacts**

```bash
curl -X GET "${PROXY_URL}/crm/contacts/search?q=sarah" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of matching contacts

---

**6. List Companies**

```bash
curl -X GET "${PROXY_URL}/crm/companies" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of companies with id, name, domain, industry, size

---

**7. Create a Company**

```bash
curl -X POST "${PROXY_URL}/crm/companies" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": "acme.com",
    "industry": "Technology",
    "size": "500-1000"
  }'
```

**Response:** Returns created company object with auto-assigned `id`

---

**8. Get Company Details**

```bash
curl -X GET "${PROXY_URL}/crm/companies/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns company profile including all associated contacts and active deals

---

**9. List Deals**

```bash
curl -X GET "${PROXY_URL}/crm/deals?stage=negotiation&owner=user-123&limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of deals filtered by stage, owner, or limit with value, stage, contact_id, status

---

**10. Create a Deal**

```bash
curl -X POST "${PROXY_URL}/crm/deals" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Acme Enterprise License - Annual",
    "value": 50000,
    "currency": "USD",
    "stage": "discovery",
    "contact_id": "contact-001",
    "company_id": "acme-corp-001"
  }'
```

**Response:** Returns created deal object with auto-assigned `id`

---

**11. Update a Deal**

```bash
curl -X PUT "${PROXY_URL}/crm/deals/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "proposal",
    "value": 60000,
    "notes": "Customer requested additional features; revised quote sent"
  }'
```

**Response:** Returns updated deal object

---

**12. Get Deal Activity Timeline**

```bash
curl -X GET "${PROXY_URL}/crm/deals/{id}/activity" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns chronological log of all interactions, stage changes, and note updates for the deal

---

**13. Add a Note to Contact or Deal**

```bash
curl -X POST "${PROXY_URL}/crm/notes" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "deal",
    "entity_id": "deal-001",
    "content": "Customer expressed strong interest in Q2 implementation. Follow up with technical spec by Friday."
  }'
```

**Response:** Returns created note object with timestamp

---

**14. List Pipeline Stages**

```bash
curl -X GET "${PROXY_URL}/crm/pipelines" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of pipeline stages (e.g., discovery, proposal, negotiation, closed-won, closed-lost)

---

**15. Get Dashboard Metrics**

```bash
curl -X GET "${PROXY_URL}/crm/dashboard" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns summary object with `total_deals`, `pipeline_value`, `win_rate`, `average_deal_size`, `deals_by_stage`

---

## Important Rules

1. **Search before creating** — Always check for duplicate contacts or companies before creating new ones. Use the search endpoint.
2. **Confirm before deleting** — Deleting records is permanent. Confirm the entity and warn if it has associated deals or activity.
3. **Log all interactions** — After every customer call, email, or meeting, add a note to the contact or deal. This keeps your pipeline accurate.
4. **Keep deal stages current** — Move deals promptly when status changes. Stale stages mislead forecasting.
5. **Use consistent company data** — Ensure contact.company_id matches the parent company record to maintain referential integrity.
6. **Monitor deal velocity** — Track time in each stage to identify bottlenecks in your sales process.
7. **Tag contacts meaningfully** — Use tags like decision-maker, influencer, technical-buyer to segment outreach.
8. **Validate email addresses** — Before creating a contact, verify the email format to avoid invalid records.

## Smart Strategy

- **Check dashboard first:** Review overall pipeline metrics and deal distribution before starting daily work. This keeps priorities aligned.
- **Review recent activity:** Before reaching out to a contact, read their activity log and notes. Avoid duplicating outreach.
- **Use tags strategically:** Segment contacts by role (decision-maker, technical-buyer, influencer) to enable targeted follow-up campaigns.
- **Track deal velocity:** Monitor how long deals spend in each stage. Fast movers signal strong interest; slow movers need intervention.
- **Clean up lost deals:** Regularly mark stalled deals as closed-lost and document the reason. This keeps your forecast realistic.
- **Prioritize high-value deals:** Sort by deal value and focus on largest opportunities. High-value deals justify more personalized attention.
- **Set stage-specific actions:** Define what must happen before a deal moves to the next stage (e.g., proposal review before negotiation).
- **Sync with email campaigns:** When launching outreach campaigns, pull contact and company info from the CRM to ensure consistency.
- **Monitor win rate trends:** Track which industries, deal sizes, and sales reps have the best close rates. Use this to refine strategy.
