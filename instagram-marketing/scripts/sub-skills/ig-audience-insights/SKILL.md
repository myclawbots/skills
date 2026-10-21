---
name: ig-audience-insights
description: "Read your Instagram performance from real data through the myclawbots MCP tools: account reach and follower stats, per-post saves, shares and reach, and the comments on your top performers. Turns that into the pattern worth repeating. Competitor reads are limited to public Facebook Pages and public Threads profiles — Instagram exposes nothing about other accounts, so competitor and hashtag research runs on pasted data. Triggers on \"how are my posts doing\", \"what's working on my account\", \"competitor stats\". Not for writing captions (use ig-caption-writer)."
---

# Instagram Audience Insights

Turn the user's real Instagram data into a read on what is working: which of
their posts actually earned saves and shares, what those posts had in common,
and what to make more of. This is the read layer, so the skill works from real
numbers instead of guessing.

Two honest limits, stated up front because half of this skill is not
over-claiming:

- **Instagram exposes nothing about accounts you do not own.** No competitor
  follower counts, no reading their posts, no hashtag feed. We do not scrape.
- **Instagram caps and cookie-gates who liked or commented** even on your own
  posts — Meta withholds the username on comments the connected account does not
  own. So there is no engager roster, on any account.

What you do get, on the connected account, is better than any scraper returns:
**saves, shares and reach**, the numbers Instagram ranks on and never shows
publicly.

## When to use

- "How are my posts doing / what's working on my account"
- "Which of my posts earned the most saves"
- "What should I make more of"
- "Pull the stats for this competitor" (see the limits — Facebook Pages and
  Threads only)
- Before `ig-content-planner`, to build next week's plan on evidence

Not for writing a caption (use `ig-caption-writer`) or planning a carousel (use
`ig-carousel-planner`).

## Setup

None. The **`myclawbots` MCP server is pre-configured on this machine** and the
Instagram account is connected in the dashboard. If `list_social_accounts`
returns no Instagram account, that is the one thing to fix — point the user at
**Settings → Social** rather than working around it.

## What the read layer exposes

| Tool | Returns | Scope |
|---|---|---|
| `get_account_insights` | followers, reach, impressions | **own account** |
| `get_recent_posts` | recent posts with captions, type, permalink | **own account** |
| `get_post_insights` | **saves, shares**, reach, likes, comments per post | **own post** |
| `get_post_comments` | the comments on a post, with replies | **own post** |
| `search_public_pages` / `get_public_page_metrics` | public page stats | **Facebook only** |
| `lookup_threads_profile` | a public Threads profile + recent posts | **Threads only** |

`search_public_pages` and `get_public_page_metrics` are **Facebook-only** — the
`account_id` merely authorises the lookup. A hidden counter comes back `null`,
**not** `0`: report "not public", never zero.

`lookup_threads_profile` needs the **exact** handle (no fuzzy match, no
suggestions) and only finds profiles with 100+ followers.

## Input

- Nothing, for a read of the user's own account (the default)
- Optional: a date range, a specific post, or a goal (what is working / why did
  this post land / benchmark me)
- For competitor work: a Facebook Page name, a Threads handle, or pasted data

## Output

1. **Account pulse** — reach, impressions and follower movement over the
   period, with the direction called honestly (a flat week is a flat week)
2. **Post ranking** — recent posts ranked by **saves + shares**, not likes, with
   reach alongside so a small-reach breakout is visible
3. **The pattern** — what the top posts share: format (Reel / carousel / single
   image), hook shape, caption length, a specific number, a question. Named only
   when it recurs across several posts
4. **Comment read** — what people actually said on the top performers, and any
   question worth answering or turning into a post
5. **Action list** — what to make more of, what to stop, and what to route to
   `ig-caption-writer` or `ig-carousel-planner`

## Steps

1. **Get the account.** `list_social_accounts` → the Instagram `account_id`.
   Everything below needs it.
2. **Pull the account pulse.** `get_account_insights` for followers, reach and
   impressions over the period. A counter the account does not expose comes
   back `null`, **not** zero — report it as unavailable.
3. **Pull the posts.** `get_recent_posts`, then `get_post_insights` on each one
   worth ranking. The per-post call is where saves and shares live — the list
   alone will not have them.
4. **Rank by saves + shares.** Not likes. Saves and sends are the 2026 ranking
   levers (`../../references/algorithm-heuristics.md`); likes are the noisiest
   signal on the page. Show reach next to each so a post that did a lot with
   little reach is not buried.
5. **Extract the pattern.** For the top posts, name what they share: format,
   hook shape (question, confession, list, data-point), caption length, presence
   of a specific number, where the CTA sat. That is the repeatable part.
6. **Read the comments on the winners.** `get_post_comments` on the top two or
   three. What people asked is next week's content. If comments come back with
   no author, relay the response's `note` and move on — see below.
7. **Benchmark, if asked.** Facebook Pages via `search_public_pages` +
   `get_public_page_metrics`; a Threads competitor via `lookup_threads_profile`.
   For an Instagram competitor there is no tool — say so and offer the paste
   path. Normalize by follower count before calling anything a winner, or you
   are measuring account size, not post quality.
8. **Build the action list.** Make-more-of (the winning format), stop (what
   consistently underperforms), and the drafts to hand to `ig-caption-writer` /
   `ig-carousel-planner`.
9. **Deliver the report** in the Output shape, with the raw ranked posts
   attached.

## Working without the tools

When the user wants a niche scan, an Instagram competitor's numbers, or a
hashtag read, there is no tool. Say that plainly, then offer the paste path:
they paste the posts or the profile stats they can see, and the skill runs the
same ranking and pattern analysis on them. The analysis is the valuable half;
the fetch is not.

Do not dress this up as a limitation of their account or a setting they can
change. Instagram does not expose other accounts through the API to anyone.

## Comments with no author

Meta withholds the username on comments the connected account does not own, and
does not error. Facebook returns the author; Instagram often does not. The
response carries a `note` when it happens — **relay it and stop there.** Do not
diagnose a cause: a connection that demonstrably holds the comment permission
still hits this, so "you need to reconnect" is a guess, not an answer. The
comments are real, not anonymous, and nothing is broken on our side.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- **Rank on saves and shares, not likes.** Likes are the metric the user already
  sees and the one Instagram cares about least.
- **Never invent a post, a number, or a pattern.** If the data is thin, say it
  is thin. A week with four posts does not support a trend claim.
- A pattern is only a pattern if it recurs across several top posts, not one.
- **Normalize by reach or follower count** before calling a post a winner.
- Be honest about the walls: no Instagram competitor data, no hashtag feed, no
  engager roster. Never imply otherwise, and never present a Facebook Page's or
  a Threads profile's numbers as an Instagram account's.
- A `null` counter means "not public". Never report it as zero.
- Facebook Page insights can come back partial — Meta retires metrics on a
  schedule and names the dropped ones in a `note`. Report those as unavailable,
  never as zero, and never silently omit them.

## Related skills

- `social-manager` - the canonical tool contract for every read above
- `ig-caption-writer` - write more of what the data shows is working
- `ig-carousel-planner` - turn a winning format into a slide plan
- `ig-hook-extractor` - reverse-engineer the hook from a post that landed
- `ig-hashtag-strategist` - size the hashtag set
- `ig-content-planner` - feed the winning patterns into a weekly plan
