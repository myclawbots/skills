---
name: telegram
description: Send messages, photos, and documents to Telegram chats and groups via a connected Telegram bot.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: communication
tags: [telegram, bot, messaging, notifications]
suggested_template: general_assistant
---

# Telegram

> **IMPORTANT:** Telegram bot access is available for this agent.
> Connected Telegram bots are managed through the MyClaw Bots dashboard.
> **ALWAYS show the user a preview and ask for explicit confirmation before sending messages.**

## How it works
- Connected Telegram bots are available via the API proxy
- All messages are audited and logged automatically
- The proxy handles authentication — no secrets on this machine
- Messages can be formatted with HTML or Markdown for rich text

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Telegram bot token connected via dashboard | Yes | The proxy needs a connected bot token to send and receive messages |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the Telegram proxy endpoints |

**Pre-flight checks:**
- Verify the Telegram bot is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test getting bot info to verify bot connectivity before messaging

## Available Tools

### 1. Get bot information
```bash
curl -s -X GET "${PROXY_URL}/telegram/me" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: bot username, ID, first name, and connection status.

### 2. Get recent updates/messages
```bash
curl -s -X GET "${PROXY_URL}/telegram/updates?limit=20" \
  -H "x-api-key: $PROXY_API_KEY"
```
- `limit`: number of recent messages to return (default: 20)
- Returns: message text, sender ID, chat ID, timestamp, and message type

### 3. Send text message
```bash
curl -s -X POST "${PROXY_URL}/telegram/messages" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "text": "Hello Telegram!"
  }'
```
Returns: sent message ID.

### 4. Send formatted message (HTML)
```bash
curl -s -X POST "${PROXY_URL}/telegram/messages" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "text": "<b>Bold</b> and <i>italic</i> with <a href=\"https://example.com\">links</a>",
    "parse_mode": "HTML"
  }'
```
HTML supports: `<b>bold</b>`, `<i>italic</i>`, `<u>underline</u>`, `<s>strikethrough</s>`, `<a href="url">link</a>`, `<code>code</code>`, `<pre>block code</pre>`.

### 5. Send formatted message (Markdown)
```bash
curl -s -X POST "${PROXY_URL}/telegram/messages" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "text": "*Bold* and _italic_ with [link](https://example.com)",
    "parse_mode": "Markdown"
  }'
```
Markdown supports: `*bold*`, `_italic_`, `[link](url)`, `` `code` ``, `` ```code block``` ``.

### 6. Send photo
```bash
curl -s -X POST "${PROXY_URL}/telegram/photos" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "photo_url": "https://example.com/image.jpg",
    "caption": "Optional caption with <b>formatting</b>",
    "parse_mode": "HTML"
  }'
```
- `photo_url`: must be a valid public URL
- `caption`: optional, supports formatting
- Returns: message ID with photo

### 7. Send document
```bash
curl -s -X POST "${PROXY_URL}/telegram/documents" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "document_url": "https://example.com/file.pdf",
    "caption": "Optional document description"
  }'
```
- `document_url`: must be a valid public URL
- Supports PDFs, documents, archives, and other file types
- Returns: message ID with document

### 8. Edit message text
```bash
curl -s -X POST "${PROXY_URL}/telegram/messages/edit" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "message_id": "987654",
    "text": "Updated message text"
  }'
```
Use this to correct or update previously sent messages.

### 9. Delete message
```bash
curl -s -X DELETE "${PROXY_URL}/telegram/messages/{message_id}?chat_id=123456789" \
  -H "x-api-key: $PROXY_API_KEY"
```
⚠️ **ALWAYS** confirm with the user before deleting. This cannot be undone.

### 10. List known chats
```bash
curl -s -X GET "${PROXY_URL}/telegram/chats" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: chat IDs, titles, types (private, group, supergroup), and member counts.

### 11. Pin message
```bash
curl -s -X POST "${PROXY_URL}/telegram/pins" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "message_id": "987654"
  }'
```
Pins a message to the top of the chat for important announcements.

## Important Rules
1. **ALWAYS** list chats first to get the correct `chat_id`
2. **ALWAYS** show the user a preview of the message before sending
3. **ALWAYS** ask for explicit confirmation: "Shall I send this message?"
4. **ALWAYS** confirm before deleting messages — this cannot be undone
5. Use HTML parse_mode for rich formatting — it's more flexible than Markdown
6. Keep messages concise for mobile readers — avoid very long blocks of text
7. Break complex information into multiple short messages rather than one long message
8. Never expose bot tokens or API secrets
9. Photos and documents must be publicly accessible URLs
10. Test formatting with simple examples first before sending important announcements
11. If a message send fails, report the error clearly to the user
12. After sending, confirm the message was posted successfully
13. For groups, consider using mentions (e.g., `@username`) when relevant to notify specific members
14. Keep in mind message length limits — Telegram has character limits for different message types

## Telegram Best Practices
When communicating via Telegram:
1. **Format for mobile** — use short lines and clear structure for phone screens
2. **Use HTML for announcements** — `<b>bold</b>` headers make messages stand out
3. **Include links** — Telegram supports clickable links with `<a href="url">text</a>` (HTML)
4. **Send media with captions** — provide context for photos and documents
5. **Pin important messages** — use pins for announcements or guidelines that members should see
6. **Check recent updates** before sending — understand the conversation context first
7. **Edit for corrections** — if you make a typo or error, edit rather than delete and resend
8. **Be mindful of group timing** — avoid sending during hours when the group is typically quiet

