---
name: email_outreach
description: Send transactional and marketing emails, manage contact lists, create email campaigns with branded templates, and track delivery/open/click metrics.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: communication
tags: [email, campaigns, newsletter, outreach]
suggested_template: marketing_strategist
---

# Email Outreach

This skill enables you to send emails, build and manage contact lists, run email campaigns, and track performance metrics like opens, clicks, and bounces. All communication is handled through a proxy-wrapped email provider API that manages authentication and delivery.

> **Dashboard Connection:** Link your email provider account (SendGrid, Mailchimp, or equivalent) to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- Email provider account configured in the dashboard
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- For batch sending: list IDs from your email provider, or ability to create new contact groups
- For compliance: maintain current unsubscribe lists and honor opt-out preferences

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Email service connected via dashboard | Yes | Enables sending emails and managing contacts |
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for proxy authentication |
| `google-workspace` skill | No | Optional: for syncing contacts from Google Workspace |
| `crm` skill | No | Optional: for pulling contact lists from CRM |

**Pre-flight checks:**
- Verify email service is configured in the MyClawBots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- If syncing contacts: ensure `google-workspace` skill is available
- If pulling from CRM: ensure `crm` skill is connected

## How It Works

This skill wraps a transactional/marketing email API. You can:
- Send single emails or batch campaigns to multiple recipients
- Create, search, and update contact databases
- Design and schedule email campaigns with branded templates
- Generate branded HTML email templates customized to your brand
- Track opens, clicks, bounces, and unsubscribes in real-time
- Manage and preview reusable email templates for faster sending

All requests use the proxy endpoint format: `${PROXY_URL}/email/...`

## Available Tools

**1. Send a Single Email**

```bash
curl -X POST "${PROXY_URL}/email/send" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Welcome to Our Service",
    "html_body": "<h1>Hello!</h1><p>This is your welcome email.</p>",
    "text_body": "Hello! This is your welcome email.",
    "from_name": "Support Team",
    "reply_to": "support@company.com"
  }'
```

**Response:** Returns `{ "message_id": "...", "status": "queued" }`

---

**2. Send Batch Emails to Multiple Recipients**

```bash
curl -X POST "${PROXY_URL}/email/send-batch" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"email": "user1@example.com", "first_name": "Alice"},
      {"email": "user2@example.com", "first_name": "Bob"}
    ],
    "subject": "Special Offer Just for You",
    "html_body": "<p>Hi {{first_name}}, here is your exclusive deal.</p>",
    "text_body": "Hi {{first_name}}, here is your exclusive deal."
  }'
```

**Response:** Returns `{ "batch_id": "...", "sent_count": 2, "failed_count": 0 }`

---

**3. List Contacts**

```bash
curl -X GET "${PROXY_URL}/email/contacts?limit=50&offset=0" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns paginated array of contacts with id, email, first_name, last_name, tags, created_at

---

**4. Add a Contact**

```bash
curl -X POST "${PROXY_URL}/email/contacts" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newcontact@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "tags": ["vip", "enterprise"]
  }'
```

**Response:** Returns created contact object with auto-assigned `id`

---

**5. Update a Contact**

```bash
curl -X PUT "${PROXY_URL}/email/contacts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Janet",
    "tags": ["vip", "enterprise", "renewal"]
  }'
```

**Response:** Returns updated contact object

---

**6. Delete a Contact**

```bash
curl -X DELETE "${PROXY_URL}/email/contacts/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "deleted": true, "id": "..." }`

---

**7. Search Contacts**

```bash
curl -X GET "${PROXY_URL}/email/contacts/search?q=jane" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of matching contacts

---

**8. Create an Email Campaign**

```bash
curl -X POST "${PROXY_URL}/email/campaigns" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spring Sale 2026",
    "subject": "Don't miss our Spring Sale",
    "html_body": "<h2>Spring Sale</h2><p>Save up to 40% off.</p>",
    "list_id": "contacts_vip",
    "scheduled_at": "2026-04-01T09:00:00Z"
  }'
```

**Response:** Returns campaign object with `id`, `status`, `scheduled_at`

---

**9. List Campaigns**

```bash
curl -X GET "${PROXY_URL}/email/campaigns" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of campaigns with status (draft, scheduled, sent, paused)

---

**10. Get Campaign Statistics**

```bash
curl -X GET "${PROXY_URL}/email/campaigns/{id}/stats" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "sent": 500, "opened": 150, "open_rate": 0.30, "clicked": 45, "click_rate": 0.09, "bounced": 5, "unsubscribed": 2 }`

---

**11. List Email Templates**

```bash
curl -X GET "${PROXY_URL}/email/templates" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of saved templates with id, name, subject, created_at

---

**12. Create an Email Template**

```bash
curl -X POST "${PROXY_URL}/email/templates" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Series - Day 1",
    "subject": "Welcome to {{company_name}}!",
    "html_body": "<h1>Hello {{first_name}}</h1><p>We're excited to have you on board.</p>"
  }'
```

**Response:** Returns created template object with `id`

---

**13. Generate a Branded Email Template**

```bash
curl -X POST "${PROXY_URL}/email/template/generate" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "newsletter",
    "brand_colors": {
      "primary": "#2563EB",
      "secondary": "#1E40AF"
    },
    "logo_url": "https://example.com/logo.png",
    "tone": "professional",
    "content_blocks": [
      {"type": "header", "text": "Monthly Newsletter"},
      {"type": "section", "title": "Top Stories", "content": "..."},
      {"type": "cta", "text": "Read More", "url": "https://example.com"}
    ]
  }'
```

**Response:** Returns generated HTML template with responsive design and brand colors applied.

---

**14. Preview Email Template**

```bash
curl -X POST "${PROXY_URL}/email/template/preview" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "welcome-123",
    "sample_data": {
      "first_name": "John",
      "company_name": "Acme Inc"
    }
  }'
```

**Response:** Returns rendered HTML preview with sample data filled in.

---

**15. List Saved Templates**

```bash
curl -X GET "${PROXY_URL}/email/templates" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of saved templates with id, name, subject, created_at, and type (custom, generated).

---

**16. Update a Template**

```bash
curl -X PUT "${PROXY_URL}/email/templates/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Series - Updated",
    "html_body": "<h1>Updated Welcome</h1>..."
  }'
```

**Response:** Returns updated template object.

---

**17. Delete a Template**

```bash
curl -X DELETE "${PROXY_URL}/email/templates/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "deleted": true, "template_id": "..." }`

---

## Important Rules

1. **Always confirm before sending** — Preview the email content and recipient list. Show counts for batch sends.
2. **Never exceed recipient limits** — Double-check the `recipients` array matches the intended audience.
3. **Honor unsubscribe requests** — Never send to contacts marked as unsubscribed or bounced. Filter them out automatically.
4. **Protect email addresses** — Never log or display raw email addresses in plain text. Use masked format (e.g., `u***@example.com`) in summaries.
5. **Validate sender identity** — Ensure `from_name` and `reply_to` match approved branding guidelines.
6. **Track opt-in status** — Only send marketing emails to contacts with explicit opt-in. Transactional emails may be sent to all contacts.
7. **Monitor bounce rates** — Watch for high bounce rates (>5%) and remove invalid addresses from future sends.
8. **Test campaigns first** — Before scheduling batch sends, test with a small sample recipient list.
9. **Preview templates before use** — Always generate and preview templates to ensure brand colors, layout, and content are correct.
10. **Use consistent branding** — Generate templates with your brand colors and logo for professional appearance across all emails.

## Smart Strategy

- **Generate branded templates first:** Use the template generation endpoint to create branded HTML templates matching your brand colors and logo.
- **Preview and refine:** Always preview templates with sample data before using them in campaigns.
- **Start with templates:** Save reusable email templates to speed up campaign creation and ensure consistency across all emails.
- **Segment by tags:** Use contact tags (VIP, trial, churn-risk, etc.) to create targeted campaigns with higher engagement.
- **Track key metrics:** Monitor open rates and click rates to identify high-performing subject lines and templates.
- **Stagger sends:** For large campaigns, schedule sends at optimal engagement windows (typically Tuesday–Thursday, 9am–12pm).
- **Monitor bounce lists:** After each batch send, check for new bounces and update contact status to avoid future delivery issues.
- **A/B test templates:** Create multiple template variants with different layouts and colors, then compare performance.
- **Clean before bulk sends:** Search for and remove unsubscribed/bounced contacts before scheduling a major campaign.
- **Use reply-to smartly:** Set `reply_to` to a monitored inbox so customer responses reach the right team.
- **Maintain template library:** Keep updated templates for common campaigns (welcome, promotional, newsletter, announcement) for quick deployment.
