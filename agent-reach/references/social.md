# Social Media & Communities

Xiaohongshu, Twitter/X, Bilibili, V2EX, Reddit, Facebook, and Instagram.

## Xiaohongshu / XiaoHongShu (Multiple Backends)

Xiaohongshu has three backends. **Run `agent-reach doctor --json` first to check the `active_backend` for xiaohongshu**, then use the corresponding commands.

### Backend A: OpenCLI (Preferred for Desktop)

```bash
# Search posts
opencli xiaohongshu search "query" -f yaml

# Read a post's body and engagement data (use the full URL from search results, including xsec_token)
opencli xiaohongshu note "NOTE_URL" -f yaml

# Comments (including nested replies)
opencli xiaohongshu comments NOTE_ID -f yaml

# Recommended home feed
opencli xiaohongshu feed -f yaml

# Public posts on a user's profile
opencli xiaohongshu user USER_ID -f yaml
```

> Requires Chrome to be open with the OpenCLI extension installed. OpenCLI only uses
> an existing Chrome session explicitly controlled by the user; Agent Reach does not
> sign in on the user's behalf or read browser cookies.
> `agent-reach configure xhs-cookies` does not inject cookies into OpenCLI.
> If no existing session is available, do not sign in automatically; use backend B/C
> and follow its manual Cookie-Editor export procedure instead.

### Backend B: xiaohongshu-mcp (For Servers)

```bash
# Before authentication, have the user export cookies manually with Cookie-Editor, then explicitly import them
agent-reach configure xhs-cookies

# Read-only check of the current status
mcporter call xiaohongshu.check_login_status --timeout 120000

# Search
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000

# Post details and comments (get feed_id and xsec_token from search results)
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

> The first call automatically downloads a headless browser of approximately 150 MB; always include `--timeout 120000`.
> Authenticate only through a manual Cookie-Editor export; run `check_login_status` after importing.
> This explicit command saves/imports the user-provided cookie set for the xiaohongshu.com
> domain, so the user should confirm its scope. Cookies for other domains are ignored.

### Backend C: xhs-cli (Legacy Fallback; Upstream Unmaintained Since March 2026)

```bash
xhs search "query"          # Search
xhs read NOTE_ID_OR_URL     # Read a post (use the URL/ID from search results, not a bare note_id)
xhs comments NOTE_ID_OR_URL # Comments
xhs hot                     # Trending
xhs feed                    # Recommendations
```

> Known instability: `xhs user` / `xhs user-posts` / `xhs favorites` may return an API error (upstream is unmaintained, with no one fixing these issues). New users should use backend A/B directly.

### General Notes

> **Authentication boundaries**: Agent Reach must not sign in to Xiaohongshu on the user's
> behalf or read browser cookies. OpenCLI may only use an existing Chrome session that
> the user explicitly controls; xiaohongshu-mcp / legacy tools use manual Cookie-Editor exports.
>
> **xsec_token requirement**: Xiaohongshu enforces xsec_token, so **you cannot read a post using a bare note_id**. First obtain results through search/feed, then read using the full URL/ID from those results. This applies to all three backends.
>
> **Rate limits**: High-frequency requests (batch searches or deep comment retrieval) trigger CAPTCHAs; platform restrictions cannot be bypassed. Wait 2–3 seconds between operations.
>
> **Write operations (posting/commenting/liking)**: Read-only use is recommended. Write operations in xhs-cli v0.6.x may return 406 due to signature issues.

## Twitter/X (twitter-cli)

### Authentication Prerequisites

Cookies saved through the hidden input in `agent-reach configure twitter-cookies`
are only used by `agent-reach doctor` to check whether explicit credentials are complete.
`doctor` does not run the upstream `twitter status` command or configure the current shell.
Before running any `twitter` command below, explicitly provide these variables
in the same shell or subprocess environment:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

### Stable Commands

```bash
# Home timeline (most reliable)
twitter feed -n 20

# Read a single tweet (including replies)
twitter tweet URL_OR_ID

# Read a long-form post / X Article
twitter article URL_OR_ID

# User timeline
twitter user-posts @username -n 20

# User profile
twitter user @username
```

### Potentially Unstable Commands

```bash
# Search tweets (Twitter frequently changes GraphQL endpoints, which may cause 404 errors)
twitter search "query" -n 10

# Likes (since 2024, only your own are visible due to platform restrictions)
twitter likes
```

### Retry Sequence When search Fails (Follow in Order; Stop on Success)

1. Retry once directly (intermittent failures are common): `twitter search "query" -n 10`
2. Upgrade and retry: `pipx upgrade twitter-cli && twitter search "query" -n 10`
3. Try OpenCLI as a fallback (desktop; reuses the browser's signed-in session): `opencli twitter search "query" -f yaml`
4. If none works, use stable commands such as `twitter feed` / `twitter user-posts @somebody` as an alternative

### Important Notes

> **Installation**: `pipx install twitter-cli` (ensure v0.8.5+)
>
> **Authentication**: Only use a manual Cookie-Editor export, then explicitly set
> `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`; do not rely on automatic browser cookie access.
>
> **IP-based risk controls**: Avoid frequent calls from VPS/data-center IPs, especially followers/following requests, as they may lead to account bans. Use a residential proxy or a local environment.
>
> **OpenCLI fallback**: If OpenCLI is installed on the desktop, the full `opencli twitter search/article/user-posts -f yaml` command set is available (uses the browser's signed-in session; no cookie environment variables required).
>
> **Output format**: Use `--yaml` or `--json` for structured output that is easier for AI agents to process.

## Bilibili

> ⚠️ **Do not use yt-dlp to read Bilibili** (its risk controls now block all requests with 412 responses; testing found no workaround). Use bili-cli / OpenCLI.

```bash
# Search / trending / video details (bili-cli; read-only access requires no login)
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx

# Subtitles (OpenCLI; requires desktop Chrome)
opencli bilibili subtitle BVxxx
```

> For detailed commands (audio transcription and a direct API fallback), see [references/video.md](video.md).

## V2EX (Public API)

No authentication required; call the public API directly.

### Trending Topics

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### Node Topics

```bash
# Example node_name values: python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### Topic Details

```bash
# Get topic_id from the URL, e.g. https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### Topic Replies

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### User Information

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python Example

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# Get trending posts
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} replies)")

# Get posts from a node
node_topics = ch.get_node_topics("python", limit=5)

# Get post details and replies
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])

# Get user information
user = ch.get_user("Livid")
```

> **Node directory**: https://www.v2ex.com/planes

## Reddit (Multiple Backends; Signed-In Session Required)

**Reddit has no zero-configuration option**: anonymous `.json` endpoints are blocked (403), and manual approval for the official API has rarely been granted since November 2025. Both backends rely on a signed-in session; first run `agent-reach doctor --json` to check the `active_backend` for reddit. Access from mainland China requires a proxy.

### Backend A: OpenCLI (Preferred for Desktop; Reuses the Browser's Signed-In Session)

```bash
# Search posts
opencli reddit search "query" -f yaml

# Read a full post and its comments
opencli reddit read POST_ID -f yaml

# Browse a subreddit / hot posts / Popular
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml

# Subreddit metadata (subscriber count and description)
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> Requires Chrome to be open and signed in to reddit.com.

### Backend B: rdt-cli (Legacy/Server Fallback; Upstream Unmaintained Since March 2026)

```bash
rdt search "query" --limit 10   # Search posts
rdt read POST_ID                # Read a full post and its comments
rdt sub python --limit 20       # Browse a subreddit
rdt popular --limit 10          # Browse popular posts
rdt all --limit 10              # Browse /r/all
```

> **Installation**: `pipx install 'git+https://github.com/public-clis/rdt-cli.git'` (the PyPI version is outdated; install v0.4.2+ from GitHub). Run `rdt login` before searching or reading (on a server without a browser, supply cookies manually; see the doctor guidance).
> Use `--yaml` output for easier processing by AI agents.

### Advanced Option: Official API + PRAW (Only for Users with Existing Credentials)

Users who registered a Reddit script app before November 2025 (and have a client_id/client_secret) can use the official API through PRAW (100 QPM free). New applications require manual approval, which is rarely granted for personal projects. **Do not recommend this option to new users**.

## Facebook (OpenCLI; Signed-In Session Required)

Facebook uses OpenCLI to reuse the user's facebook.com session in Chrome. First run `agent-reach doctor --json` to check the `active_backend` for facebook; it should normally be `OpenCLI`. Do not recommend Jina/Exa/Graph API as the default option.

```bash
# Search users / pages / posts
opencli facebook search "query" -f yaml

# User or page information
opencli facebook profile zuck -f yaml

# Current account's News Feed
opencli facebook feed --limit 10 -f yaml

# Groups and recent activity visible to the current account
opencli facebook groups --limit 20 -f yaml
```

> Requires Chrome to be open with the OpenCLI extension installed and signed in to facebook.com. Facebook Groups currently only supports reading the list of groups and recent activity visible to the current account; arbitrary group post and comment APIs are not guaranteed.

## Instagram (OpenCLI; Signed-In Session Required)

Instagram uses OpenCLI to reuse the user's instagram.com session in Chrome. First run `agent-reach doctor --json` to check the `active_backend` for instagram; it should normally be `OpenCLI`. Do not revert to instaloader by default; it has historically had unstable cookie handling and 401/429 errors.

```bash
# Search users (not site-wide keyword search for posts)
opencli instagram search "query" -f yaml

# User profile
opencli instagram profile nasa -f yaml

# User's recent posts
opencli instagram user nasa --limit 12 -f yaml

# Explore / Discover
opencli instagram explore --limit 20 -f yaml

# Current account's saved posts
opencli instagram saved --limit 20 -f yaml
```

> Requires Chrome to be open with the OpenCLI extension installed and signed in to instagram.com. `instagram search` searches for users; to read posts, first identify a username, then use `instagram user USERNAME`. If you see 429 / login required, ask the user to sign in again in Chrome and reduce the request frequency.
