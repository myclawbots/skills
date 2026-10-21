---
name: whatsapp
description: Send and receive WhatsApp Business messages. Manage customer conversations, broadcast updates, set up auto-replies, and analyze chat patterns.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: communication
tags: [whatsapp, messaging, auto-reply, broadcast]
suggested_template: customer_support
---

# WhatsApp Business

> **IMPORTANT:** WhatsApp messaging is available for this agent.
> Connected accounts are managed through the MyClaw Bots dashboard.
> **ALWAYS confirm before sending, especially broadcasts.**

## How it works
- Connected WhatsApp Business accounts are available via the API proxy
- All messages are audited and logged automatically
- The proxy handles authentication — no secrets on this machine
- Approved templates are required for business-initiated messages outside the 24-hour window

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| WhatsApp Business account connected via dashboard | Yes | The proxy needs a connected account to send and receive messages |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the WhatsApp proxy endpoints |
| `google-workspace` | No | Optional; use to save chat analysis and reports to Google Sheets |

**Pre-flight checks:**
- Verify the WhatsApp Business account is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test getting account info to verify account connectivity before messaging

## Available Tools

### 1. Get account info
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/account" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: `{ "phone_number": "+1234567890", "display_name": "MyBusiness", "status": "verified" }`

### 2. Send individual message
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/send" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to_phone": "+1987654321",
    "message_type": "text",
    "content": "Hi! Your order has shipped. Track it here: https://track.example.com/123"
  }'
```

### 3. Send template message
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/send" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to_phone": "+1987654321",
    "message_type": "template",
    "template_id": "order_shipped",
    "template_params": {
      "order_id": "12345",
      "tracking_url": "https://track.example.com/123"
    }
  }'
```

### 4. Broadcast to multiple contacts
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/broadcast" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to_phones": ["+1987654321", "+1987654322"],
    "template_id": "flash_sale",
    "template_params": {
      "discount": "30%",
      "expires": "2026-04-02"
    }
  }'
```

### 5. List conversations
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/conversations?limit=20&status=open" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: active and closed conversations with unread counts and last message time.

### 6. Get conversation messages
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/conversations/conv_001/messages?limit=50" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: full message history with timestamps and authors.

### 7. Set up auto-reply rule
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/auto-reply" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "keyword",
    "match": "hours",
    "response": "Thanks for reaching out! Our hours are Mon–Fri, 9 AM–6 PM EST.",
    "active": true
  }'
```

### 8. List auto-reply rules
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/auto-replies" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: all active and inactive auto-reply rules.

### 9. Get messaging analytics
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/analytics?period=30d" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: sent, delivered, read counts, failure rates, response times, and busiest hours.

### 10. Analyze chat patterns
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/analyze-chats" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "30d",
    "extract": ["sentiment", "faqs", "topics", "sales_signals"]
  }'
```
Returns: sentiment breakdown, top FAQs, trending topics, and sales opportunities.

### 11. Get message templates
```bash
curl -s -X GET "${PROXY_URL}/whatsapp/templates" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: list of approved templates available for your account.

### 12. Submit new template
```bash
curl -s -X POST "${PROXY_URL}/whatsapp/templates" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "abandoned_cart",
    "category": "MARKETING",
    "language": "en",
    "components": [
      {
        "type": "body",
        "text": "Hi {{name}}, you have {{items}} in your cart. Complete your purchase now!"
      }
    ]
  }'
```

## Cross-Skill Synergies

- **Write messages** — Generate message copy with the agent's own intelligence
- **Save chat analysis** — Use `analyze-chats` to extract insights, save reports to Drive (via `gws`)
- **Segment customers** — Use agent intelligence to analyze conversation data and segment audiences
- **Pair with booking flows** — Coordinate with `appointment-taker` to handle booking inquiries via WhatsApp

## Important Rules
1. **ALWAYS** preview messages before sending, especially broadcasts
2. **ALWAYS** ask for explicit confirmation: "Shall I send this?"
3. **Respect the 24-hour window** — Use templates for business-initiated messages after 24 hours
4. **NEVER spam** — Only send unsolicited messages to opted-in customers
5. **Use approved templates** — All business-initiated messages outside 24 hours must use templates
6. **Segment broadcasts** — Don't send the same message to everyone; target relevant audiences
7. **Respond promptly** — Aim to respond to inquiries within 1–2 hours during business hours
8. **Monitor delivery** — Check analytics weekly for delivery rates and response trends
9. **Respect rate limits** — Don't exceed WhatsApp's 80 messages/second limit
10. If a message fails, report the error clearly to the user

