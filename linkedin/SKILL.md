---
name: linkedin
description: Write and publish LinkedIn posts (text, one image, or a 2-10 image carousel) on a connected LinkedIn profile or, when one is connected, a LinkedIn company Page, via the myclawbots MCP tools.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [linkedin, publishing, carousel, company-page]
suggested_template: content_creator
---

# LinkedIn

> **ALWAYS show the user a preview and ask for explicit confirmation before
> posting or deleting.** The preview, confirmation and media rules live in the
> `social-manager` skill — follow them; this skill only adds what is specific
> to LinkedIn.

## Use the MCP tools

The **`myclawbots` MCP server is pre-configured on this machine**. Do all
LinkedIn work through its tools — there is no separate LinkedIn API to call:

- `list_social_accounts` — call FIRST. LinkedIn rows have `platform: "linkedin"`.
- `create_upload_url` — stage a local image, then PUT the bytes (see `social-manager`).
- `post_to_social` — `{platform: "linkedin", account_id, content, media_url | media_urls}`.
- `get_recent_posts`, `delete_post` — LinkedIn **Pages** only (see below).

## Profile vs company Page

Connected accounts are managed in the MyClawBots dashboard (Settings →
Connectors). A LinkedIn account is one of two kinds, shown by `account_type`:

- `"profile"` — the person. Posting publishes **as them**. Publish-only:
  recent posts, deletion, insights and comments are not available.
- `"page"` — present only when a LinkedIn Page account is connected. `page_name`
  is the company; posting publishes **as the company**. Its recent posts can be
  read (no like or comment counts) and its own posts deleted.

Say which one in every preview — "Posting as Acme Corp (LinkedIn Page)" or
"Posting as Jane Doe (LinkedIn profile)". If both kinds are connected and the
user didn't say which, ask.

## Limits

- 3000 characters per post.
- Text, one image, or a 2-10 image carousel (JPG, PNG or GIF). **No video.**
- No scheduling, drafts, articles, polls, insights or comments — offer what is
  possible instead of trying.
- `#hashtags` stay live on a Page post; 3–5 is plenty.
- Company Page posting may not be available yet. If the user asks to post as
  their company and no `account_type: "page"` row exists, say no Page is
  connected — never post to the profile instead, and don't talk about LinkedIn
  reviews or approvals.

## Writing for LinkedIn

- Keep it professional; lead with the insight in the first two lines (the rest
  is behind "…see more").
- Avoid overly promotional language and engagement bait.
- Best reach is usually Tuesday–Thursday mornings in the audience's timezone —
  suggest a time, but post only when the user confirms.
- After posting, relay any `notice` verbatim and give the permalink when the
  result has one.
