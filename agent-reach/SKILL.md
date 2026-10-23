---
name: agent-reach
title: Agent Reach
description: >
  Read the public internet from the agent: web search (Exa), any web page or
  RSS feed, GitHub, YouTube and podcast transcripts, Twitter/X, Reddit,
  Facebook, Instagram, LinkedIn, Bilibili, XiaoHongShu, V2EX and Xueqiu.
  One router picks the healthiest backend per platform; run
  `agent-reach doctor --json` to see what is live. Read-only: it fetches,
  it never posts.
author:
  name: Linkedroid
  url: https://github.com/linkedroid
  title: English edition of Agent Reach by Agent Eyes
license: MIT
category: general
tags: [research, web-search, social-listening, twitter, reddit, youtube]
suggested_template: research_agent
source:
  name: Agent Reach (English edition)
  url: https://github.com/linkedroid/agent-reach
  repo: https://github.com/linkedroid/agent-reach
  path: agent_reach/skill
  creator: https://github.com/Panniantong/Agent-Reach
  commit: cd6d625be497a057d5a8b66aa3de18a6132ee4fb
---

# Agent Reach — internet capability router

16 platforms, multiple backends each. **When this skill exists, use it for
these platforms — do not invent your own approach.** It only *fetches*
internet content: for writing, analysis or posting use the skill that owns
that job (for example `social-publisher` to post).

## On a MyClawBots agent

The `agent-reach` command is a Python package that is **not** on the machine
until you install it. Do this once per machine, before the first use:

```bash
uv tool install --force git+https://github.com/linkedroid/agent-reach.git
export PATH="$HOME/.local/bin:$PATH"
agent-reach version
agent-reach install --env=auto     # read-only environment check, installs nothing system-wide
agent-reach doctor --json          # which backend serves each platform right now
```

- `uv`, `python3`, `curl`, `git`, `node`/`npx` and `jq` are preinstalled.
  `yt-dlp` arrives with the package. `gh` (GitHub CLI) is **not** installed:
  for GitHub use the `github` skill, or `curl https://api.github.com/search/repositories?q=…`.
- The machine's root filesystem is reset when the agent's image is updated.
  If `agent-reach` is suddenly "command not found", run the install block again.
- Anything that needs a logged-in browser (XiaoHongShu, Reddit via OpenCLI,
  Facebook/Instagram, BOSS Zhipin) assumes a desktop Chrome session. There is
  no browser on this machine: use the cookie-based backends the references
  describe (the owner exports cookies and pastes them into MyClawBots →
  Secrets), or tell the owner which platforms are out of reach here.
- Keep credentials out of logs: never echo cookies or tokens, and never write
  them into the workspace.

## Standing rules (apply for the whole session)

1. **Health-check before acting**: for multi-backend/login-backed platforms (XiaoHongShu /
   Reddit / Bilibili / Twitter / Facebook / Instagram / BOSS Zhipin), run `agent-reach doctor --json` first.
   Use a populated `active_backend`; `active_backend: null` means Doctor deliberately skipped a
   live probe to avoid browser-cookie reads or remote writes, not that no backend exists. Only when
   the user's task requires that platform, run the reference's read-only command to verify it.
   Doctor results are a snapshot; channel availability and login state may have changed.
   If you suspect stale results before a read-only command, follow the matching reference's
   health-check and recovery runbook (such as the BOSS Zhipin CDP checks in career.md).
2. **Announce what you use**: say "using agent-reach, platform X via backend Y"
   before starting.
3. **On failure, follow the retry chains in references/** — never guess
   commands.
4. **For broad research tasks**: combine platforms (Exa for web search +
   Twitter/Reddit for discussions + XiaoHongShu/Bilibili for Chinese
   perspectives), collect in parallel, then synthesize.
5. **Updates** come from re-running the install block above (`uv tool install --force …`);
   there is nothing for the owner to paste.

## Routing table

| User intent | Category | Details |
|---------|------|---------|
| Web / code search | search | [references/search.md](references/search.md) |
| XiaoHongShu / Twitter / Bilibili / V2EX / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| Jobs / LinkedIn / BOSS Zhipin | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| Web pages / articles / RSS | web | [references/web.md](references/web.md) |
| YouTube / Bilibili / podcast transcripts | video | [references/video.md](references/video.md) |
| Xueqiu / stock quotes | finance | [references/finance.md](references/finance.md) |

## Zero-config quick commands

```bash
# Exa web search (mcporter: `npx -y mcporter` on this machine)
mcporter call exa.web_search_exa query="query" numResults=5

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search (no gh CLI here — the REST API is public for search)
curl -s "https://api.github.com/search/repositories?q=query&sort=stars&per_page=10" | jq '.items[] | {full_name, stargazers_count, description}'

# YouTube subtitles (never use yt-dlp for Bilibili; retry chain in video.md)
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# Bilibili search (bili-cli, no login needed)
bili search "query" --type video -n 5
```

## Login-backed platforms (pick by doctor's active_backend)

Twitter boundary: cookies saved by `agent-reach configure twitter-cookies`
are used only by `doctor` to check whether explicit credentials are present.
`doctor` does not run `twitter status` or configure the current shell. Before
calling `twitter` directly, explicitly provide `TWITTER_AUTH_TOKEN` and
`TWITTER_CT0` in the child-process environment without logging their values.

XiaoHongShu boundary: Agent Reach must not log the user in or read browser
cookies. OpenCLI may use only an existing Chrome session explicitly controlled
by the user. If none exists, do not automate login; use a manual Cookie-Editor
export with xiaohongshu-mcp or a legacy tool instead.

```bash
# Twitter search (twitter-cli preferred; retry chain in social.md)
twitter search "query" -n 10

# Reddit (NO zero-config path — OpenCLI or rdt-cli, login required)
opencli reddit search "query" -f yaml   # desktop
rdt search "query" --limit 10            # legacy/server

# XiaoHongShu (desktop prefers OpenCLI)
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram (desktop OpenCLI, browser session)
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # user search
opencli instagram user USERNAME -f yaml        # recent posts from one user
```

## Environment check

```bash
# Channel availability + which backend serves each platform
agent-reach doctor --json
```

When the user asks "help me set up BOSS Zhipin", read the
Boss section in `references/career.md`. After explicit install approval, run
`agent-reach install --env=local --system --channels=boss`, launch the dedicated
Chrome profile bound only to `127.0.0.1:9222` for their OS, then **pause and have the user visually
confirm** the window is logged in (avatar in the top-right); if not, have them log
in manually. Then verify with `boss --cdp-url http://localhost:9222 login --cdp`
and `agent-reach doctor`. Do not make the user assemble CDP flags.
Keep reusing the dedicated Chrome profile; do not recreate it for every run or
switch to the user's daily profile by default. Search with
`boss --browser-source existing-browser --cdp-url http://localhost:9222 search ...`.
On `ENVIRONMENT_RISK`, stop without refreshing, relogging, or retrying.

**Do not trust `boss status` for CDP browser login state** — it only validates the
local `~/.boss-agent/auth/session.enc` store, which does not represent the
dedicated Chrome profile's cookies that `existing-browser` searches actually use. Use
the browser `wt2` cookie probe in `agent-reach doctor` plus the user's visual
confirmation. Never judge login state from the page URL: `security-check` /
`zhipin-security` / `_security_check` pages are anti-bot challenges that appear
even when logged in (almost always with a CDP-enabled Chrome session). If one appears,
check browser cookies with `agent-reach doctor` before deciding whether login is needed.
`AUTH_EXPIRED` from a search is the ground truth for a
logged-out browser — go straight to the login flow + `login --cdp` instead of
interpreting it as a security check.

## Discovering OpenCLI adapters

When the routing table lacks a needed platform or command, run `opencli list`,
then inspect `opencli <platform> --help`. Discovery proves only that an adapter
exists, not that authentication or target content works. Run read-only commands
only when the user's task requires that platform, and require non-empty content.

## Workspace rules

**Never create files in the agent workspace.** Use `/tmp/` for temporary
output and `~/.agent-reach/` for persistent data.

## Detailed references

Read the matching file when you need specifics (commands above cover the
common cases; references hold per-backend command groups, caveats, retry
chains):

- [Search](references/search.md) — Exa AI search
- [Social](references/social.md) — XiaoHongShu, Twitter, Bilibili, V2EX, Reddit, Facebook, Instagram (multi-backend/login-backed groups)
- [Career](references/career.md) — LinkedIn, BOSS Zhipin
- [Dev](references/dev.md) — GitHub CLI
- [Web](references/web.md) — Jina Reader, RSS
- [Video](references/video.md) — YouTube, Bilibili, Xiaoyuzhou
- [Finance](references/finance.md) — Xueqiu quotes, search and market content

## Configure a channel

If a channel needs setup, fetch the install guide:
https://raw.githubusercontent.com/linkedroid/agent-reach/main/docs/install.md

The user only provides cookies / one extension click; the agent does the rest.
