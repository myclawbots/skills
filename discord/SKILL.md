---
name: discord
description: Send messages, manage channels, read message history, and moderate a connected Discord server.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: communication
tags: [discord, messaging, moderation, community]
suggested_template: community_manager
---

# Discord

> **IMPORTANT:** Discord server access is available for this agent.
> Connected Discord servers are managed through the MyClaw Bots dashboard.
> **ALWAYS show the user a preview and ask for explicit confirmation before sending messages.**

## How it works
- Connected Discord servers are available via the API proxy
- All messages are audited and logged automatically
- The proxy handles authentication — no secrets on this machine
- Embeds allow rich message formatting and structured content

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Discord bot connected via dashboard | Yes | The proxy needs a connected bot to access Discord servers and channels |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the Discord proxy endpoints |

**Pre-flight checks:**
- Verify the Discord bot is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test listing guilds to verify bot connectivity before messaging

## Available Tools

### 1. List connected servers (guilds)
```bash
curl -s -X GET "${PROXY_URL}/discord/guilds" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: `{ "guilds": [{ "id": "123...", "name": "Community", "owner_id": "...", "member_count": 150 }] }`

### 2. List channels in a server
```bash
curl -s -X GET "${PROXY_URL}/discord/channels?guild_id=123456789" \
  -H "x-api-key: $PROXY_API_KEY"
```
Returns: channels with types (text, voice, category), permissions, and member counts.

### 3. Read message history
```bash
curl -s -X GET "${PROXY_URL}/discord/channels/{id}/messages?limit=50" \
  -H "x-api-key: $PROXY_API_KEY"
```
- `limit`: number of messages to return (default: 50, max: 100)
- Returns: message content, author, timestamp, reactions, attachment URLs

### 4. Send message to channel
```bash
curl -s -X POST "${PROXY_URL}/discord/messages" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "123456789",
    "content": "Hello Discord!"
  }'
```
Returns: message ID for future reference or edits.

### 5. Send message with embed (rich formatting)
```bash
curl -s -X POST "${PROXY_URL}/discord/messages" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "123456789",
    "content": "Optional text before embed",
    "embed": {
      "title": "Announcement",
      "description": "This is an embed message",
      "color": 3447003,
      "fields": [
        {
          "name": "Field Name",
          "value": "Field Value",
          "inline": false
        }
      ]
    }
  }'
```
Use embeds for structured information, announcements, or rich content.

### 6. Reply to a message
```bash
curl -s -X POST "${PROXY_URL}/discord/messages/reply" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "123456789",
    "message_id": "987654321",
    "content": "This is a reply"
  }'
```
Replies show context to the referenced message.

### 7. Delete a message
```bash
curl -s -X DELETE "${PROXY_URL}/discord/messages/{id}?channel_id=123456789" \
  -H "x-api-key: $PROXY_API_KEY"
```
⚠️ **ALWAYS** confirm with the user before deleting. This cannot be undone.

### 8. List server members
```bash
curl -s -X GET "${PROXY_URL}/discord/members?guild_id=123456789&limit=100" \
  -H "x-api-key: $PROXY_API_KEY"
```
- `limit`: max members to return (default: 100)
- Returns: user IDs, usernames, roles, join dates, and status

### 9. Update channel
```bash
curl -s -X PUT "${PROXY_URL}/discord/channels/{id}" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-channel-name",
    "topic": "Channel description or topic"
  }'
```
Use this to rename channels or update their topics.

### 10. Add reaction to message
```bash
curl -s -X POST "${PROXY_URL}/discord/reactions" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "123456789",
    "message_id": "987654321",
    "emoji": "👍"
  }'
```
Emoji can be Unicode (👍) or custom server emoji (`:custom_emoji:`).

## Important Rules
1. **ALWAYS** list servers and channels first to get the correct `guild_id` and `channel_id`
2. **ALWAYS** show the user a preview of the message before sending
3. **ALWAYS** ask for explicit confirmation: "Shall I send this message?"
4. **ALWAYS** confirm before deleting messages — this cannot be undone
5. Respect channel permissions — verify the agent has access before posting
6. Use embeds for announcements, structured data, or important messages
7. Keep messages concise and clear
8. Never expose internal bot tokens or Discord secrets
9. Use mentions (e.g., `<@123456789>`) or roles (e.g., `<@&role_id>`) when appropriate
10. Check channel topics and permissions before posting — ensure the content matches the channel purpose
11. If a message send fails, report the error clearly to the user
12. After sending, confirm the message was posted successfully

## Discord Moderation Best Practices
When moderating or managing the server:
1. **Review recent messages** before taking moderation action
2. **Confirm member identity** before applying roles or permissions
3. **Check member history** to understand context before warnings or removals
4. **Use embeds for announcements** so they stand out and are easy to reference
5. **Always warn before removing** — give users a chance to correct behavior
6. **Document actions** — post a summary of moderation actions in a log channel if available

