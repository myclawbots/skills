---
name: slack
description: Send messages, manage channels, read threads, and schedule messages in connected Slack workspaces. Deliver reports and notifications from other skills.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: communication
tags: [slack, messaging, notifications, channels]
suggested_template: general_assistant
---

# Slack

> **IMPORTANT:** Slack messaging is available for this agent.
> Connected workspaces are managed through the MyClaw Bots dashboard.
> **ALWAYS confirm before posting to public channels.**

## How it works
- Connected Slack workspaces are available via the API proxy
- All messages are audited and logged automatically
- The proxy handles authentication — no secrets on this machine

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Slack workspace connected via dashboard | Yes | The proxy needs a connected workspace to send and receive messages |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the Slack proxy endpoints |
| Other skills (content-auditor, review-tracker, news-aggregator) | No | Optional; these skills can deliver reports and notifications to Slack channels |

**Pre-flight checks:**
- Verify the Slack workspace is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test listing channels to verify connectivity before posting

## Available Tools

### 1. List channels
```bash
curl -s -X GET "${PROXY_URL}/slack/channels" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: `{ "channels": [{ "id": "C...", "name": "general", "is_private": false, "num_members": 42 }] }`

### 2. Read channel history
```bash
curl -s -X GET "${PROXY_URL}/slack/channel/C123456/history?limit=20" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: recent messages with timestamps, authors, and content.

### 3. Send a message
```bash
curl -s -X POST "${PROXY_URL}/slack/send" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C123456",
    "text": "Your message here"
  }'
```

### 4. Send message with formatting
```bash
curl -s -X POST "${PROXY_URL}/slack/send" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C123456",
    "text": "Message with *bold* and _italic_",
    "blocks": [{ "type": "section", "text": { "type": "mrkdwn", "text": "Formatted message" } }]
  }'
```

### 5. Send a thread reply
```bash
curl -s -X POST "${PROXY_URL}/slack/send" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C123456",
    "text": "Reply to the thread",
    "thread_ts": "1234567890.123456"
  }'
```

### 6. Read a thread
```bash
curl -s -X GET "${PROXY_URL}/slack/thread/C123456/1234567890.123456" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: parent message and all replies with timestamps and authors.

### 7. Schedule a message
```bash
curl -s -X POST "${PROXY_URL}/slack/schedule" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C123456",
    "text": "Scheduled message",
    "post_at": 1711700400
  }'
```
- `post_at` is Unix timestamp (must be in the future)

### 8. Add emoji reaction
```bash
curl -s -X POST "${PROXY_URL}/slack/react" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C123456",
    "timestamp": "1234567890.123456",
    "emoji": "thumbsup"
  }'
```

### 9. List workspace users
```bash
curl -s -X GET "${PROXY_URL}/slack/users" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: user list with IDs, names, and presence status.

### 10. Upload a file
```bash
curl -s -X POST "${PROXY_URL}/slack/file" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channels": ["C123456"],
    "filename": "report.pdf",
    "content": "<file_url_or_content>"
  }'
```

## Cross-Skill Synergies

- **Deliver news digests** — Generate content with the agent's own intelligence, then send to Slack channels
- **Send audit reports** — Use `content-auditor` to analyze, post summaries to Slack
- **Notify about reviews** — Use `review-tracker` to monitor, send notifications to designated channels
- **Share documents** — Generate or fetch files from Google Drive (via `gws`), then share links in Slack
- **Schedule announcements** — Plan ahead with scheduled messages for maximum visibility

## Important Rules
1. **ALWAYS** list channels first to verify the correct `channel` ID
2. **ALWAYS** show a preview and ask for explicit confirmation before posting to public channels
3. **NEVER** spam channels with unsolicited messages
4. **Use threads** for follow-ups to keep channels organized
5. **Respect @here and @channel** — use sparingly and only when urgent
6. Private channels are fine for internal reports; confirm before posting to company-wide channels
7. If a message fails, report the error clearly to the user
8. After posting, offer to check reactions or follow-ups later

