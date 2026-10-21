---
name: google_workspace
description: Read, search and send the user's Gmail — latest or unread emails, what's in the inbox, a message's contents, replies — plus Google Calendar events, Drive files, Sheets, Docs and Contacts. When GWS_GOOGLE_ACCOUNT is set their Google account IS connected — answer by running `gws` commands yourself; never say you cannot access their email.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [gmail, google-calendar, google-drive, sheets, docs]
suggested_template: general_assistant
---

# Google Workspace (GWS)

## How to use this skill — read first
- This is a set of shell commands, **not an agent**. Do the work yourself in
  this conversation by running `gws …` with your exec/shell tool. Never try to
  start a sub-agent or session named `google_workspace` — that is not allowed
  and does not exist.
- Before telling the user you cannot reach their email, calendar or files,
  check: `echo "$GWS_GOOGLE_ACCOUNT"`. If it prints an address, the account is
  connected — run the command. Only if it is empty (or `gws` returns an
  auth/token error) use the "not connected" message below.

**"What's my latest / most recent email?"**
```bash
gws gmail users messages list --params '{"userId": "me", "q": "in:inbox", "maxResults": 1}'
# then, with the id it returns:
gws gmail users messages get --params '{"userId": "me", "id": "<id>", "format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]}'
```
Answer with the sender, subject and when it arrived. Use `"q": "is:unread in:inbox"` for unread mail.

> **IMPORTANT:** Google Workspace access is managed through the MyClawBots dashboard.
> Do NOT run `gws auth setup` or `gws auth login` — authentication is
> handled automatically via a token proxy. You MUST NOT attempt manual OAuth setup.

## Prerequisites — MUST READ
- The user MUST connect their Google account in the MyClawBots dashboard **before** this skill can work.
- Connection is done at: **Settings → Integrations → Google Workspace → Connect**
- If `GWS_GOOGLE_ACCOUNT` is empty or `gws` commands fail with auth/token errors, you MUST tell the user:
  > "Google Workspace isn't connected yet. Connect it at https://myclawbots.ai/settings/social — Google Workspace → **Connect**. Then open this agent and hit **Save Settings** so the connection reaches me, and I'll be able to access your Gmail, Calendar, Drive, and more."
- **NEVER** suggest manual OAuth flows, token generation, or credential setup. The dashboard handles everything.
- **NEVER** expose or discuss proxy URLs, token endpoints, or internal auth mechanisms with the user.
- Run `gws` with the default exec settings — NEVER pass `host=sandbox` (there is no sandbox runtime on this machine and the command will fail).

## How it works
- `GWS_GOOGLE_ACCOUNT` is set to the connected Google email (empty if not connected)
- Authentication tokens are managed by a secure proxy (no secrets on this machine)
- You can use all `gws` commands directly — no setup needed once connected

## More than one Google account
The user can connect several Google accounts (Settings → Connectors →
Google Workspace → **Add account**), and can change which one is the
**default** at any time. `gws accounts` always shows the current list and
default; `GWS_GOOGLE_ACCOUNT` is only the default from when you started, so
when you need to say which account you used, check `gws accounts`.

For anything involving a second account, run the wrapper that ships with
this skill — **the full path below, not plain `gws`**. It is always current;
the `gws` on your PATH may be older and reject `--account`.

```bash
/root/.openclaw/skills/google-workspace/scripts/gws accounts      # connected accounts, current default marked
/root/.openclaw/skills/google-workspace/scripts/gws --account work@example.com gmail +send --to <email> --subject <subject> --body <text>
/root/.openclaw/skills/google-workspace/scripts/gws --account work@example.com calendar events list --params '{"calendarId": "primary", "timeMin": "...", "timeMax": "..."}'
```
- It takes every normal `gws` command. Without `--account`, it acts as the
  default account, exactly like plain `gws`.
- When the user names an account ("from my work email", "on my personal
  calendar"), run `gws accounts` and use the matching address with `--account`.
- If it is unclear which account they mean and it matters (sending, creating,
  deleting), **ask** — never guess.
- Always say which account you used, e.g. "Sent from work@example.com".
- If `--account` fails with "not connected", show the user the accounts
  the `accounts` command lists. Never retry on the default account instead.
- New accounts work immediately — no restart or Save Settings needed.

## Quick reference

### Gmail
- **List emails:** `gws gmail users messages list --params '{"userId": "me", "q": "newer_than:7d", "maxResults": 10}'`
- **Send email:** see **Sending email** below — always the full-path command.
- **Read email:** `gws gmail users messages get --params '{"userId": "me", "id": "<message_id>", "format": "full"}'`

### Calendar
- **List events:** `gws calendar events list --params '{"calendarId": "primary", "timeMin": "...", "timeMax": "..."}'`
- **Create event:** `gws calendar events insert --params '{"calendarId": "primary"}' --body '{"summary": "Meeting", "start": {...}, "end": {...}}'`

### Drive
- **Search files:** `gws drive files list --params '{"q": "name contains \"report\"", "pageSize": 10}'`
- **Download file:** `gws drive files get --params '{"fileId": "<file_id>", "alt": "media"}'`

### Contacts
- **List contacts:** `gws people people connections list --params '{"resourceName": "people/me", "pageSize": 20, "personFields": "names,emailAddresses"}'`

### Sheets
- **Read data:** `gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "Sheet1!A1:D10"}'`
- **Write data:** `gws sheets spreadsheets values update --params '{"spreadsheetId": "ID", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' --body '{"values": [["a","b"],["c","d"]]}'`

### Docs
- **Read doc:** `gws docs documents get --params '{"documentId": "ID"}'`

## Sending email
Always send with the copy of `gws` that ships with this skill (full path — it
works on every agent, while the `gws` on your PATH may be too old to send):

```bash
/root/.openclaw/skills/google-workspace/scripts/gws gmail +send --to a@x.com --subject "…" --body "…"
#   optional: --cc b@y.com,c@z.com  --bcc …  --html   --account other@gmail.com
#             --attach /path/file.pdf  (repeat for more files; -a works too)
```
- Show the user the email and send only when they approve it.
- MyClawBots adds an **unsubscribe link** to every email it sends, and the
  recipient can use it at any time. Do not remove or work around it.
- If sending fails with **"unsubscribed"**, that person opted out of the
  user's emails. **Never** try to reach them another way (another account,
  another tool, Outlook, a different address of theirs). Tell the user.
- One email to the people involved, never the same message to a list. At most
  20 recipients per email.
- Attachments: up to 10 files, 18 MB in total. Bigger files: share a Drive
  link in the body instead.
- No Gmail drafts. `+reply`, `+reply-all` and `+forward` are not available —
  send a new email with "Re: …" in the subject instead.

## Proactive inbox triage

**Applies only when `GWS_GOOGLE_ACCOUNT` is non-empty.** If it is empty, this
section does not apply: do nothing, and do not mention Gmail at all.

On each scheduled check, look at recent mail and report **only what needs the
user's attention**. The default outcome is silence — most inboxes, most of the
time, contain nothing worth interrupting someone for.

```bash
gws gmail users messages list --params '{"userId": "me", "q": "is:unread newer_than:1d -category:promotions -category:social -category:updates", "maxResults": 25}'
```

**Report these:**
- Time-sensitive mail — deadlines, invoices or payments due, renewals, legal or account notices
- Threads where someone is visibly waiting on the user's reply
- Meeting invites that need a response
- Security and account notices — sign-in alerts, password resets, billing failures

**Stay silent on these:**
- Newsletters, promotions, social and updates categories
- Automated notifications that need no action
- Anything already read, replied to, or archived
- Routine mail that merely arrived

**Rules:**
- **If nothing qualifies, say nothing.** Do not send "nothing to report", do not
  send a summary of how many messages you checked, do not announce that you
  looked. An empty inbox scan produces no message at all.
- When something does qualify, report at most 5 items, most urgent first, one
  line each: sender — subject — why it matters — how old it is.
- Summarise. Never paste full message bodies, and keep addresses, phone numbers
  and account identifiers out of the report unless the user asks for them.
- Read only. Never reply, archive, label or delete during a triage pass — say
  what you found and let the user decide.

## Notes
- All `gws` output is structured JSON
- For pagination, use `--page-all` or `--page-limit N`
- Always confirm before sending emails or creating calendar events
- For scripting, pipe output through `jq`

<!--
═══════════════════════════════════════════════════════════════════════════
APPROACH #2 (DISABLED — resumable): Composio tool execution via `gtool`
No Google verification needed, but no raw tokens / per-product connects.
To resume: point the dashboard connect flow back at /api/auth/composio/google,
set COMPOSIO_GMAIL_AUTH_CONFIG_ID, and restore the docs below as the active
section.

## How it works
- Use the `gtool` command: `gtool TOOL_SLUG '<json-arguments>'`
- Each call executes the action through a secure platform proxy — no credentials on this machine
- Output is JSON: { "successful": true|false, "data": {...}, "error": null|"message" }
- Always check `successful` before using `data`

### Gmail
- List emails: `gtool GMAIL_FETCH_EMAILS '{"max_results": 10, "query": "newer_than:7d"}'`
- Read email: `gtool GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID '{"message_id": "<id>", "format": "full"}'`
- Sending is never done with gtool — see **Sending email** above.

### Calendar / Drive / Sheets (require per-toolkit connections)
- `gtool GOOGLECALENDAR_EVENTS_LIST '{"calendarId": "primary"}'`
- `gtool GOOGLEDRIVE_FIND_FILE '{"query": "name contains \"report\""}'`
- `gtool GOOGLESHEETS_BATCH_GET '{"spreadsheet_id": "ID", "ranges": ["Sheet1!A1:D10"]}'`
═══════════════════════════════════════════════════════════════════════════
-->
