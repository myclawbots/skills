---
name: social_manager
description: Post to connected Facebook Pages, Instagram, Threads, LinkedIn profiles and company Pages, YouTube, TikTok and X accounts, and Pinterest when a Pinterest account is connected, via the myclawbots MCP tools. Supports text, images, carousels, video and Reels, Pinterest image Pins, scheduled posts, Threads quotes and reposts, LinkedIn comments and likes, insights, and post deletion.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [instagram, facebook, threads, linkedin, youtube, publishing]
suggested_template: content_creator
---

# Social Media Manager

> **ALWAYS show the user a preview and ask for explicit confirmation before
> posting, reposting or deleting.** Connected accounts are managed in the MyClawBots
> dashboard; all posts are audited and logged.

## Use the MCP tools

The **`myclawbots` MCP server is pre-configured on this machine** — do all
social work through its tools, never by hand-building API calls:

- `list_social_accounts` — call FIRST; every other call needs an `account_id` from here
- `create_upload_url` — stage a local file: returns a one-time `upload_url` + final `public_url`; PUT the raw bytes (`curl -X PUT --data-binary @file.png -H "Content-Type: image/png" <upload_url>`) — no credentials needed in that command
  - **Both steps are required.** The `public_url` is dead until the PUT
    succeeds. Posting it beforehand hands the platform a 404, which the
    platform then reports as its own download failure — that reads like a
    domain-verification or networking problem and is not one. If you cannot PUT
    raw bytes (for example the image only exists in this conversation, not on
    disk), use `upload_media` with base64 instead.
- `upload_media` — small images only, via base64 (1–2 small files max; otherwise `create_upload_url`)
- `post_to_social` — publish (fields below)

**Threads replies** — read the conversation with `get_post_comments`, then answer a
specific comment by passing its `reply_to_id` back to `post_to_social`. That is the
whole loop: read → pick → reply. The same field chains replies to yourself, which
is how you post a multi-part thread: publish, then reply to the id you got back,
and so on. Replies take media and carousels like any other post.

**Threads quotes** — `quote_post_id: "18077148170451907"` publishes your post as a
quote of that one: your text (and any image, video or carousel) with the quoted
post embedded under it. Use the numeric id from `get_recent_posts`,
`search_threads`, `get_threads_mentions` or `get_post_comments` — a permalink or
its short code is rejected. It combines with anything a normal post can do
except `ghost_post`. The result carries `is_quote: true` and `quoted`; confirm
it applied with `get_recent_posts` (`quoted_post`).

**Threads reposts** — `repost_on_threads` `{account_id, post_id}` shares an
existing post (anyone's) to the account's profile **with no added text**; it
shows publicly under the profile's Reposts tab. Want to add commentary? Quote it
instead. **Show the user the post you are about to repost and get an explicit
yes first**. To undo a repost, call `delete_post` with the `repost_id` it
returned — that removes it (verified; Meta does not document it). Reposting the
same post twice is refused with "already reposted" — say so, and don't retry. A repost appears in
`get_recent_posts` as its own row with `media_type: REPOST_FACADE` and
`reposted_post`.

**Threads polls** — `poll_options: ["Traditional", "Hybrid", "Agentic"]` attaches a
poll. 2-4 options, each 1-25 characters, **text-only posts only**: a poll cannot
go on a post with an image, video or carousel. Options appear in the order given.
Write them short — 25 characters is roughly two words, so "Retrieval-Augmented
Generation" will be rejected rather than trimmed.

**Threads topics** — `topic_tag: "AI agents"` files the post under a topic, which
is how it surfaces to people who do not follow the account. One per post, 1-50
characters, no `.` or `&`. It belongs to the post that **opens** a thread; sending
it on a reply is rejected, because Threads would accept the field and drop it.

**Threads long text** — a Threads post is capped at 500 characters, and
`long_text` is the way past it: up to 10,000 characters attached behind the post,
with `content` staying as the short visible hook. Text-only posts, and not
combinable with a poll. `long_text_link` adds a URL inside the attachment.

**Threads spoilers** — `spoiler_text: ["he dies at the end"]` blurs those exact
words until a reader taps them; up to 10 phrases, each quoted verbatim from
`content` (a phrase that is not in the text is rejected, not skipped, so that a
spoiler never silently fails to hide anything). `spoiler_media: true` blurs the
attached image, video or carousel.

**Threads ghost posts** — `ghost_post: true` publishes a text-only post that is
fully public now and auto-archives 24 hours later. It cannot be combined with
media, a poll, a reply, a quote, a topic tag or long text; text spoilers are the one extra
it allows. **Tell the user about the 24-hour expiry before publishing one** — the
post looks permanent in the feed, so nobody finds out by looking.
- `get_recent_posts`, `get_post_insights`, `get_post_comments`, `get_account_insights` — reads
- `search_public_pages`, `get_public_page_metrics` — public competitor research
- `delete_post` — remove a post you published
- `hide_reply` — hide or unhide a reply on your own Threads post
- `repost_on_threads` — repost a Threads post to the profile (confirm first; undo with delete_post on the repost_id)
- `reply_to_comment`, `hide_comment`, `delete_comment` — answer or moderate a
  comment on your own Facebook or Instagram post (LinkedIn: reply to any comment,
  delete your own)
- `comment_on_post`, `edit_comment`, `like_post` — LinkedIn profile only: comment on
  any post, edit your own comment, like/unlike a post or comment (all public — confirm first)
- `search_threads` — search public Threads by keyword or tag
- `get_threads_mentions` — public posts mentioning the connected account
- `lookup_threads_profile` — a public competitor's Threads profile + public posts

**Threads keyword search needs Meta's approval, and failure is silent.**
Without the `threads_keyword_search` permission Meta does not error — it
returns only the account's *own* posts, or nothing. So thin results mean
"not approved" at least as often as they mean "nobody is talking about
this". Never report an empty search as though the topic were quiet.

When a search comes back empty or only self-authored, say that plainly:

> I can't search public Threads yet — that needs keyword-search approval
> from Meta for the MyClawBots Threads app, which is a separate App Review
> submission. Until then I can only see our own posts.

Do not tell the user to change their own Threads account settings. The
permission belongs to the app, not to them, and there is nothing for them
to toggle.

`get_threads_mentions` fails the same silent way: unapproved, Meta returns
only mentions written by a Threads tester on the app. Apply the same rule —
few results is not evidence that nobody mentioned them.

**Both tools return a `note` field when the result set looks unapproved.**
Quote it. Do not invent a reason for thin results: there is no such thing as
a search permission restricted to certain topics or industries, and telling
the user their account is limited that way sends them looking for a setting
that does not exist.

`lookup_threads_profile` needs the **exact** handle; Meta offers no fuzzy
match, so a near-miss returns nothing rather than a suggestion. Only profiles
with 100+ followers are discoverable at all. Use it to read a competitor's
positioning and recent posts before drafting a content plan — never present
its numbers as the user's own.

Fallback only if the MCP tools are unavailable: the same operations exist as a
REST API at `${PROXY_URL}/social/*` with header `x-api-key: $PROXY_API_KEY` —
**shell expansion only, never paste a key value**: secrets appear masked as
`***` in your transcript, and pasting the mask sends a broken key. If auth
fails while `test -n "$PROXY_API_KEY"` says the var is set, your command was
built wrong — do not advise regenerating keys.

## Media flow

- **Images the user attaches in chat reach you as pictures, without a file
  path.** If the message has an `[attachment note: …]`, run its `curl` commands
  to get them as files. For an image pasted straight into the chat, look for
  OpenClaw's copy, newest first: `ls -t /root/.openclaw/media/inbound/ | head -5`.
  If there is none, the image is only visible to you: ask the user for a link to
  it — never for a file path.
- **A `media://inbound/<name>` reference is not a path** — curl and other tools
  cannot open it. The file (image or video) is on disk at
  `/root/.openclaw/media/inbound/<name>`; use that path, e.g.
  `curl -X PUT --data-binary @/root/.openclaw/media/inbound/<name> …`.
- **Show the user an image before posting it** with one line
  `MEDIA:<absolute path>` per file in your reply (files under
  `/root/.openclaw/workspace/`). `view_image` shows a file only to you.
- Media URLs must be publicly reachable HTTPS — platforms fetch them themselves.
  Staged URLs live ~2h. **Stage once, reuse the same `public_url` for every
  platform** — never re-upload per platform.
- **A staged URL that has expired cannot be retried.** Post it promptly after
  staging. If posting fails because the file is gone, the fix is to upload it
  again and post straight away — never offer to retry the same post later, and
  never read a media failure as the platform being down. The error says which
  it is; quote it rather than interpreting it.
- TikTok only accepts URLs on our own staged domain — always stage for TikTok.
- Google Drive files: post with `media_source: "google_drive"` + `media_file_id`.
- Accepted types: jpeg, png, webp, gif, mp4, quicktime. Images ≤12MB, video ≤300MB (via `create_upload_url`).
  Pinterest takes **JPEG or PNG only** — convert a WebP or GIF before staging it for a Pin.

## Platform support at a glance

| | Text only | Single image | Video / Reel | Carousel | Mixed carousel | Schedule | Quote / repost |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **facebook** | yes | yes | yes (`video` or `reel`) | 2–10 | **no — images only** | yes | no |
| **instagram** | **no — media required** | yes | yes (always a Reel) | 2–10 | **yes** | no | no |
| **threads** | yes | yes | yes | 2–**20** | **yes** | no | **yes** (`quote_post_id` / `repost_on_threads`) |
| **linkedin** (profile) | yes | yes | yes (one video, ≤128MB) | 2–10 | **no — images only** | no | no |
| **linkedin** (Page) | yes | yes | **no** | 2–10 | **no — images only** | no | no |
| **youtube** | **no — video only** | **no** | yes (the whole post) | **no** | **no** | no | no |
| **tiktok** | **no — media required** | yes | yes | 2–**35** photos | **no** | no | no |
| **twitter** (X) | yes | yes | yes (one video) | 2–**4** images | **no** | no | no |
| **pinterest** | **no — image required** | yes | **only when enabled** (one staged MP4/MOV) | 2–**5** images | **no** | no | no |

"Mixed carousel" = photos and videos in one post (item types are auto-detected —
no `media_type` with `media_urls`). Never combine `media_url` with `media_urls`.

## Per-platform rules

- **facebook** — `scheduled_time` (ISO 8601 **with a timezone**, 15 min–29 days ahead) schedules; on any other platform it is refused, never ignored; `media_type: "reel"` posts a Page Reel vs `"video"` a regular video.
- **instagram** — media mandatory; video always publishes as a Reel (max 15 min, 9:16 best). Licensed library music **cannot** be attached via any API — the audio must already be in the file; say so instead of trying.
- **threads** — 500 character limit. Quote with `quote_post_id` (any post type, not a ghost post); repost with `repost_on_threads` — both public, both need the user's explicit yes, and `delete_post` on the `repost_id` undoes a repost.
- **linkedin** — max 150 posts/day; 3000 characters. A **profile** can post one video
  (`media_url`, ≤128MB, never in a carousel); a **Page** cannot (offer text/images).
  - Keep the `post_id` URN (`urn:li:share:…` / `urn:li:ugcPost:…`): `delete_post`,
    `comment_on_post` and `like_post` take it.
  - **Comments and likes (profile only).** `comment_on_post {account_id, post_id, message}`
    (≤1250 chars), `reply_to_comment` to answer a comment, `edit_comment` / `delete_comment`
    on the user's **own** comments, `like_post {account_id, target_id, reaction?, unlike?}` for a
    post or comment. `reaction`: like (default), celebrate, support, love, insightful, funny;
    send a new one to change it. If LinkedIn refuses a non-Like reaction, offer a plain like.
  - The app cannot list the user's posts, so for a post it did not just publish, ask for
    its link (Copy link to post) and pass the link as the id — never guess an id.
  - **Answering every comment on a post:** `get_post_comments {account_id, post_id}` (the
    post URN or link) → each comment has `id`, `text`, `author` (a member URN — LinkedIn
    does not share names), `is_mine`, `reply_count`. Skip `is_mine` ones, draft one reply
    per comment, show the user the list of comment → draft pairs, and only after their yes
    send each with `reply_to_comment {account_id, comment_id: <that id>, message}`.
    Pass a comment's `id` as `post_id` to read its replies first, so you never answer
    twice. If LinkedIn refuses the read, say so and ask the user to paste the comments.
  - `list_social_accounts` shows the member's `email` on a profile connected since
    2026-10-02 (reconnect an older one to get it).
  - When a LinkedIn Page account is connected, `list_social_accounts` shows it with
    `account_type: "page"` and its company name as `page_name`; posting with that
    `account_id` publishes **as the company**. `account_type: "profile"` posts as the person.
  - The preview must say which: "Posting as <Page name> (LinkedIn Page)" or "Posting as
    <you> (LinkedIn profile)". If both kinds are connected and the user didn't say, ask.
  - Example: `list_social_accounts` → pick the row with `account_type: "page"` →
    `post_to_social {platform: "linkedin", account_id: "<that id>", content: "..."}`.
- **youtube** — caption's **first line becomes the title (≤100 chars)**, the rest the description; `privacy_status`: `public` (default) / `unlisted` / `private`; single `media_url` only; upload is slow; **100 uploads/day shared platform-wide** — if exhausted, try tomorrow.
- **tiktok** — video = `media_url`, photo post = `media_urls` (2–35), never mixed. Publishing is **asynchronous**: success means TikTok accepted it, not that it is live. `privacy_status`: `PUBLIC_TO_EVERYONE` (default), `SELF_ONLY`, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`. `"draft": true` sends the video or photo post to the creator's TikTok inbox to caption and publish themselves (`privacy_status` ignored). Photo posts must be JPEG or WebP.
  - **Until the app passes TikTok's audit, direct posts to a PUBLIC account are blocked** and every direct post is forced private. Either the user sets their account private (TikTok app → Settings → Privacy) or use `"draft": true` (works on any account). Say which one you are suggesting — never just report a failure.
- **twitter** (X) — up to **4 images** via `media_urls`, or **one video** via `media_url`; the two cannot be mixed and there is no carousel past 4. No `scheduled_time`.
  - **X bills the account owner per post, and a post containing a link costs far more than one without.** Mention the cost when a post carries a link, and never silently retry: a post rejected on validation will be rejected again, and a post that succeeded has already been charged.
  - The character limit depends on the owner's X subscription (280 on a standard account, far more on a premium one), so we do not pre-check it — if X rejects the text for length, report X's own message rather than guessing a number.
  - Publish-only for now: recent posts, insights, comments and deletion are **not** available on X.
- **pinterest** — these rules apply when a Pinterest account is connected (it only
  appears in `list_social_accounts` when Pinterest is enabled on MyClawBots).
  - **An image is required**: `media_url` for one image, or `media_urls` with 2–5
    images for a carousel. JPEG or PNG only. No `scheduled_time`, no text-only Pin.
  - **Video only when enabled.** Video Pins exist only when the `post_to_social`
    tool description says so; otherwise there is **No video** — offer an image instead. When it
    is on: ONE video staged with `create_upload_url` (MP4 or MOV, 4 s–15 min) as
    `media_url`, plus a cover — `cover_image_url` (a staged JPEG/PNG, the safer
    choice) or `cover_frame_seconds`. Never in `media_urls`: carousels are images
    only. Processing takes a while; if the result says Pinterest is **still
    processing**, nothing was published — send the same post again a minute later
    (the upload is reused).
  - `content` is the Pin **description (≤800 characters)**. Optional: `title`
    (≤100), `link` — the page the Pin opens, `http(s)://` only (≤2048) — and
    `alt_text` (≤500) describing the image. Write `alt_text` whenever you can.
  - **Choose the board.** Each Pinterest account in `list_social_accounts` carries
    `boards` (`id`, `name`). Pass one `id` as `board_id`. If there is more than one
    board and the user did not say which, **ask** — never guess. Only public boards
    the user owns are listed; secret and group boards cannot be pinned to. With exactly one
    board you may omit `board_id`; the result's `notice` names the board used. If
    the row has `boards_error` instead, relay it.
  - **No boards yet.** For now the user's existing Pinterest boards do not appear
    here, so a new connection usually shows `boards: []`. **Ask whether to create
    one board** for their Pins (visible only to them).
    Only after an explicit yes, post with `board_name: "<name they chose>"` instead
    of `board_id`. MyClawBots creates at most one such board; after that, use its
    `board_id`. Never send `board_name` without that yes, and never with `board_id`.
  - **AI-generated images**: when the image was generated or edited with AI, send
    `ai_disclosures: ["AI_MODIFIED"]`; add `"SYNTHETIC_PERFORMER"` when it shows an
    AI-generated person. Say in the preview that the Pin will be labelled as AI content.
  - **One Pin, one confirmation.** Preview each Pin — board, title, description,
    link, image — and get an explicit yes for **that** Pin. No bulk or automatic
    pinning, no "pin these 20 for me" in one go: Pinterest's developer guidelines
    forbid actions taken without considering each one.
  - **Relay the `notice` word for word.** For now every successful Pin comes back
    with a notice that it is visible only to the user. **Never call a Pin public**,
    and do not promise a link: `permalink` can be `null`.
  - **Don't talk about access levels.** Never mention Pinterest "Trial" or
    "Standard" access, sandboxes, test environments, reviews or approvals to the
    user, and never tell them to upgrade or contact support about it. Say only what
    they can do now.
  - **Editing** (only when the `edit_post` and `edit_board` tools are listed):
    `edit_post` changes a Pin's description (`content`), `title`, `link`,
    `alt_text` or `ai_disclosures`, or moves it to another of the user's boards
    (`board_id`); `clear_fields` empties a field. The image or video **cannot** be
    changed — that means delete and post again. `edit_board` renames a board or
    changes its description (not its privacy). Both overwrite with no undo: show
    the user the old and new text and get an explicit yes first, exactly as for
    a new Pin. If the result says editing Pins isn't available, relay that
    (offer delete-and-repost if they want); do not retry.
  - If the error says Pinterest **did not accept a carousel**,
    it means exactly that: nothing was published. Offer a single image instead; do
    not retry the carousel.
  - Example: `list_social_accounts` → pick the Pinterest row and one of its `boards`
    → preview → on "yes": `post_to_social {platform: "pinterest", account_id: "<id>",
    board_id: "<board id>", title: "Autumn table ideas", content: "Five ways to…",
    link: "https://example.com/autumn", alt_text: "A wooden table set with…",
    media_url: "<staged public_url>"}`.

## Reads & research

- Recent posts, post insights, comments and account insights: **Facebook,
  Instagram and Threads** (deletion too, within each platform's limits). TikTok
  supports recent posts + profile counters. X is publish-only. LinkedIn profiles
  can post, delete their own posts, read a post's comments and replies, comment, react
  and like — but not list their posts or read insights (LinkedIn reserves those for
  select partners); say so rather than trying.
- A connected **YouTube** channel supports `get_recent_posts` (latest uploads,
  including private and unlisted, with views, likes and comments),
  `get_post_insights` and `get_post_comments` on the channel's **own** videos,
  and `get_account_insights` (subscribers, total views, video count — lifetime
  totals). **Watch time, retention and click-through rate are not available**:
  say so and point to YouTube Studio; never report them as zero. Replying to,
  hiding or deleting YouTube comments and deleting videos are not supported.
- A connected **LinkedIn Page** supports `get_recent_posts` (no counts) and
  `delete_post` on its own posts; insights and comments are not available for it.
- A connected **Pinterest** account supports `get_recent_posts` (no counts),
  `get_post_insights`, `get_account_insights` and `delete_post` — on the user's
  **own** Pins only (and `edit_post` / `edit_board` when those tools are listed). Pinterest has **no comments** API: the comment tools refuse it.
  Pin metrics can come back `null` — report them as unavailable, never as zero.
  Detailed period analytics may not be available; the result says so in a
  `notice` — relay it.
- **Answering comments** — read with `get_post_comments`, then reply. Facebook and
  Instagram use `reply_to_comment` with the comment's `id`; Threads uses
  `post_to_social` with `reply_to_id`. Each comment carries its own `replies`,
  so check them before answering — the thread may already have your reply, or
  the person's follow-up to it. Show the user the comment and your draft
  and get their go-ahead first: this posts publicly under their name.
- **Moderating** — `hide_comment` removes a comment for everyone but its author
  and can be undone; `delete_comment` cannot. Reach for hiding unless the user
  explicitly asked to delete, and quote the comment text before either.
- **Instagram may return comments with no author.** Meta withholds the username
  on comments the connected account does not own, and does not error. Facebook
  returns the author; Instagram often does not. The response carries a `note`
  when it happens — relay it and stop there. Do not diagnose a cause: a
  connection whose token demonstrably holds the comment permission still hits
  this, so "you need to reconnect" is a guess, not an answer. The comments are
  real, not anonymous, and nothing is broken on our side.
- Public Page search/compare (competitor research): **Facebook only**; the
  `account_id` merely authorises the lookup. A hidden counter comes back `null`,
  **not** `0` — report "not public", never zero.
- **Facebook Page insights can come back partial.** Meta retires Page metrics on
  a schedule, and the response names the dropped ones in a `note`. Report those
  as unavailable — never as zero, and never silently omit them.
- When asked to optimise content: check account insights → review recent posts →
  read comments on top performers → recommend posting times → offer to check
  performance the next day.

## Truthfulness

A successful post may include a `notice` field — **relay it to the user
verbatim**. Never describe a post as "published publicly" without positive
evidence: TikTok in particular may force a post private, and the user will
otherwise hunt for a post they cannot see.

## Rules

1. `list_social_accounts` first — every call needs the right `account_id`
2. Preview + explicit "Shall I post this?" before publishing, quoting or reposting; confirm before deleting (irreversible)
3. Stage media once, reuse the URL across platforms
4. Report failures clearly; relay every `notice`; after posting, offer to check insights later (FB/IG, Pinterest)
